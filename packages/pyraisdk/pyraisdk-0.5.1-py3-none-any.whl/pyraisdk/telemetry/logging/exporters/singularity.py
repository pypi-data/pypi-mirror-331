from os import linesep
from opentelemetry.sdk._logs.export import ConsoleLogExporter
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, ReadableSpan
from ..log_environment import LogEnvironment
from .formatter import LogRecordFormatter, SpanRecordFormatter


class SingularityLogExporter(ConsoleLogExporter):
    _formatter: LogRecordFormatter

    def __init__(self, log_environment: LogEnvironment):
        self._formatter = LogRecordFormatter(log_environment, pascal_case=True)

        super().__init__(
            formatter=lambda record: self._formatter.format(record) + linesep
        )


class SingularitySpanExporter(ConsoleSpanExporter):
    _formatter: SpanRecordFormatter

    def __init__(self, log_environment: LogEnvironment):
        self._formatter = SpanRecordFormatter(log_environment, pascal_case=True)

        super().__init__(
            formatter=lambda record: self._formatter.format(record) + linesep
        )


def create_log_exporter(log_environment: LogEnvironment):
    return SingularityLogExporter(log_environment)


def create_span_exporter(log_environment: LogEnvironment):
    return SingularitySpanExporter(log_environment)
