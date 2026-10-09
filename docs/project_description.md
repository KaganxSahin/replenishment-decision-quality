# Project Description (Week 1)

## 1. What is the title of your project?

**Replenishment Decision Quality: An Evaluation and Monitoring Framework for ML-Driven Retail Stock Distribution**

## 2. What problem are you trying to solve?

Retail chains distribute products from central warehouses to stores every day. In
modern systems these decisions are produced by a pipeline that combines
machine-learning sales forecasts with business rules such as minimum stock
levels, pack sizes, and store priorities. Once such a system is deployed, it
keeps producing decisions, but the quality of those decisions is rarely measured
in a structured way. If a store runs out of a product or accumulates excess
stock, it is hard to tell whether the root cause was a weak forecast, a shortage
in the warehouse, or a business-rule constraint.

## 3. Why is this problem important?

Replenishment errors have direct financial consequences: stock-outs cause lost
sales, while overstock ties up working capital and shelf space. In seasonal
retail, mistakes can rarely be corrected later in the season. In addition, the
machine learning literature shows that deployed models degrade silently when
they are not monitored. Measuring decision quality is therefore the precondition
for any targeted improvement of the system.

## 4. Who will use the system?

Three groups: retail analytics and planning teams who need to know where the
replenishment system performs well or poorly; category managers and demand
planners who monitor stock health for their product ranges; and ML engineers who
maintain the forecasting models and need systematic feedback about model
performance.

## 5. What is the main objective of your project?

To develop an evaluation and monitoring framework that measures the quality of
ML-driven replenishment decisions, is validated on real-world data from an
industry partner, and remains fully reproducible without access to confidential
data through a synthetic data generator.

## 6. What are the main things you expect your system to do?

- Ingest sales, forecast, inventory, and replenishment-decision records from a
  SQL data source.
- Compute forecast-accuracy metrics (WAPE, MAPE, bias) at store-product level,
  aggregated by store, product category, and season.
- Compare forecast quantities with final shipped quantities and classify the
  causes of deviations (stock constraint, rule constraint, other).
- Present the results in an interactive dashboard with drill-downs.
- Generate realistic synthetic retail data with known ground truth for testing
  and reproducibility.

## 7. What will not be included in the first version of the project?

The framework will evaluate decisions but will not modify the production
replenishment engine itself. Automatic model retraining, real-time streaming
analysis, customer-level analysis, and price optimization are out of scope for
the first version.
