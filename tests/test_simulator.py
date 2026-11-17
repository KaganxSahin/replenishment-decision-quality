import unittest

import pandas as pd

from src.rdq.evaluation import evaluate_results
from src.rdq.generator import WorldConfig
from src.rdq.pipeline import PipelineConfig, run_pipeline as execute_pipeline
from src.rdq.simulator import SimulationConfig, simulate_replenishment


class ReplenishmentSimulationTests(unittest.TestCase):
    def make_inputs(self):
        forecasts = pd.DataFrame({
            "date": ["2024-01-01"] * 4 + ["2024-01-02"],
            "store_id": [1, 2, 1, 1, 1],
            "product_id": [10, 10, 20, 30, 20],
            "qty_forecast": [2.0, 2.0, 2.0, 1.0, 2.0],
        })
        true_demand = pd.DataFrame({
            "date": ["2024-01-01"] * 4 + ["2024-01-02"],
            "store_id": [1, 2, 1, 1, 1],
            "product_id": [10, 10, 20, 30, 20],
            "qty_true": [2, 2, 1, 1, 3],
        })
        products = pd.DataFrame({
            "product_id": [10, 20, 30],
            "category": ["tops", "trousers", "outerwear"],
            "pack_size": [2, 1, 4],
        })
        warehouse = pd.DataFrame({"product_id": [10, 20, 30], "qty_available": [3, 10, 10]})
        return forecasts, true_demand, products, warehouse

    def test_rules_stock_cap_and_inventory_carry_are_simulated(self) -> None:
        inputs = self.make_inputs()
        outcomes = simulate_replenishment(*inputs, SimulationConfig(minimum_stock=0))
        product10 = outcomes[outcomes["product_id"] == 10].sort_values("store_id")
        self.assertEqual(product10["qty_shipped"].sum(), 2)
        self.assertEqual(product10.iloc[0]["deviation_cause"], "other")
        self.assertEqual(product10.iloc[1]["deviation_cause"], "stock constraint")
        product30 = outcomes[outcomes["product_id"] == 30].iloc[0]
        self.assertEqual(product30["qty_shipped"], 0)
        self.assertEqual(product30["qty_forecast"], product30["qty_true"])
        self.assertEqual(product30["deviation_cause"], "rule constraint")
        carried = outcomes[(outcomes["product_id"] == 20) & (outcomes["date"] == pd.Timestamp("2024-01-02"))].iloc[0]
        self.assertEqual(carried["store_inventory_start"], 1)
        self.assertEqual(carried["qty_shipped"], 1)
        self.assertEqual(carried["lost_sales"], 1)
        self.assertEqual(carried["deviation_cause"], "model error")
        self.assertTrue((outcomes["qty_shipped"] <= outcomes["qty_requested"]).all())
        self.assertTrue((outcomes["lost_sales"] >= 0).all())

    def test_mismatched_forecast_and_demand_keys_are_rejected(self) -> None:
        forecasts, true_demand, products, warehouse = self.make_inputs()
        true_demand.loc[0, "store_id"] = 99
        with self.assertRaisesRegex(ValueError, "identical date-store-product keys"):
            simulate_replenishment(forecasts, true_demand, products, warehouse)

    def test_invalid_pack_size_is_rejected(self) -> None:
        forecasts, true_demand, products, warehouse = self.make_inputs()
        products.loc[0, "pack_size"] = 0
        with self.assertRaisesRegex(ValueError, "positive whole units"):
            simulate_replenishment(forecasts, true_demand, products, warehouse)

    def test_invalid_simulation_config_is_rejected(self) -> None:
        for minimum_stock in (-1, 0.5, True):
            with self.subTest(minimum_stock=minimum_stock):
                with self.assertRaisesRegex(ValueError, "non-negative integer"):
                    SimulationConfig(minimum_stock=minimum_stock)


class EvaluationMetricTests(unittest.TestCase):
    def test_metrics_match_hand_calculated_values_and_aggregate_segments(self) -> None:
        outcomes = pd.DataFrame({
            "date": ["2024-01-01", "2024-04-01"],
            "store_id": [1, 2],
            "product_id": [10, 10],
            "category": ["tops", "tops"],
            "qty_forecast": [3.0, 1.0],
            "qty_true": [2, 0],
            "deviation_cause": ["model error", "rule constraint"],
            "lost_sales": [1, 0],
        })
        result = evaluate_results(outcomes)
        overall = result.metrics[result.metrics["level"] == "overall"].iloc[0]
        self.assertEqual(overall["wape"], 1.0)
        self.assertEqual(overall["mape"], 0.5)
        self.assertEqual(overall["bias"], 1.0)
        self.assertEqual(set(result.metrics["level"]), {
            "overall", "store", "product_category", "season", "store_product"
        })
        self.assertAlmostEqual(result.cause_summary["observation_share"].sum(), 1.0)
        self.assertEqual(result.cause_summary["lost_sales"].sum(), 1)

    def test_mapes_zero_actuals_and_empty_data_are_handled(self) -> None:
        outcomes = pd.DataFrame({
            "date": ["2024-01-01"],
            "store_id": [1],
            "product_id": [1],
            "category": ["tops"],
            "qty_forecast": [2.0],
            "qty_true": [0],
            "deviation_cause": ["model error"],
            "lost_sales": [0],
        })
        overall = evaluate_results(outcomes).metrics.query("level == 'overall'").iloc[0]
        self.assertTrue(pd.isna(overall["wape"]))
        self.assertTrue(pd.isna(overall["mape"]))
        self.assertTrue(pd.isna(overall["bias"]))
        with self.assertRaisesRegex(ValueError, "must not be empty"):
            evaluate_results(outcomes.iloc[:0])


class PipelineIntegrationTests(unittest.TestCase):
    def run_small_pipeline(self):
        result = execute_pipeline(PipelineConfig(
            world=WorldConfig(
                seed=17,
                stores=3,
                products=4,
                history_days=28,
                future_days=3,
            ),
            forecast_bias=0.1,
            forecast_variance=0.02,
        ))
        return result.forecasts, result.outcomes, result.evaluation.metrics, result.evaluation.cause_summary

    def test_end_to_end_pipeline_is_reproducible(self) -> None:
        first = self.run_small_pipeline()
        second = self.run_small_pipeline()
        for first_frame, second_frame in zip(first, second):
            pd.testing.assert_frame_equal(first_frame, second_frame)


if __name__ == "__main__":
    unittest.main()
