# Requirements Specification (Week 2, revised)

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
generator and the error-injection emulator; the real forecasting model and
the dashboard can wait. One assumption changed during Week 2: the project
will not reuse any previous personal project or be calibrated from any real
dataset, even in aggregate form - the entire pipeline, including the
forecaster used to validate the evaluation framework, is self-contained and
based only on general retail domain knowledge.

## 2. Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | The system shall generate a synthetic retail world - stores, products, a central warehouse, daily sales history, and a hidden future period with known true demand - from user-specified parameters and a random seed, using only general retail domain knowledge (never real or confidential data, nor statistics derived from it). | Must |
| FR-02 | The system shall provide a pluggable forecaster interface and a built-in parametric error-injection emulator capable of producing forecasts with controllable, precisely known error characteristics (bias, variance, seasonal drift). | Must |
| FR-03 | The system shall optionally support a real forecasting model (statistical or ML-based) trained purely on the synthetic history, implementing the same forecaster interface as the emulator. | Should |
| FR-04 | The system shall simulate rule-based replenishment decisions (minimum stock level, pack size, warehouse availability) and the resulting store inventory, sales, and stock-out days. | Must |
| FR-05 | The system shall compute forecast-accuracy metrics (WAPE, MAPE, bias) at store-product level and aggregate them by store, product category, and season. | Must |
| FR-06 | The system shall classify each forecast-vs-shipped deviation by cause: model error, stock constraint, rule constraint, or other. | Must |
| FR-07 | The system shall display metrics, deviation-cause distributions, and outcome indicators (stock-outs, overstock, lost sales) in an interactive dashboard with store, category, and date filters. | Should |

## 3. Non-Functional Requirements

| ID | Quality | Requirement | How to Verify |
|----|---------|-------------|---------------|
| NFR-01 | Performance | With the default configuration (30 stores, 300 products, 2 years of daily history), the synthetic world generator shall complete within 60 seconds on the development laptop. | Timed test run of the generator, recorded as testing evidence in Week 6. |
| NFR-02 | Reproducibility | With identical parameters and random seed, the system shall produce identical datasets and identical evaluation results across repeated runs. | Automated test: run the pipeline twice with the same seed and compare output checksums / DataFrame equality. |
| NFR-03 | Correctness | (a) Metric implementations (WAPE, MAPE, bias) shall return values that match hand-calculated results on a small fixed test dataset. (b) When the error-injection emulator (FR-02) produces a deviation with a single known cause, the deviation classifier (FR-06) shall recover that exact cause. | Unit tests with hand-computed expected metric values, and known-answer classification tests driven by the emulator (pytest, Week 6). |
| NFR-04 | Data Independence | The full pipeline (generate -> forecast -> simulate -> evaluate -> dashboard) shall run end to end without any database connection, external API call, or real data file; only generated data and a small committed synthetic test fixture are used. | Run the default pipeline on a machine with no network access and no database configured; it must complete successfully. |

## 4. Scope, Constraints and Assumptions

| Category | Content |
|----------|---------|
| In scope | Synthetic retail world generation; pluggable forecaster interface with a built-in error-injection emulator; an optional real forecasting model; rule-based replenishment simulation; accuracy metrics and deviation classification (validated with known-answer tests); interactive dashboard; automated tests. |
| Out of scope | Any use of real or confidential data, or any parameter calibrated from such data; modifying a production replenishment engine; automatic model retraining; real-time streaming analysis; customer-level analysis; price optimization. |
| Constraint | No real or confidential data - and no parameter derived from such data - may be used anywhere in the project; the generator's behaviour is informed only by general, non-proprietary retail domain knowledge. |
| Constraint | Single developer with a fixed 9-week timeline alongside a part-time internship; compute resources limited to a consumer laptop. |
| Assumption | A parametric error-injection emulator with controllable bias, variance, and seasonal drift is a sufficient proxy for the range of forecast-error patterns a real ML-driven replenishment system can exhibit - sufficient both to validate the evaluation framework under known conditions and to demonstrate its use. |

**Most important limitation:** because calibration is based on general retail
domain knowledge rather than any specific dataset, the project validates the
*evaluation methodology* under controlled, known conditions; it does not
measure the real accuracy of any specific company's system. The component
design (a standard forecaster interface and standard input tables) keeps a
future connection to a real data source possible outside the scope of this
graduation project.

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

Linked requirements: FR-05, FR-07.

### US-02: Deviation cause analysis

> As an ML engineer, I want forecast-vs-shipped deviations classified by
> cause (model error, stock constraint, rule constraint), so that I know
> whether to improve the forecaster, the rules, or warehouse operations.

Acceptance criteria:

1. Given a day on which the warehouse held less stock than requested, the
   deviation for that store-product pair is labeled "stock constraint".
2. Given a day on which the shipped quantity was rounded down to a multiple
   of the pack size, the deviation is labeled "rule constraint".

Linked requirements: FR-04, FR-06.

### US-03: Reproducible experiments with no external dependencies

> As a demand planner, I want to regenerate the synthetic retail world with
> a specific seed and custom parameters, with no database or external file
> required, so that I can reproduce experiments and share exact
> configurations with anyone.

Acceptance criteria:

1. Running the generation twice with the same seed and parameters produces
   identical output (checksum equality).
2. The full pipeline runs successfully on a machine with no database
   configured and no network access.

Linked requirements: FR-01, NFR-02, NFR-04.

### US-04: Framework self-validation through controlled error injection

> As the developer, I want to inject forecast errors with precisely known
> causes using the emulator, so that I can verify the evaluation framework
> attributes each deviation to the correct cause before trusting it on any
> real forecaster.

Acceptance criteria:

1. Given a store-product-day where only a stock constraint was injected (the
   forecast was accurate but the warehouse could not supply the full
   quantity), the classifier labels the deviation "stock constraint" and not
   any other cause.
2. Given a store-product-day where only a rule constraint was injected (the
   forecast was accurate but the shipped quantity was rounded to a pack
   size), the classifier labels the deviation "rule constraint" and not any
   other cause.

Linked requirements: FR-02, FR-06, NFR-03.

## 6. Development Milestones

| Week | Project-Specific Deliverable |
|------|------------------------------|
| 3 | Component and data-flow design: module layout, synthetic world table schema (stores, products, sales, warehouse, decisions), forecaster interface definition, technology decisions with justification. |
| 4 | Working prototype: the synthetic world generator produces 1 year of daily sales for a small world (e.g., 10 stores, 200 products) with category seasonality, deterministically from a fixed seed; no real data or external file is read. |
| 5 | Core functionality: error-injection emulator, optional real forecaster, replenishment simulator, WAPE/MAPE/bias computation, deviation classification, first dashboard page. |
| 6 | Testing and validation evidence: known-answer tests proving the deviation classifier recovers emulator-injected causes correctly, metric correctness tests (hand-computed examples), generator determinism test, timed performance run. |
| 7 | Reproducibility: single-command pipeline (install + run) with no database or external file dependency, requirements.txt, setup guide in README, peer clone-and-run test. |
| 8 | Completed report, professional README, masked/sample screenshots of the dashboard and pipeline outputs. |
| 9 | Final demonstration: live end-to-end run (generate -> forecast -> simulate -> evaluate -> dashboard), including the self-validation (known-answer) results, and presentation. |
