"""Tests for BaseTool."""

from typing import Dict, Any, Union
import pytest

from src.tools.meta.base import BaseTool


class DummyTool(BaseTool[Any]):
    """A concrete implementation of BaseTool for testing purposes."""

    @property
    def name(self) -> str:
        return "dummy_tool"

    @property
    def description(self) -> str:
        return "A dummy tool for testing"

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "test_param": {"type": "string", "description": "A test parameter"}
            },
        }

    async def execute(self, input_data: Union[str, Dict[str, Any]], *args: Any) -> Any:
        return {"result": "dummy_result"}


class TestBaseTool:
    """Test suite for the BaseTool abstract base class."""

    def test_abstract_methods_exist(self) -> None:
        """Test that BaseTool has the expected abstract methods."""
        assert hasattr(BaseTool, "name")
        assert hasattr(BaseTool, "description")
        assert hasattr(BaseTool, "input_schema")
        assert hasattr(BaseTool, "execute")

    def test_to_mcp_schema(self) -> None:
        """Test the to_mcp_schema method which is currently not covered."""
        tool = DummyTool()

        schema = tool.to_mcp_schema()

        assert schema["name"] == "dummy_tool"
        assert schema["description"] == "A dummy tool for testing"
        assert schema["parameters"] == {
            "type": "object",
            "properties": {
                "test_param": {"type": "string", "description": "A test parameter"}
            },
        }

    def test_concrete_implementation(self) -> None:
        """Test that a concrete implementation works as expected."""
        tool = DummyTool()
        assert tool.name == "dummy_tool"
        assert tool.description == "A dummy tool for testing"
        assert "type" in tool.input_schema
        assert "properties" in tool.input_schema

    @pytest.mark.asyncio
    async def test_execute_method(self) -> None:
        """Test the execute method of the concrete implementation."""
        tool = DummyTool()
        result = await tool.execute({"test_param": "value"})
        assert result == {"result": "dummy_result"}
