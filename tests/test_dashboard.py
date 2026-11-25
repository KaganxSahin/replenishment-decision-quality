import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

import pandas as pd
from streamlit.testing.v1 import AppTest


class DashboardSmokeTests(unittest.TestCase):
    def test_dashboard_renders_metrics_and_filters_without_exceptions(self) -> None:
        project_root = Path(__file__).resolve().parent.parent
        app = AppTest.from_file(str(project_root / "src" / "rdq" / "dashboard.py"), default_timeout=60).run()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any("Synthetic Retail Decision Quality" in item.value for item in app.title))
        self.assertGreaterEqual(len(app.metric), 5)
        self.assertEqual(len(app.multiselect), 2)
        app.multiselect[0].set_value([app.multiselect[0].options[0]])
        app.multiselect[1].set_value([app.multiselect[1].options[0]])
        app.run()
        self.assertEqual(len(app.exception), 0)

    def test_dashboard_loads_when_repository_root_is_not_working_directory(self) -> None:
        project_root = Path(__file__).resolve().parent.parent
        app = AppTest.from_file(str(project_root / "src" / "rdq" / "dashboard.py"), default_timeout=60)
        with patch.object(Path, "cwd", return_value=project_root.parent):
            app.run()
        self.assertEqual(len(app.exception), 0)
        self.assertGreaterEqual(len(app.metric), 5)


class DashboardDateFilterTests(unittest.TestCase):
    def test_partial_date_range_selection_does_not_raise(self) -> None:
        project_root = Path(__file__).resolve().parent.parent
        app = AppTest.from_file(str(project_root / "src" / "rdq" / "dashboard.py"), default_timeout=60).run()
        self.assertEqual(len(app.exception), 0)
        app.number_input[1].set_value(2)
        app.number_input[2].set_value(5)
        app.number_input[3].set_value(28)
        app.number_input[4].set_value(3)
        app.run()
        self.assertEqual(len(app.exception), 0)
        app.date_input[0].set_value((date(2024, 1, 30),))
        app.run()
        self.assertEqual(len(app.exception), 0)
        raw = app.dataframe[-1].value
        self.assertFalse(raw.empty)
        self.assertTrue((pd.to_datetime(raw["date"]).dt.date >= date(2024, 1, 30)).all())


if __name__ == "__main__":
    unittest.main()
