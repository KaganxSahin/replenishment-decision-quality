import platform
import sys
import time
from datetime import date
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))

import pandas as pd

from src.rdq.evaluation import evaluate_results
from src.rdq.generator import WorldConfig, generate_world
from src.rdq.pipeline import PipelineConfig, run_pipeline
from test_week6_validation import KnownAnswerCauseTests, MetricValidationTests


def print_known_answers():
    tester = KnownAnswerCauseTests()
    scenarios = (
        ("isolated stock", 0, 4, 1, 2, 4, 2, 2, "stock constraint"),
        ("isolated rule", 0, 4, 3, 20, 4, 3, 1, "rule constraint"),
        ("underforecast", -0.5, 4, 1, 20, 2, 2, 2, "model error"),
        ("overforecast", 0.5, 4, 1, 20, 6, 6, 0, "model error"),
        ("no error", 0, 4, 1, 20, 4, 4, 0, "other"),
        ("overlap: stock + rule + model", 0.5, 4, 4, 2, 6, 0, 4, "stock constraint"),
        ("overlap: rule + model", 0.5, 4, 4, 20, 6, 4, 0, "rule constraint"),
    )
    for name, bias, actual, pack, stock, forecast, shipped, lost, expected in scenarios:
        row = tester.run_scenario(bias, actual, pack, stock)
        observed = (row["qty_forecast"], row["qty_shipped"], row["lost_sales"], row["deviation_cause"])
        wanted = (forecast, shipped, lost, expected)
        print(f"{name}: input bias={bias}, actual={actual}, pack={pack}, warehouse={stock}; "
              f"expected forecast/shipped/lost/cause={wanted}; actual={observed}; "
              f"{'PASS' if observed == wanted else 'FAIL'}")
        if observed != wanted:
            raise AssertionError(name)


def print_metrics():
    tester = MetricValidationTests()
    tester.setUp()
    metrics = evaluate_results(tester.outcomes).metrics
    overall = metrics[metrics["level"] == "overall"].iloc[0]
    observed = (float(overall["wape"]), float(overall["mape"]), float(overall["bias"]))
    expected = (3 / 7, 0.35, 1 / 7)
    passed = all(abs(left - right) < 1e-12 for left, right in zip(observed, expected))
    print(f"metric input forecast=[3,1,4], actual=[2,0,5]; expected WAPE/MAPE/bias={expected}; "
          f"actual={observed}; {'PASS' if passed else 'FAIL'}")
    if not passed:
        raise AssertionError("hand-calculated metrics")


def print_network_guard():
    config = PipelineConfig(world=WorldConfig(seed=2, stores=2, products=3, history_days=28, future_days=2))
    with patch("socket.create_connection", side_effect=RuntimeError("network connection blocked")), \
         patch("socket.socket.connect", side_effect=RuntimeError("network connection blocked")):
        result = run_pipeline(config)
    print(f"socket-guarded small pipeline: expected 12 outcomes; actual {len(result.outcomes)}; "
          f"{'PASS' if len(result.outcomes) == 12 else 'FAIL'}")
    if len(result.outcomes) != 12:
        raise AssertionError("small pipeline row count")
    print("Limit: Python socket hooks only; not an OS-isolated network test and dashboard not included.")


def print_performance():
    config = WorldConfig(seed=42, stores=30, products=300, history_days=730,
                         future_days=1, start_date=date(2024, 1, 1))
    print(f"generator config: {config}", flush=True)
    start = time.perf_counter()
    world = generate_world(config)
    elapsed = time.perf_counter() - start
    history_rows = len(world["sales_history"])
    future_rows = len(world["true_demand"])
    passed = elapsed < 60 and history_rows == 30 * 300 * 730 and future_rows == 30 * 300
    print(f"expected history rows=6570000, future rows=9000, generator time <60 seconds; "
          f"actual history rows={history_rows}, future rows={future_rows}, "
          f"time={elapsed:.3f} seconds; {'PASS' if passed else 'FAIL'}")
    if not passed:
        raise AssertionError("NFR-01 generator performance")


if __name__ == "__main__":
    print(f"Python {platform.python_version()} | {platform.platform()}", flush=True)
    print_known_answers()
    print_metrics()
    print_network_guard()
    print_performance()
