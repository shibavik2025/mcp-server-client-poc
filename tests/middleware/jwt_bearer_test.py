# pylint: disable=redefined-outer-name

"""
Tests for JWTMiddleware.
"""

from unittest.mock import patch
from typing import Dict, Any

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials
import jwt
from httpx import RequestError
from starlette import status

from src.middleware.jwt_bearer import JWTMiddleware  # type: ignore[attr-defined]
from src.core.config import settings

app = FastAPI()


@app.get("/secure")
async def secure_endpoint(request: Request) -> Dict[str, Any]:
    """Endpoint to return user information from the request state."""
    return {"user_info": request.state.user_info}


app.add_middleware(JWTMiddleware)


@pytest.fixture
def client() -> TestClient:
    """Fixture to provide a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def valid_token_payload() -> Dict[str, Dict[str, str]]:
    """Fixture to provide a valid token payload for testing."""
    return {"UserInfo": {"id": "user123", "role": "admin"}}


def test_valid_token_in_header(
    client: TestClient, valid_token_payload: Dict[str, Dict[str, str]]
) -> None:
    """Test that a valid token in the header returns user info successfully."""
    with patch("jwt.decode", return_value=valid_token_payload):
        token = "valid.token.here"
        response = client.get("/secure", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert response.json() == {"user_info": valid_token_payload["UserInfo"]}


def test_token_from_cookie(
    client: TestClient, valid_token_payload: Dict[str, Dict[str, str]]
) -> None:
    """Test that a valid token in cookies returns user info successfully."""
    with patch("jwt.decode", return_value=valid_token_payload):
        client.cookies.set("Authorization", "cookie.token.here")
        response = client.get("/secure")
        assert response.status_code == 200
        assert response.json() == {"user_info": valid_token_payload["UserInfo"]}


def test_invalid_authentication_scheme(client: TestClient) -> None:
    """Test that an invalid authentication scheme returns a 403 status (from HTTPBearer)."""
    response = client.get("/secure", headers={"Authorization": "Basic invalid.token"})
    assert response.status_code == 403
    assert "Invalid authentication credentials" in response.json()["detail"]


def test_no_token_found(client: TestClient) -> None:
    """Test that missing token after Bearer returns 403 (from HTTPBearer)."""
    response = client.get("/secure", headers={"Authorization": "Bearer "})
    assert response.status_code == 403
    assert "Not authenticated" in response.json()["detail"]


def test_invalid_token(client: TestClient) -> None:
    """Test that an invalid token returns a 401 status with an appropriate error message."""
    with patch("jwt.decode", side_effect=jwt.InvalidTokenError("Invalid!")):
        response = client.get("/secure", headers={"Authorization": "Bearer bad.token"})
        assert response.status_code == 401
        assert "Invalid token: Invalid!" in response.json()["detail"]


def test_expired_token(client: TestClient) -> None:
    """Test that an expired token returns a 401 status with an expiration error message."""
    with patch("jwt.decode", side_effect=jwt.ExpiredSignatureError("Expired")):
        response = client.get(
            "/secure", headers={"Authorization": "Bearer expired.token"}
        )
        assert response.status_code == 401
        assert "Token has expired" in response.json()["detail"]


def test_missing_token(client: TestClient) -> None:
    """Test that a missing token returns a 403 status with a not authenticated message."""
    response = client.get("/secure")
    assert response.status_code == 403
    assert "Not authenticated" in response.json()["detail"]


def test_missing_user_info(client: TestClient) -> None:
    """Test that a token missing user info returns a 401 status with an error message."""
    with patch("jwt.decode", return_value={}):
        response = client.get(
            "/secure", headers={"Authorization": "Bearer no.userinfo"}
        )
        assert response.status_code == 401
        assert "missing user info" in response.json()["detail"]


def test_skip_path() -> None:
    """Test that paths in the skip list bypass authentication."""
    skip_app = FastAPI()

    @skip_app.get("/api/v1/skip")
    async def skip() -> Dict[str, str]:
        """Endpoint to test skipping authentication."""
        return {"message": "Skipped auth"}

    with (
        patch.object(settings, "base_path", "/api/v1"),
        patch.object(settings, "skip_paths", ["/skip"]),
    ):
        skip_app.add_middleware(JWTMiddleware)
        skip_client = TestClient(skip_app)

        response = skip_client.get("/api/v1/skip")
        assert response.status_code == 200
        assert response.json()["message"] == "Skipped auth"


def test_unexpected_exception_during_token_validation(client: TestClient) -> None:
    """Test that an unexpected exception during token validation returns a 401."""
    with patch("jwt.decode", side_effect=Exception("Boom")):
        response = client.get(
            "/secure", headers={"Authorization": "Bearer whatever.token"}
        )
        assert response.status_code == 401
        assert "Unhandled JWT validation error: Boom" in response.json()["detail"]


def test_request_error_in_middleware() -> None:
    """Test that RequestError in middleware returns 500 status."""
    test_app = FastAPI()

    @test_app.get("/test")
    async def test_endpoint() -> Dict[str, str]:
        return {"message": "test"}

    test_app.add_middleware(JWTMiddleware)
    test_client = TestClient(test_app)

    with patch.object(JWTMiddleware, "dispatch") as mock_dispatch:
        # pylint: disable=unused-argument
        async def side_effect(request, call_next):  # type: ignore
            try:
                raise RequestError("Network error")
            except RequestError:
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content={"detail": "Internal server error"},
                )

        mock_dispatch.side_effect = side_effect
        response = test_client.get("/test")
        assert response.status_code == 500
        assert "Internal server error" in response.json()["detail"]


def test_header_injection_logic(
    client: TestClient, valid_token_payload: Dict[str, Dict[str, str]]
) -> None:
    """Test that Authorization header is properly handled when token comes from cookie."""
    with patch("jwt.decode", return_value=valid_token_payload):
        client.cookies.set("Authorization", "cookie.token.here")
        response = client.get("/secure")
        assert response.status_code == 200
        assert response.json() == {"user_info": valid_token_payload["UserInfo"]}


def test_empty_authorization_header(client: TestClient) -> None:
    """Test handling of empty Authorization header value."""
    response = client.get("/secure", headers={"Authorization": ""})
    assert response.status_code == 403
    assert "Not authenticated" in response.json()["detail"]


def test_bearer_without_token(client: TestClient) -> None:
    """Test handling of Bearer without actual token."""
    response = client.get("/secure", headers={"Authorization": "Bearer"})
    assert response.status_code == 403
    assert "Not authenticated" in response.json()["detail"]


def test_bearer_with_only_whitespace(client: TestClient) -> None:
    """Test Bearer authorization with only whitespace after Bearer keyword."""
    response = client.get("/secure", headers={"Authorization": "Bearer    "})
    assert response.status_code == 401
    assert "Invalid token: Not enough segments" in response.json()["detail"]


def test_non_bearer_scheme_with_token(client: TestClient) -> None:
    """Test handling of non-Bearer authentication schemes returns 403 from HTTPBearer."""
    response = client.get("/secure", headers={"Authorization": "Basic dGVzdDp0ZXN0"})
    assert response.status_code == 403
    assert "Invalid authentication credentials" in response.json()["detail"]


def test_cookie_token_priority(
    client: TestClient, valid_token_payload: Dict[str, Dict[str, str]]
) -> None:
    """Test that cookie token takes priority over header when both are present."""
    with patch("jwt.decode", return_value=valid_token_payload):
        client.cookies.set("Authorization", "cookie.token.here")
        response = client.get(
            "/secure", headers={"Authorization": "Bearer header.token.here"}
        )
        assert response.status_code == 200
        assert response.json() == {"user_info": valid_token_payload["UserInfo"]}


def test_jwt_decode_with_correct_parameters(
    client: TestClient, valid_token_payload: Dict[str, Dict[str, str]]
) -> None:
    """Test that jwt.decode is called with correct parameters."""
    with patch("jwt.decode", return_value=valid_token_payload) as mock_decode:
        token = "test.token.here"
        response = client.get("/secure", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200

        mock_decode.assert_called_once_with(
            token,
            settings.enterprise_auth_public_key,
            algorithms=[settings.encryption_algorithm],
        )


def test_malformed_jwt_token(client: TestClient) -> None:
    """Test handling of malformed JWT tokens that cause 'Not enough segments' error."""
    with patch("jwt.decode", side_effect=jwt.InvalidTokenError("Not enough segments")):
        response = client.get(
            "/secure", headers={"Authorization": "Bearer malformed.token"}
        )
        assert response.status_code == 401
        assert "Invalid token: Not enough segments" in response.json()["detail"]


def test_custom_invalid_scheme() -> None:
    """Test invalid scheme."""
    test_app = FastAPI()

    @test_app.get("/test")
    async def test_endpoint(request: Request) -> Dict[str, str]:
        return {"user_info": request.state.user_info}

    test_app.add_middleware(JWTMiddleware)
    test_client = TestClient(test_app)

    mock_credentials = HTTPAuthorizationCredentials(
        scheme="Basic", credentials="test.token"
    )

    with patch(
        "src.middleware.jwt_bearer.HTTPBearer.__call__", return_value=mock_credentials
    ):
        response = test_client.get(
            "/test", headers={"Authorization": "Basic test.token"}
        )
        assert response.status_code == 401
        assert "Invalid authentication scheme" in response.json()["detail"]


def test_empty_token() -> None:
    """Test empty token."""
    test_app = FastAPI()

    @test_app.get("/test")
    async def test_endpoint(request: Request) -> Dict[str, str]:
        return {"user_info": request.state.user_info}

    test_app.add_middleware(JWTMiddleware)
    test_client = TestClient(test_app)

    mock_credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="")

    with patch(
        "src.middleware.jwt_bearer.HTTPBearer.__call__", return_value=mock_credentials
    ):
        response = test_client.get("/test", headers={"Authorization": "Bearer "})
        assert response.status_code == 401
        assert "Invalid authorization code" in response.json()["detail"]
