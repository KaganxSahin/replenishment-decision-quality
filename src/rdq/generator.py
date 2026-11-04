from dataclasses import dataclass
from datetime import date

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class WorldConfig:
    seed: int = 42
    stores: int = 10
    products: int = 200
    history_days: int = 365
    future_days: int = 28
    start_date: date = date(2024, 1, 1)

    def __post_init__(self) -> None:
        if self.seed < 0:
            raise ValueError("seed must be non-negative")
        for name in ("stores", "products", "history_days", "future_days"):
            if getattr(self, name) < 1:
                raise ValueError(f"{name} must be at least 1")


def generate_world(config: WorldConfig) -> dict[str, pd.DataFrame]:
    random = np.random.default_rng(config.seed)
    store_ids = np.arange(1, config.stores + 1)
    product_ids = np.arange(1, config.products + 1)
    categories = np.array(["tops", "trousers", "dresses", "outerwear", "knitwear"])
    store_sizes = random.choice(["S", "M", "L"], size=config.stores)
    regions = random.choice(["north", "central", "south"], size=config.stores)
    product_categories = random.choice(categories, size=config.products)

    stores = pd.DataFrame({
        "store_id": store_ids,
        "store_size": store_sizes,
        "region": regions,
    })
    products = pd.DataFrame({
        "product_id": product_ids,
        "category": product_categories,
        "base_price": np.round(random.uniform(20, 150, size=config.products), 2),
        "pack_size": random.choice([1, 2, 4, 6], size=config.products),
    })
    dates = pd.date_range(config.start_date, periods=config.history_days + config.future_days)
    warehouse = pd.DataFrame({
        "date": np.repeat(dates[config.history_days - 1], config.products),
        "product_id": product_ids,
        "qty_available": random.integers(100, 1001, size=config.products),
    })

    store_scale = pd.Series(store_sizes).map({"S": 0.7, "M": 1.0, "L": 1.4}).to_numpy()
    region_shift = pd.Series(regions).map({"north": 0.2, "central": 0.0, "south": -0.2}).to_numpy()
    category_phase = pd.Series(product_categories).map({
        "tops": 2.4, "trousers": 1.0, "dresses": 3.1,
        "outerwear": 0.0, "knitwear": 0.3,
    }).to_numpy()
    product_scale = random.uniform(0.5, 3.0, size=config.products)
    year_angle = 2 * np.pi * (dates.dayofyear.to_numpy() - 1) / 365.25
    seasonal = 1 + 0.35 * np.cos(
        year_angle[:, None, None] + region_shift[None, :, None] + category_phase[None, None, :]
    )
    demand_rate = seasonal * store_scale[None, :, None] * product_scale[None, None, :]
    quantities = random.poisson(demand_rate)

    def records(start: int, stop: int, quantity_name: str) -> pd.DataFrame:
        period = dates[start:stop]
        return pd.DataFrame({
            "date": np.repeat(period.to_numpy(), config.stores * config.products),
            "store_id": np.tile(np.repeat(store_ids, config.products), len(period)),
            "product_id": np.tile(product_ids, len(period) * config.stores),
            quantity_name: quantities[start:stop].reshape(-1),
        })

    return {
        "stores": stores,
        "products": products,
        "warehouse": warehouse,
        "sales_history": records(0, config.history_days, "qty"),
        "true_demand": records(config.history_days, len(dates), "qty_true"),
    }
