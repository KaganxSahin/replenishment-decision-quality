# Requirements Specification (Week 2)

## 1. Week 1 Definition Review

The primary user is a retail analytics and planning team, supported by ML
engineers who maintain the forecasting models. Their problem: a
machine-learning-driven replenishment system produces daily distribution
decisions, but nobody measures those decisions systematically - forecast
accuracy is not tracked, and when shipped quantities differ from forecasts,
the cause is unknown. The single most important result of this project is an
evaluation framework that measures forecast accuracy and classifies
forecast-vs-shipped deviations by cause (model error, stock constraint, rule
constraint), so that improvement can be targeted at the right layer. For the
first demonstrable prototype, the essential features are the synthetic world
generator and the accuracy metrics; the dashboard and additional models can
wait. One Week 1 assumption changed: validation was originally planned on
locally accessed real data, but after the industry partner's decision the
project runs entirely on synthetic data, which also makes every result fully
reproducible.

## 2. Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | The system shall generate a synthetic retail world - stores, products, a central warehouse, daily sales history, and a hidden future period with known true demand - from user-specified parameters and a random seed. | Must |
| FR-02 | The system shall produce store-product level demand forecasts for a chosen horizon from the synthetic sales history, using at least one statistical baseline and one machine-learning model. | Must |
| FR-03 | The system shall simulate rule-based replenishment decisions (minimum stock level, pack size, warehouse availability) and the resulting store inventory, sales, and stock-out days. | Must |
| FR-04 | The system shall compute forecast-accuracy metrics (WAPE, MAPE, bias) at store-product level and aggregate them by store, product category, and season. | Must |
| FR-05 | The system shall classify each forecast-vs-shipped deviation by cause: model error, stock constraint, rule constraint, or other. | Must |
| FR-06 | The system shall display metrics, deviation-cause distributions, and outcome indicators (stock-outs, overstock, lost sales) in an interactive dashboard with store, category, and date filters. | Should |

## 3. Non-Functional Requirements

| ID | Quality | Requirement | How to Verify |
|----|---------|-------------|---------------|
| NFR-01 | Performance | With the default configuration (30 stores, 300 products, 2 years of daily history), the synthetic world generator shall complete within 60 seconds on the development laptop. | Timed test run of the generator, recorded as testing evidence in Week 6. |
| NFR-02 | Reproducibility | With identical parameters and random seed, the system shall produce identical datasets and identical evaluation results across repeated runs. | Automated test: run the pipeline twice with the same seed and compare output checksums / DataFrame equality. |
| NFR-03 | Correctness | Metric implementations (WAPE, MAPE, bias) shall return values that match hand-calculated results on a small fixed test dataset. | Unit tests with hand-computed expected values (pytest, Week 6). |

## 4. Scope, Constraints and Assumptions

| Category | Content |
|----------|---------|
| In scope | Synthetic retail world generation; forecasting engine; rule-based replenishment simulation; accuracy metrics and deviation classification; interactive dashboard; automated tests. |
| Out of scope | Any use of real or confidential data; modifying a production replenishment engine; automatic model retraining; real-time streaming analysis; customer-level analysis; price optimization. |
| Constraint | No real or confidential data may be used at any point (industry partner requirement) - all validation happens on synthetic data. |
| Constraint | Single developer with a fixed 9-week timeline alongside a part-time internship; compute resources limited to a consumer laptop. |
| Assumption | The simulated rule structure (minimum stock, pack size, warehouse availability) captures the essential decision dynamics of real replenishment systems, and synthetic data calibrated from aggregate retail patterns is realistic enough to validate the framework. |

**Most important limitation:** because no real data is used, the project
demonstrates the *evaluation methodology*, not measured facts about any real
retailer. The component design keeps a future connection to a real data
source possible (the evaluation framework consumes standard tables, whether
generated or exported from a real system).

## 5. User Stories

### US-01: Forecast accuracy by segment

> As a retail analytics team member, I want to see forecast accuracy (WAPE,
> MAPE, bias) broken down by store, product category, and season, so that I
> can identify where the replenishment system performs poorly.

Acceptance criteria:

1. Given a completed evaluation run, when the user selects a store and
   category filter, then the displayed metrics equal the values recomputed
   from the raw records for that segment.
2. When no filter is selected, the system displays overall metrics for the
   entire dataset.

Linked requirements: FR-04, FR-06.

### US-02: Deviation cause analysis

> As an ML engineer, I want forecast-vs-shipped deviations classified by
> cause (model error, stock constraint, rule constraint), so that I know
> whether to improve the model, the rules, or warehouse operations.

Acceptance criteria:

1. Given a day on which the warehouse held less stock than requested, the
   deviation for that store-product pair is labeled "stock constraint".
2. Given a day on which the shipped quantity was rounded down to a multiple
   of the pack size, the deviation is labeled "rule constraint".

Linked requirements: FR-03, FR-05.

### US-03: Reproducible experiments

> As a demand planner, I want to regenerate the synthetic retail world with
> a specific seed and custom parameters, so that I can reproduce experiments
> and share exact configurations.

Acceptance criteria:

1. Running the generation twice with the same seed and parameters produces
   identical output (checksum equality).
2. Changing a parameter (e.g., number of stores) is reflected in the
   generated output.

Linked requirements: FR-01, NFR-02.

## 6. Development Milestones

| Week | Project-Specific Deliverable |
|------|------------------------------|
| 3 | Component and data-flow design: module layout, synthetic world table schema (stores, products, sales, warehouse, decisions), technology decisions with justification. |
| 4 | Working prototype: the synthetic world generator produces 1 year of daily sales for a small world (e.g., 10 stores, 200 products) with category seasonality, deterministically from a fixed seed. |
| 5 | Core functionality: forecast engine (baseline + one ML model), replenishment simulator, WAPE/MAPE/bias computation, deviation classification, first dashboard page. |
| 6 | Testing and validation evidence: unit tests for generator determinism and metric correctness (hand-computed examples), timed performance run, documented results. |
| 7 | Reproducibility: single-command pipeline (install + run), requirements.txt, setup guide in README, peer clone-and-run test. |
| 8 | Completed report, professional README, masked screenshots of the dashboard and pipeline outputs. |
| 9 | Final demonstration: live end-to-end run (generate -> forecast -> simulate -> evaluate -> dashboard) and presentation. |
