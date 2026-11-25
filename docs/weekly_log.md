# Weekly Progress Log

## Week 1 - Project Definition, References, Data Strategy and GitHub

| Field | Content |
|---|---|
| **Week** | 1 (October 2026) |
| **Tasks planned** | Define project idea and scope, identify target users, find academic and technical references, create the GitHub repository, start the Graduation Project Report, finalize the data strategy. |
| **Tasks completed** | Project idea defined (evaluation and monitoring framework for ML-driven replenishment decisions); target users identified; 3 academic and 3 technical references collected and summarized; GitHub repository created with initial README; report draft sections written (Introduction, Problem Statement, Motivation, Objective, Preliminary Scope). Data strategy finalized with the industry partner: the project runs **entirely on synthetic data** - a synthetic retail world generator is the data source, and a forecasting engine plus a rule-based replenishment simulator produce the decisions to be evaluated. README, project description, and report draft updated to this simulation-based design; architecture overview added (`docs/architecture.md`). |
| **GitHub commits** | `docs: create initial README with project definition` / `docs: add project description and report draft` / `docs: add references and weekly progress log` / `docs: switch project definition to fully synthetic simulation approach` / `docs: add architecture overview of simulation pipeline` / `docs: log data strategy decision in weekly log` / `docs: finalize week 1 status in README and weekly log` |
| **Problems encountered** | (1) Choosing between several candidate project ideas; (2) how to handle confidential industry data; (3) real production data cannot be used in the project at all, so the original plan had to be revised; (4) simply masking real records would still leak real data. |
| **Solutions attempted** | (1) Evaluated candidates against feasibility, academic reference availability, and real-world value; selected the evaluation/monitoring direction. (2)-(4) Adopted a fully synthetic, simulation-based design: no real records are copied, and the repository contains no real data at all. The known ground truth of the simulation also enables measuring forecasts against true demand, which is impossible with real data where stock-outs censor sales. |
| **References consulted** | A1-A3, T1-T3 (see `docs/references.md`). |
| **Tests performed** | None yet - documentation phase; the generator will be the first tested module. |
| **Report sections updated** | Introduction, Problem Statement (added the data-confidentiality barrier), Motivation, Project Objective, Preliminary Scope - all in `docs/report_draft.md`. |
| **Next week's plan** | Await Week 2 instructions from the instructor; expected focus: requirements engineering. |

## Week 2 - Requirements Engineering, Architecture Revision and Planning

| Field | Content |
|---|---|
| **Week** | 2 (October 2026) |
| **Tasks planned** | Review the Week 1 definition; write functional and non-functional requirements; define scope, constraints, and assumptions; write user stories with acceptance criteria; plan development milestones; organize GitHub Issues; update the report and README. |
| **Tasks completed** | An initial requirements draft was written early in the week around a design that would train forecasting models (reusing a prior personal forecasting project) and be validated against locally accessed real company data. After further reflection on the data-confidentiality constraint and a closer reading of the course's reproducibility requirement (the project must be runnable by someone else with no access to any private resource), **this design was revised from scratch**: the project no longer reuses any previous project, and no real data - or any parameter calibrated from real data, even in aggregate form - is used anywhere, not even locally. The architecture was redesigned around a **pluggable forecaster interface**: a built-in parametric error-injection emulator (the core, "Must" component, which can produce forecasts with precisely known error causes) and an optional real statistical/ML model trained purely on synthetic data. This also solves a second problem: a black-box forecaster alone would give no way to verify that the evaluation framework classifies deviation causes correctly, whereas the emulator enables genuine known-answer validation of the framework itself. `docs/requirements.md` was rewritten: FR-01..FR-07 (7 functional requirements, including the pluggable forecaster and emulator), NFR-01..NFR-04 (added a Data Independence requirement), scope/constraints/assumptions, 4 user stories (US-01..US-04, including a new self-validation story), and the Week 3-9 milestone plan. `docs/architecture.md` was updated to show the forecaster interface and the framework's self-validation loop. README and `docs/report_draft.md` (Sections 1-12) were revised to match. GitHub Issues were updated accordingly (#2, #4, #5 revised; new issue #6 created for the forecaster interface and emulator). |
| **GitHub commits** | `docs: rewrite readme and project description for data-independent architecture` / `docs: rewrite architecture overview with pluggable forecaster and self-validation` / `docs: rewrite requirements specification with emulator-based architecture` / `docs: rewrite report sections 1-12 for data-independent architecture` / `docs: record week 2 architecture revision in weekly log` |
| **Problems encountered** | (1) The original plan risked tying the project's forecasting component, even indirectly, to data patterns adjacent to confidential company information; (2) evaluating a single opaque forecaster provides no way to verify that the evaluation framework itself classifies deviation causes correctly - there was no ground truth to check the checker against. |
| **Solutions attempted** | (1) Removed all dependency on any previous project and any real-data-derived calibration; the synthetic world's behaviour is now based only on general, non-proprietary retail domain knowledge. (2) Introduced a parametric error-injection emulator that can generate forecasts with a precisely known, controllable error cause (bias, variance, seasonal drift, or a specific business-rule interaction), enabling known-answer tests of the evaluation framework before it is ever applied to any forecaster's real output. |
| **References consulted** | A1-A3, T1-T3 (see `docs/references.md`); GitHub Issues documentation (https://docs.github.com/en/issues). |
| **Tests performed** | None yet - documentation phase; NFR-02/NFR-03/NFR-04 define the tests to be implemented in Weeks 5-6, including the known-answer classification tests enabled by the emulator. |
| **Report sections updated** | Sections 1, 3, 4, 5 revised, and Sections 6-12 rewritten (Project Scope, Requirements Analysis, Functional Requirements, Non-Functional Requirements, Constraints and Assumptions, Use Cases / User Stories, Development Plan) in `docs/report_draft.md`. |
| **Next week's plan** | Architecture and technical design (Week 3): module layout of the five components, synthetic world table schema, forecaster interface definition, data-flow description, technology decisions with justification. |

## Week 3 - Architecture and Technical Design

| Field | Content |
|---|---|
| **Week** | 3 (October 2026) |
| **Tasks planned** | Convert Week 2 requirements into a technical design: requirements-to-design traceability, component responsibility sheet, student-created architecture diagrams, one end-to-end data flow, data dictionary / interface spec, ADR-style technology decisions, design risks, and a Week 4 prototype goal; update the report and GitHub. |
| **Tasks completed** | Table A (FR-01/02/06 + NFR-03/04 to design), Table B (5-component responsibility sheet + boundaries), Table C (one store-product-day end-to-end flow), Table E (2 risks + Week 4 hand-off) all written in `docs/design/design-decisions.md`. Two student-created diagrams produced: Figure 3.1 (high-level architecture) and Figure 3.2 (forecaster self-validation / known-answer loop), each with a caption and a paragraph explanation. `docs/design/component-interfaces.md` holds the forecaster interface contract and the full data dictionary (Task 3.5). Two ADRs recorded: ADR-01 (error-injection emulator as core forecaster vs real model) and ADR-02 (seed-generated data vs committed data files). Report Sections 13-17 added (Methodology, Proposed System, System Architecture with figures, Technology Selection, Design Decisions/Risks). `docs/weekly-progress/week03.md` written (Table F + prepared answers). |
| **GitHub commits** | `docs: add architecture and component interfaces` (2bf62f3) / `docs: add design decisions and ADR records` (be1a651) / `docs: add architecture diagrams and self-validation figure` (3c9a44a) / `docs: add week 3 report sections and progress log` (ecec781) on design branch `docs/week3-architecture`; merged to main via PR #7 (squash commit 2b20265); issue #2 closed referencing the PR. Follow-up: `docs: add diagram generation script and finalize week 3 evidence links`. |
| **Problems encountered** | (1) Mermaid CLI / Node were not available locally, so the `.mmd` source could not be rendered directly. (2) First matplotlib render placed arrow labels on top of component titles (text overlap). |
| **Solutions attempted** | (1) Kept the Mermaid source as the documented diagram source and rendered the figures with a versioned matplotlib script, which is itself reproducible. (2) Adjusted box title/body layout and rerouted the ground-truth arrow below the forecaster box; re-rendered and visually verified both PNGs. |
| **References consulted** | A1-A3, T1-T3 (docs/references.md); NumPy Generator/PCG64 docs (ADR-02); Beel & Lange on ground-truth evaluation (ADR-01). |
| **Tests performed** | None yet - design phase; Week 4 will add the first runnable code (generator). |
| **Report sections updated** | Sections 13-17 in `docs/report_draft.md`. |
| **Next week's plan** | Week 4 prototype: implement the synthetic world generator, demonstrate determinism (same seed -> identical output), and capture terminal output as evidence (issue #3). |

## Week 4 - First Working Prototype

| Field | Content |
|---|---|
| **Week** | 4 (4 November 2026) |
| **Tasks planned** | Implement an FR-01 generator prototype, verify preliminary behavior, capture a repeatable demonstration, and document Development Stage 1. |
| **Tasks completed locally** | Prepared the Python environment; implemented seeded generation of fictional stores, products, a warehouse snapshot, historical sales and separate future demand; added a CLI and preliminary tests; recorded demonstration output; updated the report, README and Stage 1 record. |
| **Git commits** | [3fd8bdb](https://github.com/KaganxSahin/replenishment-decision-quality/commit/3fd8bdb) initializes the development environment; [63f6f72](https://github.com/KaganxSahin/replenishment-decision-quality/commit/63f6f72) implements the generator and preliminary tests. |
| **Problems encountered** | A combined Git commit command failed because of Windows `cmd.exe` quoting. No generator defect was observed in the preliminary checks. |
| **Solutions attempted** | Retried the Git command using PowerShell and created the local setup commit. No generator bug fix is claimed. |
| **Tests performed** | Eight generator `unittest` tests passed, covering valid, boundary and invalid inputs, same and different seeds, references, quantities and date separation. See report Section 20. |
| **Evidence** | [First run](../evidence/week-04/run-1.txt), [second run](../evidence/week-04/run-2.txt) and [comparison](../evidence/week-04/comparison.txt): the captured seed-42 outputs match byte for byte in the recorded environment. |
| **Report sections updated** | Sections 18-24: implementation, environment, preliminary checks, prototype, challenges, Stage 1, limitations and next steps. |
| **Next week's plan** | Week 5: implement the forecaster interface and controllable error-injection emulator, then the rule-based replenishment simulator. |

See the [Stage 1 record](development-stage-1.md) and [Week 4 progress record](weekly-progress/week04.md) for details. Full-system validation remains future work.

## Week 5 - Forecaster, Replenishment Simulation, Evaluation, and Dashboard

| Field | Content |
|---|---|
| **Week** | 5 (17 November 2026) |
| **Tasks planned** | Implement the emulator and forecaster interface, replenishment simulation, initial metrics and cause analysis, and the first dashboard; compare implementation with the Week 3 architecture and record actual technical evidence. |
| **Tasks completed locally** | Implemented `Forecaster` and `ErrorInjectionEmulator`; added replenishment simulation with minimum-stock, pack-size, warehouse-stock, inventory, sales, and stock-out logic; added WAPE/MAPE/bias metrics and heuristic cause summaries; added the common pipeline and Streamlit dashboard. Documented architecture differences and actual CLI/test outputs. |
| **Requirements addressed** | FR-02, FR-04, FR-05, FR-06, and FR-07 are represented in the local prototype. The optional statistical/ML forecaster (FR-03) is not implemented. |
| **Technical decisions** | The forecaster receives historical sales only; future truth is used downstream by the simulation/evaluation flow. CLI and dashboard share one pipeline. The simulator returns combined decision/outcome rows. Cause labels use the fixed priority stock constraint → rule constraint → model error → other, and are heuristic rather than independently inferred causal proof. |
| **Environment** | Windows; Python 3.12.10; NumPy 2.5.3; pandas 3.0.6; Streamlit 1.67.0; standard-library `unittest`. `pip check` reported no broken requirements. |
| **Problems encountered and solutions** | Streamlit AppTest exposed package-relative imports; dashboard imports were switched to absolute `src.rdq` paths. Streamlit 1.67 required supported dataframe width arguments; calls were updated. A simulator rule-check edge case that mislabeled a pack-size restriction was corrected to test for actual minimum-stock or pack-size limiting. |
| **Tests and observed result** | The full suite ran 27 tests and passed, including metric hand-checks, simulator behavior, pipeline repeatability, and dashboard smoke/filter coverage. Default seed-42 runs produced byte-identical CLI output. Dedicated known-answer cause-classification tests and the planned performance run remain for Week 6. |
| **Evidence** | [First pipeline run](../evidence/week-05/pipeline-run.txt), [repeat run](../evidence/week-05/pipeline-run-repeat.txt), [byte comparison](../evidence/week-05/repeatability-check.txt), [test output](../evidence/week-05/tests.txt), and [architecture comparison](design/architecture-comparison-week5.md). |
| **Stage records** | [Stage 2 - Forecaster and Error Emulator](development-stage-2.md); [Stage 3 - Replenishment and Initial Evaluation](development-stage-3.md); [Week 5 progress record](weekly-progress/week05.md). |
| **Commit / GitHub status** | Implementation: [9fa5d47](https://github.com/KaganxSahin/replenishment-decision-quality/commit/9fa5d47dbfcbba332bd31494a32af780450ea6a2). Documentation/evidence: [d000103](https://github.com/KaganxSahin/replenishment-decision-quality/commit/d00010385d81f161504c5ce5ca41c08e814d60f7). Both are pushed to `origin/main`; issue statuses were not changed. |
| **Next week's plan** | Week 6: implement known-answer classification tests for isolated and combined causes, broaden metric and boundary validation, and run the planned performance test. |

The Week 5 record describes tested synthetic prototype behavior only. It does not
claim that the cause labels provide universally correct or production-ready
causal attribution.

## Week 6 - Testing and Validation

| Field | Actual record |
|---|---|
| **Week** | 6 (23 November 2026) |
| **Tasks planned** | Test key requirements, record expected/actual results, investigate any defects, update report, Stage 4 and GitHub. |
| **Tasks completed** | Added controlled cause, metric, input, reproducibility and dashboard filter tests; measured generator performance; documented test strategy, detailed results and limits. |
| **GitHub commit** | [5749236](https://github.com/KaganxSahin/replenishment-decision-quality/commit/5749236): tests and actual evidence. No product bug-fix commit is claimed. |
| **Problems and solutions** | No application defect observed. Git commit command quoting failed once on Windows; retrying with an unspaced message succeeded. |
| **Tests performed** | 33 tests passed in 12.601 s; known-answer scenarios and hand-calculated metrics matched. Generator: 30 stores, 300 products, 730 historical days, 6,570,000 rows in 0.607 s. Socket-guarded small pipeline passed; genuine offline dashboard test remains outstanding. |
| **Evidence** | [Detailed testing table](testing-week-06.md), [test log](../evidence/week-06/tests.txt), [numeric results](../evidence/week-06/checks.txt), and [Stage 4](development-stage-4.md). |
| **Report sections updated** | Sections 31–34: testing methodology, validation, results, Stage 4 and next steps. |
| **Next week** | Independent installation and integration verification; genuine offline/no-database full pipeline and dashboard run; examine remaining attribution limitations. |

Post-submission note (25 November 2026): a pre-Week-7 review found and fixed
two defects (lost sales from an underforecast were mislabeled `rule
constraint` when the minimum-stock rule had raised shipments; a partially
selected dashboard date range raised a `TypeError`), added three regression
tests, and reran the full 36-test suite successfully. See the
[post-submission correction record](testing-week-06.md).

## Week 7 - Integration and Reproducibility

| Field | Actual record |
|---|---|
| Week | 7 (25 November 2026) |
| Tasks completed | Fresh-clone installation, dependency/configuration documentation, integrated CLI/dashboard check, R01–R06 results, Stage 5 and report answers. |
| Integration correction | Dashboard `AppTest` outside repository root failed with `ModuleNotFoundError: src`; added script-relative project root and regression test, then retested successfully. |
| Results | 37 tests passed; pip check clean; small pipeline produced 168 history, 12 future, 12 forecast and 12 outcome rows. |
| Environment and limitations | Windows 11, Python 3.12.10; no peer available, so developer-led clean-environment test. No browser or OS-offline dashboard proof; blanket socket guard blocked local AppTest loopback. |
| Evidence | [R01–R06](reproducibility-week-07.md), [terminal check](../evidence/week-07/reproducibility-check.txt), [test output](../evidence/week-07/reproducibility-tests.txt). |
| Commit | Week 7 commit link to be recorded after publication. |
| Next week | Final report/README, screenshots and presentation preparation. |
