# pylint: disable=redefined-outer-name
"""TEMP MCP Server Main Application"""

from typing import Any, Dict

import uvicorn
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from src.core.config import settings
from src.core.logger import logger
from src.middleware.jwt_bearer import JWTMiddleware
from src.server.server import create_mcp_server
import traceback

    
def custom_generate_unique_id(route: APIRoute) -> str:
    """Generate unique operation ID for OpenAPI documentation.

    Args:
        route: The API route to generate ID for

    Returns:
        Unique string identifier for the route
    """
    if route.tags:
        return f"{route.tags[0]}-{route.name}"
    return route.name


def create_application() -> FastAPI:
    """Factory function to create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    # Create MCP server app 
    # MCP Model Context Protocol is an open protocol that standardizes how applications provide context to LLMs. 
    mcp = create_mcp_server("TEMP")
    mcp_app = mcp.http_app()  

    # Create FastAPI application
    app = FastAPI(
        title=settings.title,
        root_path=settings.base_path,
        version=settings.app["version"],
        description=settings.app["description"],
        generate_unique_id_function=custom_generate_unique_id,
        openapi_url="/openapi.json",
        lifespan=mcp_app.lifespan,
    )

    # Mount the FastMCP application at the root path
    app.mount("/mcp", mcp_app)

    for route in app.routes:
        print("ROUTE:", route.path)
    _configure_middleware(app)
    _configure_openapi(app)
    _register_exception_handlers(app)

    return app


def _configure_middleware(app: FastAPI) -> None:
    """Configure application middleware.

    Args:
        app: FastAPI application instance
        mcp_instance: MCP server instance
    """
    # Note: the order that middleware gets added is important
    # The execution order is reversed so that last added to the stack is first executed

    # Auth middleware
    # app.add_middleware(JWTMiddleware)

    # # CORS middleware
    # if settings.backend_cors_origins:
    #     app.add_middleware(
    #         CORSMiddleware,
    #         allow_origins=[str(origin) for origin in settings.backend_cors_origins],
    #         allow_credentials=True,
    #         allow_methods=["*"],
    #         allow_headers=["*"],
    #         expose_headers=["Content-Type", "Authorization"],
    #     )


def _configure_openapi(app: FastAPI) -> None:
    """Configure custom OpenAPI schema for docs.

    Args:
        app: FastAPI application instance
    """

    def custom_openapi() -> Dict[str, Any]:
        """Generate custom OpenAPI schema"""
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=settings.title,
            version=settings.app["version"],
            description=settings.description,
            routes=app.routes,
            servers=[
                {
                    "url": f"{settings.hostname}{settings.base_path}",
                    "description": "Server URL",
                },
            ],
        )
        openapi_schema["info"]["x-logo"] = {
            "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
        }
        app.openapi_schema = openapi_schema
        return app.openapi_schema

    app.openapi = custom_openapi  # type: ignore[method-assign]



def _register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

def _register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers.

    Args:
        app: FastAPI application instance
    """

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        """Handle request validation errors"""
        logger.warning(f"Validation error for {request.url}: {exc.errors()}")
        return JSONResponse(
            content={
                "error": "Bad Request",
                "detail": "Invalid request data",
                "errors": exc.errors(),
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    @app.exception_handler(ValueError)
    async def value_error_exception_handler(
        request: Request,
        exc: ValueError,
    ) -> JSONResponse:
        """Handle ValueError exceptions"""
        logger.error(f"ValueError for {request.url}: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Bad Request", "detail": str(exc)},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(
        request: Request,
        exc: HTTPException,
    ) -> JSONResponse:
        """Handle HTTP exceptions"""
        logger.warning(f"HTTP {exc.status_code} for {request.url}: {exc.detail}")
        return JSONResponse(
            content={"error": exc.detail},
            status_code=exc.status_code,
        )


app = create_application()


def start() -> None:
    """Start the server with uvicorn"""

    logger.info("Starting up TEMP MCP Server...")

    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
    )


if __name__ == "__main__":
    start()