import logging
import time
import uuid

from opencensus.ext.azure import metrics_exporter
from opencensus.ext.azure.log_exporter import AzureLogHandler


from opencensus.stats import aggregation as aggregation_module
from opencensus.stats import measure as measure_module
from opencensus.stats import stats as stats_module
from opencensus.stats import view as view_module
from opencensus.tags import tag_map as tag_map_module

from ml_service.util.env_variables import Env
from utils.logger.logger_interface import (
    LoggerInterface,
    ObservabilityAbstract,
    Severity,
)


class AppInsightsLogger(LoggerInterface, ObservabilityAbstract):
    def __init__(self, run, export_interval):
        self.env = Env()
        # initializes log exporter
        handler = AzureLogHandler(
            connection_string=self.env.app_insights_connection_string,
            logging_sampling_rate=1.0,
        )
        handler.add_telemetry_processor(self.callback_function)
        self.run_id = self.get_run_id(run)
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(handler)
        # initializes metric exporter
        self.export_interval = export_interval
        exporter = metrics_exporter.new_metrics_exporter(
            enable_standard_metrics=False,
            export_interval=self.export_interval,
            connection_string=self.env.app_insights_connection_string,
        )
        exporter.add_telemetry_processor(self.callback_function)
        stats_module.stats.view_manager.register_exporter(exporter)

    def log_metric(
        self, name="", value="", description="", log_parent=False,
    ):
        """
        Sends a custom metric to appInsights
        :param name: name  of the metric
        :param value: value of the metric
        :param description: description of the metric
        :param log_parent: not being used for this logger
        :return:
        """
        measurement_map = \
            stats_module.stats.stats_recorder.new_measurement_map()
        tag_map = tag_map_module.TagMap()

        measure = measure_module.MeasureFloat(name, description)
        self.set_view(name, description, measure)
        measurement_map.measure_float_put(measure, value)
        measurement_map.record(tag_map)
        # Default export interval is every 15.0s
        # Your application should run for at least this amount
        # of time so the exporter will meet this interval
        # Sleep can fulfill this https://pypi.org/project/opencensus-ext-azure/
        time.sleep(self.export_interval)

    def log(self, description="", severity=Severity.WARNING):
        """
        Sends the logs to App Insights
        :param description: log description
        :param severity: log severity
        :return:
        """

        if severity == self.severity.DEBUG:
            self.logger.debug(description)
        elif severity == self.severity.INFO:
            self.logger.info(description)
        elif severity == self.severity.WARNING:
            self.logger.warning(description)
        elif severity == self.severity.ERROR:
            self.logger.error(description)
        elif severity == self.severity.CRITICAL:
            self.logger.critical(description)

    def get_run_id(self, run):
        """
        gets the correlation ID by the in following order:
        - If the script is running  in an Online run Context of AML --> run_id
        - If the script is running where a build_id
        environment variable  is set --> build_id
        - Else --> generate a unique id
        :param run:
        :return: correlation_id
        """
        run_id = str(uuid.uuid1())
        if not run.id.startswith(self.OFFLINE_RUN):
            run_id = run.id
        elif self.env.build_id:
            run_id = self.env.build_id
        return run_id

    @staticmethod
    def set_view(metric, description, measure):
        """
        Sets the view for the custom metric
        """
        prompt_view = view_module.View(
            metric,
            description,
            [],
            measure,
            aggregation_module.LastValueAggregation()
        )
        stats_module.stats.view_manager.register_view(prompt_view)

    def callback_function(self, envelope):
        """
        Attaches a correlation_id as a custom
        dimension to the exporter just before
        sending the logs/metrics
        :param envelope:
        :return: Always return True
        (if False, it  does not export metrics/logs)
        """
        envelope.data.baseData.properties[self.CORRELATION_ID] = self.run_id
        return True
