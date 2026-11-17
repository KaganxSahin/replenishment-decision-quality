import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
