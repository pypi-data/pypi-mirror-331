import logging
from opentelemetry.sdk._logs import LogRecord
from opentelemetry.sdk._logs import LoggingHandler as BaseLoggingHandler
from .record import get_log_record_factory


class LoggingHandler(BaseLoggingHandler):
    def __init__(self, env, logger_provider=None):
        super().__init__(logger_provider=logger_provider)

        self.log_record_factory = get_log_record_factory(env)

    def _translate(self, record: logging.LogRecord) -> LogRecord:
        record_translated = super()._translate(record)

        return self.log_record_factory(record_translated, record)
