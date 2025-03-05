# -*- coding:utf-8 -*-

import logging
from opentelemetry.sdk._logs import LogRecord as BaseLogRecord
from .utils import ms_to_iso_str
from .log_environment import LogEnvironment


def default_record(log_environment: LogEnvironment):
    return {
        "cloud": log_environment.cloud,
        "environment": log_environment.environment,
        "region": log_environment.region,
        "app": log_environment.app,
        "service_id": log_environment.service_id,
        "service_name": log_environment.service_name,
        "service_version": log_environment.service_version,
        "node_id": log_environment.node,
        "pod_id": log_environment.pod_id,
        "profile": log_environment.profile,
        "service": log_environment.service,
        "node": log_environment.node,
        **({"flight": log_environment.flight} if log_environment.flight else {}),
    }


def default_log_record(log_environment: LogEnvironment):
    return {
        "level": "%(levelname)s",
        "level_no": "%(levelno)d",
        "category": "%(name)s",
        "hostname": "%(hostname)s",
        "message": "%(message)s",
        "stack": "%(exc_text)s",
        "pid": "%(process)d",
        "processName": "%(processName)s",
        "thread": "%(threadName)s",
        "precise_timestamp": "%(precise_timestamp)s",
        "ts": "%(timestamp)d",
        "pathname": "%(pathname)s",
        "lineno": "%(lineno)d",
        "funcName": "%(funcName)s",
        **default_record(log_environment),
    }


def get_logging_record_factory(log_environment: LogEnvironment):
    class LoggingLogRecord(logging.LogRecord):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.timestamp = int(self.created * 1000)
            self.precise_timestamp = ms_to_iso_str(self.created)

    return LoggingLogRecord


class LogRecord(BaseLogRecord):
    _original: BaseLogRecord = None
    _original_record: logging.LogRecord = None

    def __init__(self, record: BaseLogRecord, original_record: logging.LogRecord):
        super().__init__(**record.__dict__)

        self._original = record
        self._original_record = original_record
        self.created = original_record.created

    def getMessage(self):
        return self._original_record.getMessage()


def get_log_record_factory(log_environment: LogEnvironment):
    return LogRecord
