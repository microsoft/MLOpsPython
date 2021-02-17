import logging
import unittest
from unittest.mock import patch

from utils.logger.app_insights_logger import AppInsightsLogger


class RealAppInsightsLogger(AppInsightsLogger):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.env = MockEnv("")


class MockRun:
    def __init__(self, run_id):
        self.id = run_id


class MockEnv:
    def __init__(self, run_id):
        self.build_id = run_id


class TestObservability(unittest.TestCase):
    @patch("utils.logger.app_insights_logger.AppInsightsLogger")
    def setUp(cls, mock_app_insights_logger):
        cls.concert_app_insights_logger = RealAppInsightsLogger()
        cls.mock_app_insights_logger = mock_app_insights_logger

    def test_get_run_id_having_online_context(self):
        expected = "FOO"

        response = self.concert_app_insights_logger.get_run_id(MockRun("FOO"))

        self.assertEqual(expected, response)

    def test_get_run_id_having_online_context_using_build_id(self):
        self.concert_app_insights_logger.env.build_id = expected = "FOO"

        response = self.concert_app_insights_logger.\
            get_run_id(MockRun("OfflineRun"))

        self.assertEqual(expected, response)

    def test_get_run_id_having_online_context_using_uuid(self):
        self.concert_app_insights_logger.env.build_id = ""

        response = self.concert_app_insights_logger.\
            get_run_id(MockRun("OfflineRun"))

        self.assertIsNotNone(response)

    def test_log_called_with_parameters(self):
        self.mock_app_insights_logger.log("FOO", "BAZ")

        self.mock_app_insights_logger.log.assert_called_with("FOO", "BAZ")

    def test_log_metric_called_with_parameters(self):
        self.mock_app_insights_logger.log_metric("FOO", "BAZ", "BAR", False)

        self.mock_app_insights_logger.log_metric.assert_called_with(
            "FOO", "BAZ", "BAR", False
        )

    def test_set_view_is_called_with_parameters(self):
        self.mock_app_insights_logger.set_view("FOO", "BAR", "BAZ")
        self.mock_app_insights_logger.set_view.\
            assert_called_with("FOO", "BAR", "BAZ")


if __name__ == "__main__":
    unittest.main()
