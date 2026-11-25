# Week 7 Integration and Reproducibility

## Environment and method

Tester: Kağan Şahin, the project developer. No peer was available, so this is a
developer-led clean-environment test as permitted by the Week 7 guide; it is
not independent peer validation. The test was performed on 25 November 2026
using Windows 11 build 26300, Python 3.12.10 and Git for Windows. The public
GitHub repository was cloned into a separate folder, a new `.venv` was created,
and `requirements.txt` installed NumPy 2.5.3, pandas 3.0.6 and Streamlit 1.67.0.
The baseline commit was
[8740ff5](https://github.com/KaganxSahin/replenishment-decision-quality/commit/8740ff5).

The complete use case is `WorldConfig` → synthetic world →
`ErrorInjectionEmulator.fit/predict` → `simulate_replenishment` →
`evaluate_results` → CLI or Streamlit dashboard. `run_pipeline` coordinates
in-memory pandas DataFrames. Future true demand reaches the simulator and
evaluator, not the forecaster. The five-component architecture did not change.
The dashboard shares this pipeline and recomputes filtered metrics; it is a
separate Streamlit entry point, not a service automatically started by the CLI.

## Reproducibility results

| ID | Operation | Expected result | Actual result / status |
|---|---|---|---|
| R01 | Clone repository | Public repository downloads into a separate folder | Baseline `8740ff5` cloned successfully. **PASS** |
| R02 | Install dependencies | Fresh venv installs `requirements.txt` | NumPy, pandas, Streamlit and transitive dependencies installed; `pip check` reported no broken requirements. **PASS** |
| R03 | Configure system | No unprovided secret, database or data file needed | No `.env`, credentials, database or external dataset required. Placeholder `.env.example` was not used. **PASS** |
| R04 | Build/start | Pipeline and dashboard start | CLI passed. Dashboard `AppTest` initially failed outside repository root; corrected and retested. **PASS after fix** |
| R05 | Main use case | Integrated generation → forecast → simulation → evaluation produces expected output | Small seeded run returned 168 history rows, 12 future rows, 12 forecasts and 12 outcomes, with metrics/cause summary. **PASS** |
| R06 | Run tests | Full automated suite executes successfully | 37 tests passed after the integration correction. **PASS** |

See [terminal results](../evidence/week-07/reproducibility-check.txt) and
[full test output](../evidence/week-07/reproducibility-tests.txt).

## Actual problems, corrections and boundaries

**Dashboard import failure.** During the clean-environment verification,
`AppTest.from_file()` launched the dashboard from outside the repository root.
Python could not resolve `from src.rdq...`, producing `ModuleNotFoundError`.
The dashboard now derives `PROJECT_ROOT` from its own file location and adds it
to `sys.path` when necessary. A regression test covers a working directory
outside the root. The clean-environment check and full suite were rerun
successfully. Failure evidence:
[dashboard-import-failure.txt](../evidence/week-07/dashboard-import-failure.txt).

**Environment/tooling observations.** An interrupted Windows venv setup lacked
pip; `python -m ensurepip --upgrade` restored it and installation succeeded.
The command environment also ignored a working-directory parameter; explicit
`cd` commands were used. Neither required an application change.

**Socket-guard limitation.** Blocking both `socket.create_connection` and
`socket.socket.connect` caused the AppTest startup to fail: Windows asyncio
uses a loopback socketpair, which the blanket guard also blocks. Therefore the
experiment cannot prove that the dashboard works with all network access
disabled. The failed output is retained in
[reproducibility-socket-dashboard-failure.txt](../evidence/week-07/reproducibility-socket-dashboard-failure.txt).
The unguarded AppTest dashboard passed. No OS-isolated network, live browser,
or independent peer test is claimed.

Installation requires package-index access or a local package cache; the
runtime uses generated in-memory data only. Other operating systems and Python
versions were not tested. No real or confidential data or credentials were
used. A final live dashboard demonstration remains for Week 9; Week 8 will
complete the report and add presentation screenshots.
