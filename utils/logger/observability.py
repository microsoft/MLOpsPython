from azureml.core import Run

from ml_service.util.env_variables import Env
from utils.logger.app_insights_logger import AppInsightsLogger
from utils.logger.azure_ml_logger import AzureMlLogger
from utils.logger.logger_interface import (
    ObservabilityAbstract,
    LoggerInterface,
    Severity,
)


class Loggers(ObservabilityAbstract):
    def __init__(self, export_interval) -> None:
        self.loggers: LoggerInterface = []
        self.register_loggers(export_interval)

    def add(self, logger) -> None:
        self.loggers.append(logger)

    def get_loggers_string(self) -> None:
        return ", ".join([type(x).__name__ for x in self.loggers])

    def register_loggers(self, export_interval):
        """
        This method is responsible to create loggers/tracers
        and add them to the list of loggers
        Notes:
        - If the context of the Run object is offline,
        we do not create AzureMlLogger instance
        - If APP_INSIGHTS_CONNECTION_STRING is notset
        to ENV variable, we do not create AppInsightsLogger
        instance
        """
        run = Run.get_context()
        if not run.id.startswith(self.OFFLINE_RUN):
            self.loggers.append(AzureMlLogger(run))
        if Env().app_insights_connection_string:
            self.loggers.append(AppInsightsLogger(run, export_interval))


class Observability(LoggerInterface):
    def __init__(self, export_interval=15) -> None:
        self._loggers = Loggers(export_interval)

    def log_metric(
            self, name="", value="", description="", log_parent=False,
    ):
        """
        this method sends the metrics to all registered loggers
        :param name: metric name
        :param value: metric value
        :param description: description of the metric
        :param log_parent: (only for AML), send the metric to the run.parent
        :return:
        """
        for logger in self._loggers.loggers:
            logger.log_metric(name, value, description, log_parent)

    def log(self, description="", severity=Severity.WARNING):
        """
        this method sends the logs to all registered loggers
        :param description: Actual log description to be sent
        :param severity: log Severity
        :return:
        """
        for logger in self._loggers.loggers:
            logger.log(description, severity)

    def get_logger(self, logger_class):
        """
        This method iterate over the loggers and it
        returns the logger with the same type as the provided one.
        this is a reference that can be used in case
        any of the built in functions of the loggers is required
        :param logger_class:
        :return: a logger class
        """
        for logger in self._loggers.loggers:
            if type(logger) is type(logger_class):
                return logger
