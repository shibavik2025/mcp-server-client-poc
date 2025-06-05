"""
This module contains tests for the MCP server functionality.
"""

from unittest.mock import MagicMock, patch
import pytest

from src.server.server import create_mcp_server


class TestMCPServer:
    """Tests for the MCP server functionality."""

    def test_create_server_success(self) -> None:
        """Test successful server creation and configuration."""
        with patch("src.server.server.FastMCP") as mock_fast_mcp:
            mock_instance = MagicMock()
            mock_fast_mcp.return_value = mock_instance

            with patch("src.server.server.register_tools") as mock_register_tools:
                mcp = create_mcp_server("TEMP")

                mock_fast_mcp.assert_called_once_with("TEMP")
                mock_register_tools.assert_called_once_with(mock_instance)
                assert mcp == mock_instance

    def test_create_server_exception_during_registration(self) -> None:
        """Test server creation when tool registration fails."""
        with patch("src.server.server.FastMCP") as mock_fast_mcp:
            mock_instance = MagicMock()
            mock_fast_mcp.return_value = mock_instance

            with patch(
                "src.server.server.register_tools",
                side_effect=Exception("Registration failed"),
            ):
                with patch("src.server.server.logger") as mock_logger:
                    with pytest.raises(Exception) as exc_info:
                        create_mcp_server("TestServer")

                    assert (
                        "Failed to create MCP server 'TestServer': Registration failed"
                        in str(exc_info.value)
                    )

                    mock_logger.error.assert_called_once_with(
                        "Failed to create MCP server 'TestServer': Registration failed"
                    )

    def test_create_server_exception_during_initialization(self) -> None:
        """Test server creation when FastMCP initialization fails."""
        with patch("src.server.server.FastMCP", side_effect=Exception("Init failed")):
            with patch("src.server.server.logger") as mock_logger:
                with pytest.raises(Exception) as exc_info:
                    create_mcp_server("TestServer")

                assert "Failed to create MCP server 'TestServer': Init failed" in str(
                    exc_info.value
                )

                mock_logger.error.assert_called_once_with(
                    "Failed to create MCP server 'TestServer': Init failed"
                )
