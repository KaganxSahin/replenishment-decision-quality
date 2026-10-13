# Graduation Project Report - Draft

**Project:** Replenishment Decision Quality: A Simulation-Based Evaluation and
Monitoring Framework for ML-Driven Retail Stock Distribution
**Author:** Kagan Sahin
**Date:** October 2026

> Draft status: Week 1 sections (definition) and Week 2 sections (scope and
> requirements) written. These will be extended weekly as the project
> develops.

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

## 6. Project Scope (Week 2 Update)

The confirmed scope of the first version covers the five pipeline components:
synthetic retail world generation, the forecasting engine, the rule-based
replenishment simulator, the evaluation framework (metrics and
deviation-cause classification), and the interactive dashboard, supported by
automated tests. Explicitly excluded: any use of real or confidential data,
modifying a production replenishment engine, automatic model retraining,
real-time streaming analysis, customer-level analysis, and price
optimization. The full specification, including priorities and acceptance
criteria, is maintained in `docs/requirements.md`.

## 7. Requirements Analysis

The system serves three stakeholder groups with distinct needs. Retail
analytics and planning teams need aggregated, segment-level views of system
performance to steer improvement efforts. Category managers and demand
planners need stock-health indicators (stock-outs, overstock) for their
product ranges. ML engineers need model-level feedback (forecast accuracy,
systematic bias) separated from operational effects (warehouse shortages,
rule constraints), because each of these problems has a different owner.
The unifying need is traceability: every observed error should be
attributable to a cause, so that responsibility for improvement is
actionable. This analysis directly motivates the functional requirements
FR-04 and FR-05 as the core of the system.

## 8. Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | The system shall generate a synthetic retail world - stores, products, a central warehouse, daily sales history, and a hidden future period with known true demand - from user-specified parameters and a random seed. | Must |
| FR-02 | The system shall produce store-product level demand forecasts for a chosen horizon from the synthetic sales history, using at least one statistical baseline and one machine-learning model. | Must |
| FR-03 | The system shall simulate rule-based replenishment decisions (minimum stock level, pack size, warehouse availability) and the resulting store inventory, sales, and stock-out days. | Must |
| FR-04 | The system shall compute forecast-accuracy metrics (WAPE, MAPE, bias) at store-product level and aggregate them by store, product category, and season. | Must |
| FR-05 | The system shall classify each forecast-vs-shipped deviation by cause: model error, stock constraint, rule constraint, or other. | Must |
| FR-06 | The system shall display metrics, deviation-cause distributions, and outcome indicators (stock-outs, overstock, lost sales) in an interactive dashboard with store, category, and date filters. | Should |

## 9. Non-Functional Requirements

| ID | Quality | Requirement | How to Verify |
|----|---------|-------------|---------------|
| NFR-01 | Performance | With the default configuration (30 stores, 300 products, 2 years of daily history), the synthetic world generator shall complete within 60 seconds on the development laptop. | Timed test run of the generator, recorded as testing evidence in Week 6. |
| NFR-02 | Reproducibility | With identical parameters and random seed, the system shall produce identical datasets and identical evaluation results across repeated runs. | Automated test: run the pipeline twice with the same seed and compare output checksums / DataFrame equality. |
| NFR-03 | Correctness | Metric implementations (WAPE, MAPE, bias) shall return values that match hand-calculated results on a small fixed test dataset. | Unit tests with hand-computed expected values (pytest, Week 6). |

## 10. Constraints and Assumptions

**Constraints:**

1. No real or confidential data may be used at any point (industry partner
   requirement); all validation therefore happens on synthetic data.
2. Single developer with a fixed 9-week timeline alongside a part-time
   internship; compute resources limited to a consumer laptop.

**Assumptions:**

1. The simulated rule structure (minimum stock, pack size, warehouse
   availability) captures the essential decision dynamics of real
   replenishment systems, and synthetic data calibrated from aggregate
   retail patterns is realistic enough to validate the framework.

Because no real data is used, the project demonstrates the *evaluation
methodology*, not measured facts about any real retailer; the component
design keeps a future connection to a real data source possible.

## 11. Use Cases / User Stories

### US-01: Forecast accuracy by segment (FR-04, FR-06)

> As a retail analytics team member, I want to see forecast accuracy (WAPE,
> MAPE, bias) broken down by store, product category, and season, so that I
> can identify where the replenishment system performs poorly.

Acceptance criteria: (1) given a completed evaluation run, when the user
selects a store and category filter, the displayed metrics equal the values
recomputed from the raw records for that segment; (2) when no filter is
selected, overall metrics for the entire dataset are displayed.

### US-02: Deviation cause analysis (FR-03, FR-05)

> As an ML engineer, I want forecast-vs-shipped deviations classified by
> cause (model error, stock constraint, rule constraint), so that I know
> whether to improve the model, the rules, or warehouse operations.

Acceptance criteria: (1) given a day on which the warehouse held less stock
than requested, the deviation for that store-product pair is labeled "stock
constraint"; (2) given a day on which the shipped quantity was rounded down
to a multiple of the pack size, the deviation is labeled "rule constraint".

### US-03: Reproducible experiments (FR-01, NFR-02)

> As a demand planner, I want to regenerate the synthetic retail world with
> a specific seed and custom parameters, so that I can reproduce experiments
> and share exact configurations.

Acceptance criteria: (1) running the generation twice with the same seed and
parameters produces identical output (checksum equality); (2) changing a
parameter (e.g., number of stores) is reflected in the generated output.

## 12. Development Plan

| Week | Project-Specific Deliverable |
|------|------------------------------|
| 3 | Component and data-flow design: module layout, synthetic world table schema (stores, products, sales, warehouse, decisions), technology decisions with justification. |
| 4 | Working prototype: the synthetic world generator produces 1 year of daily sales for a small world (e.g., 10 stores, 200 products) with category seasonality, deterministically from a fixed seed. |
| 5 | Core functionality: forecast engine (baseline + one ML model), replenishment simulator, WAPE/MAPE/bias computation, deviation classification, first dashboard page. |
| 6 | Testing and validation evidence: unit tests for generator determinism and metric correctness (hand-computed examples), timed performance run, documented results. |
| 7 | Reproducibility: single-command pipeline (install + run), requirements.txt, setup guide in README, peer clone-and-run test. |
| 8 | Completed report, professional README, masked screenshots of the dashboard and pipeline outputs. |
| 9 | Final demonstration: live end-to-end run (generate -> forecast -> simulate -> evaluate -> dashboard) and presentation. |
