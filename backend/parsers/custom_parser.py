import re
from datetime import datetime


CUSTOM_PATTERN = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2}) "
    r"(?P<time>\d{2}:\d{2}:\d{2}) "
    r"(?P<level>[A-Z]+) "
    r"(?P<method>GET|POST|PUT|PATCH|DELETE|OPTIONS|HEAD) "
    r"(?P<endpoint>\S+) "
    r"(?P<status>\d{3}) "
    r"(?P<response_time>\d+(?:\.\d+)?)ms"
)


def parse_custom_log(line):
    match = CUSTOM_PATTERN.fullmatch(
        line.strip()
    )

    if not match:
        return None

    data = match.groupdict()

    timestamp = datetime.strptime(
        f"{data['date']} {data['time']}",
        "%Y-%m-%d %H:%M:%S"
    )

    return {
        "timestamp": timestamp,
        "method": data["method"],
        "endpoint": data["endpoint"],
        "status": int(data["status"]),
        "response_time": float(
            data["response_time"]
        ),
        "ip": None,
        "bytes": None,
        "user_agent": None,
        "level": data["level"],
        "format": "Custom",
    }