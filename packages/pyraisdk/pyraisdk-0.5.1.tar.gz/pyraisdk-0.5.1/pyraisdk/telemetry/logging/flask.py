from typing import Optional
from os import environ
from .log_environment import LogEnvironment
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.util.http import (
    OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST,
    OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_RESPONSE,
)


def configure_logging(env: LogEnvironment, flask_app: Optional["Flask"] = None):
    environ[
        OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_REQUEST
    ] = env.auto_collect_request_headers
    environ[
        OTEL_INSTRUMENTATION_HTTP_CAPTURE_HEADERS_SERVER_RESPONSE
    ] = env.auto_collect_response_headers

    if flask_app:
        from flask.app import Flask
        if not isinstance(flask_app, Flask):
            raise ValueError("Invalid flask app")
        
        global flask_instrumentor
        flask_instrumentor = FlaskInstrumentor()
        flask_instrumentor.instrument_app(flask_app)


def shutdown():
    global flask_instrumentor
    if flask_instrumentor:
        flask_instrumentor.uninstrument_app()
