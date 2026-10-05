from collections import Counter

from backend.parsers.custom_parser import (
    parse_custom_log,
)

from backend.parsers.json_parser import (
    parse_json_log,
)

from backend.parsers.access_parser import (
    parse_access_log,
)


PARSERS = [
    parse_json_log,
    parse_access_log,
    parse_custom_log,
]


def parse_log_line(line):
    if not line.strip():
        return None

    for parser in PARSERS:
        result = parser(line)

        if result is not None:
            return result

    return None


def parse_log_content(content):
    requests = []

    total_lines = 0
    ignored_lines = 0

    formats = Counter()

    for line in content.splitlines():
        if not line.strip():
            continue

        total_lines += 1

        result = parse_log_line(line)

        if result is None:
            ignored_lines += 1
            continue

        requests.append(result)

        formats[result["format"]] += 1

    return {
        "requests": requests,
        "total_lines": total_lines,
        "ignored_lines": ignored_lines,
        "formats": dict(formats),
    }