import asyncio
from fastmcp import Client
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve the MCP URL from environment variables
mcp_url = os.getenv("MCP_URL")

client = Client(mcp_url)

async def main():
    # Connection is established here
    async with client:
        print(f"Client connected: {client.is_connected()}")

        # Make MCP calls within the context
        tools = await client.list_tools()
        tool_names = [tool.name for tool in tools]
        print("Available tool names:")
        for name in tool_names:
            print(f"- {name}")


        #  # Call the list_inventory tool
        result = await client.call_tool("list_inventory_json", {"input_data": {}})
        print("list_inventory result:", result)
    # Connection is closed automatically here
    print(f"Client connected: {client.is_connected()}")

if __name__ == "__main__":
    asyncio.run(main())







