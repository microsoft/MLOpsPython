import unittest
from unittest.mock import patch

from utils.logger.azure_ml_logger import AzureMlLogger


class TestObservability(unittest.TestCase):
    @patch("utils.logger.azure_ml_logger.AzureMlLogger")
    def setUp(cls, mock_azure_ml_logger):
        cls.azure_ml_logger = mock_azure_ml_logger

    def test_log_called_with_parameters(self):
        self.azure_ml_logger.log("FOO", "BAZ")

        self.azure_ml_logger.log.assert_called_with("FOO", "BAZ")

    def test_log_metric_called_with_parameters(self):
        self.azure_ml_logger.log_metric("FOO", "BAZ", "BAR")

        self.azure_ml_logger.log_metric.assert_called_with("FOO", "BAZ", "BAR")

    def test_get_callee_returns_callee_file_with_line_number(self):
        azure_ml_logger = AzureMlLogger()
        expected = "test_azure_ml_logger.py:26"

        response = azure_ml_logger.get_callee(0)

        self.assertEqual(expected, response)


if __name__ == "__main__":
    unittest.main()
