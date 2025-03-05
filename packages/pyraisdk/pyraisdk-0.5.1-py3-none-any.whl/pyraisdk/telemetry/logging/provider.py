from opentelemetry.sdk._logs import (
    LoggerProvider as OpenTelemetryLoggerProvider,
    Logger,
)
from opentelemetry.sdk.resources import Resource
from .log_environment import LogEnvironment


class LoggerProvider(OpenTelemetryLoggerProvider):
    def __init__(self, env: LogEnvironment, *args, **kwargs):
        super().__init__(
            *args,
            resource=Resource.create(
                {
                    "service.name": env.service,
                }
            ),
            **kwargs,
        )

    def _get_logger_no_cache(
        self,
        name: str,
        *args,
        **kwargs,
    ) -> Logger:
        logger = super()._get_logger_no_cache(name, *args, **kwargs)

        return logger
