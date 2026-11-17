import unittest
from datetime import date

import pandas as pd
from pandas.testing import assert_frame_equal

from src.rdq.forecaster import EmulatorConfig, ErrorInjectionEmulator


class ErrorInjectionEmulatorTests(unittest.TestCase):
    def setUp(self) -> None:
        dates = pd.date_range(date(2024, 1, 1), periods=3)
        self.history = pd.DataFrame({
            "date": list(dates) * 2,
            "store_id": [1] * 3 + [2] * 3,
            "product_id": [10] * 6,
            "qty": [2, 4, 6, 1, 3, 5],
        })

    def test_predict_requires_fit(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "fit"):
            ErrorInjectionEmulator().predict(1)

    def test_forecast_rows_and_dates_follow_history_pairs(self) -> None:
        emulator = ErrorInjectionEmulator(EmulatorConfig(variance=0, seasonal_drift=0))
        emulator.fit(self.history)
        forecasts = emulator.predict(2)
        self.assertEqual(len(forecasts), 4)
        self.assertEqual(list(forecasts.columns), ["date", "store_id", "product_id", "qty_forecast"])
        self.assertEqual(list(forecasts["date"].drop_duplicates()), list(pd.date_range("2024-01-04", periods=2)))
        self.assertFalse(forecasts.duplicated(["date", "store_id", "product_id"]).any())
        self.assertTrue((forecasts["qty_forecast"] >= 0).all())

    def test_bias_applies_to_trailing_baseline(self) -> None:
        config = EmulatorConfig(bias=0.5, variance=0, seasonal_drift=0, baseline_days=2)
        emulator = ErrorInjectionEmulator(config)
        emulator.fit(self.history)
        forecasts = emulator.predict(1).sort_values("store_id")
        self.assertEqual(forecasts["qty_forecast"].tolist(), [7.5, 6.0])

    def test_same_seed_reproduces_forecasts(self) -> None:
        config = EmulatorConfig(seed=29, variance=0.25)
        outputs = []
        for _ in range(2):
            emulator = ErrorInjectionEmulator(config)
            emulator.fit(self.history)
            outputs.append(emulator.predict(5))
        assert_frame_equal(outputs[0], outputs[1])

    def test_different_seed_changes_noisy_forecasts(self) -> None:
        outputs = []
        for seed in (29, 30):
            emulator = ErrorInjectionEmulator(EmulatorConfig(seed=seed, variance=0.25))
            emulator.fit(self.history)
            outputs.append(emulator.predict(5))
        self.assertFalse(outputs[0].equals(outputs[1]))

    def test_future_demand_is_not_an_input_to_forecaster(self) -> None:
        emulator = ErrorInjectionEmulator(EmulatorConfig(variance=0, seasonal_drift=0))
        emulator.fit(self.history)
        forecasts = emulator.predict(1)
        self.assertGreater(forecasts["date"].min(), self.history["date"].max())
        self.assertNotIn("qty_true", forecasts.columns)

    def test_fit_rejects_missing_columns_and_empty_history(self) -> None:
        emulator = ErrorInjectionEmulator()
        with self.assertRaisesRegex(ValueError, "missing required columns"):
            emulator.fit(self.history.drop(columns="qty"))
        with self.assertRaisesRegex(ValueError, "must not be empty"):
            emulator.fit(self.history.iloc[:0])

    def test_fit_rejects_invalid_quantities_and_duplicate_grain(self) -> None:
        emulator = ErrorInjectionEmulator()
        negative = self.history.copy()
        negative.loc[0, "qty"] = -1
        with self.assertRaisesRegex(ValueError, "non-negative"):
            emulator.fit(negative)
        duplicate = pd.concat([self.history, self.history.iloc[[0]]], ignore_index=True)
        with self.assertRaisesRegex(ValueError, "one row per date"):
            emulator.fit(duplicate)

    def test_predict_rejects_invalid_horizon(self) -> None:
        emulator = ErrorInjectionEmulator()
        emulator.fit(self.history)
        for horizon in (0, -1, 1.5, True):
            with self.subTest(horizon=horizon):
                with self.assertRaisesRegex(ValueError, "positive integer"):
                    emulator.predict(horizon)

    def test_invalid_emulator_settings_are_rejected(self) -> None:
        invalid = (
            {"seed": -1},
            {"bias": -1.1},
            {"variance": -0.1},
            {"seasonal_drift": -0.1},
            {"baseline_days": 0},
        )
        for values in invalid:
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    EmulatorConfig(**values)


if __name__ == "__main__":
    unittest.main()
