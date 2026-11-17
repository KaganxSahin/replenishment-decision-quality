# Development Process - Stage 2: Forecaster and Error Emulator

| Field | Record |
|---|---|
| Date | 17 November 2026 |
| Objective | Implement the Week 3 forecaster contract and a configurable synthetic forecast-error emulator for the Week 5 pipeline. |
| Requirements | FR-02; supports controlled development toward NFR-02 and NFR-03. |
| Implemented functionality | `src/rdq/forecaster.py` defines a `Forecaster` protocol with `fit(sales_history)` and `predict(horizon)`, an `EmulatorConfig`, and `ErrorInjectionEmulator`. The emulator fits a trailing 28-observation average for each store-product pair and applies configurable bias, seasonal drift, variance, and seed. Forecasts are clipped to non-negative quantities. |
| Inputs and boundaries | The emulator accepts historical rows with `date`, `store_id`, `product_id`, and `qty`. It does not receive the separate future `true_demand` table. Missing/invalid data, duplicate grain, negative quantities, invalid settings, or prediction before fitting are rejected. |
| Output | A DataFrame with `date`, `store_id`, `product_id`, and `qty_forecast`, one row per history pair per requested horizon date. |
| Technical decision and limitation | The emulator is the implemented core forecaster; its noise scale is computed from the configured variance. No optional statistical or ML forecaster is implemented. The emulator's forecast patterns are synthetic and do not establish realism for production forecast errors. |
| Problems and solutions | No unresolved Stage 2 defect is reported. The full forecaster tests passed in the Week 5 run. |
| Verification | The suite contains 10 forecaster tests covering same/different seed behavior, bias, dates and rows, input validation, invalid horizon, fit-before-predict, and separation from future demand. All 10 passed as part of the 27-test suite. See [test output](../evidence/week-05/tests.txt). |
| Evidence and related work | [Week 5 architecture comparison](design/architecture-comparison-week5.md); [first pipeline run](../evidence/week-05/pipeline-run.txt); related GitHub issue [#6](https://github.com/KaganxSahin/replenishment-decision-quality/issues/6). |
| Commit / publication status | The implementation was committed as [9fa5d47](https://github.com/KaganxSahin/replenishment-decision-quality/commit/9fa5d47dbfcbba332bd31494a32af780450ea6a2), and this record was included in [d000103](https://github.com/KaganxSahin/replenishment-decision-quality/commit/d00010385d81f161504c5ce5ca41c08e814d60f7); both were pushed to `origin/main`. The GitHub issue status was not changed. |
| Next step | Stage 3: connect forecasts to replenishment simulation, initial evaluation, and dashboard reporting; then validate known-answer cause scenarios in Week 6. |
