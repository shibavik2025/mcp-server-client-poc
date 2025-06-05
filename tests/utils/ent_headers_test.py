"""This module contains tests for Headers utilities."""

import unittest

from src.utils.ent_headers import add_ent_headers


class TestEntHeadersUtilities(unittest.TestCase):
    """Tests for the Headers utilties."""

    def test_add_ent_headers_with_dict(self) -> None:
        """Test add_ent_headers with a dictionary of headers.

        Ensures that the function correctly updates the default headers
        with the enterprise headers provided as a dictionary.
        """
        default_headers = {"Content-Type": "application/json"}
        ent_headers = {
            "traceparent": "123",
            "x-client-id": "abc",
            "x-project-id": "def",
            "x-portfolio-id": "ghi",
            "x-workspace-id": "jkl",
        }
        updated_headers = add_ent_headers(default_headers, ent_headers)
        self.assertEqual(updated_headers["traceparent"], "123")
        self.assertEqual(updated_headers["x-client-id"], "abc")

    def test_add_ent_headers_with_json_string(self) -> None:
        """Test add_ent_headers with a JSON string of headers.

        Ensures that the function correctly updates the default headers
        with the enterprise headers provided as a JSON string.
        """
        default_headers = {"Content-Type": "application/json"}
        ent_headers = '{"traceparent": "123", "x-client-id": "abc"}'
        updated_headers = add_ent_headers(default_headers, ent_headers)
        self.assertEqual(updated_headers["traceparent"], "123")
        self.assertEqual(updated_headers["x-client-id"], "abc")
