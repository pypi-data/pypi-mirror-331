# -*- coding:utf-8 -*-

from typeguard import typechecked
from typing import List, Optional
from enum import Enum
import os
import logging
import json
from flask import Flask


NOT_FOUND_VALUE = "unspecified"


class LogExport(Enum):
    Unspecified = "unspecified"
    Console = "console"
    Singularity = "singularity"
    Fluent = "fluent"


@typechecked
class LogEnvironment:
    kwargs: dict = {}

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def get(
        self,
        arg_name: str,
        default_value: Optional[str] = None,
        *,
        env_name: Optional[str] = None,
    ):
        if hasattr(self, "_" + arg_name):
            return getattr(self, "_" + arg_name)

        if arg_name in self.kwargs and self.kwargs[arg_name]:
            setattr(self, "_" + arg_name, self.kwargs[arg_name])
            return getattr(self, "_" + arg_name)

        if env_name:
            setattr(self, "_" + arg_name, os.getenv(env_name, default_value))
            return getattr(self, "_" + arg_name)

        setattr(self, "_" + arg_name, default_value)
        return default_value

    @property
    def app(self):
        return self.get(
            "app", os.getenv("LOG_APP", NOT_FOUND_VALUE), env_name="APP_NAME"
        )

    @property
    def hostname(self):
        return self.get("hostname", "unknown", env_name="HOSTNAME")

    @property
    def node(self):
        return self.get("node", "local", env_name="KUBERNETES_NODE_NAME")

    @property
    def profile(self):
        return self.get(
            "profile",
            os.getenv("LOG_PROFILE", NOT_FOUND_VALUE),
            env_name="SERVICE_PROFILE",
        )

    @property
    def service(self):
        return self.get("service_name", NOT_FOUND_VALUE, env_name="SERVICE_NAME")

    @property
    def tag(self):
        return self.get("tag", "microsoft.rai.application", env_name="FLUENTD_PREFIX")

    @property
    def fluent_host(self):
        return self.get("fluent_host", "logging", env_name="FLUENTD_HOST")

    @property
    def fluent_port(self) -> int:
        return int(self.get("fluent_port", "24224", env_name="FLUENTD_PORT"))

    @property
    def level(self) -> Optional[int]:
        if "level" in self.kwargs:
            level_mapping = logging._nameToLevel

            if (
                isinstance(self.kwargs["level"], int)
                and self.kwargs["level"] in level_mapping.values()
            ):
                return self.kwargs["level"]
            elif isinstance(self.kwargs["level"], str):
                level = self.kwargs["level"].upper()
                if level in level_mapping:
                    return level_mapping[level]

        return logging.INFO

    @property
    def cloud(self) -> str:
        """
        Get the cloud of the service

        PUBLIC/USNAT
        :return: cloud
        """
        return self.get("cloud", NOT_FOUND_VALUE, env_name="CLOUD_NAME")

    @property
    def environment(self) -> str:
        """
        Get the environment of the service

        DEV/TEST/INT/PPE/PROD
        :return: environment
        """
        return self.get("environment", NOT_FOUND_VALUE, env_name="ENVIRONMENT")

    @property
    def region(self) -> str:
        """
        Get the region of the service
        name column from `az account list-locations -o table`

        :return: region
        """
        return self.get("region", NOT_FOUND_VALUE, env_name="LOCATION")

    @property
    def service_id(self) -> str:
        """
        Get the service id

        :return: service id
        """
        return self.get("service_id", NOT_FOUND_VALUE, env_name="SERVICE_ID")

    @property
    def service_name(self) -> str:
        """
        Get the service name

        :return: service name
        """
        return self.get("service_name", NOT_FOUND_VALUE, env_name="SERVICE_NAME")

    @property
    def service_version(self) -> str:
        """
        Get the service version

        :return: service version
        """
        return self.get("service_version", NOT_FOUND_VALUE, env_name="SERVICE_VERSION")

    @property
    def pod_id(self) -> str:
        """
        Get the pod id

        :return: pod id
        """
        return self.get("pod_id", NOT_FOUND_VALUE, env_name="POD_ID")

    @property
    def flight(self) -> Optional[str]:
        """
        Get flight

        :return: flight
        """
        flight = self.get("flight")
        if flight is None:
            return None

        return flight if isinstance(flight, str) else json.dumps(flight)

    @property
    def log_exporters(self) -> Optional[List[LogExport]]:
        """
        Get the collector of the service

        Fluentd/Singularity
        :return: collector
        """
        handlers = self.get("log_exporters")
        if not handlers:
            return None

        if isinstance(handlers, str):
            handlers = [handler.strip() for handler in handlers.split(",")]
        elif isinstance(handlers, LogExport):
            return [handlers]

        if isinstance(handlers, list):
            log_handlers = []
            for handler in handlers:
                if isinstance(handler, LogExport):
                    log_handlers.append(handler)
                elif isinstance(handler, str):
                    handler = handler.lower().capitalize()
                    if handler not in LogExport.__members__:
                        raise ValueError(f"Invalid log handler: {handler}")
                    log_handlers.append(LogExport[handler])
                else:
                    raise ValueError(f"Invalid log handler: {handler}")

            return [handler for handler in log_handlers]

        return None

    @property
    def flask_app(self) -> Optional[Flask]:
        flask_app = self.get("flask_app")
        if not flask_app:
            return None

        if isinstance(flask_app, Flask):
            return flask_app

        raise ValueError("Invalid flask app")

    @property
    def auto_collect_request_headers(self) -> str:
        return self.get("auto_collect_request_headers", "Correlation-Id,x-.*")

    @property
    def auto_collect_response_headers(self) -> str:
        return self.get("auto_collect_response_headers", "x-.*")
