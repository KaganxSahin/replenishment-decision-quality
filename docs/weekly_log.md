# Weekly Progress Log

## Week 1 - Project Definition, References, Data Strategy and GitHub

| Field | Content |
|---|---|
| **Week** | 1 (October 2026) |
| **Tasks planned** | Define project idea and scope, identify target users, find academic and technical references, create the GitHub repository, start the Graduation Project Report, finalize the data strategy. |
| **Tasks completed** | Project idea defined (evaluation and monitoring framework for ML-driven replenishment decisions); target users identified; 3 academic and 3 technical references collected and summarized; GitHub repository created with initial README; report draft sections written (Introduction, Problem Statement, Motivation, Objective, Preliminary Scope). Data strategy finalized with the industry partner: the project runs **entirely on synthetic data** - a synthetic retail world generator (fictional footwear retailer, calibrated from real retail patterns, no real records) is the data source, and a forecasting engine plus a rule-based replenishment simulator produce the decisions to be evaluated. README, project description, and report draft updated to this simulation-based design; architecture overview added (`docs/architecture.md`). |
| **GitHub commits** | `docs: create initial README with project definition` / `docs: add project description and report draft` / `docs: add references and weekly progress log` / `docs: switch project definition to fully synthetic simulation approach` / `docs: add architecture overview of simulation pipeline` / `docs: log data strategy decision in weekly log` / `docs: finalize week 1 status in README and weekly log` |
| **Problems encountered** | (1) Choosing between several candidate project ideas; (2) how to handle confidential industry data; (3) real production data cannot be used in the project at all, so the original plan had to be revised; (4) simply masking real records would still leak real data. |
| **Solutions attempted** | (1) Evaluated candidates against feasibility, academic reference availability, and real-world value; selected the evaluation/monitoring direction. (2)-(4) Adopted a fully synthetic, simulation-based design: the generator is calibrated from aggregate statistical patterns only (seasonality curves, store/product profiles); no real records are copied, and the repository contains no real data at all. The known ground truth of the simulation also enables measuring forecasts against true demand, which is impossible with real data where stock-outs censor sales. |
| **References consulted** | A1-A3, T1-T3 (see `docs/references.md`); LightGBM and statsmodels documentation reviewed for the forecasting engine. |
| **Tests performed** | None yet - documentation phase; the generator will be the first tested module. |
| **Report sections updated** | Introduction, Problem Statement (added the data-confidentiality barrier), Motivation, Project Objective, Preliminary Scope - all in `docs/report_draft.md`. |
| **Next week's plan** | Await Week 2 instructions from the instructor; expected focus: requirements engineering (functional and non-functional requirements, use cases / user stories, constraints and assumptions; GitHub Issues for planned work). |

## Week 2 - Requirements Engineering and Planning

| Field | Content |
|---|---|
| **Week** | 2 (October 2026) |
| **Tasks planned** | Review the Week 1 definition; write functional and non-functional requirements; define scope, constraints, and assumptions; write user stories with acceptance criteria; plan development milestones; organize GitHub Issues; update the report and README. |
| **Tasks completed** | Requirements specification written (`docs/requirements.md`): Week 1 review paragraph, FR-01..FR-06 with priorities (5 Must, 1 Should), NFR-01..NFR-03 with verification methods (performance, reproducibility, correctness), scope/constraints/assumptions, 3 user stories (US-01..US-03) each with 2 acceptance criteria linked to FRs, and the Week 3-9 milestone plan. GitHub Issues #1-#5 created (requirements, design, generator prototype, forecast engine + simulator, evaluation metrics). README updated with Planned Features, Scope, and Week 2 status. Report draft extended with Sections 6-12 (scope, requirements analysis, FR/NFR, constraints/assumptions, user stories, development plan). |
| **GitHub commits** | `docs: add requirements specification for week 2` / `docs: update README with planned features and week 2 status` / `docs: add scope and requirements sections to report draft` / `docs: record week 2 progress in weekly log` |
| **Problems encountered** | (1) Deciding realistic, measurable numbers for the non-functional requirements without any implementation yet; (2) prioritizing features for the first prototype given the single-developer constraint. |
| **Solutions attempted** | (1) Chose verifiable targets tied to the default configuration (30 stores / 300 products / 2 years) with explicit verification methods to be validated in Week 6; (2) marked the dashboard as "Should" and kept the generator, forecasts, simulator, metrics, and classification as "Must", so the Week 4 prototype can already demonstrate FR-01. |
| **References consulted** | A1-A3, T1-T3 (see `docs/references.md`); GitHub Issues documentation (https://docs.github.com/en/issues). |
| **Tests performed** | None yet - documentation phase; NFR-02/NFR-03 define the tests to be implemented in Weeks 5-6. |
| **Report sections updated** | New Sections 6-12 (Project Scope, Requirements Analysis, Functional Requirements, Non-Functional Requirements, Constraints and Assumptions, Use Cases / User Stories, Development Plan) in `docs/report_draft.md`. |
| **Next week's plan** | Architecture and technical design (Week 3): module layout of the five components, synthetic world table schema, data-flow description, technology decisions with justification. |
