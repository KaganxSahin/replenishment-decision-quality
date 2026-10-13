# Architecture Overview

> Status: conceptual design (Week 2). Detailed diagrams and technology
> decisions will be added in Week 3.

## Pipeline

```
+------------------+     +-------------------+     +------------------------+
|  1. SYNTHETIC    |     |  2. FORECAST      |     |  3. REPLENISHMENT      |
|     WORLD        | --> |     ENGINE        | --> |     SIMULATOR          |
|     GENERATOR    |     |                   |     |                        |
|                  |     | ML + statistical  |     | forecast + business    |
| stores, products,|     | models produce    |     | rules -> daily ship    |
| warehouse, 2y    |     | store-product     |     | decisions per store    |
| sales history,   |     | demand forecasts  |     | and product            |
| hidden future    |     |                   |     |                        |
| (ground truth)   |     |                   |     |                        |
+------------------+     +-------------------+     +-----------+------------+
                                                               |
                                                               v
+----------------------+     +--------------------------------------------+
|  5. DASHBOARD        |     |  4. EVALUATION FRAMEWORK                   |
|                      | <-- |                                            |
| interactive charts,  |     | - forecast vs actual demand (accuracy:     |
| drill-downs by       |     |   WAPE, MAPE, bias)                        |
| store / category /   |     | - forecast vs shipped (deviation causes:    |
| season               |     |   model error / stock constraint /         |
|                      |     |   rule constraint / other)                 |
|                      |     | - outcomes: stock-outs, overstock,         |
|                      |     |   lost sales                               |
+----------------------+     +--------------------------------------------+
```

## Components

| # | Component | Responsibility |
|---|-----------|----------------|
| 1 | Synthetic world generator | Creates a fictional footwear retailer: stores, products, warehouse stock, and two years of daily sales, plus a hidden future period whose true demand is known only to the evaluation step. Statistical behaviour (seasonality, store/product profiles) is calibrated from real retail patterns; the generated data is fully artificial. |
| 2 | Forecast engine | Trains selected forecasting models (e.g., LightGBM, SARIMAX-style baselines) on the synthetic history and produces store-product level demand forecasts for the next horizons. |
| 3 | Replenishment simulator | Turns forecasts into distribution decisions by applying business rules (minimum stock levels, pack sizes, warehouse availability), then simulates the future: inventory movements, sales, and stock-outs. |
| 4 | Evaluation framework | The core deliverable. Compares (a) forecasts vs true demand, (b) forecasts vs shipped quantities, and (c) decisions vs outcomes; classifies deviation causes and aggregates everything by store, category, and season. |
| 5 | Dashboard | Interactive presentation layer (Streamlit) with drill-downs and worst/best performer views. |

## Design Principles

- **No real data anywhere.** All data in the repository is generated. The
  generator itself is parameterized; real records are never copied or masked.
- **Known ground truth.** Because the simulation generates the future, the
  framework can measure forecast accuracy against true demand (not just
  against censored sales), which is impossible with real retail data.
- **Separation of concerns.** Each component is an independent Python module
  with clear inputs and outputs, so the evaluation framework could later be
  pointed at a real replenishment system's exports instead of the simulator.
- **Reproducibility.** A single entry point with a fixed seed regenerates the
  whole world and pipeline end to end.
