# type: ignore
# pylint: disable=redefined-outer-name
"""
This module contains tests for the FastAPI application setup and its components.
"""

import asyncio
import json
from typing import Any, Dict
from unittest.mock import MagicMock, patch, AsyncMock

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.main import (
    create_application,
    start,
    custom_generate_unique_id,
    _configure_middleware,
    _configure_openapi,
    _register_exception_handlers,
    app as main_app,
)
from src.core.config import settings


@pytest.fixture
def mcp_server() -> MagicMock:
    """Fixture for creating a mock MCP server."""
    server = MagicMock()
    server.create_initialization_options = MagicMock(return_value={})
    server.run = AsyncMock()
    return server


@pytest.fixture
def mock_app() -> MagicMock:
    """Fixture for creating a mock FastAPI app."""
    app = MagicMock()
    app.openapi_schema = None
    app.routes = []
    app.exception_handlers = {}
    return app


class TestFastAPIApp:
    """Tests for the FastAPI application setup."""

    def test_custom_generate_unique_id_with_tags(self) -> None:
        """Test custom_generate_unique_id function with tags."""
        mock_route = MagicMock()
        mock_route.tags = ["test_tag"]
        mock_route.name = "test_route"

        result = custom_generate_unique_id(mock_route)
        assert result == "test_tag-test_route"

    def test_custom_generate_unique_id_without_tags(self) -> None:
        """Test custom_generate_unique_id function without tags."""
        mock_route = MagicMock()
        mock_route.tags = None
        mock_route.name = "test_route"

        result = custom_generate_unique_id(mock_route)
        assert result == "test_route"

    @patch("src.main.create_mcp_server")
    def test_create_application(self, mock_create_mcp_server: Any) -> None:
        """Test the create_application function."""
        mock_mcp_instance = MagicMock()
        mock_mcp_app = MagicMock()
        mock_mcp_instance.http_app.return_value = mock_mcp_app
        mock_create_mcp_server.return_value = mock_mcp_instance

        app = create_application()

        mock_create_mcp_server.assert_called_once_with("TEMP")
        mock_mcp_instance.http_app.assert_called_once_with(path="/stream")
        assert app is not None

    @patch("src.main.create_mcp_server")
    def test_cors_middleware_not_added_when_no_origins(
        self, mock_create_mcp_server: Any
    ) -> None:
        """Test CORS middleware is not added when no origins are configured."""
        mock_mcp_instance = MagicMock()
        mock_mcp_app = MagicMock()
        mock_mcp_instance.http_app.return_value = mock_mcp_app
        mock_create_mcp_server.return_value = mock_mcp_instance

        with patch("src.core.config.settings.backend_cors_origins", []):
            app = create_application()
            assert app is not None

    @patch("src.main.create_mcp_server")
    def test_cors_middleware_added_when_origins_configured(
        self, mock_create_mcp_server: Any
    ) -> None:
        """Test CORS middleware is added when origins are configured."""
        mock_mcp_instance = MagicMock()
        mock_mcp_app = MagicMock()
        mock_mcp_instance.http_app.return_value = mock_mcp_app
        mock_create_mcp_server.return_value = mock_mcp_instance

        with patch(
            "src.core.config.settings.backend_cors_origins", ["http://localhost:8000"]
        ):
            app = create_application()
            assert app is not None

    def test_configure_openapi_function(self, mock_app: Any) -> None:
        """Test the _configure_openapi function and custom OpenAPI generation."""
        with patch("src.main.get_openapi") as mock_get_openapi:
            mock_openapi_schema: Dict[str, Any] = {
                "info": {},
                "paths": {},
            }
            mock_get_openapi.return_value = mock_openapi_schema

            _configure_openapi(mock_app)

            assert hasattr(mock_app, "openapi")

            result = mock_app.openapi()

            assert "x-logo" in result["info"]
            assert (
                result["info"]["x-logo"]["url"]
                == "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
            )

            mock_app.openapi_schema = result
            result2 = mock_app.openapi()
            assert result2 == result

    def test_configure_openapi_with_existing_schema(self, mock_app: Any) -> None:
        """Test _configure_openapi when schema already exists."""
        existing_schema = {"info": {"title": "Test"}}
        mock_app.openapi_schema = existing_schema

        _configure_openapi(mock_app)

        result = mock_app.openapi()
        assert result == existing_schema

    def test_register_exception_handlers(self, mock_app: Any) -> None:
        """Test the _register_exception_handlers function."""
        _register_exception_handlers(mock_app)

        assert mock_app.exception_handler.call_count == 3

    def test_validation_exception_handler_direct(self) -> None:
        """Test RequestValidationError exception handler directly."""
        app = FastAPI()
        _register_exception_handlers(app)

        handler = app.exception_handlers[RequestValidationError]

        mock_request = MagicMock()
        mock_request.url = "http://test.com/test"
        mock_exc = RequestValidationError(
            [{"type": "missing", "loc": ["field"], "msg": "field required"}]
        )

        with patch("src.main.logger") as mock_logger:
            response: JSONResponse = asyncio.run(handler(mock_request, mock_exc))

            assert response.status_code == 400
            content = json.loads(response.body.decode())
            assert content["error"] == "Bad Request"
            assert content["detail"] == "Invalid request data"
            assert "errors" in content

            mock_logger.warning.assert_called_once()

    def test_value_error_exception_handler_direct(self) -> None:
        """Test ValueError exception handler directly."""
        app = FastAPI()
        _register_exception_handlers(app)

        handler = app.exception_handlers[ValueError]

        mock_request = MagicMock()
        mock_request.url = "http://test.com/test"
        mock_exc = ValueError("Test error")

        with patch("src.main.logger") as mock_logger:
            response: JSONResponse = asyncio.run(handler(mock_request, mock_exc))

            assert response.status_code == 400
            content = json.loads(response.body.decode())
            assert content["error"] == "Bad Request"
            assert content["detail"] == "Test error"

            mock_logger.error.assert_called_once()

    def test_http_exception_handler_direct(self) -> None:
        """Test HTTPException exception handler directly."""
        app = FastAPI()
        _register_exception_handlers(app)

        handler = app.exception_handlers[HTTPException]

        mock_request = MagicMock()
        mock_request.url = "http://test.com/test"
        mock_exc = HTTPException(status_code=404, detail="Not found")

        with patch("src.main.logger") as mock_logger:
            response: JSONResponse = asyncio.run(handler(mock_request, mock_exc))

            assert response.status_code == 404
            content = json.loads(response.body.decode())
            assert content["error"] == "Not found"

            mock_logger.warning.assert_called_once()

    @patch("uvicorn.run")
    @patch("src.main.logger")
    def test_start_function(self, mock_logger: Any, mock_uvicorn_run: Any) -> None:
        """Test the start function."""
        start()

        mock_logger.info.assert_called_with("Starting up TEMP MCP Server...")
        mock_uvicorn_run.assert_called_once_with(
            "src.main:app",
            host=settings.host,
            port=settings.port,
            reload=settings.reload,
        )

    def test_configure_middleware_function(self) -> None:
        """Test the _configure_middleware function."""
        mock_app = MagicMock()

        with patch(
            "src.core.config.settings.backend_cors_origins", ["http://localhost:8000"]
        ):
            _configure_middleware(mock_app)

            assert mock_app.add_middleware.call_count == 2

    def test_configure_middleware_no_cors(self) -> None:
        """Test _configure_middleware without CORS origins."""
        mock_app = MagicMock()

        with patch("src.core.config.settings.backend_cors_origins", []):
            _configure_middleware(mock_app)

            assert mock_app.add_middleware.call_count == 1

    def test_app_instance_exists(self) -> None:
        """Test that the app instance is created."""
        assert main_app is not None
        assert hasattr(main_app, "title")


if __name__ == "__main__":
    pytest.main([__file__])
