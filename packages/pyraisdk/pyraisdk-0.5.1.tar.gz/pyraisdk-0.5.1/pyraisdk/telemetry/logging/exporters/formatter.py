import json
import json
from fluent import handler
from opentelemetry.sdk.trace.export import ReadableSpan
from opentelemetry.trace import format_span_id, format_trace_id, get_current_span
from ..log_environment import LogEnvironment
from ..utils import underscore_to_pascal_case
from ..record import default_log_record, default_record, LogRecord


AllowableKeys = (
    "OperationId",
    "ParentOperationId",
    "RequestIp",
    "CorrelationId",
    "ParentCorrelationId",
    "ApimRequestId",
    "ClientRequestId",
    "ResourceId",
    "Location",
    "ApiName",
    "ApiVersion",
    "ModelOutput",
    "ResponseCode",
    "Latency",
)


class LogRecordFormatter(handler.FluentRecordFormatter):
    pascal_case: bool = False

    def __init__(self, log_environment: LogEnvironment, pascal_case: bool = False):
        super().__init__(default_log_record(log_environment))
        self.pascal_case = pascal_case

    def format(self, record: LogRecord):
        data = super().format(record._original_record)

        try:
            self._add_dic(
                data,
                {
                    "trace_id": (
                        f"0x{format_trace_id(record.trace_id)}"
                        if record.trace_id is not None
                        else ""
                    ),
                    "span_id": (
                        f"0x{format_span_id(record.span_id)}"
                        if record.span_id is not None
                        else ""
                    ),
                    "trace_flags": record.trace_flags,
                    "resource": json.loads(record.resource.to_json())
                    if record.resource
                    else None,
                    "attributes": (
                        dict(record.attributes) if bool(record.attributes) else None
                    ),
                },
            )

            if bool(record.attributes):
                items = record.attributes.items()
                additional_values = {}
                for key, value in items:
                    if key in AllowableKeys:
                        data[key] = value
                    elif key.startswith("code.") or key in (
                        "timestamp",
                        "precise_timestamp",
                    ):
                        pass
                    else:
                        additional_values[key] = value
                if bool(additional_values):
                    data["additional_values"] = additional_values

            current_span = get_current_span()
            if (
                current_span
                and hasattr(current_span, "attributes")
                and current_span.attributes
            ):
                attributes = dict(current_span.attributes)

                self._add_dic(
                    data,
                    {
                        "span": attributes,
                    },
                )

                for header in "correlation_id":
                    if f"http.request.header.{header}" in attributes:
                        value = attributes[f"http.request.header.{header}"]
                        if (
                            isinstance(value, tuple) or isinstance(value, list)
                        ) and len(value) == 1:
                            value = ",".join(value)
                        data[header] = value

        except Exception as e:
            data["log_error"] = str(e)

        data["log_type"] = "log"

        if self.pascal_case:
            return json.dumps(
                {
                    underscore_to_pascal_case(k): v
                    for k, v in data.items()
                    if v is not None
                }
            )
        else:
            return json.dumps(data)


class SpanRecordFormatter(handler.FluentRecordFormatter):
    default_record: dict
    pascal_case: bool = False

    def __init__(self, log_environment: LogEnvironment, pascal_case: bool = False):
        super().__init__()

        self.default_record = default_record(log_environment)
        self.pascal_case = pascal_case

    def format(self, record: ReadableSpan):
        result: dict = json.loads(record.to_json(indent=None))

        for key, value in self.default_record.items():
            if key not in result:
                result[key] = value

        result["log_type"] = "trace"

        if self.pascal_case:
            return json.dumps(
                {
                    underscore_to_pascal_case(k): v
                    for k, v in result.items()
                    if v is not None
                }
            )
        else:
            return json.dumps(result)
