import json
from datetime import datetime


def get_first(data, keys):
    for key in keys:
        if key in data and data[key] is not None:
            return data[key]

    return None


def parse_timestamp(value):
    if value is None:
        return None

    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(value)
        except (ValueError, OSError):
            return None

    value = str(value)

    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except ValueError:
        pass

    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
    ]

    for date_format in formats:
        try:
            return datetime.strptime(
                value,
                date_format
            )
        except ValueError:
            continue

    return None


def parse_json_log(line):
    line = line.strip()

    if not line.startswith("{"):
        return None

    try:
        data = json.loads(line)
    except json.JSONDecodeError:
        return None

    timestamp = parse_timestamp(
        get_first(
            data,
            [
                "timestamp",
                "time",
                "datetime",
                "@timestamp",
            ]
        )
    )

    method = get_first(
        data,
        [
            "method",
            "http_method",
            "request_method",
        ]
    )

    endpoint = get_first(
        data,
        [
            "endpoint",
            "path",
            "url",
            "route",
        ]
    )

    status = get_first(
        data,
        [
            "status",
            "status_code",
            "http_status",
        ]
    )

    response_time = get_first(
        data,
        [
            "response_time",
            "duration_ms",
            "latency_ms",
            "response_time_ms",
        ]
    )

    if (
        timestamp is None
        or method is None
        or endpoint is None
        or status is None
    ):
        return None

    try:
        status = int(status)
    except (TypeError, ValueError):
        return None

    if response_time is not None:
        try:
            response_time = float(
                response_time
            )
        except (TypeError, ValueError):
            response_time = None

    bytes_sent = get_first(
        data,
        [
            "bytes",
            "bytes_sent",
            "response_size",
        ]
    )

    if bytes_sent is not None:
        try:
            bytes_sent = int(bytes_sent)
        except (TypeError, ValueError):
            bytes_sent = None

    return {
        "timestamp": timestamp,
        "method": str(method).upper(),
        "endpoint": str(endpoint),
        "status": status,
        "response_time": response_time,
        "ip": get_first(
            data,
            [
                "ip",
                "client_ip",
                "remote_addr",
            ]
        ),
        "bytes": bytes_sent,
        "user_agent": get_first(
            data,
            [
                "user_agent",
                "userAgent",
            ]
        ),
        "level": get_first(
            data,
            [
                "level",
                "severity",
            ]
        ),
        "format": "JSON",
    }