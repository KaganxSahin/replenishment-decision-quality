# Graduation Project Report - Draft

**Project:** Replenishment Decision Quality: A Simulation-Based Evaluation and
Monitoring Framework for ML-Driven Retail Stock Distribution
**Author:** Kagan Sahin
**Date:** October 2026

> Draft status: Week 1 sections (definition) and Week 2 sections (scope and
> requirements) written, then revised within Week 2 after finalizing the
> data-independence decision (see Section 10). These will be extended weekly
> as the project develops.

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
evaluating a real system on confidential production data is rarely possible
- and even aggregate statistics derived from it can be sensitive - the
project uses a fully self-contained simulation: a synthetic retail world,
built from general retail domain knowledge only, in which every decision can
be measured against a known ground truth, and in which the evaluation
framework itself can be validated by injecting errors with known causes
before it is ever applied to a real forecaster.

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
of depending on confidential production data - or even on statistics derived
from it - the project builds a fully self-contained synthetic retail world: a
fictional multi-category retail chain whose behaviour (seasonality, store and
product heterogeneity) is based only on general, publicly known retail domain
knowledge. This makes the entire evaluation pipeline reproducible by anyone
with no external dependency, while the known ground truth of the simulation
enables measurements that are impossible on real data - such as comparing
forecasts to true demand rather than to censored sales - and allows the
evaluation framework itself to be validated by injecting forecast errors with
precisely known causes before it is ever applied to a real forecaster.

## 4. Project Objective

The objective is to develop a simulation-based evaluation and monitoring
framework for ML-driven replenishment decisions that:

1. generates a realistic synthetic retail world (stores, products, warehouse
   stock, daily sales history, and a hidden future period with known true
   demand) using only general retail domain knowledge, with no real or
   confidential data of any kind;
2. provides forecasts through a pluggable interface: a built-in
   error-injection emulator (for self-validating the evaluation framework)
   and, optionally, a real statistical/ML model trained on the synthetic
   history;
3. simulates rule-based replenishment decisions (minimum stock levels, pack
   sizes, warehouse availability) and the resulting store inventory and
   sales;
4. computes forecast-accuracy metrics (WAPE, MAPE, bias) at store-product
   level and aggregates them by store, product category, and season;
5. classifies the causes of forecast-vs-shipped deviations (model error,
   stock constraint, rule constraint, other), validated with known-answer
   tests before being applied to any forecaster;
6. presents results in an interactive dashboard.

## 5. Preliminary Scope

### 5.1 In scope (first version)

- Synthetic retail world generator with known ground truth (no real data).
- Pluggable forecaster interface with a built-in error-injection emulator.
- Optional real forecasting model using the same interface.
- Rule-based replenishment simulator.
- Forecast-accuracy metrics and multi-level aggregation (store, category,
  season).
- Deviation-cause classification, validated with known-answer tests.
- Interactive dashboard for exploring the results.
- Unit and integration tests for the generator, emulator, metrics, and
  classification logic.

### 5.2 Out of scope (first version)

- Any use of real or confidential data, or any parameter calibrated from such
  data (the project runs fully on synthetic data based on general domain
  knowledge).
- Modifying a production replenishment engine (the project evaluates
  decisions; it does not optimize them).
- Automatic retraining or tuning of forecasting models.
- Real-time or streaming analysis.
- Customer-level analysis and price optimization.
- A database connector (an optional one may be added later as an extension
  outside this graduation project).

## 6. Project Scope (Week 2 Update)

The confirmed scope of the first version covers the five pipeline
components: synthetic retail world generation, the pluggable forecaster
(built-in error-injection emulator plus an optional real model), the
rule-based replenishment simulator, the evaluation framework (metrics and
deviation-cause classification, validated with known-answer tests), and the
interactive dashboard, supported by automated tests. Explicitly excluded:
any use of real or confidential data (or parameters derived from it),
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
actionable. A second, equally important need is trust in the measurement
tool itself: before the evaluation framework is applied to any forecaster,
it must be shown to recover known deviation causes correctly, which is why
the forecaster interface includes a controllable error-injection emulator.
This analysis directly motivates FR-02 (emulator), FR-05, and FR-06 as the
core of the system.

## 8. Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | The system shall generate a synthetic retail world - stores, products, a central warehouse, daily sales history, and a hidden future period with known true demand - from user-specified parameters and a random seed, using only general retail domain knowledge (never real or confidential data, nor statistics derived from it). | Must |
| FR-02 | The system shall provide a pluggable forecaster interface and a built-in parametric error-injection emulator capable of producing forecasts with controllable, precisely known error characteristics (bias, variance, seasonal drift). | Must |
| FR-03 | The system shall optionally support a real forecasting model (statistical or ML-based) trained purely on the synthetic history, implementing the same forecaster interface as the emulator. | Should |
| FR-04 | The system shall simulate rule-based replenishment decisions (minimum stock level, pack size, warehouse availability) and the resulting store inventory, sales, and stock-out days. | Must |
| FR-05 | The system shall compute forecast-accuracy metrics (WAPE, MAPE, bias) at store-product level and aggregate them by store, product category, and season. | Must |
| FR-06 | The system shall classify each forecast-vs-shipped deviation by cause: model error, stock constraint, rule constraint, or other. | Must |
| FR-07 | The system shall display metrics, deviation-cause distributions, and outcome indicators (stock-outs, overstock, lost sales) in an interactive dashboard with store, category, and date filters. | Should |

## 9. Non-Functional Requirements

| ID | Quality | Requirement | How to Verify |
|----|---------|-------------|---------------|
| NFR-01 | Performance | With the default configuration (30 stores, 300 products, 2 years of daily history), the synthetic world generator shall complete within 60 seconds on the development laptop. | Timed test run of the generator, recorded as testing evidence in Week 6. |
| NFR-02 | Reproducibility | With identical parameters and random seed, the system shall produce identical datasets and identical evaluation results across repeated runs. | Automated test: run the pipeline twice with the same seed and compare output checksums / DataFrame equality. |
| NFR-03 | Correctness | (a) Metric implementations (WAPE, MAPE, bias) shall return values that match hand-calculated results on a small fixed test dataset. (b) When the error-injection emulator (FR-02) produces a deviation with a single known cause, the deviation classifier (FR-06) shall recover that exact cause. | Unit tests with hand-computed expected metric values, and known-answer classification tests driven by the emulator (pytest, Week 6). |
| NFR-04 | Data Independence | The full pipeline (generate -> forecast -> simulate -> evaluate -> dashboard) shall run end to end without any database connection, external API call, or real data file; only generated data and a small committed synthetic test fixture are used. | Run the default pipeline on a machine with no network access and no database configured; it must complete successfully. |

## 10. Constraints and Assumptions

**Constraints:**

1. No real or confidential data - and no parameter derived from such data -
   may be used anywhere in the project; the generator's behaviour is informed
   only by general, non-proprietary retail domain knowledge.
2. Single developer with a fixed 9-week timeline alongside a part-time
   internship; compute resources limited to a consumer laptop.

**Assumptions:**

1. A parametric error-injection emulator with controllable bias, variance,
   and seasonal drift is a sufficient proxy for the range of forecast-error
   patterns a real ML-driven replenishment system can exhibit - sufficient
   both to validate the evaluation framework under known conditions and to
   demonstrate its use.

Because calibration is based on general retail domain knowledge rather than
any specific dataset, the project validates the *evaluation methodology*
under controlled, known conditions; it does not measure the real accuracy of
any specific company's system. The component design (a standard forecaster
interface and standard input tables) keeps a future connection to a real data
source possible outside the scope of this graduation project.

## 11. Use Cases / User Stories

### US-01: Forecast accuracy by segment (FR-05, FR-07)

> As a retail analytics team member, I want to see forecast accuracy (WAPE,
> MAPE, bias) broken down by store, product category, and season, so that I
> can identify where the replenishment system performs poorly.

Acceptance criteria: (1) given a completed evaluation run, when the user
selects a store and category filter, the displayed metrics equal the values
recomputed from the raw records for that segment; (2) when no filter is
selected, overall metrics for the entire dataset are displayed.

### US-02: Deviation cause analysis (FR-04, FR-06)

> As an ML engineer, I want forecast-vs-shipped deviations classified by
> cause (model error, stock constraint, rule constraint), so that I know
> whether to improve the forecaster, the rules, or warehouse operations.

Acceptance criteria: (1) given a day on which the warehouse held less stock
than requested, the deviation for that store-product pair is labeled "stock
constraint"; (2) given a day on which the shipped quantity was rounded down
to a multiple of the pack size, the deviation is labeled "rule constraint".

### US-03: Reproducible experiments with no external dependencies (FR-01, NFR-02, NFR-04)

> As a demand planner, I want to regenerate the synthetic retail world with
> a specific seed and custom parameters, with no database or external file
> required, so that I can reproduce experiments and share exact
> configurations with anyone.

Acceptance criteria: (1) running the generation twice with the same seed and
parameters produces identical output (checksum equality); (2) the full
pipeline runs successfully on a machine with no database configured and no
network access.

### US-04: Framework self-validation through controlled error injection (FR-02, FR-06, NFR-03)

> As the developer, I want to inject forecast errors with precisely known
> causes using the emulator, so that I can verify the evaluation framework
> attributes each deviation to the correct cause before trusting it on any
> real forecaster.

Acceptance criteria: (1) given a store-product-day where only a stock
constraint was injected, the classifier labels the deviation "stock
constraint" and not any other cause; (2) given a store-product-day where
only a rule constraint was injected, the classifier labels the deviation
"rule constraint" and not any other cause.

## 12. Development Plan

| Week | Project-Specific Deliverable |
|------|------------------------------|
| 3 | Component and data-flow design: module layout, synthetic world table schema (stores, products, sales, warehouse, decisions), forecaster interface definition, technology decisions with justification. |
| 4 | Working prototype: the synthetic world generator produces 1 year of daily sales for a small world (e.g., 10 stores, 200 products) with category seasonality, deterministically from a fixed seed; no real data or external file is read. |
| 5 | Core functionality: error-injection emulator, optional real forecaster, replenishment simulator, WAPE/MAPE/bias computation, deviation classification, first dashboard page. |
| 6 | Testing and validation evidence: known-answer tests proving the deviation classifier recovers emulator-injected causes correctly, metric correctness tests (hand-computed examples), generator determinism test, timed performance run. |
| 7 | Reproducibility: single-command pipeline (install + run) with no database or external file dependency, requirements.txt, setup guide in README, peer clone-and-run test. |
| 8 | Completed report, professional README, masked/sample screenshots of the dashboard and pipeline outputs. |
| 9 | Final demonstration: live end-to-end run (generate -> forecast -> simulate -> evaluate -> dashboard), including the self-validation (known-answer) results, and presentation. |
