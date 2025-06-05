"""MCP Server implementation using FastMCP."""

from typing import Any

from fastmcp import FastMCP

from src.core.logger import logger
from src.tools.registration import register_tools


def create_mcp_server(server_name: str) -> FastMCP[Any]:
    """Create and configure the MCP server with all registered resources and tools.

    Args:
        server_name: Custom name for the server.

    Returns:
        Configured FastMCP server instance ready for use

    Raises:
        Exception: If tool registration fails
    """
    name = server_name

    try:
        mcp: FastMCP[Any] = FastMCP(name)
        register_tools(mcp)
        return mcp
    except Exception as e:  # pylint: disable=broad-exception-caught
        error_msg = f"Failed to create MCP server '{name}': {e}"
        logger.error(error_msg)
        raise Exception(error_msg) from e  # pylint: disable=broad-exception-raised
