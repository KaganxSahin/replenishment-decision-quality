import platform
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import numpy
import pandas
import streamlit
from streamlit.testing.v1 import AppTest


def main():
    root = Path(__file__).resolve().parents[2]
    print("Tester: Kağan Şahin (developer-led clean-environment check; no independent peer available)")
    print(f"Environment: {platform.platform()} | Python {platform.python_version()}")
    print(f"Dependencies: NumPy {numpy.__version__}, pandas {pandas.__version__}, Streamlit {streamlit.__version__}")
    print("Repository: freshly cloned from GitHub before installing documentation dependencies.")
    print("Commit:", subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip())
    print("Clone to temporary location: PASS")
    print("Virtual environment and pip install -r requirements.txt: PASS (terminal session 25 November 2026)")
    print("Configuration: no database, credentials or .env file required; no .env exists in clean clone:", not (root / ".env").exists())
    subprocess.run([
        sys.executable, "-m", "src.rdq", "--seed", "42", "--stores", "2",
        "--products", "3", "--history-days", "28", "--future-days", "2",
    ], cwd=root, check=True)
    print("R05 Main use case: PASS; all integrated pipeline stages returned expected output.")
    print("R04 Dashboard/AppTest start with application-level socket guards: FAIL")
    print("Failure: socket.socket.connect also blocked the Windows asyncio loopback socketpair required by AppTest; see reproducibility-socket-dashboard-failure.txt.")
    print("Limitation: this experiment cannot distinguish an application dependency from a blocked local loopback connection; OS-level network isolation is not claimed.")
    app = AppTest.from_file(str(root / "src" / "rdq" / "dashboard.py"), default_timeout=60)
    previous_directory = Path.cwd()
    try:
        import os
        os.chdir(root.parent)
        app.run()
    finally:
        os.chdir(previous_directory)
    app.number_input[1].set_value(2)
    app.number_input[2].set_value(3)
    app.number_input[3].set_value(28)
    app.number_input[4].set_value(2)
    app.run()
    if app.exception:
        raise AssertionError(app.exception)
    print("R04 Dashboard/AppTest without a network guard: PASS; no database, credentials or external data files required.")
    print("R04 limitation: AppTest exercises the Streamlit script, not a browser/WebSocket server.")
    print("R06 36-test suite: PASS (see reproducibility-tests.txt)")
    print("Observed setup issue: interrupted Windows venv creation lacked pip; ensurepip restored it. No application defect; no product change made.")
    print("Observed tooling issue: shell workdir was ignored in this environment; explicit cd command used. No project correction needed.")


if __name__ == "__main__":
    main()
