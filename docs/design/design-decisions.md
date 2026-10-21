# Design Decisions (Week 3)

This document holds the requirements-to-architecture mapping, the component
responsibility sheet, one end-to-end data flow, the design risk table, and the
two architecture decision records (ADRs). It complements `docs/architecture.md`
(pipeline narrative) and `docs/design/component-interfaces.md` (interface and
data dictionary).

## Table A - Requirements-to-Design Traceability

| ID | Requirement in my project | Design response / component |
|----|---------------------------|-----------------------------|
| FR-01 | Generate a synthetic retail world (stores, products, warehouse, history, hidden future true demand) from a seed, using only general domain knowledge. | Component 1 (Synthetic World Generator). A single, deterministic entry point (`generate_world(config, seed)`) that emits the world tables; seeding and fixed generators guarantee NFR-02. Because ground truth is produced here, the evaluation component can compare forecasts to true demand, which is impossible with real (censored) sales data. |
| FR-02 | Provide a pluggable forecaster interface and a built-in error-injection emulator with controllable, known error characteristics. | Component 2 (Forecaster). A shared interface `predict(history, horizon) -> forecasts` with two implementations: (a) the emulator, which exposes bias / variance / seasonal-drift parameters; (b) an optional real model. The emulator is the Must-have implementation because it enables NFR-03b (known-answer validation of the evaluator). |
| FR-06 | Classify each forecast-vs-shipped deviation by cause (model error, stock constraint, rule constraint, other). | Component 4 (Evaluation Framework). Compares three pairwise views (forecast vs true demand, forecast vs shipped, decision vs outcome) and assigns a cause by inspecting rule inputs (warehouse availability, pack size) and the forecast error. Validated by the emulator's known-cause output (NFR-03b). |
| NFR-03 | Correctness: metrics match hand-calculated values; the deviation classifier recovers emulator-injected causes. | The evaluation framework exposes pure, deterministic functions (no I/O) so they can be unit-tested; the emulator produces scenarios with a single, precisely known cause, enabling known-answer (ground-truth) tests of the classifier. |
| NFR-04 | Data Independence: the full pipeline runs end to end with no database, external API, or real data file. | A single CLI entry point (`python -m rdq.pipeline --seed 42`) that orchestrates generate -> forecast -> simulate -> evaluate -> dashboard; all data lives in memory / committed synthetic test fixtures only. No connector code is present by default. |

## Table B - Component Responsibility Sheet

| Component | Responsibility / main input | Output / connection |
|-----------|----------------------------|---------------------|
| 1. Synthetic World Generator | Build the fictional retailer from config + seed. Input: generation config (store count, product count, category set, seasonality amplitudes, warehouse capacity, rule parameters) and a random seed. | World tables: `stores`, `products`, `warehouse`, `sales_history` (training window), `true_demand` (hidden future). Feeds the Forecaster (history) and the Simulator (rules, catalog, warehouse); the hidden `true_demand` feeds only the Evaluator. |
| 2. Forecaster (pluggable) | Produce store-product-level demand forecasts for a horizon. Input: `sales_history` and horizon. | `forecasts` table (date, store_id, product_id, qty_forecast). (a) emulator: forecasts with controllable, known error; (b) optional real model: same interface, trained on synthetic history. Output feeds the Simulator. |
| 3. Replenishment Simulator | Turn forecasts into daily ship decisions by applying business rules; simulate inventory, sales, stock-outs. Input: `forecasts` + world rules (min stock, pack size, warehouse availability). | `decisions` table (requested vs shipped per store-product-day), `outcomes` table (inventory, sales, stock-out flags, lost sales). Output feeds the Evaluator. |
| 4. Evaluation Framework | Measure decision quality. Input: `forecasts`, `decisions`, `outcomes`, and the hidden `true_demand`. | `metrics` (WAPE/MAPE/bias by store/category/season), `deviation_causes` (model/stock/rule/other), `outcome_indicators`. Output feeds the Dashboard and the known-answer tests. |
| 5. Dashboard | Present results interactively. Input: `metrics`, `deviation_causes`, `outcome_indicators`. | Streamlit UI with store/category/date filters and drill-downs. This is the only user-facing component. |

**Boundaries.** All five components run locally on the user's machine; there is
no server, controller, cloud service, database, or external API. The only
"user" is the developer/analyst running the CLI and viewing the dashboard.
There are no external systems outside our control. The Synthetic World
Generator and the Evaluation Framework are the components that own the
important data (the world tables and the evaluation outputs); the hidden
`true_demand` is deliberately visible only to the Evaluator, never to the
Forecaster, so that "forecast vs true demand" remains a fair comparison.

## Table C - End-to-End Execution Scenario (one day, one store-product)

| Step | Component | Input, operation, and output |
|------|-----------|------------------------------|
| 1 | Forecaster (2a emulator) | Input: `sales_history` for store S, product P + horizon=1. Operation: produce forecast Q_f; the emulator applies its configured error profile (e.g., +20% bias). Output: forecast Q_f. |
| 2 | Replenishment Simulator | Input: Q_f + rules (min stock M, pack size K, warehouse availability W). Operation: requested = max(Q_f, M); shipped = round_down(requested, K); shipped = min(shipped, W). Output: decision record (requested, shipped). |
| 3 | Replenishment Simulator | Input: shipped + true demand D (from hidden world). Operation: sales = min(shipped, D); lost_sales = max(0, D - shipped); inventory updates; stock-out flag if lost_sales > 0. Output: outcome record. |
| 4 | Evaluation Framework | Input: Q_f, decision, outcome, true demand D. Operation: compare Q_f vs D (accuracy); Q_f vs shipped (deviation + cause: stock if shipped<requested due to W, rule if due to K, model if Q_f wrong, else other); outcome indicators. Output: metric + cause + indicator rows. |
| 5 | Dashboard | Input: aggregated evaluation rows. Operation: render by store/category/season with filters. Output: interactive charts. |

**Interface note (model).** The forecaster is the only model-like interface.
Input features: per store-product time series from `sales_history` (date,
quantity). Output prediction: a non-negative quantity per date in the horizon.
The emulator's "model" is deterministic given the seed and error profile; the
optional real model uses lag/rolling features.

**Failure case (expected).** If the Forecaster produces a missing or negative
forecast for a store-product-day, the Simulator treats it as zero demand (a
safe default), still records the decision, and the Evaluator flags the row as
an anomaly cause="other" rather than crashing the pipeline. This keeps a single
bad forecast from aborting a whole run.

## Table E - Design Risk and Mitigation

| Risk | Potential impact | Mitigation / verification |
|------|------------------|---------------------------|
| R1: The parametric demand model (seasonality + heterogeneity) may not reproduce realistic retail error patterns, so the evaluation framework could be "trained/tested" on too-easy data. | The framework works on synthetic data but does not generalise; conclusions are weak. | Mitigate by making the emulator's error profiles configurable (bias, variance, seasonal drift, plus rule interactions) and by including an optional real forecaster as a stress case. Verify in Week 5-6 by running the evaluator on emulator scenarios of increasing difficulty and confirming it still separates causes correctly (NFR-03b). |
| R2: The deviation-cause classification rules may be ambiguous when several causes coincide on one day (e.g., both a warehouse shortage and a pack-size rounding). | The classifier picks the wrong or an arbitrary cause, undermining NFR-03b and the project's core claim. | Mitigate by defining an explicit priority order (stock constraint -> rule constraint -> model error -> other) and by making the emulator inject exactly one cause at a time for the known-answer tests. Verify with unit tests that each single-cause scenario is recovered, and that the priority rule is applied deterministically when causes coincide. |

**Week 4 hand-off (verifiable).** "In Week 4, I will demonstrate the synthetic
world generator, where a generation config (e.g., 10 stores, 200 products,
1 year) passes through the Synthetic World Generator component to produce
`sales_history` and a hidden `true_demand` table, printed as row counts and a
sample to the terminal, and re-running with the same seed produces an
identical checksum." Proof: terminal output showing the generated row counts,
a `head()` of the sales table, and the two identical run checksums.

## ADR-01 - How to produce forecasts: emulator vs real model first

- **Issue:** The evaluation framework must be fed forecasts, and it must also
  be proven correct. Should the core forecaster be a real ML model or a
  controllable emulator?
- **Selected option:** A parametric **error-injection emulator** as the core
  (Must) forecaster, behind a pluggable interface, with a real ML model as an
  optional (Should) plug-in.
- **Alternative:** Use a real ML model (e.g., LightGBM) as the only / core
  forecaster.
- **Reason / trade-off:** The project's central claim is that the evaluator
  attributes deviations to the correct cause. With a black-box real model we
  cannot know the true cause of any deviation, so we could never verify the
  evaluator. The emulator can inject a single, precisely known cause, enabling
  known-answer tests (NFR-03b) - it is the only way to prove the evaluator
  works before trusting it. It is also far less code and fits the 9-week,
  single-developer, part-time constraint. The trade-off (emulator errors are
  synthetic) is accepted and declared as an assumption (Section 10 of the
  report). The pluggable interface keeps a real model attachable without
  redesign.
- **Reference URL:** Beel & Lange, "A Comparison of Offline Evaluations,
  Online Evaluations, and User Studies" - motivation for controlled /
  ground-truth evaluation (see docs/references.md, A2); NFR-03b and US-04.

## ADR-02 - Where does the data come from: committed data file vs seed-generated

- **Issue:** The course requires the project to be reproducible by anyone, and
  data must not be confidential. Should the synthetic data be committed as
  files, or generated on demand?
- **Selected option:** **Generate all data on demand** from a fixed seed via a
  single CLI entry point; commit only a tiny, hand-built synthetic test
  fixture for unit tests.
- **Alternative:** Generate the data once and commit the resulting data files
  (CSV/parquet) to the repository.
- **Reason / trade-off:** A fixed seed with deterministic generators already
  guarantees bit-for-bit reproducibility (NFR-02) without storing any data,
  keeping the repository small and guaranteeing data independence (NFR-04) by
  construction - there is no data file to leak or to depend on. Committing
  large data files would bloat the repo, still requires the generator for new
  configurations, and adds nothing the seed does not already provide. The
  trade-off (generation must run before evaluation, ~seconds) is negligible
  (NFR-01 allows 60 s).
- **Reference URL:** NumPy `Generator` / `PCG64` documentation - deterministic
  pseudo-random generation from a seed (https://numpy.org/doc/stable/reference/random/);
  NFR-02 and NFR-04.
