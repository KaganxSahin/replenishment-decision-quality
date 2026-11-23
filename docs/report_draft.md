# Graduation Project Report - Draft

**Project:** Replenishment Decision Quality: A Simulation-Based Evaluation and
Monitoring Framework for ML-Driven Retail Stock Distribution
**Author:** Kagan Sahin
**Date:** Updated 17 November 2026

> Draft status: Weeks 1-3 define the project, requirements and design. Week 4
> delivered the initial synthetic-world generator. Week 5 added the emulator,
> replenishment simulation, initial evaluation, and dashboard. Full validation,
> including known-answer cause-classification scenarios, remains future work.

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

## 13. Methodology (Week 3)

Sections 13-17 describe the proposed design, not a completed pipeline. As of
Week 4, only the generator prototype described in Sections 18-24 is implemented.

The engineering approach follows a simulation-based evaluation methodology.
Rather than evaluating a deployed system on confidential production data, the
project reproduces the essential decision chain of a replenishment system
inside a controlled simulation, and builds the evaluation layer on top of it.
This fits the problem for three reasons:

1. **Ground truth is available.** Because the simulation generates the future,
   true demand is known, so forecast accuracy can be measured against demand
   rather than against stock-out-censored sales - something impossible with
   real retail data.
2. **The evaluation tool can be tested under controlled conditions.** A
   controllable emulator can create specified forecast-error patterns; separate
   simulator scenarios can impose stock or rule limits. Known-answer tests can
   check the evaluator on those scenarios, but do not establish universal
   correctness (Section 15, Figure 3.2).
3. **It is reproducible and data-independent.** A single seed regenerates the
   whole world and the whole pipeline, with no database, external API, or real
   data file (NFR-02, NFR-04), so anyone can reproduce every result.

Development proceeds iteratively along the pipeline: generator (Week 4), then
forecaster + simulator + evaluator (Week 5), then testing and validation
(Week 6), matching the milestone plan in Section 12.

## 14. Proposed System (Week 3)

**Goal.** Measure the decision quality of an ML-driven replenishment system:
track forecast accuracy by segment, and attribute every forecast-vs-shipped
deviation to a cause (model error, stock constraint, rule constraint, other).

**Users.** Retail analytics and planning teams, category managers / demand
planners, and ML engineers (Section 7). Within the graduation project the
direct user is the developer/analyst running the pipeline and the dashboard.

**Main functions.** The five pipeline functions FR-01..FR-07: generate the
world, produce forecasts (emulator + optional real model), simulate
replenishment, evaluate (metrics + deviation-cause classification), and
visualise, with automated tests.

**Boundaries.** All components run locally; there is no server, database,
cloud, or external API. The system reads no real data. It evaluates decisions
produced inside the simulation; it does not modify any production engine
(Section 5.2). The only user-facing component is the dashboard; everything
else is library/CLI code.

## 15. System Architecture (Week 3)

**Figure 3.1 - High-Level System Architecture** (docs/design/architecture.png;
editable source: docs/design/architecture.mmd and the rendering script).

Figure 3.1 presents the proposed architecture. The current diagram omits the
Forecaster-to-Simulator arrow and some routes are unclear; the intended flow is
described below and the figure requires correction in later design work. The Synthetic World Generator
sends the daily sales history to the Forecaster, and the world rules, catalog,
and warehouse state to the Replenishment Simulator. The Forecaster produces
forecasts that the Simulator turns into daily ship decisions by applying the
business rules; the Simulator emits decisions and outcomes to the Evaluation
Framework. The Generator also sends the hidden true demand (dashed arrow) to
the Evaluation Framework only, so that "forecast vs true demand" stays a fair
comparison. The Evaluation Framework forwards metrics and deviation causes to
the Dashboard. This separation was selected because the project is an
evaluation layer, not a model: each link of the decision chain
(generate -> forecast -> decide -> evaluate -> present) is an isolated,
separately testable component, and the evaluator - the core deliverable - can
be verified independently of any forecaster.

*Reading Figure 3.1:* the run starts in the Generator (1); the Forecaster (2)
receives history and produces forecasts; processing is split between the
Simulator (3, decision logic) and the Evaluation Framework (4, measurement);
output is produced by the Dashboard (5); if the Forecaster fails, the
Simulator treats the missing forecast as zero demand and the Evaluator flags
it (see Table C in docs/design/design-decisions.md).

**Figure 3.2 - Forecaster Self-Validation (Known-Answer Loop)**
(docs/design/emulator-selfvalidation.png).

Figure 3.2 illustrates a proposed known-answer loop, but conflates forecast-error
injection with stock or rule constraints; the figure requires correction in
later design work. The intended approach is for the emulator to control forecast
errors and for separate simulator scenarios to impose stock or rule limits. A
known-answer test would compare the evaluator's output with the specified
scenario. Such tests can check defined cases, but cannot by themselves prove
correctness in all cases or resolve overlapping real-world causes. None of these
components or tests has been implemented yet.

**Component responsibilities and one complete data flow** are given in Tables
B and C of docs/design/design-decisions.md (single store-product-day followed
through all five components), and the interface/data dictionary in
docs/design/component-interfaces.md.

## 16. Technology Selection (Week 3)

Two consequential decisions are recorded as ADRs (docs/design/design-decisions.md):

- **ADR-01 - emulator vs real model first.** Selected: a parametric
  error-injection emulator as the core forecaster behind a pluggable
  interface; alternative: a real ML model as the core forecaster. Rationale:
  the emulator is the only way to verify the evaluation framework with
  known-answer tests, and it fits the single-developer, 9-week constraint;
  the pluggable interface keeps a real model attachable.
- **ADR-02 - seed-generated vs committed data.** Selected: generate all data
  on demand from a fixed seed via one CLI entry point; alternative: commit
  generated data files. Rationale: a fixed seed already guarantees bit-for-bit
  reproducibility without storing data, keeping the repo small and guaranteeing
  data independence by construction.

The Week 3 proposal selected Python 3.12 with NumPy/pandas, LightGBM or
statsmodels for a possible optional model, Streamlit for the dashboard, and
pytest for tests. The Week 5 implementation uses the standard-library
`unittest` runner and does not include LightGBM, statsmodels, or pytest. The
installed Week 5 stack and actual versions are recorded in Section 26.

## 17. Design Decisions, Risks and Limitations (Week 3)

**Trade-offs.** The emulator-based core (ADR-01) trades realism of the error
source for verifiability of the evaluator; the seed-generated-data choice
(ADR-02) trades a pre-built dataset for guaranteed reproducibility and data
independence. Both are deliberate and documented.

**Risks** (full table in docs/design/design-decisions.md, Table E):

- **R1:** the parametric demand model may not reproduce realistic error
  patterns - mitigated by configurable emulator error profiles and the
  optional real forecaster as a stress case.
- **R2 (highest):** deviation-cause classification may be ambiguous when
  several causes coincide on one day - mitigated by an explicit priority rule
  (stock -> rule -> model -> other) and by single-cause known-answer tests.

**Known limitations.** The synthetic world is a simplification (no promotions,
price elasticity, or supply delays in the first version); the framework
validates the evaluation methodology under controlled conditions and does not
measure any real retailer's accuracy; connecting to a real data source is a
future, out-of-scope extension (Section 10).

**Week 4 prototype goal (verifiable).** In Week 4, I will demonstrate the
synthetic world generator, where a generation config (10 stores, 200 products,
1 year) passes through the Synthetic World Generator to produce `sales_history`
and a hidden `true_demand`, printed as row counts and a sample to the
terminal, with two identical-seed checksums as proof of determinism.

## 18. Implementation Overview (Week 4 - In Progress)

The first prototype implements a synthetic world generator addressing FR-01.
A seed and command-line parameters determine the store and product counts,
historical duration, future horizon, and start date. The generator creates
fictional store and product catalogs, a warehouse stock snapshot, daily
historical sales, and a separate future true-demand period. Illustrative
category seasonality and store/product characteristics are generated without
using confidential records or real-data-derived parameters.

The historical sales series is a simplified demand-based series: it does not
simulate historical inventory, stock-outs or replenishment. Future demand is
provided separately for later evaluation, and no forecaster is implemented.
The default run (10 stores, 200 products, 365 historical days and 28 future
days) produced 730,000 historical sales rows and 56,000 future-demand rows.
Two runs with seed 42 produced matching checksums for all five tables in the
current environment. Initial automated generator checks are recorded in
Section 20; full system validation remains future work.
Forecasting, replenishment decisions, metrics, attribution, and the dashboard
remain unimplemented. The prototype does not use a database or save datasets.

**Figure 4.1 - Synthetic world generator demonstration (terminal output).**
The [first run](../evidence/week-04/run-1.txt) shows the five table row counts,
three fictional sample rows per table, and table checksums. The [second
run](../evidence/week-04/run-2.txt) used the same command and seed; the
[byte comparison](../evidence/week-04/comparison.txt) reports no differences
between the two captured outputs. Both runs were performed on 4 November 2026
with Python 3.12.10 and the dependency versions described in Section 19.
This demonstrates repeatability for this configuration and environment, not
statistical realism or validation of the unimplemented components. The
samples contain only generated fictional data; no confidential records or
real-data-derived parameters were used. The README explains how to reproduce
the comparison.

## 19. Development Environment and Technologies (Week 4)

The development environment uses Python 3.12.10 and Git 2.55.0 on Windows.
An isolated `.venv` was created using Python's `venv` module. NumPy 2.5.3 and
pandas 3.0.6 are specified in `requirements.txt` and were installed in this
virtual environment. The initial environment-check entry point was later
replaced by `python -m src.rdq`, which runs the generator. Installation and
execution commands are documented in the README. The entry point and
`python -m pip check` both completed successfully in `.venv`. A separate clean
virtual environment was also created on 4 November 2026; installation from
`requirements.txt`, `pip check`, the
default run and all eight tests succeeded. Its default output matched the
recorded first run byte for byte in the same Python environment.

| Component | Actual technology | Role and reason |
|---|---|---|
| Language and environment | Python 3.12.10, `venv`, Windows | Python provides a locally runnable CLI; `venv` isolates dependencies. |
| Libraries | NumPy 2.5.3, pandas 3.0.6 | NumPy generates seeded random quantities and pandas holds the tabular outputs. |
| Testing | Python standard-library `unittest` | Runs preliminary checks without an additional test dependency. |
| Data and database | Generated in memory; no database | Keeps the prototype self-contained and independent of confidential data. |
| Version control | Git 2.55.0; GitHub repository | Git records development history; GitHub hosts the project and issues. |

## 20. Preliminary Generator Validation (Week 4)

The following checks were run on 4 November 2026 using Python 3.12.10 and the
standard-library `unittest` runner. The small test world has 3 stores, 5
products, 4 historical days and 2 future days. The command
`.venv\Scripts\python -m unittest discover -s tests -v` ran 8 tests; all 8
passed. These results apply to the generator prototype only, not to the
unimplemented forecasting and evaluation components.

| ID | Input / check | Expected result | Observed result | Status |
|---|---|---|---|---|
| P01 | Small world (3 stores, 5 products, 4 history days, 2 future days) | Five tables with 3, 5, 5, 60 and 30 rows respectively | Expected tables and counts returned | Pass |
| P02 | Same settings and seed 42, generated twice | Each corresponding table is identical | All five DataFrames matched | Pass |
| P03 | Same small-world settings, seed 42 versus 43 | Historical sales output changes | Sales tables differed | Pass |
| P04 | Small-world references and quantities | Valid store/product references, unique date-store-product rows and nonnegative quantities | Checks passed for historical sales, future demand and warehouse stock | Pass |
| P05 | Start date 2024-02-27, including leap day | Contiguous history and future dates, with future strictly after history | Expected dates and warehouse snapshot date matched | Pass |
| P06 | Minimum dimensions of 1 and seed 0 | One row per table and a separate future date | Expected rows and dates returned | Pass |
| P07 | Zero or negative sizes/durations, or negative seed | Invalid configuration rejected | ValueError raised for each case | Pass |
| P08 | CLI with zero stores, negative seed or invalid date | Nonzero exit and informative error, without a traceback | All three were rejected as expected | Pass |

No generator defect was observed in these preliminary checks. They do not
establish statistical realism, performance at larger scales, or the accuracy
of the future forecasting, replenishment or attribution logic.

## 21. Prototype Implementation (Week 4)

**Feature:** Seeded synthetic retail world generation. **Requirement:** FR-01,
implemented for the limited generator scope described in Section 18.

**Input:** The CLI accepts a non-negative seed, positive store and product
counts, positive history and future durations, and an ISO start date. The
reproducible demonstration uses seed 42 and the defaults described in
Section 18. Invalid values are rejected rather than generating a world.

**Processing:** `src/rdq/__main__.py` parses arguments and constructs the
validated `WorldConfig`. In `src/rdq/generator.py`, `generate_world` uses a
seeded NumPy generator to create fictional store and product characteristics
and warehouse quantities. It combines illustrative category seasonality with
store and product factors and draws daily quantities from a Poisson
distribution. It builds separate history and future DataFrames over consecutive,
non-overlapping dates. These values are simulated assumptions, not estimates
from real data.

**Output and architecture:** The generator returns five pandas tables:
`stores`, `products`, `warehouse`, `sales_history`, and `true_demand`. The CLI
prints row counts, three examples and a checksum for each table. This implements
the Synthetic World Generator component of the Week 3 design; the planned
forecaster, replenishment simulator, evaluation framework and dashboard are not
connected or implemented yet. Figure 4.1 in Section 18 shows the actual output.
The preliminary checks in Section 20 test selected generator behavior only.

## 22. Technical Challenges and Solutions (Week 4)

During environment setup, a combined Git commit command failed because of
Windows `cmd.exe` quoting. The command was retried using PowerShell, after
which the local environment setup commit `3fd8bdb` was created. The commit is
verifiable in the local Git history; no separate failure transcript was saved.

The generator's normal, boundary and invalid-input checks found no defect, so
no generator bug fix is claimed. Separating future demand from historical sales
and using a fixed seed were design decisions for the prototype, not fixes for
observed failures. The comparison in Figure 4.1 and the tests in Section 20
record the resulting behavior.

## 23. Development Process - Stage 1 (Week 4)

| Field | Actual record |
|---|---|
| Date | 4 November 2026 |
| Objective | Demonstrate an input-to-output prototype for FR-01. |
| Implemented functionality | Seeded generation of fictional stores, products, warehouse stock, sales history and separate future demand, with CLI summaries. |
| Technical decision | Generate values in memory from illustrative parameters and a seed, keeping the history and future periods separate. |
| Problem and solution | A Windows command-quoting issue interrupted the setup commit; retrying with PowerShell succeeded. No generator defect was observed in preliminary checks. |
| Related issue | [Issue #3](https://github.com/KaganxSahin/replenishment-decision-quality/issues/3) tracks the Week 4 generator prototype. |
| Commit | [3fd8bdb](https://github.com/KaganxSahin/replenishment-decision-quality/commit/3fd8bdb) initializes the environment; [63f6f72](https://github.com/KaganxSahin/replenishment-decision-quality/commit/63f6f72) implements the generator and preliminary tests. |
| Evidence | Figure 4.1: [first run](../evidence/week-04/run-1.txt), [second run](../evidence/week-04/run-2.txt), and [comparison](../evidence/week-04/comparison.txt). |
| Next step | Week 5: develop the forecaster interface and error-injection emulator, followed by the replenishment simulator. |

The separate [Stage 1 record](development-stage-1.md) and
[Week 4 progress record](weekly-progress/week04.md) provide further details.

## 24. Week 4 Limitations and Handoff

At the end of Week 4, the prototype contained only the seeded synthetic-world
generator. The history was a demand-based approximation, not simulated sales
subject to inventory constraints. Warehouse inventory was a single snapshot,
and forecasting, replenishment, evaluation, and dashboard functionality had not
yet been implemented. The Week 4 evidence and preliminary generator checks in
Sections 18-23 remain historical records of that milestone.

## 25. Implementation Overview (Week 5)

The Week 5 implementation extends the Week 4 generator into a runnable local
pipeline. `src/rdq/forecaster.py` defines a `Forecaster` protocol and the
`ErrorInjectionEmulator`. Its `fit` method accepts historical sales only; its
`predict` method produces non-negative forecast quantities for a requested
future horizon, using a trailing baseline and configurable bias, seasonal
drift, variance, and seed. The future true-demand table is not passed to the
forecaster.

`src/rdq/simulator.py` applies minimum-stock and pack-size rules, allocates
finite warehouse stock, carries store inventory across simulated days, and
records shipped quantities, sales, lost sales, overstock, and stock-out flags.
`src/rdq/evaluation.py` calculates WAPE, MAPE, and bias overall and by store,
product category, season, and store-product pair. It also summarizes the
simulator's assigned cause labels. The current cause labels are a deterministic
heuristic with the priority stock constraint, rule constraint, model error,
then other; they are not independently inferred by the evaluator and do not
establish exclusive real-world causality.

`src/rdq/pipeline.py` provides the shared `run_pipeline` orchestration used by
the CLI and dashboard. `src/rdq/dashboard.py` provides Streamlit controls for
synthetic run settings and store/category/date filters, and displays metrics,
cause summaries, forecast-versus-demand charts, stock indicators, and records.
The optional statistical/ML forecaster is not implemented.

**Figure 5.1 - Week 5 end-to-end CLI output.** The actual default run is
recorded in [pipeline-run.txt](../evidence/week-05/pipeline-run.txt). With seed
42, the world contained 10 stores, 200 products, 200 warehouse rows, 730,000
historical rows, and 56,000 future-demand rows; the pipeline produced 56,000
forecasts and simulation records. The CLI withheld future-demand samples. The
run's overall synthetic metrics were WAPE 0.5973, MAPE 0.5137, and bias 0.0711.
These values apply only to this synthetic configuration and are not estimates
of any real retailer's system performance.

## 26. Development Environment and Technologies (Week 5)

The project was run on Windows with Python 3.12.10 in the repository's
`.venv`. The installed and pinned core versions are NumPy 2.5.3, pandas 3.0.6,
and Streamlit 1.67.0. Tests use Python's standard-library `unittest`; the
project does not use pytest, LightGBM, or statsmodels in this implementation.
`python -m pip check` reported no broken requirements.

| Component | Technology | Current use |
|---|---|---|
| Synthetic generation and numerical processing | NumPy 2.5.3, pandas 3.0.6 | Seeded world generation and in-memory DataFrames. |
| Forecast emulator and simulation | Python 3.12.10, NumPy, pandas | Forecast generation, replenishment rules, inventory and outcomes. |
| Evaluation and dashboard | pandas, Streamlit 1.67.0 | Metrics, cause summaries, interactive filtering and charts. |
| Verification | `unittest` | 27 tests across generator, emulator, simulation, evaluation, pipeline, and dashboard. |
| Data and external services | In-memory synthetic data; no database or API | No real data files, external service calls, or database connections are required for the run. |

Install and run instructions are in the updated README. The CLI command is
`.venv\Scripts\python -m src.rdq --seed 42`; launch the dashboard separately
with `.venv\Scripts\python -m streamlit run src\rdq\dashboard.py`.

## 27. Prototype Implementation (Week 5)

**Implemented pipeline:** `generate_world` creates the synthetic world;
`ErrorInjectionEmulator.fit` and `predict` use historical sales to generate
forecasts; `simulate_replenishment` combines forecasts with generated future
demand and inventory constraints; `evaluate_results` calculates segment metrics
and summarizes simulator cause labels. `run_pipeline` returns the world,
forecasts, combined simulation outcomes, and evaluation results. The CLI prints
row counts, selected samples, metrics, and cause summaries. It does not persist
any generated data.

**Demonstration and repeatability:** [The first run](../evidence/week-05/pipeline-run.txt)
and [the repeated run](../evidence/week-05/pipeline-run-repeat.txt) were
executed with the same command and seed. The recorded
[byte comparison](../evidence/week-05/repeatability-check.txt) reports no
differences in the complete CLI outputs. The full test output is in
[tests.txt](../evidence/week-05/tests.txt): 27 tests ran and passed. This
verifies the tested implementation behavior in the recorded environment; it is
not the comprehensive Week 6 validation and does not establish statistical
realism or general causal-classification correctness.

## 28. Technical Challenges and Solutions (Week 5)

The first dashboard smoke-test run exposed import failures when Streamlit's
`AppTest` loaded modules using package-relative imports. The dashboard imports
were changed to the project's absolute `src.rdq` package paths. Streamlit 1.67
also required the supported dataframe width argument; the calls were updated
and the dashboard smoke/filter test passed in the final 27-test run.

A simulator rule check initially treated a pack-size rounding case incorrectly
when determining whether the business rule constrained the requested quantity.
The condition was narrowed to the minimum-stock rule or an actual pack-size
reduction, and the targeted simulator scenario and complete test suite passed.

The architecture comparison also identified an intentional simplification that
must not be overstated: the simulator returns a combined decisions/outcomes
table, and the simulator—not the evaluator—assigns heuristic cause labels.
The Week 5 report and README now state these boundaries. Dedicated known-answer
cause-classification tests remain outstanding; no claim of completing them is
made.

## 29. Development Process - Stages 2 and 3 (Week 5)

Stage 2 records the forecaster protocol, error emulator, inputs and outputs,
repeatability behavior, and its remaining optional-model limitation in
[development-stage-2.md](development-stage-2.md). Stage 3 records the
replenishment simulation, evaluation metrics, dashboard handoff, and cause
classification limitation in [development-stage-3.md](development-stage-3.md).
The detailed weekly record is in [week05.md](weekly-progress/week05.md) and the
[weekly log](weekly_log.md). The implementation commit is
[9fa5d47](https://github.com/KaganxSahin/replenishment-decision-quality/commit/9fa5d47dbfcbba332bd31494a32af780450ea6a2); the documentation and evidence
commit is [d000103](https://github.com/KaganxSahin/replenishment-decision-quality/commit/d00010385d81f161504c5ce5ca41c08e814d60f7). Both were pushed to `origin/main`.
GitHub issue statuses were not changed during this step.

## 30. Current Limitations and Next Steps

The current prototype is a controlled synthetic demonstration, not a production
monitoring tool. Historical sales are generated from demand without historical
stock-outs. Warehouse stock is an opening snapshot that depletes during the
horizon; no warehouse replenishment inflows, lead times, or store priorities are
modeled. The emulator uses a trailing average and injected noise rather than a
trained forecasting model. The simulator's precedence-based cause labels are
heuristic; overlapping constraints can obscure attribution, and known-answer
classification tests have not yet been implemented. The evaluation reports
synthetic-run metrics only and cannot substantiate any real retailer's
performance.

Next, Week 6 work should add focused known-answer tests for isolated and
combined stock/rule/model-error scenarios, strengthen metric and boundary
validation, and perform the planned performance run. The Week 5 implementation
and documentation were subsequently committed and pushed; issue statuses were
not changed at that time.

## 31. Testing Methodology (Week 6)

On 23 November 2026 the project was tested on Windows 11 build 26200 with
Python 3.12.10, NumPy 2.5.3, pandas 3.0.6 and Streamlit 1.67.0. Python
`unittest` was selected for unit, boundary, CLI and integration tests; Streamlit
`AppTest` was used to check the actual dashboard filters. The generator was
measured using `time.perf_counter`. The complete suite contained 33 tests and
passed in 12.601 seconds. All inputs were fictional synthetic data.

Test cases were selected from the numbered functional/non-functional
requirements. They include positive, invalid and boundary inputs, same-seed
reproducibility, hand-calculated metrics, simulator conservation, controlled
cause scenarios, UI filter agreement and a generator performance run. The
[detailed testing report](testing-week-06.md) supplies each important case ID,
component/goal, input, expected and actual result, status, and evidence.

## 32. Validation Against Requirements (Week 6)

FR-01 generation tests validate table sizes, unique references, date separation,
minimum dimensions and repeatability. FR-02 tests validate baseline/bias,
seed-controlled noise, and invalid inputs. FR-04 and FR-06 are checked using
an emulator fitted to constant four-unit history plus independently specified
demand, warehouse and pack constraints. Seven controlled cases cover isolated
stock and rule restrictions, under/overforecast, no error, and overlapping
constraints under documented priority. The emulator injects forecast bias;
warehouse and rule constraints are separate scenario inputs. FR-05 is checked
against manually calculated WAPE, MAPE and bias, zero actuals, and segment
values. FR-07 is checked through store, category and date filters with displayed
metrics recomputed independently from filtered raw rows.

These checks provide evidence for selected configurations rather than proof of
universal correctness. FR-03 remains unimplemented. The simulator—not an
independent causal classifier—assigns priority-based labels to all rows; this
does not demonstrate exclusive real-world cause attribution or fully establish
FR-06's forecast-versus-shipped wording. NFR-02 was tested in one environment.
NFR-04 is partially tested: a small pipeline succeeded with Python socket
connection hooks blocked, but an OS-isolated offline dashboard run was not
performed. These boundaries and the historical baseline assumptions remain
explicitly documented.

## 33. Testing Results and Experimental Results (Week 6)

| Test / requirement | Input and expected result | Observed result | Status |
|---|---|---|---|
| T05: stock, FR-06/NFR-03 | Forecast 4, demand 4, pack 1, stock 2: ship 2 and label stock | Ship 2, lost sales 2, stock constraint | PASS |
| T06: rule, FR-06/NFR-03 | Forecast 4, demand 4, pack 3, stock 20: ship 3 and label rule | Ship 3, lost sales 1, rule constraint | PASS |
| T07: model/no error | Forecast 2, 6, 4 against demand 4: model, model, other | Expected shipments, losses and labels matched | PASS |
| T08: overlapping constraints | Stock+rule+model, then rule+model: stock priority, then rule | Both priority labels and expected shipments matched | PASS |
| T09: FR-05/NFR-03 | Forecast [3,1,4], demand [2,0,5]: WAPE 3/7, MAPE 0.35, bias 1/7 | 0.4285714286, 0.35, 0.1428571429 | PASS |
| T11: FR-07 | Store/category/date filter: metrics match independent calculation from raw rows | Filter and WAPE/MAPE/bias/lost-sales assertions matched | PASS |
| T12: NFR-01 | 30 stores, 300 products, 730 history days; generator <60 seconds | 6,570,000 history rows, 9,000 future rows, 0.607 seconds | PASS |
| T13: NFR-04 partial | Small pipeline with Python socket connects blocked; 12 outcomes | 12 outcomes; no OS-level isolation or dashboard included | PARTIAL |

Full inputs and results are recorded in [testing-week-06.md](testing-week-06.md),
[checks.txt](../evidence/week-06/checks.txt), and the
[33-test log](../evidence/week-06/tests.txt). The performance figure refers to
one generator-only run on the recorded machine; it is not a measurement of
the entire pipeline. No application defect was observed in these Week 6 runs,
so there is no invented failure/fix/retest sequence or product bug-fix commit.
The Windows Git commit command initially failed because of quoting; retrying
with an unspaced message successfully recorded the test/evidence commit
[5749236](https://github.com/KaganxSahin/replenishment-decision-quality/commit/5749236).

## 34. Development Process - Stage 4 and Next Steps

The [Stage 4 record](development-stage-4.md) documents date, objective,
methods, actual problems, evidence, commit and next steps. The
[Week 6 progress record](weekly-progress/week06.md) and
[weekly log](weekly_log.md) summarize the same actual results.

Week 7 should independently install and run the project and test the complete
pipeline and dashboard in a genuinely offline, no-database environment.
Further work must distinguish heuristic labels from independent causal
attribution and keep real retailer performance claims outside the project.
