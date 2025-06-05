"""This module handles the registration of tools with the MCP server."""

from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers

from src.schemas.example_tool import ExampleToolInput
from src.tools.impl.example_tool import ExampleTool
from src.core.config import settings
from src.schemas.version import VersionResponse
from src.core.logger import logger


def register_tools(mcp: FastMCP[Any]) -> None:
    """Register tools with the MCP server."""

    @mcp.resource("config://app-version")
    def get_app_version() -> VersionResponse:
        """Returns the application version details."""
        return VersionResponse(
            name=settings.app["name"],
            version=settings.app["version"],
            commit=settings.commit_id,
            branch=settings.branch_name,
            buildTime=settings.build_time,
            tag=settings.tag,
        )

    @mcp.tool()
    async def example_tool(
        input_data: ExampleToolInput,
    ) -> List[Dict[str, str]]:
        """Example tool that uses uses a CoreAI service and requires request headers."""
        request_headers = get_http_headers()
        return await execute_tool(
            tool_instance=ExampleTool(),
            input_data=input_data,
            tool_name="example_tool",
            request_headers=request_headers,
        )


async def execute_tool(
    tool_instance: Any,
    input_data: Any,
    tool_name: str,
    request_headers: Optional[Dict[str, str]] = None,
) -> List[Dict[str, str]]:
    """
    Execute a tool with common logging and header extraction logic.

    Args:
        tool_instance: The tool instance to execute
        input_data: Input data for the tool
        tool_name: Name of the tool for logging
        requires_headers: Optional request headers

    Returns:
        List of dictionaries containing tool execution results
    """
    logger.info(f"Executing {tool_name} with input: {input_data}")

    if request_headers:
        return await tool_instance.execute(input_data, request_headers)

    return await tool_instance.execute(input_data)
