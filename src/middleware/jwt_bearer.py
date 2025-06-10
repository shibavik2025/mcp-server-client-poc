# type: ignore
# pylint: disable=too-few-public-methods
"""JWTBearer class to Verify the Authorization header"""

from typing import Optional

import jwt
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from httpx import RequestError

from src.core.config import settings
from src.core.logger import logger


# JWTBearer class to Verify the Authorization header
class JWTBearer(HTTPBearer):
    """JWTBearer class to Verify the Authorization header"""

    def __init__(self, auto_error: bool = False, **kwargs):
        """
        Initializes a new instance of the JWTBearer class.

        Args:
            auto_error (bool, optional): Determines whether to automatically
            raise an error when the token is invalid.
                Defaults to False.
        """
        super().__init__(auto_error=auto_error, **kwargs)
        logger.info("JWTBearer initialized")

    async def __call__(
        self, request: Request
    ) -> Optional[HTTPAuthorizationCredentials]:
        """Verify and extract JWT token"""
        try:
            logger.info("Starting JWT validation")

            # Try token from cookie
            # auth_token = request.cookies.get("Authorization")
            auth_token= "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Il9GcnhmUVZTbFBVbHZHWjVIdmRrTlN1Z1FzeXJkbjB1cWxXSkdJTVlfWXcifQ.eyJ0eXBlIjoiYXQiLCJjbGllbnRJZCI6IjEyNmJjNDU0LTJjZDYtNDlmZS05Y2RmLTJjZjdlZjNhOWNlNyIsImlkcCI6Im1zZnQiLCJpc3MiOiJodHRwczovL2Rldi5saW9uaXMuYWkiLCJyb2xlcyI6WyJzdXBlcl91c2VyIl0sImp0aSI6InNvVDRtYWNBeUciLCJVc2VySW5mbyI6eyJpZCI6IjkxZTVmOTIzLWIzODctNGU1Yi04Y2VkLTgzODk1ZjUzMjRiOSIsImVtYWlsIjoic2hpYmF2aWtAcHVibGljaXNncm91cGUubmV0IiwiZGlzcGxheU5hbWUiOiJTaGl0YWwgQmF2aWthciJ9LCJhcHBLZXkiOiJza19kMjE0ODAwMmM2OGNjIiwiYXBwSWQiOiIyM2I2MWU3NS0yNGNhLTRjZDAtOTk5OS0wMTY1NmY1YTZhNzEiLCJzZXJ2aWNlcyI6WyJ0YXhvbm9teSIsInByb2plY3RzIiwibGxtIiwiYXNzZXQiLCJub3RpZmljYXRpb24iLCJhdWRpZW5jZSIsImRhdGEiLCJhc3NldC1hbmFseXplciIsImJvZGhpIiwiaW52ZW50b3J5Iiwic3RhdGUiXSwiYXBwTmFtZSI6IkFQSS1BR0VOVC1XT1JLQkVOQ0giLCJpbmR1c3RyeSI6IjM2ODgzOTkzLTNkNmEtNDhjNC05YzVjLWVmMTg2ZDQ5ZmFhOCIsImlhdCI6MTc0OTU1NzMxOCwiZXhwIjoxNzQ5NTY0NTE4fQ.OPxjh2rTTMjIVohpv2l_TRG1fpL3HwrvsKcerb3dGf3unKind65vF_kO8Z7lVv3Asq-blCQeqaGCc3DrQKfeCiaf4FEMFDY4InIzs4Dx6anDjskHe2vcqW6DXXnz2wKoA6whsSDoTzxy0k_wWG0S3MEKE6ZJnpmsvIIYIbRAA1UKkNvYZuGMUjqp9tGxnCxdCQFF2GmcGPbbhEbipEwVifyoNBgbY1UWEOapxlSbznMLfaW2H3BomNNqMZOFGv4L_u7M3HZ7Za3ABbIZ-owuhBChfMrsOmZGXKHOc1yHdpBe1GEpxtIaTy294zlUa-uPOERONGlRy8aZatAlvaZvUw"
            # Fallback to header
            if not auth_token:
                # If not in cookie, try Authorization header
                logger.info("No token in cookie, checking Authorization header")
                credentials = await super().__call__(request)
                if credentials.scheme != "Bearer":
                    logger.error("Invalid authentication scheme")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid authentication scheme.",
                    )
                auth_token = credentials.credentials

            if not auth_token:
                logger.error("No token found")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authorization code",
                )
            # Verify the token
            try:
                payload = jwt.decode(
                    auth_token,
                    settings.enterprise_auth_public_key,
                    algorithms=[settings.encryption_algorithm],
                )
            except jwt.ExpiredSignatureError as exc:
                logger.warning("Token has expired")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                ) from exc
            except jwt.InvalidTokenError as e:
                logger.warning(f"Token is invalid: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token: {str(e)}",
                ) from e

            # Check user info
            user_info = payload.get("UserInfo")
            if not user_info:
                logger.error("No user info in token")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing user info",
                )

            logger.info(f"Token verified. User info: {user_info}")
            request.state.token = auth_token
            request.state.user_info = user_info
            return credentials if "credentials" in locals() else None

        except HTTPException:
            raise  # Re-raise FastAPI exceptions
        except Exception as e:
            logger.error(f"Unexpected error during token validation: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Unhandled JWT validation error: {str(e)}",
            ) from e


# JWTMiddleware class which invokes the middleware
class JWTMiddleware(BaseHTTPMiddleware):
    """JWT Middleware for validating tokens"""

    def __init__(self, app):
        super().__init__(app)
        logger.info("JWT Middleware initialized")

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process each request through JWT validation"""
        logger.info(f"JWT Middleware processing request: {request.url.path}")
        try:
            skip_paths = [
                f"{settings.base_path}{suffix}" for suffix in settings.skip_paths
            ]
            # Skip if path is excluded
            if request.url.path in skip_paths:
                logger.info(f"Skipping JWT validation for path: {request.url.path}")
                return await call_next(request)

            # Validate with JWTBearer
            jwt_bearer = JWTBearer(auto_error=True)
            await jwt_bearer(request)

            logger.info("JWT validation passed")

            # Inject Authorization header if missing
            if "Authorization" not in request.headers:
                token = request.state.token
                headers = dict(request.headers)
                headers["Authorization"] = f"Bearer {token}"
                request._headers = headers  # pylint: disable=protected-access

            return await call_next(request)

        except HTTPException as exc:
            logger.error(f"JWT validation failed: {exc.detail}")
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
            )
        except RequestError as e:
            logger.error(f"Request error in middleware: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error"},
            )
