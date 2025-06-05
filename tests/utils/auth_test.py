"""
This module contains tests for the Authorization utilities.
"""

from typing import Any, Dict
from unittest.mock import patch

from src.utils.auth import get_authorization_token


def test_get_authorization_token_with_valid_bearer_header() -> None:
    """Test extraction of token from a valid Bearer authorization header."""
    headers: Dict[str, str] = {"Authorization": "Bearer test.jwt.token"}
    token: str | None = get_authorization_token(headers)
    assert token == "test.jwt.token"


def test_get_authorization_token_with_non_bearer_header() -> None:
    """Test extraction of token from a non-Bearer authorization header."""
    headers: Dict[str, str] = {"Authorization": "InvalidScheme token"}
    token: str | None = get_authorization_token(headers)
    assert token == "InvalidScheme token"


def test_get_authorization_token_with_missing_header() -> None:
    """Test extraction of token when authorization header is missing."""
    headers: Dict[str, str] = {}
    token: str | None = get_authorization_token(headers)
    assert token is None


def test_get_authorization_token_cookie_priority_over_header() -> None:
    """Test that cookie takes priority over authorization header."""
    headers: Dict[str, str] = {
        "Cookie": "authorization=cookie_token",
        "Authorization": "Bearer header.token",
    }
    token: str | None = get_authorization_token(headers)
    assert token == "cookie_token"


def test_get_authorization_token_case_insensitive_headers() -> None:
    """Test that header matching is case insensitive."""
    headers: Dict[str, str] = {"authorization": "Bearer test.jwt.token"}
    token: str | None = get_authorization_token(headers)
    assert token == "test.jwt.token"


def test_get_authorization_token_empty_cookie_header() -> None:
    """Test handling of empty cookie header."""
    headers: Dict[str, str] = {"Cookie": ""}
    token: str | None = get_authorization_token(headers)
    assert token is None


def test_get_authorization_token_empty_cookie_header_with_auth_header() -> None:
    """Test handling of empty cookie header with authorization header fallback."""
    headers: Dict[str, str] = {"Cookie": "", "Authorization": "Bearer fallback.token"}
    token: str | None = get_authorization_token(headers)
    assert token == "fallback.token"


def test_get_authorization_token_mixed_case_headers() -> None:
    """Test case insensitive header processing."""
    headers: Dict[str, str] = {
        "Cookie": "session=test",
        "AUTHORIZATION": "Bearer mixed.case.token",
    }
    token: str | None = get_authorization_token(headers)
    assert token == "mixed.case.token"


def test_get_authorization_token_header_without_bearer() -> None:
    """Test authorization header without Bearer prefix."""
    headers: Dict[str, str] = {"Authorization": "simple.token"}
    token: str | None = get_authorization_token(headers)
    assert token == "simple.token"


def test_get_authorization_token_empty_authorization_header() -> None:
    """Test empty authorization header."""
    headers: Dict[str, str] = {"Authorization": ""}
    token: str | None = get_authorization_token(headers)
    assert token is None


def test_get_authorization_token_bearer_only_header() -> None:
    """Test authorization header with only 'Bearer ' prefix."""
    headers: Dict[str, str] = {"Authorization": "Bearer "}
    token: str | None = get_authorization_token(headers)
    assert token is None


def test_get_authorization_token_bearer_cookie_no_quotes() -> None:
    """Test Bearer cookie without quotes."""
    headers: Dict[str, str] = {"Cookie": "authorization=BearerToken"}
    token: str | None = get_authorization_token(headers)
    assert token == "BearerToken"


def test_get_authorization_token_multiple_cookies_with_auth() -> None:
    """Test multiple cookies where one is authorization."""
    headers: Dict[str, str] = {
        "Cookie": "session=abc123; authorization=my_token; theme=dark"
    }
    token: str | None = get_authorization_token(headers)
    assert token == "my_token"


def test_get_authorization_token_cookie_case_insensitive() -> None:
    """Test that cookie name matching is case insensitive."""
    headers: Dict[str, str] = {"Cookie": "AUTHORIZATION=case_token"}
    token: str | None = get_authorization_token(headers)
    assert token == "case_token"


def test_get_authorization_token_cookie_with_quotes() -> None:
    """Test authorization cookie with quoted value."""
    headers: Dict[str, str] = {"Cookie": 'authorization="quoted_token"'}
    token: str | None = get_authorization_token(headers)
    assert token == "quoted_token"


@patch("src.utils.auth.logger")
def test_get_authorization_token_malformed_cookie_exception(mock_logger: Any) -> None:
    """Test handling of malformed cookie that causes parsing exception."""
    with patch("src.utils.auth.SimpleCookie") as mock_cookie:
        mock_cookie.return_value.load.side_effect = Exception("Cookie parsing error")

        headers: Dict[str, str] = {
            "Cookie": "authorization=token; invalid_cookie_format"
        }
        token: str | None = get_authorization_token(headers)
        assert token is None
        mock_logger.error.assert_called_once()
        assert "Error parsing cookies:" in mock_logger.error.call_args[0][0]


@patch("src.utils.auth.logger")
def test_get_authorization_token_no_token_warning(mock_logger: Any) -> None:
    """Test that warning is logged when no authorization token is found."""
    headers: Dict[str, str] = {"Content-Type": "application/json"}
    token: str | None = get_authorization_token(headers)
    assert token is None
    mock_logger.warning.assert_called_once_with(
        "No authorization token found in MCP instance"
    )


def test_get_authorization_token_cookie_no_authorization_key() -> None:
    """Test cookie header without authorization key."""
    headers: Dict[str, str] = {"Cookie": "session=abc123; theme=dark"}
    token: str | None = get_authorization_token(headers)
    assert token is None


def test_get_authorization_token_authorization_header_case_variations() -> None:
    """Test various case combinations for authorization header."""
    test_cases = [
        {"AUTHORIZATION": "Bearer test.token"},
        {"Authorization": "Bearer test.token"},
        {"authorization": "Bearer test.token"},
        {"AuThOrIzAtIoN": "Bearer test.token"},
    ]

    for headers in test_cases:
        token: str | None = get_authorization_token(headers)
        assert token == "test.token"


def test_get_authorization_token_cookie_header_case_variations() -> None:
    """Test various case combinations for cookie header."""
    test_cases = [
        {"COOKIE": "authorization=test.token"},
        {"Cookie": "authorization=test.token"},
        {"cookie": "authorization=test.token"},
        {"CoOkIe": "authorization=test.token"},
    ]

    for headers in test_cases:
        token: str | None = get_authorization_token(headers)
        assert token == "test.token"


def test_get_authorization_token_bearer_empty_string() -> None:
    """Test authorization header that results in empty string after stripping Bearer."""
    headers: Dict[str, str] = {"Authorization": "Bearer"}
    token: str | None = get_authorization_token(headers)
    assert token == "Bearer"
