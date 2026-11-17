# Week 5 Progress Record

| Field | Record |
|---|---|
| Date | 17 November 2026 |
| Objective | Extend the Week 4 synthetic generator into a working forecast → replenishment → evaluation flow and add the first dashboard. |
| Work completed locally | Implemented the forecaster protocol and error-injection emulator; connected the emulator to a replenishment simulator; added WAPE/MAPE/bias metrics and cause summaries; added shared pipeline orchestration and a Streamlit dashboard with synthetic configuration and filters. Recorded an architecture-to-implementation comparison and actual CLI/test evidence. |
| Requirements addressed | FR-02 (emulator), FR-04 (simulation), FR-05 (metrics), FR-06 (heuristic cause labels), and FR-07 (dashboard). Optional real model FR-03 remains unimplemented. |
| Technical decisions | Kept future true demand out of forecaster inputs; used one shared pipeline for CLI and dashboard; returned decisions and outcomes in a combined table. Cause labels are assigned by a fixed simulator heuristic and should not be interpreted as proven exclusive causal attribution. |
| Environment | Windows; Python 3.12.10; NumPy 2.5.3; pandas 3.0.6; Streamlit 1.67.0; Python standard-library `unittest`. `pip check` reported no broken requirements. |
| Problems and solutions | Streamlit AppTest exposed package-relative imports and its dataframe API required an updated width argument; absolute imports and supported arguments resolved the smoke test. A simulator rule-check edge case incorrectly identified a pack-size restriction; the condition was corrected to detect actual minimum-stock or pack-size constraints. No known-answer cause-classification test is claimed. |
| Verification | Default seed-42 CLI run generated 10 stores, 200 products, 730,000 historical rows, 56,000 forecasts, and 56,000 simulation rows. A second same-seed run had byte-identical CLI output. The full suite ran 27 tests and passed. See [pipeline run](../../evidence/week-05/pipeline-run.txt), [repeat](../../evidence/week-05/pipeline-run-repeat.txt), [comparison](../../evidence/week-05/repeatability-check.txt), and [tests](../../evidence/week-05/tests.txt). |
| Architecture comparison | [Week 5 comparison](../design/architecture-comparison-week5.md) documents the five-component design match, deviations, rationale, and remaining boundaries. |
| GitHub / commit record | The implementation was committed as [9fa5d47](https://github.com/KaganxSahin/replenishment-decision-quality/commit/9fa5d47dbfcbba332bd31494a32af780450ea6a2); this Week 5 documentation and evidence was committed as [d000103](https://github.com/KaganxSahin/replenishment-decision-quality/commit/d00010385d81f161504c5ce5ca41c08e814d60f7). Both commits are on `origin/main`. GitHub issue statuses were not changed. Related issues: [#4](https://github.com/KaganxSahin/replenishment-decision-quality/issues/4), [#5](https://github.com/KaganxSahin/replenishment-decision-quality/issues/5), [#6](https://github.com/KaganxSahin/replenishment-decision-quality/issues/6). |
| Next week | Week 6: validate isolated and combined known-answer cause scenarios, expand boundary/metric checks, and record the planned performance test. |

The completed stages are documented in [Stage 2](../development-stage-2.md) and
[Stage 3](../development-stage-3.md). Full production applicability and
statistical realism are outside what these synthetic tests establish.
