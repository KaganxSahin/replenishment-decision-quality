# Week 6 Testing and Validation

## Strategy and environment

On 23 November 2026, tests were run on Windows 11 (build 26200), Python
3.12.10, NumPy 2.5.3, pandas 3.0.6 and Streamlit 1.67.0. The standard-library
`unittest` runner was used for unit, boundary, integration and CLI checks;
Streamlit `AppTest` exercised the UI. `time.perf_counter()` measured generator
runtime. The entire suite ran 33 tests in 12.601 seconds, all passing; the
Streamlit bare-mode warnings in the log are expected and did not fail tests.
Only fictional data generated from explicit inputs was used.

The metric test derives its expected values independently from the given
quantities. The classification scenarios use a constant fictional sales history
of four units, zero noise and drift, controlled forecast bias, and separately
configured pack size and warehouse stock. The emulator only controls forecast
error; a stock or rule constraint is imposed by the simulator inputs, not by
the forecast emulator. The simulator assigns the labels that the evaluator
summarizes, so these are tests of the implemented simulator/evaluator pipeline,
not an independent causal inference algorithm.

## Test cases and actual results

All runs below occurred on 23 November 2026. Full method-level outcomes are in
[tests.txt](../evidence/week-06/tests.txt); detailed numeric results and the
benchmark are in [checks.txt](../evidence/week-06/checks.txt). Test-method
names below identify the assertions behind results; a passing grouped unittest
means all its individual assertions and subtests passed.

| ID | Requirement / objective | Input | Expected | Observed | Status / evidence |
|---|---|---|---|---|---|
| T01 | FR-01: generated counts and period separation | Seed 42; 3 stores, 5 products, 4 history and 2 future days | 3 stores, 5 products/warehouse rows, 60 history, 30 future rows; future after history | All counts and dates matched, including leap day | PASS: `test_expected_tables_and_row_counts`, `test_dates_are_contiguous_and_future_is_separate` |
| T02 | FR-01, NFR-02: repeatability | Same small-world configuration and seed twice; small pipeline seed 19 twice | Equal world, forecast, outcome and evaluation DataFrames | Every world table and pipeline output matched | PASS: `test_same_seed_reproduces_all_tables`, `test_all_tables_and_results_repeat_for_same_seed` |
| T03 | FR-01/02: seed and error settings | Generator seeds 42/43; emulator seeds 29/30 and bias 0.5 | Different seeds change respective stochastic outputs; 2-observation baselines produce 7.5 and 6.0 with bias 0.5 | Output changes and bias values matched | PASS: `test_different_seed_changes_generated_data`, `test_different_seed_changes_noisy_forecasts`, `test_bias_applies_to_trailing_baseline` |
| T04 | FR-01/02/04: invalid/boundary inputs | Minimum world dimensions 1, seed 0; invalid CLI dimensions/seed/date, forecast horizon and pack size | Minimum valid input works; invalid input rejected; CLI has no traceback | One row per minimum-world table; invalid cases rejected as expected | PASS: `test_minimum_valid_dimensions_and_zero_seed`, `test_cli_rejects_invalid_arguments_without_traceback`, `test_predict_rejects_invalid_horizon`, `test_invalid_pack_size_is_rejected` |
| T05 | FR-02/04/06, NFR-03: isolated stock constraint | Emulator history [4,4,4], bias 0, true demand 4, pack 1, warehouse 2 | Forecast 4, shipment 2, lost sales 2, stock constraint | 4, 2, 2, stock constraint | PASS: `test_isolated_known_causes_and_no_error`; checks.txt |
| T06 | FR-02/04/06, NFR-03: isolated pack rule | Same history, bias 0, demand 4, pack 3, warehouse 20 | Forecast 4, shipment 3, lost sales 1, rule constraint | 4, 3, 1, rule constraint | PASS: same test; checks.txt |
| T07 | FR-02/04/06: model error and no error | History [4,4,4], demand 4, pack 1, warehouse 20; bias -0.5 / +0.5 / 0 | Forecast/ship/lost: 2/2/2, 6/6/0, 4/4/0; labels model/model/other | Each tuple and label matched | PASS: same test; checks.txt |
| T08 | FR-04/06: overlapping rules | Forecast 6, demand 4, pack 4; warehouse 2 and then 20 | Stock + rule + model => stock constraint; rule + model => rule constraint | Shipment 0 / 4; labels stock / rule respectively | PASS: `test_overlapping_constraints_follow_documented_priority`; checks.txt. This checks priority, not exclusive causal attribution. |
| T09 | FR-05, NFR-03: hand-calculated metrics and segments | Forecast [3,1,4], actual [2,0,5], two stores/products, winter/spring | Overall WAPE 3/7, MAPE 0.35 excluding zero actual, bias 1/7; each selected segment matches hand calculation | 0.4285714286 / 0.35 / 0.1428571429; asserted segment values matched | PASS: `test_hand_computed_metrics_and_each_segment`; checks.txt |
| T10 | FR-05: zero and invalid values | All actuals zero; empty input, infinity, negative quantities, missing lost sales, invalid cause, duplicated key | Undefined zero-denominator metrics are NaN; invalid input rejected | Expected NaNs and ValueErrors observed | PASS: `test_mapes_zero_actuals_and_empty_data_are_handled`, `test_invalid_values_and_unknown_cause_are_rejected` |
| T11 | FR-07, US-01: dashboard filters | Two stores, five products, 28 history/3 future days; first store/category and 29 Jan 2024 | Selected records match all three filters; displayed WAPE, MAPE, bias and lost sales equal independent calculations from raw rows | All filter and metric assertions matched | PASS: `test_dashboard_filtered_metrics_match_raw_records` |
| T12 | NFR-01: generator performance | Seed 42, 30 stores, 300 products, 730 history days, 1 future day | 6,570,000 history rows, 9,000 future rows; under 60 s | Expected rows; generator 0.607 s in this run | PASS: checks.txt. This is generator-only, not full-pipeline performance. |
| T13 | NFR-04: external dependence, partial check | Small 2-store/3-product/28-history/2-future pipeline; Python socket connect hooks reject outgoing connections | 12 outcome rows without database or data files | 12 outcome rows | PASS for this limited socket-guarded run, not for full NFR-04: checks.txt. OS-level no-network machine and dashboard were not tested. |

## Requirement coverage and limits

FR-01, FR-02, FR-04, FR-05 and FR-07 have representative positive and boundary
coverage; FR-06 and NFR-03 have the seven listed controlled cause scenarios and
hand-checked metrics. These do not exhaust every forecast error or overlapping
constraint. The label algorithm is a precedence-based heuristic; even the
`model error` label means the forecast and generated demand differ, not that a
real-world causal diagnosis is established. It assigns labels to all rows, not
only rows with forecast-vs-shipment deviations. Further assessment is needed
before treating the complete wording of FR-06 as verified.

NFR-01 passed for one measured generator configuration and machine. NFR-02
passed for the tested seed/configuration and environment, not across all
platforms or dependency versions. NFR-04 is only partially verified; patching
Python socket connection methods is not equivalent to isolating an operating
system network, nor did that check include the Streamlit dashboard. Week 7
should perform a genuine offline, no-database end-to-end check including UI,
and an independent developer installation/run. FR-03 is optional and remains
unimplemented. Statistical realism and application to any real retailer are
outside these results.

No product defect was observed in the Week 6 test runs; no code bug-fix or
failure-to-fix-to-retest sequence is claimed. Test and evidence commit:
[5749236](https://github.com/KaganxSahin/replenishment-decision-quality/commit/5749236).
