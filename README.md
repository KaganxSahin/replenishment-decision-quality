# Replenishment Decision Quality: An Evaluation and Monitoring Framework for ML-Driven Retail Stock Distribution

## Project Description

Retail chains move products from central warehouses to individual stores every day.
These distribution decisions are increasingly made by machine-learning-driven
replenishment systems, which combine sales forecasts with business rules such as
minimum stock levels, pack sizes, and store priorities.

Although such systems produce decisions daily, the *quality* of those decisions is
rarely measured in a structured way. Forecasts are seldom compared with actual
sales in a systematic manner, and when the shipped quantity differs from the
forecast, it is difficult to tell whether the cause was a model error, a warehouse
stock shortage, or a business-rule constraint. Without measurement, the system
cannot be improved in a targeted way.

This project develops an evaluation and monitoring framework for ML-driven
replenishment decisions. It is being designed and validated against a production
replenishment system of an industry partner. No confidential data is stored in
this repository; a synthetic data generator makes the full pipeline reproducible
by anyone.

## Objective

Develop a framework that can:

1. **Measure forecast accuracy** - compare ML sales forecasts with actual sales
   using standard metrics (e.g., WAPE, MAPE, bias) at store-product level.
2. **Evaluate decision quality** - compare forecast quantities with final shipped
   quantities and classify the causes of deviations (stock constraints, rule
   constraints, other).
3. **Aggregate and visualize** - break results down by store, product category,
   and season in an interactive dashboard.
4. **Stay reproducible** - generate realistic synthetic retail data with known
   ground truth so the framework can be run and tested without confidential data.

## Target Users

- Retail analytics and planning teams who need to know where the replenishment
  system performs well or poorly.
- Category managers and demand planners who monitor stock health for their
  product ranges.
- ML engineers who maintain forecasting models and need systematic feedback.

## Planned Technologies

- Python 3.12
- pandas (data processing)
- scikit-learn (metric utilities)
- Streamlit (interactive dashboard)
- PostgreSQL / any SQL data warehouse (data source)
- psycopg2 (database connector)
- pytest (testing)
- Git & GitHub (version control)

Technologies may evolve during the project.

## Current Status

Week 1 - Project definition and research.
