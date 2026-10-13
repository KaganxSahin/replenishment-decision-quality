# Architecture Overview

> Status: conceptual design (Week 1-2). Detailed diagrams and technology
> decisions will be added in Week 3.

## Pipeline

```
+------------------+     +----------------------+     +------------------------+
|  1. SYNTHETIC    |     |  2. FORECASTER       |     |  3. REPLENISHMENT      |
|     WORLD        | --> |     (pluggable)      | --> |     SIMULATOR          |
|     GENERATOR    |     |                      |     |                        |
|                  |     |  (a) Error-injection |     | forecast + business    |
| stores, products,|     |      emulator (MUST) |     | rules -> daily ship    |
| warehouse, daily |     |      - controllable  |     | decisions per store    |
| sales history,   |     |        bias/variance/|     | and product            |
| hidden future    |     |        seasonal drift|     |                        |
| (ground truth)   |     |  (b) Optional real   |     |                        |
|                  |     |      ML/statistical  |     |                        |
| no real data,    |     |      model (SHOULD)  |     |                        |
| no calibration   |     |      - same interface|     |                        |
| from real data   |     |                      |     |                        |
+------------------+     +----------------------+     +-----------+------------+
                                                                   |
                                                                   v
+----------------------+     +--------------------------------------------+
|  5. DASHBOARD        |     |  4. EVALUATION FRAMEWORK                   |
|                      | <-- |                                            |
| interactive charts,  |     | - forecast vs true demand (accuracy:       |
| drill-downs by       |     |   WAPE, MAPE, bias)                        |
| store / category /   |     | - forecast vs shipped (deviation causes:    |
| season               |     |   model error / stock constraint /         |
|                      |     |   rule constraint / other)                 |
|                      |     | - outcomes: stock-outs, overstock,         |
|                      |     |   lost sales                               |
|                      |     | - SELF-VALIDATION: when the emulator (2a)  |
|                      |     |   injects a known-cause error, this step   |
|                      |     |   must recover that exact cause            |
+----------------------+     +--------------------------------------------+
```

## Components

| # | Component | Responsibility |
|---|-----------|----------------|
| 1 | Synthetic world generator | Creates a fictional multi-category retail chain: stores, products, warehouse stock, and daily sales, plus a hidden future period whose true demand is known only to the evaluation step. Behaviour (seasonality, store/product heterogeneity) is based on general, publicly known retail domain knowledge; no real data or statistic derived from real data is used. |
| 2 | Forecaster (pluggable interface) | A common `predict(history, horizon) -> forecasts` interface with two implementations: **(a)** a parametric error-injection emulator that can produce forecasts with precisely known, controllable error characteristics (bias, variance, seasonal drift) - this is the core, Must-have implementation and enables self-validation of the evaluation framework; **(b)** an optional real forecasting model (e.g., LightGBM or a statistical baseline) trained only on the synthetic history, implementing the same interface. |
| 3 | Replenishment simulator | Turns forecasts into distribution decisions by applying business rules (minimum stock levels, pack sizes, warehouse availability), then simulates the future: inventory movements, sales, and stock-outs. |
| 4 | Evaluation framework | The core deliverable. Compares (a) forecasts vs true demand, (b) forecasts vs shipped quantities, and (c) decisions vs outcomes; classifies deviation causes and aggregates everything by store, category, and season. Validated through known-answer tests: when the emulator (2a) injects an error with a known cause, the framework must recover that exact cause before being trusted on any forecaster's output. |
| 5 | Dashboard | Interactive presentation layer (Streamlit) with drill-downs and worst/best performer views. |

## Design Principles

- **No real data, no real-data-derived calibration, anywhere.** All data in
  the repository is generated or is a small synthetic test fixture. The
  generator's behaviour is informed only by general, non-proprietary retail
  domain knowledge (e.g., that winter categories sell more in winter), never
  by any specific company's figures.
- **Pluggable, self-validating forecaster.** Because the error-injection
  emulator can produce forecasts with a precisely known error cause, the
  evaluation framework can be proven correct under controlled conditions
  (known-answer tests) before it is ever applied to a real model's forecasts.
- **Known ground truth.** Because the simulation generates the future, the
  framework can measure forecast accuracy against true demand (not just
  against censored sales), which is impossible with real retail data.
- **Separation of concerns.** Each component is an independent Python module
  with clear inputs and outputs, so the evaluation framework could later be
  pointed at a real replenishment system's exports instead of the simulator.
- **Reproducibility and zero external dependencies.** A single entry point
  with a fixed seed regenerates the whole world and runs the full pipeline
  end to end, with no database connection or external data file required.
