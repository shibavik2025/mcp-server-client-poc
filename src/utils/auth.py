"""Authorization utilities."""

from typing import Dict, Optional
from http.cookies import SimpleCookie

from src.core.logger import logger


def get_authorization_token(headers: Dict[str, str]) -> Optional[str]:
    """Extract authorization token from headers, checking both cookies and authorization header."""
    headers_lower = {k.lower(): v for k, v in headers.items()}

    # Try to get token from cookies first
    token_cookies = _extract_token_from_cookies(headers_lower)
    if token_cookies:
        return token_cookies

    # If token not in cookies try to get from auth header
    token_auth_header = _extract_token_from_auth_header(headers_lower)
    if token_auth_header:
        return token_auth_header

    logger.warning("No authorization token found in MCP instance")
    return None


def _extract_token_from_cookies(headers_lower: Dict[str, str]) -> Optional[str]:
    """Extract token from cookie header."""
    cookie_header = headers_lower.get("cookie", "")
    if not cookie_header:
        return None

    try:
        cookie = SimpleCookie()
        cookie.load(cookie_header)

        # Look for authorization cookie
        for key, morsel in cookie.items():
            if key.lower() == "authorization":
                return _strip_bearer_prefix(morsel.value)
    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.error(f"Error parsing cookies: {str(e)}")
        return None

    return None


def _extract_token_from_auth_header(headers_lower: Dict[str, str]) -> Optional[str]:
    """Extract token from authorization header."""
    auth_header = headers_lower.get("authorization", "")
    return _strip_bearer_prefix(auth_header) if auth_header else None


def _strip_bearer_prefix(token: str) -> str:
    """Remove 'Bearer ' prefix from token if present."""
    bearer_prefix = "Bearer "
    return token[len(bearer_prefix) :] if token.startswith(bearer_prefix) else token
