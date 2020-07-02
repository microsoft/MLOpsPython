import inspect


class Severity:
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50


class LoggerInterface:
    def log_metric(self, name, value, description, log_parent):
        pass

    def log(self, name, value, description, severity, log_parent):
        pass


class ObservabilityAbstract:
    OFFLINE_RUN = "OfflineRun"
    CORRELATION_ID = "correlation_id"
    severity = Severity()
    severity_map = {10: "DEBUG", 20: "INFO",
                    30: "WARNING", 40: "ERROR", 50: "CRITICAL"}

    @staticmethod
    def get_callee(stack_level):
        """
        This method get the callee location in [file_name:line_number] format
        :param stack_level:
        :return: string of [file_name:line_number]
        """
        try:
            stack = inspect.stack()
            file_name = stack[stack_level + 1].filename.split("/")[-1]
            line_number = stack[stack_level + 1].lineno
            return "{}:{}".format(file_name, line_number)
        except IndexError:
            print("Index error, failed to log to AzureML")
            return ""
