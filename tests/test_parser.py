import unittest

from backend.parsers.detector import (
    parse_log_line,
    parse_log_content,
)


class TestParsers(
    unittest.TestCase
):

    def test_custom_format(self):
        line = (
            "2026-10-04 14:32:01 "
            "INFO GET /api/users "
            "200 43ms"
        )

        result = parse_log_line(
            line
        )

        self.assertIsNotNone(
            result
        )

        self.assertEqual(
            result["format"],
            "Custom"
        )

        self.assertEqual(
            result["response_time"],
            43
        )


    def test_json_format(self):
        line = (
            '{"timestamp":'
            '"2026-10-04T18:32:10Z",'
            '"method":"GET",'
            '"path":"/api/users",'
            '"status":200,'
            '"duration_ms":43}'
        )

        result = parse_log_line(
            line
        )

        self.assertIsNotNone(
            result
        )

        self.assertEqual(
            result["format"],
            "JSON"
        )

        self.assertEqual(
            result["endpoint"],
            "/api/users"
        )


    def test_access_format(self):
        line = (
            '127.0.0.1 - - '
            '[04/Oct/2026:18:32:10 -0400] '
            '"GET /api/users HTTP/1.1" '
            '200 1243 '
            '"-" "Mozilla/5.0"'
        )

        result = parse_log_line(
            line
        )

        self.assertIsNotNone(
            result
        )

        self.assertEqual(
            result["format"],
            "Nginx/Apache"
        )

        self.assertEqual(
            result["status"],
            200
        )

        self.assertIsNone(
            result["response_time"]
        )


    def test_invalid_line(self):
        result = parse_log_line(
            "random unsupported text"
        )

        self.assertIsNone(
            result
        )


    def test_mixed_formats(self):
        content = """
2026-10-04 14:32:01 INFO GET /api/users 200 43ms
{"timestamp":"2026-10-04T18:32:10Z","method":"GET","path":"/api/products","status":200,"duration_ms":81}
127.0.0.1 - - [04/Oct/2026:18:32:10 -0400] "GET /api/orders HTTP/1.1" 500 1243 "-" "Mozilla/5.0"
unsupported line
"""

        result = parse_log_content(
            content
        )

        self.assertEqual(
            len(
                result["requests"]
            ),
            3
        )

        self.assertEqual(
            result[
                "ignored_lines"
            ],
            1
        )

        self.assertEqual(
            result["formats"][
                "Custom"
            ],
            1
        )

        self.assertEqual(
            result["formats"][
                "JSON"
            ],
            1
        )

        self.assertEqual(
            result["formats"][
                "Nginx/Apache"
            ],
            1
        )


if __name__ == "__main__":
    unittest.main()