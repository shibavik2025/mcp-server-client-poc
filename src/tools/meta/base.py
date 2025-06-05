"""Base definitions for MCP-compatible tools.

This module defines the abstract base class that all tools must implement
to be compatible with the MCP server.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, TypeVar, Union, Generic

T = TypeVar("T")


class BaseTool(Generic[T], ABC):
    """Base class for all MCP tools.

    This is an abstract base class that defines the interface that all tools
    must implement to be compatible with the MCP server.

    Args:
        Generic[T]: Enables the class to work with any input type T
        ABC: Marks this class as an abstract base class
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the tool."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Return the description of the tool."""

    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """Return the JSON schema for the tool input."""

    @abstractmethod
    async def execute(self, input_data: Union[T, Dict[str, Any]], *args: Any) -> Any:
        """Execute the tool with the given input."""

    def to_mcp_schema(self) -> Dict[str, Any]:
        """Convert the tool to MCP schema format."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.input_schema,
        }
