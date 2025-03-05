from os import linesep
import sys
import logging
from opentelemetry.sdk._logs import LogRecord
from opentelemetry.sdk._logs.export import ConsoleLogExporter as BaseConsoleLogExporter
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter as BaseConsoleSpanExporter,
    ReadableSpan,
)
from ..log_environment import LogEnvironment
from ..record import default_record


def overflow_handler(pending_events):
    print(
        "Fluentd buffer overflowed. %d events will be discarded." % len(pending_events)
    )


class ConsoleLogFormatter(logging.Formatter):
    def __init__(self, log_environment: LogEnvironment):
        super().__init__()

    def format(self, record: LogRecord):
        return record.body + linesep


class ConsoleLogExporter(BaseConsoleLogExporter):
    formatter: ConsoleLogFormatter

    def __init__(self, log_environment: LogEnvironment):
        self.formatter = ConsoleLogFormatter(log_environment)

        super().__init__(out=sys.stderr, formatter=self.formatter.format)


class ConsoleSpanFormatter(logging.Formatter):
    default_record: dict

    def __init__(self, log_environment: LogEnvironment):
        super().__init__()

        self.default_record = default_record(log_environment)

    def format(self, record: ReadableSpan):
        for key, value in self.default_record.items():
            if key not in record._attributes:
                record._attributes[key] = value

        return record.to_json(indent=None)


class ConsoleSpanExporter(BaseConsoleSpanExporter):
    _formatter: ConsoleSpanFormatter

    def __init__(self, log_environment: LogEnvironment):
        self._formatter = ConsoleSpanFormatter(log_environment)

        super().__init__(
            service_name=log_environment.service_name,
            out=sys.stderr,
            formatter=lambda span: self._formatter.format(span) + linesep,
        )


def create_log_exporter(log_environment: LogEnvironment):
    return ConsoleLogExporter(log_environment)


def create_span_exporter(log_environment: LogEnvironment):
    return ConsoleSpanExporter(log_environment)
