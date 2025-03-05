# -*- coding:utf-8 -*-

from typeguard import typechecked
from typing import Tuple
import logging
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs.export import (
    BatchLogRecordProcessor,
    SimpleLogRecordProcessor,
    LogExporter,
    ConsoleLogExporter,
)
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    SimpleSpanProcessor,
    BatchSpanProcessor,
    ConsoleSpanExporter,
)
from .handler import LoggingHandler
from .provider import LoggerProvider
from .log_environment import LogEnvironment, LogExport
from .record import get_logging_record_factory
from .exporters import singularity, fluent, console
from . import flask


DEFAULT_LOG_EXPORTERS = (LogExport.Singularity,)


@typechecked
def configure_logging(env: LogEnvironment) -> LoggerProvider:
    logger_provider = LoggerProvider(env)
    set_logger_provider(logger_provider)

    logging.basicConfig(level=env.level)
    logging.setLogRecordFactory(get_logging_record_factory(env))

    logger = logging.getLogger()
    logger.level = env.level

    logger.addHandler(LoggingHandler(env, logger_provider=logger_provider))

    for handler in env.log_exporters or DEFAULT_LOG_EXPORTERS:
        if handler == LogExport.Singularity:
            logger_provider.add_log_record_processor(
                SimpleLogRecordProcessor(singularity.create_log_exporter(env))
            )
        elif handler == LogExport.Fluent:
            logger_provider.add_log_record_processor(
                SimpleLogRecordProcessor(fluent.create_log_exporter(env))
            )
        elif handler == LogExport.Console:
            logger_provider.add_log_record_processor(
                SimpleLogRecordProcessor(console.create_log_exporter(env))
            )

    return logger_provider


@typechecked
def configure_trace(env: LogEnvironment) -> TracerProvider:
    provider = TracerProvider()
    trace.set_tracer_provider(provider)

    for handler in env.log_exporters or DEFAULT_LOG_EXPORTERS:
        if handler == LogExport.Singularity:
            provider.add_span_processor(
                SimpleSpanProcessor(singularity.create_span_exporter(env))
            )
        elif handler == LogExport.Fluent:
            provider.add_span_processor(
                SimpleSpanProcessor(fluent.create_span_exporter(env))
            )
        elif handler == LogExport.Console:
            provider.add_span_processor(
                SimpleSpanProcessor(console.create_span_exporter(env))
            )

    return provider


@typechecked
def configure(
    **kwargs,
) -> Tuple[LoggerProvider, TracerProvider]:
    """
    Initializes the logging system
    """

    env = LogEnvironment(**kwargs)

    print(
        f"Start initializing - app: {env.app}, service: {env.service}, profile: {env.profile},"
        f" host: {env.hostname}, node: {env.node}, tag: {env.tag}"
    )

    logger_provider = configure_logging(env)
    tracer_provider = configure_trace(env)

    if env.flask_app:
        flask.configure_logging(env, env.flask_app)

    print("Config log successfully.")
    return logger_provider, tracer_provider


@typechecked
def shutdown():
    flask.shutdown()
