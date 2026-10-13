# Project Description (Week 1, updated in Week 2)

## 1. What is the title of your project?

**Replenishment Decision Quality: A Simulation-Based Evaluation and Monitoring
Framework for ML-Driven Retail Stock Distribution**

## 2. What problem are you trying to solve?

Retail chains distribute products from central warehouses to stores every day.
In modern systems these decisions are produced by a pipeline that combines
machine-learning sales forecasts with business rules such as minimum stock
levels, pack sizes, and store priorities. Once such a system is deployed, it
keeps producing decisions, but the quality of those decisions is rarely
measured in a structured way. If a store runs out of a product or accumulates
excess stock, it is hard to tell whether the root cause was a weak forecast, a
warehouse shortage, or a business-rule constraint. In addition, evaluating
such systems on real production data is often impossible, because retail data
is commercially confidential.

## 3. Why is this problem important?

Replenishment errors have direct financial consequences: stock-outs cause
lost sales, while overstock ties up working capital and shelf space. In
seasonal retail, mistakes can rarely be corrected later in the season. The
machine learning literature also shows that deployed models degrade silently
when they are not monitored. Measuring decision quality is therefore the
precondition for any targeted improvement - and a safe, reproducible way to
perform such measurements is valuable both for research and practice.

## 4. Who will use the system?

Three groups: retail analytics and planning teams who need to know where a
replenishment system performs well or poorly; category managers and demand
planners who monitor stock health for their product ranges; and ML engineers
who maintain the forecasting models and need systematic feedback about model
performance.

## 5. What is the main objective of your project?

To develop a simulation-based evaluation and monitoring framework for
ML-driven replenishment decisions: a synthetic retail world with known ground
truth, a forecasting engine, and a rule-based replenishment simulator, all
measured by an evaluation framework with an interactive dashboard. The
project runs entirely on synthetic data - no real or confidential data is used
at any point.

## 6. What are the main things you expect your system to do?

- Generate a realistic synthetic retail world: stores, products, a warehouse,
  two years of daily sales history, and a hidden future period with known true
  demand (seasonality, store and product profiles calibrated from real retail
  patterns, but fully artificial data).
- Produce sales forecasts from the synthetic history (selected machine
  learning and statistical algorithms).
- Simulate rule-based replenishment decisions (minimum stock levels, pack
  sizes, warehouse availability), store inventory, and resulting sales.
- Compute forecast-accuracy metrics (WAPE, MAPE, bias) at store-product level,
  aggregated by store, product category, and season.
- Classify the causes of forecast-vs-shipped deviations (model error, stock
  constraint, rule constraint, other).
- Present results in an interactive dashboard with drill-downs.

## 7. What will not be included in the first version of the project?

No real or confidential data is used at any point. The framework evaluates
simulated decisions; it does not modify any production replenishment engine.
Automatic model retraining, real-time streaming analysis, customer-level
analysis, and price optimization are out of scope for the first version.
