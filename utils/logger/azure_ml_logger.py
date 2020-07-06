import datetime
import time

from utils.logger.logger_interface import (
    LoggerInterface,
    ObservabilityAbstract,
    Severity,
)


class AzureMlLogger(LoggerInterface, ObservabilityAbstract):
    def __init__(self, run=None):
        self.run = run

    def log_metric(self, name, value, description, log_parent):
        """Log a metric value to the run with the given name.
        :param log_parent: mark True  if you want to log to parent Run
        :param name: The name of metric.
        :type name: str
        :param value: The value to be posted to the service.
        :type value:
        :param description: An optional metric description.
        :type description: str
        """
        if name != "" and value != "":
            self.run.log(
                name, value, description
            ) if log_parent is False \
                else self.run.parent.log(name, value, description)

    def log(self, description="", severity=Severity.WARNING):
        """
        Sends the logs to AML (experiments -> logs/outputs)
        :param description: log description
        :param severity: log severity
        :return:
        """

        time_stamp = datetime.datetime.fromtimestamp(time.time()).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        callee = self.get_callee(
            2
        )  # to get the script who is calling Observability
        print(
            "{}, [{}], {}:{}".format(
                time_stamp, self.severity_map[severity], callee, description
            )
        )
