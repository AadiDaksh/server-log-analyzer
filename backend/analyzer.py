from collections import Counter, defaultdict
from statistics import median
import math


def percentile(values, percent):
    if not values:
        return None

    values = sorted(values)

    position = (
        len(values) - 1
    ) * (
        percent / 100
    )

    lower = math.floor(position)
    upper = math.ceil(position)

    if lower == upper:
        return values[lower]

    lower_value = values[lower]
    upper_value = values[upper]

    return lower_value + (
        upper_value - lower_value
    ) * (
        position - lower
    )


def calculate_latency(requests):
    times = [
        request["response_time"]
        for request in requests
        if request["response_time"] is not None
    ]

    if not times:
        return {
            "available": False,
            "samples": 0,
            "average": None,
            "p50": None,
            "p95": None,
            "p99": None,
            "max": None,
        }

    return {
        "available": True,
        "samples": len(times),

        "average": round(
            sum(times) / len(times),
            2
        ),

        "p50": round(
            median(times),
            2
        ),

        "p95": round(
            percentile(times, 95),
            2
        ),

        "p99": round(
            percentile(times, 99),
            2
        ),

        "max": round(
            max(times),
            2
        ),
    }


def calculate_summary(requests):
    total = len(requests)

    if total == 0:
        return {
            "total_requests": 0,
            "successful_requests": 0,
            "client_errors": 0,
            "server_errors": 0,
            "error_requests": 0,
            "success_rate": 0,
            "error_rate": 0,
            "latency": calculate_latency([]),
        }

    successful = sum(
        1
        for request in requests
        if 200 <= request["status"] < 400
    )

    client_errors = sum(
        1
        for request in requests
        if 400 <= request["status"] < 500
    )

    server_errors = sum(
        1
        for request in requests
        if request["status"] >= 500
    )

    errors = (
        client_errors
        + server_errors
    )

    return {
        "total_requests": total,

        "successful_requests": successful,

        "client_errors": client_errors,

        "server_errors": server_errors,

        "error_requests": errors,

        "success_rate": round(
            successful / total * 100,
            2
        ),

        "error_rate": round(
            errors / total * 100,
            2
        ),

        "latency": calculate_latency(
            requests
        ),
    }


def analyze_status_codes(requests):
    counter = Counter(
        request["status"]
        for request in requests
    )

    return [
        {
            "status": status,
            "count": count,
        }
        for status, count
        in sorted(counter.items())
    ]


def analyze_endpoints(requests):
    grouped = defaultdict(list)

    for request in requests:
        grouped[
            (
                request["method"],
                request["endpoint"],
            )
        ].append(request)

    results = []

    for (
        method,
        endpoint
    ), endpoint_requests in grouped.items():

        total = len(
            endpoint_requests
        )

        errors = sum(
            1
            for request in endpoint_requests
            if request["status"] >= 400
        )

        server_errors = sum(
            1
            for request in endpoint_requests
            if request["status"] >= 500
        )

        error_rate = (
            errors / total * 100
        )

        server_error_rate = (
            server_errors / total * 100
        )

        latency = calculate_latency(
            endpoint_requests
        )

        if server_error_rate >= 10:
            health = "Critical"

        elif error_rate >= 10:
            health = "Warning"

        elif (
            latency["available"]
            and latency["p95"] >= 1000
        ):
            health = "Slow"

        else:
            health = "Healthy"

        results.append(
            {
                "method": method,
                "endpoint": endpoint,
                "requests": total,
                "errors": errors,

                "error_rate": round(
                    error_rate,
                    2
                ),

                "average_latency":
                    latency["average"],

                "p95_latency":
                    latency["p95"],

                "latency_available":
                    latency["available"],

                "health": health,
            }
        )

    priorities = {
        "Critical": 0,
        "Warning": 1,
        "Slow": 2,
        "Healthy": 3,
    }

    results.sort(
        key=lambda item: (
            priorities[
                item["health"]
            ],
            -item["requests"],
        )
    )

    return results


def requests_over_time(requests):
    counter = Counter()

    for request in requests:
        timestamp = request[
            "timestamp"
        ]

        key = timestamp.strftime(
            "%Y-%m-%d %H:%M"
        )

        counter[key] += 1

    return [
        {
            "time": time,
            "requests": count,
        }
        for time, count
        in sorted(counter.items())
    ]


def recent_problems(
    requests,
    limit=15
):
    problems = []

    for request in requests:
        is_error = (
            request["status"] >= 400
        )

        is_slow = (
            request["response_time"]
            is not None
            and request["response_time"]
            >= 1000
        )

        if not is_error and not is_slow:
            continue

        if request["status"] >= 500:
            issue = "Server Error"

        elif request["status"] >= 400:
            issue = "Client Error"

        else:
            issue = "Slow Request"

        problems.append(
            {
                "timestamp":
                    request[
                        "timestamp"
                    ].isoformat(),

                "method":
                    request["method"],

                "endpoint":
                    request["endpoint"],

                "status":
                    request["status"],

                "response_time":
                    request["response_time"],

                "ip":
                    request["ip"],

                "issue":
                    issue,
            }
        )

    problems.sort(
        key=lambda item:
            item["timestamp"],
        reverse=True
    )

    return problems[:limit]


def top_endpoints(
    requests,
    limit=5
):
    counter = Counter(
        request["endpoint"]
        for request in requests
    )

    return [
        {
            "endpoint": endpoint,
            "requests": count,
        }
        for endpoint, count
        in counter.most_common(limit)
    ]


def build_dashboard_data(requests):
    return {
        "summary":
            calculate_summary(
                requests
            ),

        "status_codes":
            analyze_status_codes(
                requests
            ),

        "endpoints":
            analyze_endpoints(
                requests
            ),

        "requests_over_time":
            requests_over_time(
                requests
            ),

        "recent_problems":
            recent_problems(
                requests
            ),

        "top_endpoints":
            top_endpoints(
                requests
            ),
    }