"""Example tool implementation."""

from typing import Any, Dict, Union
import json
import httpx

from src.schemas.example_tool import ExampleToolInput
from src.tools.meta.base import BaseTool
from src.utils.auth import get_authorization_token
from src.utils.ent_headers import add_ent_headers
from src.core.config import settings
from src.core.logger import logger


class ExampleTool(BaseTool[ExampleToolInput]):
    """Example implementation of a tool that uses a CoreAI service

    Attributes:
        name (str): The name of the tool.
        description (str): A description of the tool's functionality.
        input_schema (Dict[str, Any]): The schema for input data required by the tool.
    """

    @property
    def name(self) -> str:
        """Get the name of the tool.

        Returns:
            str: The name of the tool.
        """
        return "example_tool"

    @property
    def description(self) -> str:
        """Get the description of the tool.

        Returns:
            str: A detailed description of the tool's capabilities.
        """
        # This is the description used for the agent to determine when the tool call is needed
        return (
            "An example tool description. "
            "Describe how and when the tool should be used. "
        )

    @property
    def input_schema(self) -> Dict[str, Any]:
        # Schema generated from the tool's input schema model
        schema = ExampleToolInput.model_json_schema()
        return {
            "type": "object",
            "properties": schema.get("properties", {}),
            "required": schema.get("required", []),
            "additionalProperties": False,
        }

    async def execute(
        self, input_data: Union[ExampleToolInput, Dict[str, Any]], *args: Any
    ) -> Any:
        """Execute the tool."""
        # Validate input data matches input schema
        if isinstance(input_data, ExampleToolInput):
            data = input_data.model_dump()
        else:
            raise ValueError("Invalid input data.")

        request_headers = args[0] if args else {}

        # Call the tool with the input data
        # This tool also requires request headers to execute
        return await self._call_tool(data, request_headers)

    async def _call_tool(
        self, input_data: Dict[str, Any], request_headers: Dict[str, str]
    ) -> str:
        """
        The tool call implementation.

        This example tool performs an API call to an example CoreAI service.
        """
        try:
            async with httpx.AsyncClient() as client:
                url = f"{settings.enterprise_base_url}/example-coreai-service"  # Example url

                # Extract auth token from request headers
                # auth_token = get_authorization_token(request_headers)
                auth_token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Il9GcnhmUVZTbFBVbHZHWjVIdmRrTlN1Z1FzeXJkbjB1cWxXSkdJTVlfWXcifQ.eyJ0eXBlIjoiYXQiLCJjbGllbnRJZCI6IjEyNmJjNDU0LTJjZDYtNDlmZS05Y2RmLTJjZjdlZjNhOWNlNyIsImlkcCI6Im1zZnQiLCJpc3MiOiJodHRwczovL2Rldi5saW9uaXMuYWkiLCJyb2xlcyI6WyJzdXBlcl91c2VyIl0sImp0aSI6IkN0dlYwajY4M2IiLCJVc2VySW5mbyI6eyJpZCI6IjkxZTVmOTIzLWIzODctNGU1Yi04Y2VkLTgzODk1ZjUzMjRiOSIsImVtYWlsIjoic2hpYmF2aWtAcHVibGljaXNncm91cGUubmV0IiwiZGlzcGxheU5hbWUiOiJTaGl0YWwgQmF2aWthciJ9LCJhcHBLZXkiOiJza19kMjE0ODAwMmM2OGNjIiwiYXBwSWQiOiIyM2I2MWU3NS0yNGNhLTRjZDAtOTk5OS0wMTY1NmY1YTZhNzEiLCJzZXJ2aWNlcyI6WyJ0YXhvbm9teSIsInByb2plY3RzIiwibGxtIiwiYXNzZXQiLCJub3RpZmljYXRpb24iLCJhdWRpZW5jZSIsImRhdGEiLCJhc3NldC1hbmFseXplciIsImJvZGhpIiwiaW52ZW50b3J5Iiwic3RhdGUiXSwiYXBwTmFtZSI6IkFQSS1BR0VOVC1XT1JLQkVOQ0giLCJpbmR1c3RyeSI6IjM2ODgzOTkzLTNkNmEtNDhjNC05YzVjLWVmMTg2ZDQ5ZmFhOCIsImlhdCI6MTc0OTY0MDQ2MSwiZXhwIjoxNzQ5NjQ3NjYxfQ.yvnmLQHmDa4GRHbOm5I7k3T_pK93OpYK5XmgscUeMcKL6PMJOwIiSjm6mFaPlI8Eo9-M-KTQ6goHmoxVcslWOyR1t8B_AQSiWixCRCNxZoCTxpuZNUsV-e471c7-Y3GQqs8g0nKUeFlClY2cPWjZaXQciWGfgANdP4z376_Ok5YG2CVGjH2IdkMu9eXyIjjputEqhWXf2Ia0mt20faRwFHXsu3G_UjoJCnCATaPFd-8ootSeOEFalHnO_Gk213cJQk5ItbrbH6qOI4MDWBSNoAyKJkBnbaORaThOynVFJwtVs033GQPVkIC1akQz8N1DOI9vdOTHzZTLUymA3eiVzg"
                
                default_headers = {
                    "Authorization": f"Bearer {auth_token}",
                    "Content-Type": "application/json",
                }
                # Add enterprise headers
                headers = add_ent_headers(default_headers, request_headers)

                # Add the required params for the call
                params = {
                    "query": input_data["query"],
                    "workspace_id": input_data["workspace_id"],
                }
                # Add the optional params for the call if they're provided in the input data
                if (
                    "workflow_id" in input_data
                    and input_data["workflow_id"] is not None
                ):
                    params["workflow_id"] = input_data["workflow_id"]

                response = await client.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=30.0,
                )

                logger.info(f"Example API response status: {response.status_code}")

                if response.status_code != 200:
                    error_text = response.text
                    logger.error(f"Example API error: {error_text}")
                    return json.dumps({"error": f"Example API error: {error_text}"})

                try:
                    data = response.json()
                except (TypeError, AttributeError, ValueError) as e:
                    logger.error(f"Error parsing Example API response: {str(e)}")
                    raise

                result = {
                    "function": self.name,
                    "data": {"results": data, "query": input_data["query"]},
                }
                return json.dumps(result)

        except Exception as e:  # pylint: disable=broad-exception-caught
            error_msg = f"Exception during {self.name} tool call"
            logger.error(f"{error_msg}: {str(e)}")
            return json.dumps({"error": error_msg})

    def to_mcp_schema(self) -> Dict[str, Any]:
        """Return the MCP-compatible schema for this tool.

        Returns:
            Dict[str, Any]: A dictionary representing the MCP-compatible schema.
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.input_schema,
        }
