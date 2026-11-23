import unittest
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
from streamlit.testing.v1 import AppTest

from src.rdq.evaluation import evaluate_results
from src.rdq.forecaster import EmulatorConfig, ErrorInjectionEmulator
from src.rdq.generator import WorldConfig
from src.rdq.pipeline import PipelineConfig, run_pipeline
from src.rdq.simulator import SimulationConfig, simulate_replenishment


class KnownAnswerCauseTests(unittest.TestCase):
    def run_scenario(self, bias, actual, pack_size, warehouse, minimum_stock=0):
        history = pd.DataFrame({
            "date": pd.date_range("2024-01-01", periods=3),
            "store_id": [1, 1, 1],
            "product_id": [10, 10, 10],
            "qty": [4, 4, 4],
        })
        emulator = ErrorInjectionEmulator(EmulatorConfig(
            seed=7, bias=bias, variance=0, seasonal_drift=0,
        ))
        emulator.fit(history)
        forecasts = emulator.predict(1)
        demand = pd.DataFrame({
            "date": [pd.Timestamp("2024-01-04")],
            "store_id": [1],
            "product_id": [10],
            "qty_true": [actual],
        })
        products = pd.DataFrame({
            "product_id": [10], "category": ["tops"], "pack_size": [pack_size],
        })
        stock = pd.DataFrame({"product_id": [10], "qty_available": [warehouse]})
        return simulate_replenishment(
            forecasts, demand, products, stock, SimulationConfig(minimum_stock),
        ).iloc[0]

    def test_isolated_known_causes_and_no_error(self):
        scenarios = (
            ("stock", 0, 4, 1, 2, 4, 2, 2, "stock constraint"),
            ("rule", 0, 4, 3, 20, 4, 3, 1, "rule constraint"),
            ("underforecast", -0.5, 4, 1, 20, 2, 2, 2, "model error"),
            ("overforecast", 0.5, 4, 1, 20, 6, 6, 0, "model error"),
            ("none", 0, 4, 1, 20, 4, 4, 0, "other"),
        )
        for name, bias, actual, pack, warehouse, forecast, shipped, lost, cause in scenarios:
            with self.subTest(name=name):
                row = self.run_scenario(bias, actual, pack, warehouse)
                self.assertEqual(row["qty_forecast"], forecast)
                self.assertEqual(row["qty_shipped"], shipped)
                self.assertEqual(row["lost_sales"], lost)
                self.assertEqual(row["deviation_cause"], cause)
                self.assertEqual(row["qty_sold"] + row["lost_sales"], actual)
                self.assertEqual(row["store_inventory_end"], shipped - row["qty_sold"])

    def test_overlapping_constraints_follow_documented_priority(self):
        row = self.run_scenario(bias=0.5, actual=4, pack_size=4, warehouse=2)
        self.assertEqual(row["qty_forecast"], 6)
        self.assertEqual(row["qty_to_order"], 6)
        self.assertEqual(row["qty_shipped"], 0)
        self.assertEqual(row["deviation_cause"], "stock constraint")
        rule_and_model = self.run_scenario(bias=0.5, actual=4, pack_size=4, warehouse=20)
        self.assertEqual(rule_and_model["qty_shipped"], 4)
        self.assertEqual(rule_and_model["deviation_cause"], "rule constraint")


class MetricValidationTests(unittest.TestCase):
    def setUp(self):
        self.outcomes = pd.DataFrame({
            "date": ["2024-01-01", "2024-01-02", "2024-04-01"],
            "store_id": [1, 1, 2],
            "product_id": [10, 10, 20],
            "category": ["tops", "tops", "trousers"],
            "qty_forecast": [3.0, 1.0, 4.0],
            "qty_true": [2, 0, 5],
            "deviation_cause": ["model error", "other", "model error"],
            "lost_sales": [0, 0, 1],
        })

    def test_hand_computed_metrics_and_each_segment(self):
        metrics = evaluate_results(self.outcomes).metrics
        overall = metrics[metrics["level"] == "overall"].iloc[0]
        self.assertAlmostEqual(overall["wape"], 3 / 7)
        self.assertAlmostEqual(overall["mape"], (0.5 + 0.2) / 2)
        self.assertAlmostEqual(overall["bias"], 1 / 7)
        segments = (
            ("store", "store_id", 1),
            ("product_category", "category", "tops"),
            ("season", "season", "winter"),
        )
        for level, column, value in segments:
            with self.subTest(level=level):
                row = metrics[(metrics["level"] == level) & (metrics[column] == value)].iloc[0]
                self.assertEqual(row["observations"], 2)
                self.assertEqual(row["wape"], 1.0)
                self.assertEqual(row["mape"], 0.5)
                self.assertEqual(row["bias"], 1.0)
        pair = metrics[(metrics["level"] == "store_product") &
                       (metrics["store_id"] == 2) & (metrics["product_id"] == 20)].iloc[0]
        self.assertEqual(pair["wape"], 0.2)
        self.assertEqual(pair["mape"], 0.2)
        self.assertEqual(pair["bias"], -0.2)

    def test_invalid_values_and_unknown_cause_are_rejected(self):
        for column, invalid in (("qty_forecast", np.inf), ("qty_true", -1),
                                ("lost_sales", np.nan), ("deviation_cause", "unknown")):
            with self.subTest(column=column):
                frame = self.outcomes.copy()
                frame.loc[0, column] = invalid
                with self.assertRaises(ValueError):
                    evaluate_results(frame)
        with self.assertRaisesRegex(ValueError, "one row per date"):
            evaluate_results(pd.concat([self.outcomes, self.outcomes.iloc[[0]]]))


class EndToEndValidationTests(unittest.TestCase):
    def test_all_tables_and_results_repeat_for_same_seed(self):
        config = PipelineConfig(world=WorldConfig(
            seed=19, stores=2, products=3, history_days=28, future_days=3,
        ))
        first = run_pipeline(config)
        second = run_pipeline(config)
        for name in first.world:
            with self.subTest(table=name):
                pd.testing.assert_frame_equal(first.world[name], second.world[name])
        for left, right in ((first.forecasts, second.forecasts),
                            (first.outcomes, second.outcomes),
                            (first.evaluation.metrics, second.evaluation.metrics),
                            (first.evaluation.cause_summary, second.evaluation.cause_summary)):
            pd.testing.assert_frame_equal(left, right)

    def test_dashboard_filtered_metrics_match_raw_records(self):
        root = Path(__file__).resolve().parent.parent
        app = AppTest.from_file(str(root / "src" / "rdq" / "dashboard.py"), default_timeout=90).run()
        self.assertFalse(app.exception)
        app.number_input[1].set_value(2)
        app.number_input[2].set_value(5)
        app.number_input[3].set_value(28)
        app.number_input[4].set_value(3)
        app.run()
        self.assertFalse(app.exception)
        app.multiselect[0].set_value([app.multiselect[0].options[0]])
        app.multiselect[1].set_value([app.multiselect[1].options[0]])
        selected_day = date(2024, 1, 29)
        app.date_input[0].set_value((selected_day, selected_day))
        app.run()
        self.assertFalse(app.exception)
        raw = app.dataframe[-1].value
        self.assertFalse(raw.empty)
        self.assertEqual(len(raw), len(raw.drop_duplicates(["date", "store_id", "product_id"])))
        self.assertEqual(set(raw["store_id"]), {app.multiselect[0].value[0]})
        self.assertEqual(set(raw["category"]), {app.multiselect[1].value[0]})
        self.assertEqual(set(pd.to_datetime(raw["date"]).dt.date), {selected_day})
        actual = raw["qty_true"].to_numpy(dtype=float)
        forecast = raw["qty_forecast"].to_numpy(dtype=float)
        error = forecast - actual
        wape = "N/A" if actual.sum() == 0 else f"{np.abs(error).sum() / actual.sum():.1%}"
        mape = "N/A" if not (actual > 0).any() else f"{np.mean(np.abs(error[actual > 0] / actual[actual > 0])):.1%}"
        bias = "N/A" if actual.sum() == 0 else f"{error.sum() / actual.sum():+.1%}"
        self.assertEqual([item.value for item in app.metric[:3]], [wape, mape, bias])
        self.assertEqual(app.metric[3].value, f"{int(raw['lost_sales'].sum()):,}")


if __name__ == "__main__":
    unittest.main()
