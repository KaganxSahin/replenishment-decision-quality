# Replenishment Decision Quality: A Simulation-Based Evaluation and Monitoring Framework for ML-Driven Retail Stock Distribution

## Project Description

Retail chains move products from central warehouses to individual stores every
day. These distribution decisions are increasingly made by machine-learning-
driven replenishment systems, which combine sales forecasts with business rules
such as minimum stock levels, pack sizes, and store priorities.

Although such systems produce decisions daily, the *quality* of those decisions
is rarely measured in a structured way. Forecasts are seldom compared with
actual sales systematically, and when the shipped quantity differs from the
forecast, it is difficult to tell whether the cause was a model error, a
warehouse stock shortage, or a business-rule constraint. Evaluating such a
system on real production data is also often impossible, because retail data
is commercially confidential - and even aggregate statistics derived from it
can be sensitive.

This project removes both barriers with a fully self-contained simulation.
It builds a **synthetic retail world** - a fictional multi-category retail
chain with stores, products, and a warehouse - whose behaviour is informed
only by general, publicly known retail domain knowledge (e.g., that demand is
seasonal, that stores and products differ in popularity), never by any
confidential dataset. The current pipeline includes a **pluggable forecaster**
contract and a built-in parametric emulator with controllable bias, noise
variance, and seasonal drift. An optional statistical/ML model using synthetic
history is a future extension. A rule-based replenishment simulator turns
forecasts into daily decisions, and an evaluation framework measures forecasts
against generated true demand. The current local pipeline runs end to end from
one CLI command, with no database, external data file, or real data of any kind.
Cause labels are heuristic simulator outputs; Week 6 controlled known-answer
scenarios validate selected cases but do not prove general causal attribution.

## Objective

Develop a framework that can:

1. **Generate a realistic synthetic retail world** - stores, products,
   warehouse stock, sales history, and a hidden future with known true demand
   - using only general retail domain knowledge, never any confidential data.
2. **Produce forecasts through a pluggable interface** - a built-in
   error-injection emulator (for controlled, self-validating experiments) and,
   optionally, a real forecasting model trained on the synthetic history.
3. **Simulate rule-based replenishment** - turn forecasts into distribution
   decisions through business rules (minimum stock, pack size, warehouse
   availability).
4. **Measure decision quality** - compute forecast-accuracy metrics (WAPE,
   MAPE, bias) and classify forecast-vs-shipped deviations by cause (model
   error, stock constraint, rule constraint, other), validated with
   known-answer tests before being applied to any forecaster.
5. **Visualize** - present results by store, product category, and season in
   an interactive dashboard.

## Target Users

- Retail analytics and planning teams who need to know where a replenishment
  system performs well or poorly.
- Category managers and demand planners who monitor stock health for their
  product ranges.
- ML engineers who maintain forecasting models and need systematic feedback.

## Technologies

- Python 3.12
- NumPy / pandas (synthetic data generation and processing)
- Streamlit 1.67.0 (interactive dashboard)
- Python standard-library `unittest` (testing)
- Git & GitHub (version control)
- Optional statistical/ML forecaster: planned, not implemented

No database connector is required: the current pipeline uses generated in-memory
data only, and no dataset files are committed. Technologies may evolve during
the project.

## Features and Status

- FR-01: Seeded synthetic retail world generation - implemented
- FR-02: Pluggable forecaster interface and error-injection emulator - implemented
- FR-03: Optional real forecasting model - not implemented
- FR-04: Rule-based replenishment simulation - implemented
- FR-05: WAPE/MAPE/bias metrics by segment - implemented
- FR-06: Heuristic deviation-cause labels; controlled known-answer cases passed, general causality not established
- FR-07: Interactive dashboard with store, category, and date filters - implemented

## Scope

The first version includes the synthetic world generator, emulator,
replenishment simulator, evaluation framework, and dashboard. Selected known-answer cases
have been tested; broader attribution remains limited. No real or confidential
data, or parameters derived from it, are used. Excluded: modifying a production
replenishment engine, automatic model retraining, real-time streaming analysis,
customer-level analysis, and price optimization. The full specification with
non-functional requirements, user stories, and milestones is in
`docs/requirements.md`; planned work is tracked in
[GitHub Issues](https://github.com/KaganxSahin/replenishment-decision-quality/issues).

## Installation and Reproducibility

Tested on Windows 11 with Python 3.12.10 and Git for Windows. Required libraries
are pinned in `requirements.txt`: NumPy 2.5.3, pandas 3.0.6 and Streamlit 1.67.0
(transitive dependencies are resolved by pip). A normal consumer laptop is
sufficient; no GPU, database, external data file, API key or `.env` file is used.
`.env.example` contains only placeholders for a possible, out-of-scope future
data-source connection; do not copy or configure it for this application.

From a terminal, clone the repository and enter the **repository root**:

```cmd
git clone https://github.com/KaganxSahin/replenishment-decision-quality.git
cd replenishment-decision-quality
python -m venv .venv
```

Activate the new environment. Windows Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Then install and run the integrated pipeline:

```bash
python -m pip install -r requirements.txt
python -m src.rdq --seed 42
```

A smaller demonstration for a quick installation check:

```bash
python -m src.rdq --seed 42 --stores 2 --products 3 --history-days 28 --future-days 2
```

Expected output includes the table names and row counts, SHA-256 hashes, three
sample forecasts, simulation outcomes, segment metrics, and a cause summary.
For the small run, the world contains 168 historical and 12 future rows, with
12 forecasts and 12 simulation outcomes. All values are synthetic; future
true-demand samples are withheld from CLI output. Default demo settings are
10 stores, 200 products, 365 historical days and 28 future days. The separate
NFR-01 benchmark scenario uses 30 stores, 300 products and 730 days.

Run all tests from the repository root:

```bash
python -m unittest discover -s tests -v
```

Launch the interactive dashboard:

```bash
python -m streamlit run src\rdq\dashboard.py --server.address 127.0.0.1 --server.port 8501 --server.headless true
```

On Linux/macOS, use forward slashes: `src/rdq/dashboard.py`. Open the local
address printed by Streamlit (normally `http://127.0.0.1:8501`). The dashboard
runs the same shared pipeline and exposes run settings, store/category/date
filters, metrics, cause summaries and simulation records.

### Common installation issues

- **Package installation:** internet access or a populated local package cache
  is needed only for dependency installation. Once installed, the application
  reads no external data files and requires no configured service.
- **New venv without pip:** run `python -m ensurepip --upgrade`, then repeat
  the dependency installation.
- **`No module named src`:** use the commands above from the repository root;
  do not run `python -m src.rdq` from inside `src` or another directory.
- **Different Python:** use Python 3.12 as tested; other versions/platforms
  have not been verified. Recreate `.venv` if it points to another interpreter.
- **Dashboard address in use:** change `--server.port` and open the printed URL.

### Week 7 clean-environment evidence

On 25 November 2026 the repository was freshly cloned at commit `8740ff5`, a
new virtual environment was created, and dependencies were installed from
`requirements.txt`. CLI, dashboard/AppTest and the full suite passed after one
integration correction. The dashboard previously failed when executed by
`AppTest` outside the repository root; deriving the project root from the script
location fixed it. The final suite contains 37 tests. A peer was unavailable,
so this was a developer-led clean-environment check, not an independent test.

See [reproducibility results](docs/reproducibility-week-07.md),
[terminal evidence](evidence/week-07/reproducibility-check.txt), and
[37-test output](evidence/week-07/reproducibility-tests.txt). The attempted
all-socket guard blocked AppTest's own Windows loopback socketpair; it does not
establish OS-level offline operation. No independent peer, browser-based
dashboard, or OS-isolated offline test is claimed.

Week 5 evidence: [pipeline output](evidence/week-05/pipeline-run.txt),
[repeat run](evidence/week-05/pipeline-run-repeat.txt),
[byte comparison](evidence/week-05/repeatability-check.txt), and
[test results](evidence/week-05/tests.txt). The comparison reports no differences
for identical seed-42 runs in the recorded environment. The Week 4 generator
demonstration remains available at [first run](evidence/week-04/run-1.txt),
[second run](evidence/week-04/run-2.txt), and
[comparison](evidence/week-04/comparison.txt).

The generated history is still a simplified demand-based series and does not
model historical stock-outs or replenishment. Warehouse availability is a
single opening snapshot that depletes during the simulated horizon; replenishment
inflows are not modeled. Cause labels use a deterministic heuristic; controlled
known-answer cases passed, but this does not establish general causality. An
OS-isolated offline run including the dashboard remains unverified. The optional
real forecaster is not implemented. `.venv/` is ignored by Git; installation requires
package-index access or a local package cache.

## Current Status

The Week 6 validation suite ran 33 tests successfully. Controlled isolated and
combined cause scenarios, hand-calculated metrics, repeatability and dashboard
filters passed. The generator produced 6,570,000 historical rows for 30 stores,
300 products and 730 days in 0.607 seconds on the recorded machine. The Python
socket-guarded small-pipeline check does not replace an OS-isolated offline test.
See the [test report](docs/testing-week-06.md), [Stage 4](docs/development-stage-4.md),
[Week 6 progress](docs/weekly-progress/week06.md), [test output](evidence/week-06/tests.txt)
and [measured checks](evidence/week-06/checks.txt).

A 25 November pre-Week-7 review fixed two post-submission defects (lost sales
from an underforecast were mislabeled `rule constraint` when the minimum-stock
rule had actually raised shipments, and a partially selected dashboard date
range raised a `TypeError`), added three regression tests, and reran the full
36-test suite successfully ([correction record](docs/testing-week-06.md),
[retest log](evidence/week-06/post-submission-fix-retest.txt)).

The Week 5 prototype implements the synthetic generator, pluggable forecaster
contract with its built-in error-injection emulator, replenishment simulation,
initial evaluation metrics and heuristic cause summaries, and a Streamlit
dashboard. The default seed-42 run produced 730,000 historical rows, 56,000
forecasts, and 56,000 simulation records. Same-seed CLI output matched byte for
byte in the recorded environment.

See the [Week 5 architecture-to-implementation comparison](docs/design/architecture-comparison-week5.md),
[Stage 2 record](docs/development-stage-2.md), [Stage 3 record](docs/development-stage-3.md),
and [Week 5 progress record](docs/weekly-progress/week05.md). The report contains
the Week 4 generator evidence and the current Week 5 implementation, environment,
technical boundaries, and next steps.

Week 3 architecture and technical design are documented in `docs/design/`:

- [High-level architecture diagram](docs/design/architecture.png) (Figure 3.1)
  and the [self-validation / known-answer loop](docs/design/emulator-selfvalidation.png)
  (Figure 3.2), with editable sources. These are conceptual diagrams and some
  routes require later correction, as noted in the report.
- [Design decisions](docs/design/design-decisions.md) - traceability,
  component sheet, data flow, risks, ADR-01 / ADR-02.
- [Component interfaces](docs/design/component-interfaces.md) - forecaster
  interface and data dictionary.
