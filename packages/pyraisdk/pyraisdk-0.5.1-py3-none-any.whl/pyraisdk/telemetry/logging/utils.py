# -*- coding:utf-8 -*-

import datetime


def underscore_to_pascal_case(name: str) -> str:
    return "".join([x.capitalize() if x else "_" for x in name.split("_")])


def ms_to_iso_str(milliseconds):
    """Get an ISO 8601 string from time_ns value."""
    ts = datetime.datetime.fromtimestamp(milliseconds, tz=datetime.timezone.utc)
    return ts.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
