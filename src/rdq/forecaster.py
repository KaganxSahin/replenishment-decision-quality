from dataclasses import dataclass
from numbers import Integral, Real
from typing import Protocol

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class EmulatorConfig:
    seed: int = 42
    bias: float = 0.0
    variance: float = 0.01
    seasonal_drift: float = 0.1
    baseline_days: int = 28

    def __post_init__(self) -> None:
        if (
            isinstance(self.seed, bool)
            or not isinstance(self.seed, Integral)
            or self.seed < 0
        ):
            raise ValueError("seed must be a non-negative integer")
        if (
            isinstance(self.baseline_days, bool)
            or not isinstance(self.baseline_days, Integral)
            or self.baseline_days < 1
        ):
            raise ValueError("baseline_days must be a positive integer")
        for name in ("bias", "variance", "seasonal_drift"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, Real) or not np.isfinite(value):
                raise ValueError(f"{name} must be a finite number")
        if self.bias < -1:
            raise ValueError("bias must be at least -1")
        if self.variance < 0:
            raise ValueError("variance must be non-negative")
        if self.seasonal_drift < 0:
            raise ValueError("seasonal_drift must be non-negative")


class Forecaster(Protocol):
    def fit(self, sales_history: pd.DataFrame) -> None: ...

    def predict(self, horizon: int) -> pd.DataFrame: ...


class ErrorInjectionEmulator:
    required_columns = ("date", "store_id", "product_id", "qty")

    def __init__(self, config: EmulatorConfig | None = None) -> None:
        self.config = config or EmulatorConfig()
        self._pairs: pd.DataFrame | None = None
        self._last_date: pd.Timestamp | None = None

    def fit(self, sales_history: pd.DataFrame) -> None:
        if not isinstance(sales_history, pd.DataFrame):
            raise TypeError("sales_history must be a pandas DataFrame")
        missing = set(self.required_columns) - set(sales_history.columns)
        if missing:
            raise ValueError(f"sales_history is missing required columns: {', '.join(sorted(missing))}")
        if sales_history.empty:
            raise ValueError("sales_history must not be empty")

        history = sales_history.loc[:, self.required_columns].copy()
        history["date"] = pd.to_datetime(history["date"], errors="coerce")
        history["qty"] = pd.to_numeric(history["qty"], errors="coerce")
        if history[["date", "store_id", "product_id", "qty"]].isna().any().any():
            raise ValueError("sales_history must not contain missing or invalid values")
        if not np.isfinite(history["qty"].to_numpy(dtype=float)).all():
            raise ValueError("sales_history quantities must be finite")
        if (history["qty"] < 0).any():
            raise ValueError("sales_history quantities must be non-negative")
        if history.duplicated(["date", "store_id", "product_id"]).any():
            raise ValueError("sales_history must have one row per date, store, and product")

        history = history.sort_values(["date", "store_id", "product_id"], kind="stable")
        recent = history.groupby(["store_id", "product_id"], sort=False).tail(self.config.baseline_days)
        baselines = (
            recent.groupby(["store_id", "product_id"], sort=False)["qty"]
            .mean()
            .rename("baseline")
            .reset_index()
        )
        pairs = history[["store_id", "product_id"]].drop_duplicates().merge(
            baselines,
            on=["store_id", "product_id"],
            how="left",
            validate="one_to_one",
        )
        self._pairs = pairs.reset_index(drop=True)
        self._last_date = history["date"].max()

    def predict(self, horizon: int) -> pd.DataFrame:
        if self._pairs is None or self._last_date is None:
            raise RuntimeError("fit must be called with sales_history before predict")
        if isinstance(horizon, bool) or not isinstance(horizon, Integral) or horizon < 1:
            raise ValueError("horizon must be a positive integer")

        forecast_dates = pd.date_range(self._last_date + pd.Timedelta(days=1), periods=horizon)
        baseline = self._pairs["baseline"].to_numpy(dtype=float)
        day_of_year = forecast_dates.dayofyear.to_numpy(dtype=float)
        annual_cycle = np.sin(2 * np.pi * (day_of_year - 1) / 365.25)[:, None]
        expected = baseline[None, :] * (
            1 + self.config.bias + self.config.seasonal_drift * annual_cycle
        )
        random = np.random.default_rng(self.config.seed)
        noise = random.normal(
            loc=0.0,
            scale=np.sqrt(self.config.variance) * baseline[None, :],
            size=(horizon, len(self._pairs)),
        )
        quantities = np.maximum(0.0, expected + noise).reshape(-1)

        return pd.DataFrame({
            "date": np.repeat(forecast_dates.to_numpy(), len(self._pairs)),
            "store_id": np.tile(self._pairs["store_id"].to_numpy(), horizon),
            "product_id": np.tile(self._pairs["product_id"].to_numpy(), horizon),
            "qty_forecast": quantities,
        })
