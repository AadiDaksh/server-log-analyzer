import unittest

from datetime import datetime

from backend.analyzer import (
    calculate_latency,
    calculate_summary,
    analyze_endpoints,
)


class TestAnalyzer(
    unittest.TestCase
):

    def setUp(self):
        timestamp = datetime(
            2026,
            10,
            4,
            12,
            0,
            0
        )

        self.requests = [
            {
                "timestamp": timestamp,
                "method": "GET",
                "endpoint": "/users",
                "status": 200,
                "response_time": 100,
                "ip": None,
                "bytes": None,
                "user_agent": None,
                "level": "INFO",
                "format": "Custom",
            },

            {
                "timestamp": timestamp,
                "method": "GET",
                "endpoint": "/users",
                "status": 200,
                "response_time": 200,
                "ip": None,
                "bytes": None,
                "user_agent": None,
                "level": "INFO",
                "format": "Custom",
            },

            {
                "timestamp": timestamp,
                "method": "GET",
                "endpoint": "/orders",
                "status": 500,
                "response_time": None,
                "ip": "127.0.0.1",
                "bytes": 200,
                "user_agent": None,
                "level": None,
                "format": "Nginx/Apache",
            },
        ]


    def test_summary(self):
        result = calculate_summary(
            self.requests
        )

        self.assertEqual(
            result[
                "total_requests"
            ],
            3
        )

        self.assertEqual(
            result[
                "server_errors"
            ],
            1
        )


    def test_missing_latency(self):
        requests = [
            self.requests[2]
        ]

        latency = (
            calculate_latency(
                requests
            )
        )

        self.assertFalse(
            latency["available"]
        )

        self.assertIsNone(
            latency["p95"]
        )


    def test_available_latency(self):
        latency = (
            calculate_latency(
                self.requests
            )
        )

        self.assertTrue(
            latency["available"]
        )

        self.assertEqual(
            latency["p50"],
            150
        )


    def test_critical_endpoint(self):
        endpoints = (
            analyze_endpoints(
                self.requests
            )
        )

        orders = next(
            endpoint
            for endpoint in endpoints
            if endpoint["endpoint"]
            == "/orders"
        )

        self.assertEqual(
            orders["health"],
            "Critical"
        )


if __name__ == "__main__":
    unittest.main()