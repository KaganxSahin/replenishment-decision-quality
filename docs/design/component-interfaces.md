# Component Interfaces and Data Dictionary (Week 3)

Concrete interfaces and data structures the Week 4 prototype will be built
against. All data is synthetic, generated from a seed; no real data is used.

## 1. Forecaster Interface (the pluggable contract)

Every forecaster (emulator and optional real model) implements the same
interface so they are interchangeable:

```python
class Forecaster(Protocol):
    def fit(self, sales_history: pd.DataFrame) -> None: ...
    def predict(self, horizon: int) -> pd.DataFrame: ...
        # returns columns: [date, store_id, product_id, qty_forecast]
        # qty_forecast is non-negative float; one row per store-product-date
```

- `sales_history` schema: `date`, `store_id`, `product_id`, `qty`.
- The emulator adds its error profile as constructor parameters
  (`bias`, `variance`, `seasonal_drift`, `seed`), all deterministic.
- The optional real model fits lag/rolling features from the same history.

## 2. Pipeline Entry Point

```
python -m rdq.pipeline --seed 42 --config config/default.yaml
```

Reads a config, then runs generate -> forecast -> simulate -> evaluate and
launches the dashboard. No database, network, or real data file is required
(NFR-04). The same seed reproduces the entire run (NFR-02).

## 3. Data Dictionary (world and pipeline tables)

### stores
| Field | Type | Notes |
|-------|------|-------|
| store_id | int | primary key |
| store_size | enum {S,M,L} | drives base demand scale |
| region | enum | drives regional seasonality shift |

### products
| Field | Type | Notes |
|-------|------|-------|
| product_id | int | primary key |
| category | enum | e.g., 6 top-level categories; drives seasonality profile |
| base_price | float | representative (not calibrated from real data) |
| pack_size | int | replenishment rule parameter K |

### warehouse
| Field | Type | Notes |
|-------|------|-------|
| date | date | |
| product_id | int | |
| qty_available | int | warehouse availability W |

### sales_history (training window)
| Field | Type | Notes |
|-------|------|-------|
| date | date | daily grain |
| store_id | int | FK stores |
| product_id | int | FK products |
| qty | int | observed sales in training window |

### true_demand (hidden future, evaluation-only)
| Field | Type | Notes |
|-------|------|-------|
| date | date | future period |
| store_id | int | |
| product_id | int | |
| qty_true | int | uncensored demand (ground truth) |

### forecasts (forecaster output)
| Field | Type | Notes |
|-------|------|-------|
| date | date | |
| store_id | int | |
| product_id | int | |
| qty_forecast | float | non-negative |

### decisions (simulator output)
| Field | Type | Notes |
|-------|------|-------|
| date | date | |
| store_id | int | |
| product_id | int | |
| qty_requested | int | max(forecast, min_stock) |
| qty_shipped | int | after pack-size rounding and warehouse cap |

### outcomes (simulator output)
| Field | Type | Notes |
|-------|------|-------|
| date | date | |
| store_id | int | |
| product_id | int | |
| qty_sold | int | min(shipped, true demand) |
| lost_sales | int | max(0, true demand - shipped) |
| stock_out | bool | lost_sales > 0 |

## 4. Storage, Validity, Privacy, and Security Notes

- **Where data lives:** all pipeline data is held in memory (pandas
  DataFrames) during a run and is not persisted by default - there is no
  database and no data file. A run can optionally export the generated world
  and evaluation outputs to local CSV files for inspection (an explicit
  `--export-dir` flag); those exports are synthetic, derived from the seed,
  and safe to share. The only committed data is a tiny, hand-written
  synthetic test fixture for unit tests.
- **Validity:** referential integrity is enforced by construction (all
  store_id/product_id values come from the generated `stores`/`products`
  tables); quantities are non-negative; dates form a contiguous range.
- **Privacy / authorization:** no personal data, no real retailer data, and
  no statistics derived from real data are present anywhere; there is nothing
  to anonymize and no access control is needed.
- **Secure storage:** not applicable - no secrets, credentials, or external
  connections exist in the default pipeline (the optional future connector is
  out of scope and never committed). No real passwords, API keys, or tokens
  appear in the repository.
