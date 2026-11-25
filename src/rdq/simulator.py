from dataclasses import dataclass
from math import ceil
from numbers import Integral
from typing import Any

import numpy as np
import pandas as pd


KEY_COLUMNS = ["date", "store_id", "product_id"]
FORECAST_COLUMNS = [*KEY_COLUMNS, "qty_forecast"]
DEMAND_COLUMNS = [*KEY_COLUMNS, "qty_true"]


@dataclass(frozen=True)
class SimulationConfig:
    minimum_stock: int = 1

    def __post_init__(self) -> None:
        if (
            isinstance(self.minimum_stock, bool)
            or not isinstance(self.minimum_stock, Integral)
            or self.minimum_stock < 0
        ):
            raise ValueError("minimum_stock must be a non-negative integer")


def _validated_frame(
    frame: pd.DataFrame,
    required_columns: list[str],
    name: str,
) -> pd.DataFrame:
    if not isinstance(frame, pd.DataFrame):
        raise TypeError(f"{name} must be a pandas DataFrame")
    missing = set(required_columns) - set(frame.columns)
    if missing:
        raise ValueError(f"{name} is missing required columns: {', '.join(sorted(missing))}")
    if frame.empty:
        raise ValueError(f"{name} must not be empty")
    return frame.loc[:, required_columns].copy()


def _numeric_column(frame: pd.DataFrame, column: str, name: str) -> None:
    frame[column] = pd.to_numeric(frame[column], errors="coerce")
    values = frame[column].to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values < 0).any():
        raise ValueError(f"{name}.{column} must contain finite non-negative values")


def _allocate_packs(requested_units: list[int], pack_size: int, available_units: int) -> list[int]:
    requested_packs = np.asarray([units // pack_size for units in requested_units], dtype=int)
    total_requested = int(requested_packs.sum())
    available_packs = min(available_units // pack_size, total_requested)
    if total_requested == 0 or available_packs == 0:
        return [0] * len(requested_units)
    if available_packs == total_requested:
        return (requested_packs * pack_size).tolist()

    exact_allocations = requested_packs * (available_packs / total_requested)
    allocated_packs = np.floor(exact_allocations).astype(int)
    remainder = available_packs - int(allocated_packs.sum())
    order = sorted(
        range(len(requested_units)),
        key=lambda index: (-(exact_allocations[index] - allocated_packs[index]), index),
    )
    for index in order:
        if remainder == 0:
            break
        if allocated_packs[index] < requested_packs[index]:
            allocated_packs[index] += 1
            remainder -= 1
    return (allocated_packs * pack_size).tolist()


def simulate_replenishment(
    forecasts: pd.DataFrame,
    true_demand: pd.DataFrame,
    products: pd.DataFrame,
    warehouse: pd.DataFrame,
    config: SimulationConfig | None = None,
) -> pd.DataFrame:
    """Run a daily, inventory-carrying simulation against opening warehouse stock."""
    settings = config or SimulationConfig()
    forecast_frame = _validated_frame(forecasts, FORECAST_COLUMNS, "forecasts")
    demand_frame = _validated_frame(true_demand, DEMAND_COLUMNS, "true_demand")
    product_frame = _validated_frame(products, ["product_id", "category", "pack_size"], "products")
    warehouse_frame = _validated_frame(
        warehouse,
        ["product_id", "qty_available"],
        "warehouse",
    )

    for frame, name in ((forecast_frame, "forecasts"), (demand_frame, "true_demand")):
        frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
        if frame[KEY_COLUMNS].isna().any().any():
            raise ValueError(f"{name} keys must not contain missing or invalid values")
        if frame.duplicated(KEY_COLUMNS).any():
            raise ValueError(f"{name} must have one row per date, store, and product")
    _numeric_column(forecast_frame, "qty_forecast", "forecasts")
    _numeric_column(demand_frame, "qty_true", "true_demand")
    demand_values = demand_frame["qty_true"].to_numpy(dtype=float)
    if not np.equal(demand_values, np.floor(demand_values)).all():
        raise ValueError("true_demand.qty_true must contain whole units")

    key_check = forecast_frame[KEY_COLUMNS].merge(
        demand_frame[KEY_COLUMNS],
        on=KEY_COLUMNS,
        how="outer",
        indicator=True,
        validate="one_to_one",
    )
    if not key_check["_merge"].eq("both").all():
        raise ValueError("forecasts and true_demand must contain identical date-store-product keys")

    if product_frame["product_id"].isna().any() or product_frame["product_id"].duplicated().any():
        raise ValueError("products must have unique, non-missing product_id values")
    product_frame["pack_size"] = pd.to_numeric(product_frame["pack_size"], errors="coerce")
    pack_sizes = product_frame["pack_size"].to_numpy(dtype=float)
    if (
        not np.isfinite(pack_sizes).all()
        or (pack_sizes < 1).any()
        or not np.equal(pack_sizes, np.floor(pack_sizes)).all()
    ):
        raise ValueError("products.pack_size must contain positive whole units")
    product_frame["pack_size"] = product_frame["pack_size"].astype(int)

    if warehouse_frame["product_id"].isna().any() or warehouse_frame["product_id"].duplicated().any():
        raise ValueError("warehouse must have unique, non-missing product_id values")
    _numeric_column(warehouse_frame, "qty_available", "warehouse")
    warehouse_values = warehouse_frame["qty_available"].to_numpy(dtype=float)
    if not np.equal(warehouse_values, np.floor(warehouse_values)).all():
        raise ValueError("warehouse.qty_available must contain whole units")
    warehouse_frame["qty_available"] = warehouse_frame["qty_available"].astype(int)

    rows = forecast_frame.merge(demand_frame, on=KEY_COLUMNS, validate="one_to_one")
    rows = rows.merge(product_frame, on="product_id", how="left", validate="many_to_one")
    if rows["pack_size"].isna().any() or rows["category"].isna().any():
        raise ValueError("every forecast product must exist in products with a category")
    warehouse_stock = warehouse_frame.set_index("product_id")["qty_available"]
    missing_stock = set(rows["product_id"]) - set(warehouse_stock.index)
    if missing_stock:
        raise ValueError("warehouse must contain stock for every forecast product")

    rows = rows.sort_values(KEY_COLUMNS, kind="stable").reset_index(drop=True)
    remaining_warehouse = warehouse_stock.to_dict()
    store_inventory: dict[tuple[Any, Any], int] = {}
    results: list[dict[str, Any]] = []

    for (day, product_id), group in rows.groupby(["date", "product_id"], sort=False):
        pack_size = int(group["pack_size"].iloc[0])
        requested_targets = [
            max(ceil(float(forecast)), settings.minimum_stock)
            for forecast in group["qty_forecast"]
        ]
        inventory_at_start = [
            store_inventory.get((store_id, product_id), 0)
            for store_id in group["store_id"]
        ]
        requested_orders = [
            max(target - on_hand, 0)
            for target, on_hand in zip(requested_targets, inventory_at_start)
        ]
        pack_limited_orders = [order - order % pack_size for order in requested_orders]
        shipped_units = _allocate_packs(
            pack_limited_orders,
            pack_size,
            int(remaining_warehouse[product_id]),
        )
        remaining_warehouse[product_id] -= sum(shipped_units)

        for position, (_, row) in enumerate(group.iterrows()):
            start_inventory = inventory_at_start[position]
            shipped = shipped_units[position]
            available_at_store = start_inventory + shipped
            actual = int(row["qty_true"])
            sold = min(available_at_store, actual)
            end_inventory = available_at_store - sold
            lost_sales = actual - sold
            forecast = float(row["qty_forecast"])
            stock_limited = shipped < pack_limited_orders[position]
            rule_reduced_order = pack_limited_orders[position] < requested_orders[position]
            model_error = not np.isclose(forecast, actual, rtol=0, atol=1e-9)
            # Lost sales can only arise from a warehouse, pack-size, or forecast
            # limitation: the minimum-stock rule raises shipments, so it must not
            # absorb losses caused by an underforecast.
            if stock_limited:
                cause = "stock constraint"
            elif rule_reduced_order:
                cause = "rule constraint"
            elif lost_sales > 0:
                cause = "model error" if model_error else "other"
            elif settings.minimum_stock > forecast:
                cause = "rule constraint"
            elif model_error:
                cause = "model error"
            else:
                cause = "other"

            store_inventory[(row["store_id"], product_id)] = end_inventory
            results.append({
                "date": day,
                "store_id": row["store_id"],
                "product_id": product_id,
                "category": row["category"],
                "qty_forecast": forecast,
                "qty_true": actual,
                "qty_requested": requested_targets[position],
                "qty_to_order": requested_orders[position],
                "qty_shipped": shipped,
                "warehouse_remaining": remaining_warehouse[product_id],
                "store_inventory_start": start_inventory,
                "store_inventory_end": end_inventory,
                "qty_sold": sold,
                "lost_sales": lost_sales,
                "overstock": max(end_inventory - requested_targets[position], 0),
                "stock_out": lost_sales > 0,
                "deviation_cause": cause,
            })

    return pd.DataFrame(results)
