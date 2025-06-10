"""This module handles the registration of tools with the MCP server."""

from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Request

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers
from fastapi import Request, Depends



from src.schemas.example_tool import ExampleToolInput
from src.tools.impl.example_tool import ExampleTool
from src.core.config import settings
from src.schemas.version import VersionResponse
from src.core.logger import logger

from src.tools.impl.inventory_tools import (
    LoadInventoryTool,
    ForecastedDemandTool,
    ExpectedInventoryTool,
    PromotionCandidateTool,
)
from src.schemas.inventory import NoInput


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
    
    @mcp.tool()
    async def load_inventory(input_data: NoInput) -> List[Dict[str, str]]:
        request_headers = get_http_headers()
        return await execute_tool(
            LoadInventoryTool(),
            input_data,
            "load_inventory",
            request_headers=request_headers,
        )
       



    @mcp.tool()
    async def forecasted_demand(input_data: NoInput) -> List[Dict[str, str]]:
        request_headers = get_http_headers()
        session_id = request_headers.get("x-session-id")
        logger.info(f"Received x-session-id: {session_id}")

        if not session_id:
            raise ValueError("Missing x-session-id in headers")

        return await execute_tool(
            ForecastedDemandTool(),
            input_data,
            "forecasted_demand",
            {"x-session-id": session_id}
        )

    @mcp.tool()
    async def expected_inventory(input_data: NoInput) -> List[Dict[str, str]]:
        return await execute_tool(ExpectedInventoryTool(), input_data, "expected_inventory")

    @mcp.tool()
    async def promotion_candidates(input_data: NoInput) -> List[Dict[str, str]]:
        return await execute_tool(PromotionCandidateTool(), input_data, "promotion_candidates")

async def execute_tool(
    tool_instance: Any,
    input_data: Any,
    tool_name: str,
    request_headers: Optional[Dict[str, str]] = None,
) -> List[Dict[str, str]]:
    logger.info(f"Executing {tool_name} with input: {input_data}")

    session_id = None
    if request_headers:
        session_id = request_headers.get("x-session-id") or request_headers.get("session_id")
        logger.info(f"Extracted session_id: {session_id}")
        return await tool_instance.execute(input_data, request_headers)

    return await tool_instance.execute(input_data)
