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
confidential dataset. Inside this world, a **pluggable forecaster**
component produces demand forecasts: a built-in parametric emulator that can
inject forecast errors with precisely known causes (used to validate the
framework itself), and optionally a real statistical/ML model trained purely
on the synthetic history. A rule-based replenishment simulator turns forecasts
into daily decisions, and an evaluation framework measures their quality
against a known ground truth. The entire pipeline runs end to end from a
single command, with no database, external file, or real data of any kind.

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

## Planned Technologies

- Python 3.12
- NumPy / pandas (data processing and synthetic data generation)
- LightGBM / statsmodels (optional real forecasting model)
- Streamlit (interactive dashboard)
- pytest (testing)
- Git & GitHub (version control)

No database connector is required to run the project: the default pipeline
is fully self-contained and uses only generated or committed synthetic data.
Technologies may evolve during the project.

## Planned Features

- FR-01: Parametric, seed-based synthetic retail world generation (no real data)
- FR-02: Pluggable forecaster interface with a built-in error-injection emulator
- FR-03: Optional real forecasting model using the same interface
- FR-04: Rule-based replenishment simulation (minimum stock, pack size, warehouse availability)
- FR-05: Forecast-accuracy metrics (WAPE, MAPE, bias) aggregated by store, category, and season
- FR-06: Deviation-cause classification (model error / stock constraint / rule constraint / other)
- FR-07: Interactive dashboard with store, category, and date filters

## Scope

The first version covers: the synthetic world generator, the pluggable
forecaster interface with its built-in emulator, an optional real forecasting
model, the rule-based replenishment simulator, the evaluation framework
(metrics and deviation-cause classification, validated with known-answer
tests), the dashboard, and automated tests. No real or confidential data is
used anywhere - not for storage, and not for calibrating any synthetic
parameter. Excluded: modifying a production replenishment engine, automatic
model retraining, real-time streaming analysis, customer-level analysis, and
price optimization. The full specification with non-functional requirements,
user stories, and milestones is in `docs/requirements.md`; planned work is
tracked in
[GitHub Issues](https://github.com/KaganxSahin/replenishment-decision-quality/issues).

## Current Status

Week 3 - Architecture and technical design completed. The five-component
pipeline (generator, pluggable forecaster, simulator, evaluator, dashboard)
is fully specified: requirements-to-design traceability, component
responsibility sheet, one end-to-end data flow, data dictionary, forecaster
interface contract, two ADRs (emulator-vs-real-model and seed-generated-vs-
committed-data), and two student-created architecture diagrams.

Design artifacts live in `docs/design/`:

- [High-level architecture diagram](docs/design/architecture.png) (Figure 3.1)
  and the [self-validation / known-answer loop](docs/design/emulator-selfvalidation.png)
  (Figure 3.2), with editable sources.
- [design-decisions.md](docs/design/design-decisions.md) - traceability,
  component sheet, data flow, risks, ADR-01 / ADR-02.
- [component-interfaces.md](docs/design/component-interfaces.md) - forecaster
  interface and data dictionary.

Report Sections 13-17 (Methodology, Proposed System, System Architecture,
Technology Selection, Design Decisions) added in `docs/report_draft.md`.
Next: Week 4 prototype - the synthetic world generator.
