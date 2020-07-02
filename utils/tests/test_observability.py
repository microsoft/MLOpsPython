import unittest
from unittest.mock import patch

from utils.logger.observability import Observability


class ObservabilityMock(Observability):
    @patch("utils.logger.app_insights_logger.AppInsightsLogger")
    @patch("utils.logger.azure_ml_logger.AzureMlLogger")
    @patch("utils.logger.observability.Loggers")
    def __init__(self, mock_loggers, mock_aml_logger, mock_app_insight_logger):
        mock_loggers.loggers = [mock_aml_logger, mock_app_insight_logger]
        self._loggers = mock_loggers


class TestObservability(unittest.TestCase):
    @patch("utils.logger.observability.Observability")
    def setUp(cls, mock_observability):
        cls.observability = mock_observability

    def test_log_metric_called_with_parameters(self):
        self.observability.log_metric("FOO", "BAZ", "BAR")

        self.observability.log_metric.assert_called_with("FOO", "BAZ", "BAR")

    def test_log_called_with_parameters(self):
        self.observability.log("FOO", "BAZ")

        self.observability.log.assert_called_with("FOO", "BAZ")

    def test_log_metric_is_being_called_by_all_loggers(self):
        self.observability = ObservabilityMock()

        self.observability.log_metric("FOO", "BAZ", "BAR")

        self.observability._loggers.loggers[0].log_metric.assert_called_with(
            "FOO", "BAZ", "BAR", False
        )
        self.observability._loggers.loggers[1].log_metric.assert_called_with(
            "FOO", "BAZ", "BAR", False
        )

    def test_log_is_being_called_by_all_loggers(self):
        self.observability = ObservabilityMock()

        self.observability.log("FOO", "BAZ")

        self.observability._loggers.loggers[0].\
            log.assert_called_with("FOO", "BAZ")
        self.observability._loggers.loggers[1].\
            log.assert_called_with("FOO", "BAZ")


if __name__ == "__main__":
    unittest.main()
