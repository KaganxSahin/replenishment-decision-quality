# Graduation Project Report - Draft

**Project:** Replenishment Decision Quality: A Simulation-Based Evaluation and
Monitoring Framework for ML-Driven Retail Stock Distribution
**Author:** Kagan Sahin
**Date:** October 2026

> Draft status: initial versions of the required Week 1 sections, updated
> after the Week 1 data strategy decision (fully synthetic simulation). These
> will be extended weekly as the project develops.

## 1. Introduction

Machine learning is now used routinely in retail operations, and one of its
most common applications is replenishment: deciding which products, and in
what quantities, should be distributed from central warehouses to individual
stores. A typical replenishment platform combines a sales forecasting model
with business rules such as minimum stock levels, pack sizes, and store
priorities, and produces distribution decisions every day.

Software engineering for such systems does not end at deployment. Like any
other production system, they require continuous evaluation and monitoring.
This project focuses on that often-neglected layer: measuring how good the
forecasts and the resulting replenishment decisions actually are. Because
evaluating a real system on confidential production data is rarely possible,
the project uses a simulation-based design: a fully synthetic retail world in
which every decision can be measured against a known ground truth.

## 2. Problem Statement

A production replenishment system produces daily decisions, but the quality of
those decisions is not measured in a structured way. Concretely:

1. **Forecast accuracy is not tracked systematically.** Predictions are
   compared with actual sales only occasionally and informally, so systematic
   error patterns (by store, category, or season) remain invisible.
2. **Decision deviations are unexplained.** When the quantity actually shipped
   differs from the quantity the model asked for, the difference may be
   caused by warehouse stock limits, business-rule constraints, or other
   factors. There is no automatic classification of these deviation causes.
3. **Evaluation is blocked by data confidentiality.** Real replenishment data
   is commercially sensitive, so systematic quality measurements are difficult
   to perform, share, or reproduce outside the company that owns the system.
4. **Improvement is therefore not targeted.** Without measurement, it is
   impossible to know whether effort should be spent on better models, changed
   business rules, or warehouse operations.

## 3. Motivation

The financial impact of replenishment errors is direct: stock-outs cause lost
sales and dissatisfied customers, while overstock ties up working capital and
shelf space. In seasonal retail, an over-distributed product often cannot be
sold at full price later in the season, so mistakes are expensive and largely
irreversible.

There is also a software engineering motivation. Published industry case
studies report that monitoring and evaluation are among the most commonly
neglected aspects of deployed machine learning systems, and that model
performance can degrade silently without them. A monitoring framework turns
the replenishment system from a black box into a measurable, auditable
component.

Finally, the data confidentiality problem itself motivates the design. Instead
of depending on confidential production data, the project builds a synthetic
retail world - a fictional footwear retailer - whose statistical behaviour
(seasonality, store and product profiles) is calibrated from real retail
patterns without containing any real records. This makes the entire
evaluation pipeline reproducible by anyone, while the known ground truth of
the simulation enables measurements that are impossible on real data, such as
comparing forecasts to true demand rather than to censored sales.

## 4. Project Objective

The objective is to develop a simulation-based evaluation and monitoring
framework for ML-driven replenishment decisions that:

1. generates a realistic synthetic retail world (stores, products, warehouse
   stock, two years of daily sales history, and a hidden future period with
   known true demand);
2. produces sales forecasts from the synthetic history using selected
   machine learning and statistical algorithms;
3. simulates rule-based replenishment decisions (minimum stock levels, pack
   sizes, warehouse availability) and the resulting store inventory and
   sales;
4. computes forecast-accuracy metrics (WAPE, MAPE, bias) at store-product
   level and aggregates them by store, product category, and season;
5. classifies the causes of forecast-vs-shipped deviations (model error,
   stock constraint, rule constraint, other);
6. presents results in an interactive dashboard.

## 5. Preliminary Scope

### 5.1 In scope (first version)

- Synthetic retail world generator with known ground truth.
- Forecasting engine (selected algorithms) over the synthetic history.
- Rule-based replenishment simulator.
- Forecast-accuracy metrics and multi-level aggregation (store, category,
  season).
- Deviation-cause classification.
- Interactive dashboard for exploring the results.
- Unit and integration tests for the generator, metric, and classification
  logic.

### 5.2 Out of scope (first version)

- Any use of real or confidential data (the project runs fully on synthetic
  data).
- Modifying a production replenishment engine (the project evaluates
  decisions; it does not optimize them).
- Automatic retraining or tuning of forecasting models.
- Real-time or streaming analysis.
- Customer-level analysis and price optimization.
- Multi-company or multi-schema support (an optional SQL connector for future
  real-data deployment is a planned extension).
