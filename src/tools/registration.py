"""This module handles the registration of tools with the MCP server."""

from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Request

from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers
from fastapi import Request, Depends
from pydantic.error_wrappers import ValidationError



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

from src.tools.impl.CRUD_tools import MockInventoryTool

from src.schemas.inventory import NoInput


def register_tools(mcp: FastMCP[Any]) -> None:

    inventory_tool = MockInventoryTool()
    logger.info("Starting tool registration...")
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
        logger.info(f"Request headers: {request_headers}")
        logger.info(f"All header keys: {list(request_headers.keys())}")

       
        return await execute_tool(
            LoadInventoryTool(),
            input_data,
            "load_inventory",
            request_headers=request_headers,
        )

   
    
    @mcp.tool()
    async def list_inventory(input_data: NoInput) -> List[Dict]:
        logger.info("list_inventory called.")
        try:
            return await inventory_tool.list_items()
        except ValidationError as e:
            logger.error(f"Validation error in list_inventory: {e.json()}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in list_inventory: {str(e)}")
            raise

    @mcp.tool()
    async def add_inventory_item(input_data: Dict) -> Dict:
        return await inventory_tool.add_item(input_data)

    @mcp.tool()
    async def update_inventory_item(input_data: Dict) -> Dict:
        item_id = input_data.get("item_id")
        item = input_data.get("item")
        result = await inventory_tool.update_item(item_id, item)
        if result is None:
            raise ValueError("Item not found")
        return result

    @mcp.tool()
    async def delete_inventory_item(input_data: Dict) -> Dict:
        item_id = input_data.get("item_id")
        result = await inventory_tool.delete_item(item_id)
        if result is None:
            raise ValueError("Item not found")
        return result

    logger.info("Finished tool registration.")

async def execute_tool(
    tool_instance: Any,
    input_data: Any,
    tool_name: str,
    request_headers: Optional[Dict[str, str]] = None,
) -> List[Dict[str, str]]:
    logger.info(f"Executing {tool_name} with input: {input_data}")

    
    if request_headers:
        return await tool_instance.execute(input_data, request_headers)

    return await tool_instance.execute(input_data)
