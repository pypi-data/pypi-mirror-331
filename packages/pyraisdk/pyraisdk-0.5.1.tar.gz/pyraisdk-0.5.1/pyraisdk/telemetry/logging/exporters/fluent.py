from typing import Sequence
import logging
from fluent import asynchandler, handler
from opentelemetry.sdk._logs import LogData
from opentelemetry.sdk._logs.export import LogExporter
from opentelemetry.sdk.trace.export import ReadableSpan, SpanExporter
from ..log_environment import LogEnvironment
from ..record import default_log_record
from .formatter import LogRecordFormatter, SpanRecordFormatter


def overflow_handler(pending_events):
    print(
        "Fluentd buffer overflowed. %d events will be discarded." % len(pending_events)
    )


class FluentFormatter(handler.FluentRecordFormatter):
    def __init__(self, log_environment: LogEnvironment):
        super().__init__(default_log_record(log_environment))

    def format(self, record: logging.LogRecord):
        return super().format(record)


class FluentLogExporter(LogExporter):
    fluent_handler: asynchandler.FluentHandler

    def __init__(self, log_environment: LogEnvironment):
        super().__init__()

        self.fluent_handler = asynchandler.FluentHandler(
            log_environment.tag,
            host=log_environment.fluent_host,
            port=log_environment.fluent_port,
            buffer_overflow_handler=overflow_handler,
        )

        self.fluent_handler.setFormatter(
            LogRecordFormatter(log_environment, pascal_case=False)
        )

    def export(self, batch: Sequence[LogData]):
        for data in batch:
            self.fluent_handler.emit(data.log_record)

        self.fluent_handler.flush()

    def shutdown(self):
        self.fluent_handler.close()


class FluentSpanExporter(SpanExporter):
    fluent_handler: asynchandler.FluentHandler

    def __init__(self, log_environment: LogEnvironment):
        super().__init__()

        self.fluent_handler = asynchandler.FluentHandler(
            log_environment.tag,
            host=log_environment.fluent_host,
            port=log_environment.fluent_port,
            buffer_overflow_handler=overflow_handler,
        )

        self.fluent_handler.setFormatter(
            SpanRecordFormatter(log_environment, pascal_case=False)
        )

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        return self.fluent_handler.flush()

    def export(self, batch: Sequence[ReadableSpan]):
        for data in batch:
            if not hasattr(data, "created"):
                data.created = data.end_time
            self.fluent_handler.emit(data)

    def shutdown(self):
        self.fluent_handler.close()


def create_log_exporter(log_environment: LogEnvironment):
    return FluentLogExporter(log_environment)


def create_span_exporter(log_environment: LogEnvironment):
    return FluentSpanExporter(log_environment)
