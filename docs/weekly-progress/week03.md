# Week 3 Progress Record

| Field | Student response |
|-------|------------------|
| Tasks planned and completed | Converted the Week 2 requirements into a coherent technical design: (1) requirements-to-design traceability for 3 FRs + 2 NFRs (Table A); (2) component responsibility sheet for the 5 pipeline components with explicit boundaries (Table B); (3) two student-created architecture diagrams (Figure 3.1 high-level, Figure 3.2 self-validation loop) with explanations; (4) one end-to-end data flow for a single store-product-day (Table C); (5) data dictionary and forecaster interface spec (Task 3.5); (6) two ADR-style decision records (ADR-01 emulator vs real model, ADR-02 seed-generated vs committed data); (7) design walkthrough, 2 risks, and the Week 4 prototype goal (Table E). |
| New diagrams / files | `docs/design/architecture.png` + `architecture.mmd` (source), `docs/design/emulator-selfvalidation.png`, `docs/design/design-decisions.md`, `docs/design/component-interfaces.md`, `docs/weekly-progress/week03.md`. Diagram PNGs are generated from a checked-in Python script so they remain editable and reproducible. |
| GitHub commit links or hashes | (to be filled after push this week) design branch `docs/week3-architecture`; commits adding `docs/design/` and the report sections. Issue #2 (Week 3 design) will be closed via commit. |
| Technical problems found | (1) Mermaid CLI / Node were not available locally, so the `.mmd` source could not be rendered directly. (2) First matplotlib render placed arrow labels on top of component titles (text overlap). |
| Solutions considered | (1) Kept the Mermaid source as the documented diagram source and rendered the figures with matplotlib from a versioned Python script, which is also reproducible. (2) Adjusted box text layout (title vs body offsets) and rerouted the ground-truth arrow below the forecaster box to avoid crossing it; re-rendered and visually verified both PNGs. |
| References consulted | A1-A3, T1-T3 (docs/references.md); NumPy Generator/PCG64 docs (deterministic seeding, ADR-02); Beel & Lange on controlled/ground-truth evaluation (ADR-01). |
| Report sections updated | Sections 13-17 of `docs/report_draft.md`: Methodology, Proposed System, System Architecture (with Figure 3.1 and 3.2), Technology Selection (ADR-01/02), Design Decisions (risks and limitations). |
| Week 4 prototype objective | Demonstrate the synthetic world generator: a config (10 stores, 200 products, 1 year) -> `sales_history` + hidden `true_demand`, with row counts, a sample, and two identical-seed checksums printed to the terminal as proof. |

## Prepared answers to the weekly-check questions

1. **Why these components?** Because the project is an evaluation/monitoring
   layer, not a model: the 5 components mirror the decision chain
   (generate -> forecast -> decide -> evaluate -> present) so that each link,
   and especially the evaluator, can be tested in isolation.
2. **Every arrow in Figure 3.1:** history (Generator->Forecaster), rules/
   catalog/warehouse (Generator->Simulator), forecasts (Forecaster->Simulator),
   decisions+outcomes (Simulator->Evaluator), ground truth (Generator->
   Evaluator, dashed, evaluation-only), metrics+causes (Evaluator->Dashboard).
3. **One Week 2 requirement satisfied by the design:** FR-06 (deviation-cause
   classification) is satisfied by the Evaluation Framework component, and its
   correctness is made verifiable by FR-02's emulator via NFR-03b.
4. **Why the chosen technology over the alternative:** the emulator over a
   real ML model (ADR-01) because it is the only way to verify the evaluator;
   seed-generated data over committed files (ADR-02) because it guarantees
   reproducibility and data independence without storing data.
5. **Greatest technical risk:** R2 - ambiguous deviation-cause classification
   when several causes coincide; mitigated by an explicit priority rule and
   single-cause known-answer tests. First Week 4 verification: the generator
   produces the world deterministically from a seed.
6. **Which GitHub changes / report pages prove this week:** the
   `docs/week3-architecture` branch commits adding `docs/design/` and report
   Sections 13-17, plus this log.
