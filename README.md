
# MCP Server Template

This project serves as a Python MCP Server template designed to accelerate the development of other Python MCP Servers. Contributions are welcome, and you are encouraged to improve any aspect of the code.

## Resources
- [Model Context Protocol (MCP) Guide](https://publiciscoreai.atlassian.net/wiki/spaces/COREAI/pages/64275680/Model+Context+Protocol+E2E+Guide)
- [FastMCP Documentation](https://gofastmcp.com/getting-started/welcome)
- [TypeScript Library for writing MCP Clients](https://github.com/modelcontextprotocol/typescript-sdk?tab=readme-ov-file#writing-mcp-clients)

## Getting Started

This MCP Server template uses **Streamable HTTP** transport for communication between the client and server.

The url for your MCP server will be `{hostname}{base_path}/stream`.
- E.g. The MCP server url would be `https://dev.lionis.ai/api/v1/coreai-mcp-server-alx/stream` if:
  -  `hostname` = `https://dev.lionis.ai`
  -  `base_path` = `/api/v1/coreai-mcp-server-alx`

### Setup:

- Clone the repository.
- Change directory using the following command `cd mcp-server-temp`.

- Using search and replace in your IDE with **match case** and **match whole word** on, replace `temp` and `TEMP` with your server name.
  - E.g.
    - For *ALX* MCP server, replace `temp` with `alx` and `TEMP` with `ALX`.
    - For *Discovery* MCP server, replace `temp` with `discovery` and `TEMP` with `Discovery`.

- Add or update the `.env` file with the correct environment variables values for your local development system by copying the contents in the `.env.example` file.
  > **Note:** Ensure that you do not commit your `.env` file to the git repository.

- Copy the contents of `README-TEMPLATE.md` to your `README.md` file and then delete `README-TEMPLATE.md` from your project.

- Setup `uv` using the following commands:
  > **Note:** this project uses `uv` instead of `poetry` for package management

  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  pip install uv
  ```

- Use the following command to install all project dependencies:

  ```bash
  uv sync
  ```

- To setup **git hooks** use the following command:

  ```bash
  pre-commit install --hook-type pre-commit --hook-type pre-push --hook-type commit-msg
  ```

- To start the server, use the following command:

  ```bash
  uv run start
  ```

### Running Tests with Code Coverage:

To execute the tests, run the following command:

```bash
uv run pytest
```

- The target code coverage is 95%.

- Some tests have already been included in the `tests` directory of this template.

### Code Quality Check:

To check and fix code quality using pre-commit, ensure it is installed and run:

```bash
pre-commit
```

- This repository has pre-commit and pre-push hooks enabled.

  > **Note:** If you need to skip the pre-commit and pre-push hooks for any reason when commiting or pushing changes you can add `--no-verify` to the commit or push command **(NOT recommended)**

### Adding or Removing Packages with `uv`

- To add a package to the project with `uv` run the following command (replacing `[package]` with the name of the package):

  ```bash
  uv add [package]
  ```

- To remove a package from the project run the following command (replacing `[package]` with the name of the package):

  ```bash
  uv remove [package]
  ```

## Adding Tools, Resources and Prompts to the MCP Server

- We have included an example tool in this template project for you to reference.
  - Make sure to remove this tool in your project:
      - Remove `example_tool.py` file from `src/schemas/`
      - Remove `example_tool.py` file from `src/tools/impl/`
      - Remove the following from `register_tools` in `src/tools/registration.py`:
        ```bash
        @mcp.tool()
        async def example_tool(
            input_data: ExampleToolInput,
        ) -> List[Dict[str, str]]:
            """Example tool that uses uses a CoreAI service and requires request headers."""
            return await execute_tool(
                tool_instance=ExampleTool(),
                input_data=input_data,
                mcp=mcp,
                tool_name="example_tool",
                requires_headers=True,
            )
        ```

### Adding a Tool
Documentation on Tools in FastMCP - https://gofastmcp.com/servers/tools

1. Create the input schema model for your tool in `src/schemas/`
2. Add your tool implementation in `src/tools/impl/`
3. Add your tool to `register_tools` in `src/tools/registration.py`

### Adding a Resource
Documentation on Resources in FastMCP - https://gofastmcp.com/servers/resources

- Add your resource to `register_tools` in `src/tools/registration.py`

### Adding a Prompt
Documentation on Prompts in FastMCP - https://gofastmcp.com/servers/prompts

- Add your prompt to `register_tools` in `src/tools/registration.py`

## In Progress Issues

- There are currently some pipeline issues

## Previous Issues

- **SSE** transport was recently deprecated
  - **Solution:** Switched from **SSE** transport to **Streamable HTTP**.

- **FastMCP** integration with **FastAPI**
  - When initially developing the ALX MCP Server we faced issues with **FastMCP** and **FastAPI** compatibility.
    - This caused issues with the middleware being bypassed.
  - **Solution:** **FastMCP** recently added **FastAPI** integration and support for custom middleware.

- Issues with cookie sharing between client and server
  - Authorization cookie is needed for JWT middleware and some tool calls, but cookies don't get sent when using both the MCP client and server **locally** on different ports.
    - Browsers sometimes treat localhost ports inconsistently for cookie sharing which can result in the cookies not being shared.
  - **Solution:** As a *workaround* to this issue you can manually send the Authorization header with your bearer token from your MCP client when it's running **locally**.

- Passing request headers to tools which require Authorization token and Enterprise headers (e.g. for calls to CoreAI services)
  - **Solution:** **FastMCP** recently added support for tools to access http headers.

- Issues with getting the agent to correctly send params for tools with optional input fields
  - For tools that had input schemas with optional fields, the agent wasn't ever sending the optional params.
  - **Solution:** You need to update the description of the optional fields in the input schema model of your tool to explicitly tell the agent when and why to send the optional params.

- Other things to note:
  - Middleware needs to be added in the correct order
    - The execution order of the middleware stack is reversed so that last added is first executed

## Contributing

Feel free to contribute by opening issues or submitting pull requests. Your input is valuable in enhancing the functionality and robustness of this template.
