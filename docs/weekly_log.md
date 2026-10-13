# Weekly Progress Log

## Week 1 - Project Definition, References and GitHub

| Field | Content |
|---|---|
| **Week** | 1 (October 2026) |
| **Tasks planned** | Define project idea and scope, identify target users, find academic and technical references, create GitHub repository, start the Graduation Project Report. |
| **Tasks completed** | Project idea defined (evaluation and monitoring framework for ML-driven replenishment decisions); target users identified; 3 academic and 3 technical references collected and summarized; GitHub repository created with initial README; report draft sections written (Introduction, Problem Statement, Motivation, Objective, Preliminary Scope). |
| **GitHub commits** | `docs: create initial README with project definition` / `docs: add project description and report draft` / `docs: add references and weekly progress log` |
| **Problems encountered** | (1) Choosing between several candidate project ideas; (2) how to use confidential industry data without exposing it in a public repository. |
| **Solutions attempted** | (1) Evaluated candidates against feasibility, academic reference availability, and real-world value; selected the evaluation/monitoring direction. (2) Adopted the principle "code in the repository, data stays local": real data is accessed only through a local database connection, nothing confidential is committed, and a synthetic data generator will make the project reproducible by anyone. |
| **References consulted** | A1-A3, T1-T3 (see `docs/references.md`). |
| **Tests performed** | None yet - Week 1 contains documentation only, no code. |
| **Report sections updated** | Introduction, Problem Statement, Motivation, Project Objective, Preliminary Scope (initial drafts in `docs/report_draft.md`). |
| **Next week's plan** | Requirements engineering: functional and non-functional requirements, use cases / user stories, constraints and assumptions; create GitHub Issues for planned work. |

## Week 2 - Data Strategy Decision and Architecture

| Field | Content |
|---|---|
| **Week** | 2 (October 2026) |
| **Tasks planned** | Finalize the data strategy with the industry partner, refine the project definition accordingly, document the system architecture. |
| **Tasks completed** | Data strategy decided: the project runs **entirely on synthetic data** - no real or confidential data is used at any point. A synthetic retail world generator (fictional footwear retailer, calibrated from real retail patterns, no real records) becomes the data source; a forecasting engine and a rule-based replenishment simulator produce the decisions to be evaluated. README, project description, and report draft updated to the simulation-based design; architecture overview document added (`docs/architecture.md`). |
| **GitHub commits** | `docs: switch project definition to fully synthetic simulation approach` / `docs: add architecture overview of simulation pipeline` / `docs: log data strategy decision in weekly log` |
| **Problems encountered** | (1) Real production data cannot be used even locally in the project, so the original "validate on real data" plan had to be replaced; (2) simply masking real records would still leak real data, so a proper generation approach was needed. |
| **Solutions attempted** | (1) Adopted a simulation-based design: a fully synthetic retail world with known ground truth, which also enables measuring forecasts against true demand (impossible with real data where stock-outs censor sales). (2) The generator is calibrated from aggregate statistical patterns only (seasonality curves, store/product profiles); no real records are copied, and the repository contains no real data at all. |
| **References consulted** | A1-A3, T1-T3 (see `docs/references.md`); LightGBM and statsmodels documentation reviewed for the forecasting engine. |
| **Tests performed** | None yet - documentation phase; the generator will be the first tested module. |
| **Report sections updated** | Introduction, Problem Statement (added the data-confidentiality barrier), Motivation, Project Objective, Preliminary Scope - all revised for the simulation-based design in `docs/report_draft.md`. |
| **Next week's plan** | Requirements engineering: functional and non-functional requirements, use cases / user stories, constraints and assumptions; create GitHub Issues for planned work. |
