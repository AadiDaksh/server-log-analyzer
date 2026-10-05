import re
from datetime import datetime


ACCESS_PATTERN = re.compile(
    r'(?P<ip>\S+) '
    r'\S+ '
    r'\S+ '
    r'\[(?P<timestamp>[^\]]+)\] '
    r'"(?P<method>[A-Z]+) '
    r'(?P<endpoint>\S+) '
    r'HTTP/(?P<http_version>[^"]+)" '
    r'(?P<status>\d{3}) '
    r'(?P<bytes>\S+)'
    r'(?: "(?P<referrer>[^"]*)"'
    r' "(?P<user_agent>[^"]*)")?'
    r'(?: (?P<request_time>\d+(?:\.\d+)?))?'
)


def parse_access_log(line):
    match = ACCESS_PATTERN.fullmatch(
        line.strip()
    )

    if not match:
        return None

    data = match.groupdict()

    try:
        timestamp = datetime.strptime(
            data["timestamp"],
            "%d/%b/%Y:%H:%M:%S %z"
        )
    except ValueError:
        return None

    if data["bytes"] == "-":
        bytes_sent = None
    else:
        try:
            bytes_sent = int(
                data["bytes"]
            )
        except ValueError:
            bytes_sent = None

    response_time = None

    if data["request_time"]:
        try:
            # Nginx request_time is normally
            # measured in seconds.
            response_time = (
                float(data["request_time"])
                * 1000
            )
        except ValueError:
            response_time = None

    return {
        "timestamp": timestamp,
        "method": data["method"],
        "endpoint": data["endpoint"],
        "status": int(data["status"]),
        "response_time": response_time,
        "ip": data["ip"],
        "bytes": bytes_sent,
        "user_agent": data["user_agent"],
        "level": None,
        "format": "Nginx/Apache",
    }