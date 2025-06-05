# TEMP MCP Server

## Getting Started

### Setup:

- Clone the repository.
- Change directory using the following command `cd mcp-server-temp`.
- Setup uv using the following commands

  ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install uv
  ```

- Use the following command to install all project dependencies

  ```bash
    uv sync
  ```

- To setup git hooks use the following command

  ```bash
    pre-commit install --hook-type pre-commit --hook-type pre-push --hook-type commit-msg
  ```

- Add or Update the `.env` file with the correct environment variables values for your local development system by copying the contents in the `.env.example` file.

  **Note:** Ensure that you do not commit your `.env` file to the git repository.

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

### Code Quality Check:

To check and fix code quality using pre-commit, ensure it is installed and run:

```bash
pre-commit
```

- This repository has pre-commit and pre-push hooks enabled.

  > **Note:** If you need to skip the pre-commit and pre-push hooks for any reason when commiting or pushing changes you can add `--no-verify` to the commit or push command **(NOT recommended)**

## Contributing:

Feel free to contribute by opening issues or submitting pull requests. Your input is valuable in enhancing the functionality and robustness of this template.

## Troubleshooting:

- If facing issues with SSL verification while trying to install python packages try the following:

  1. Try after install/updating ca-certificates using brew
  2. Try to locate installed certificates or export SSL certificates using any browser and add it in the `~/.bashrc` or `~/.zshrc`

  ```bash
    export REQUESTS_CA_BUNDLE=<path to ssl certificates>
  ```
