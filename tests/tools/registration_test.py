# pylint: disable=redefined-outer-name
"""Test the registration of tools in the FastMCP instance."""

import json
from typing import Iterable, Dict, Any
from unittest.mock import AsyncMock
import pytest

from mcp.server.fastmcp import FastMCP

from src.tools.registration import register_tools
from src.tools.registration import execute_tool


@pytest.fixture
def mock_mcp() -> FastMCP:
    """
    Fixture to create a mock FastMCP instance.
    Returns:
        FastMCP: A mocked instance of FastMCP.
    """
    return FastMCP()


@pytest.fixture
def setup_registration(mock_mcp: FastMCP) -> None:
    """
    Fixture to setup the registration of tools.
    Args:
        mock_mcp (FastMCP): The mocked FastMCP instance.
    """
    register_tools(mock_mcp)  # type: ignore


@pytest.mark.asyncio
async def test_get_app_version(
    setup_registration: None,  # pylint: disable=unused-argument
    mock_mcp: FastMCP,
) -> None:
    """
    Test the get_app_version resource.
    Args:
        setup_registration (None): Fixture to setup tool registration.
        mock_mcp (FastMCP): The mocked FastMCP instance.
    Asserts:
        - The resource contents are not None.
        - The parsed content matches expected values.
    """
    resource_contents: Iterable[Any] = await mock_mcp.read_resource(
        "config://app-version"
    )

    assert resource_contents is not None
    for resource_content in resource_contents:
        content_dict: Dict[str, Any] = json.loads(resource_content.content)
        assert content_dict["name"] == "TEMP MCP Server"
        assert content_dict["version"] == "0.1.0"
        assert content_dict["commit"] == ""
        assert content_dict["branch"] == ""
        assert content_dict["buildTime"] == ""


@pytest.mark.asyncio
async def test_execute_tool_with_auth() -> None:
    """Test execute_tool function with authentication required."""
    mock_tool = AsyncMock()
    mock_tool.execute = AsyncMock(return_value=[{"result": "auth data"}])

    mock_input = {"query": "test"}
    mock_headers = {"Authorization": "Bearer token"}

    result = await execute_tool(
        tool_instance=mock_tool,
        input_data=mock_input,
        tool_name="test_tool",
        request_headers=mock_headers,
    )

    assert result == [{"result": "auth data"}]
    mock_tool.execute.assert_called_once_with(
        mock_input, {"Authorization": "Bearer token"}
    )


@pytest.mark.asyncio
async def test_execute_tool_without_auth() -> None:
    """Test execute_tool function without authentication required."""
    mock_tool = AsyncMock()
    mock_tool.execute = AsyncMock(return_value=[{"result": "no auth data"}])

    mock_input = {"query": "test"}

    result = await execute_tool(
        tool_instance=mock_tool,
        input_data=mock_input,
        tool_name="test_tool",
    )

    assert result == [{"result": "no auth data"}]
    mock_tool.execute.assert_called_once_with(mock_input)
