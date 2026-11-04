import subprocess
import sys
import unittest
from datetime import date
from pathlib import Path

import pandas as pd
from pandas.testing import assert_frame_equal

from src.rdq.generator import WorldConfig, generate_world


class GeneratorPreliminaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.config = WorldConfig(
            seed=42, stores=3, products=5, history_days=4,
            future_days=2, start_date=date(2024, 2, 27),
        )
        self.world = generate_world(self.config)

    def test_expected_tables_and_row_counts(self) -> None:
        expected = {
            "stores": 3, "products": 5, "warehouse": 5,
            "sales_history": 60, "true_demand": 30,
        }
        self.assertEqual(set(self.world), set(expected))
        self.assertEqual({name: len(frame) for name, frame in self.world.items()}, expected)

    def test_same_seed_reproduces_all_tables(self) -> None:
        repeated = generate_world(self.config)
        for name in self.world:
            with self.subTest(table=name):
                assert_frame_equal(self.world[name], repeated[name])

    def test_different_seed_changes_generated_data(self) -> None:
        changed = generate_world(WorldConfig(
            seed=43, stores=3, products=5, history_days=4,
            future_days=2, start_date=date(2024, 2, 27),
        ))
        self.assertFalse(self.world["sales_history"].equals(changed["sales_history"]))

    def test_references_unique_grain_and_nonnegative_quantities(self) -> None:
        stores = self.world["stores"]
        products = self.world["products"]
        self.assertTrue(stores["store_id"].is_unique)
        self.assertTrue(products["product_id"].is_unique)
        self.assertTrue(self.world["warehouse"]["product_id"].isin(products["product_id"]).all())
        self.assertTrue((self.world["warehouse"]["qty_available"] >= 0).all())
        for name, quantity in (("sales_history", "qty"), ("true_demand", "qty_true")):
            frame = self.world[name]
            with self.subTest(table=name):
                self.assertTrue(frame["store_id"].isin(stores["store_id"]).all())
                self.assertTrue(frame["product_id"].isin(products["product_id"]).all())
                self.assertFalse(frame.duplicated(["date", "store_id", "product_id"]).any())
                self.assertTrue((frame[quantity] >= 0).all())

    def test_dates_are_contiguous_and_future_is_separate(self) -> None:
        history = self.world["sales_history"]["date"]
        future = self.world["true_demand"]["date"]
        self.assertEqual(list(history.drop_duplicates()), list(pd.date_range("2024-02-27", periods=4)))
        self.assertEqual(list(future.drop_duplicates()), list(pd.date_range("2024-03-02", periods=2)))
        self.assertLess(history.max(), future.min())
        self.assertEqual(self.world["warehouse"]["date"].iloc[0], history.max())

    def test_minimum_valid_dimensions_and_zero_seed(self) -> None:
        world = generate_world(WorldConfig(seed=0, stores=1, products=1, history_days=1, future_days=1))
        self.assertTrue(all(len(frame) == 1 for frame in world.values()))
        self.assertLess(world["sales_history"]["date"].iloc[0], world["true_demand"]["date"].iloc[0])

    def test_invalid_dimensions_and_seed_are_rejected(self) -> None:
        for field in ("stores", "products", "history_days", "future_days"):
            for value in (0, -1):
                with self.subTest(field=field, value=value):
                    with self.assertRaisesRegex(ValueError, field):
                        WorldConfig(**{field: value})
        with self.assertRaisesRegex(ValueError, "seed"):
            WorldConfig(seed=-1)

    def test_cli_rejects_invalid_arguments_without_traceback(self) -> None:
        root = Path(__file__).resolve().parent.parent
        for args, expected in ((["--stores", "0"], "stores must be at least 1"),
                               (["--seed", "-1"], "seed must be non-negative"),
                               (["--start-date", "not-a-date"], "invalid")):
            with self.subTest(args=args):
                result = subprocess.run(
                    [sys.executable, "-m", "src.rdq", *args], cwd=root,
                    capture_output=True, text=True, check=False,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stderr)
                self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
