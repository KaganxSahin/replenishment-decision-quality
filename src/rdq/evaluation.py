from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class EvaluationResult:
    metrics: pd.DataFrame
    cause_summary: pd.DataFrame


def _calculate_metrics(group: pd.DataFrame) -> dict[str, Any]:
    actual = group["qty_true"].to_numpy(dtype=float)
    forecast = group["qty_forecast"].to_numpy(dtype=float)
    error = forecast - actual
    total_actual = float(actual.sum())
    nonzero_actual = actual > 0
    return {
        "observations": len(group),
        "wape": float(np.abs(error).sum() / total_actual) if total_actual else np.nan,
        "mape": float(np.mean(np.abs(error[nonzero_actual] / actual[nonzero_actual])))
        if nonzero_actual.any()
        else np.nan,
        "bias": float(error.sum() / total_actual) if total_actual else np.nan,
    }


def _season(month: int) -> str:
    if month in (12, 1, 2):
        return "winter"
    if month in (3, 4, 5):
        return "spring"
    if month in (6, 7, 8):
        return "summer"
    return "autumn"


def _metric_rows(
    frame: pd.DataFrame,
    level: str,
    group_columns: list[str],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not group_columns:
        rows.append({"level": level, **_calculate_metrics(frame)})
        return rows
    for key, group in frame.groupby(group_columns, sort=True, dropna=False):
        keys = key if isinstance(key, tuple) else (key,)
        rows.append({
            "level": level,
            **dict(zip(group_columns, keys)),
            **_calculate_metrics(group),
        })
    return rows


def evaluate_results(outcomes: pd.DataFrame) -> EvaluationResult:
    required = {
        "date",
        "store_id",
        "product_id",
        "category",
        "qty_forecast",
        "qty_true",
        "deviation_cause",
        "lost_sales",
    }
    if not isinstance(outcomes, pd.DataFrame):
        raise TypeError("outcomes must be a pandas DataFrame")
    missing = required - set(outcomes.columns)
    if missing:
        raise ValueError(f"outcomes is missing required columns: {', '.join(sorted(missing))}")
    if outcomes.empty:
        raise ValueError("outcomes must not be empty")
    frame = outcomes.copy()
    for column in ("qty_forecast", "qty_true", "lost_sales"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
        values = frame[column].to_numpy(dtype=float)
        if not np.isfinite(values).all() or (values < 0).any():
            raise ValueError(f"outcomes.{column} must contain finite non-negative values")
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    if frame[["date", "store_id", "product_id", "category", "deviation_cause"]].isna().any().any():
        raise ValueError("outcomes keys, category, and deviation_cause must not be missing")
    allowed_causes = {"model error", "stock constraint", "rule constraint", "other"}
    unexpected_causes = set(frame["deviation_cause"]) - allowed_causes
    if unexpected_causes:
        raise ValueError(f"outcomes contains unsupported deviation causes: {', '.join(sorted(unexpected_causes))}")
    if frame.duplicated(["date", "store_id", "product_id"]).any():
        raise ValueError("outcomes must have one row per date, store, and product")
    if not np.equal(frame["qty_true"].to_numpy(dtype=float), np.floor(frame["qty_true"])).all():
        raise ValueError("outcomes.qty_true must contain whole units")
    frame["season"] = frame["date"].dt.month.map(_season)

    metric_rows: list[dict[str, Any]] = []
    groupings = (
        ("overall", []),
        ("store", ["store_id"]),
        ("product_category", ["category"]),
        ("season", ["season"]),
        ("store_product", ["store_id", "product_id"]),
    )
    for level, columns in groupings:
        metric_rows.extend(_metric_rows(frame, level, columns))
    metrics = pd.DataFrame(metric_rows)

    cause_summary = (
        frame.groupby("deviation_cause", sort=True)
        .agg(observations=("deviation_cause", "size"), lost_sales=("lost_sales", "sum"))
        .reset_index()
    )
    total_observations = int(cause_summary["observations"].sum())
    total_lost_sales = float(cause_summary["lost_sales"].sum())
    cause_summary["observation_share"] = cause_summary["observations"] / total_observations
    cause_summary["lost_sales_share"] = (
        cause_summary["lost_sales"] / total_lost_sales if total_lost_sales else 0.0
    )
    return EvaluationResult(metrics=metrics, cause_summary=cause_summary)
