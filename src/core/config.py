"""Global Configs"""

import os
import json

from functools import lru_cache
from typing import Dict, List

from dotenv import load_dotenv

import toml
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class GlobalConfigs(BaseSettings, extra="allow"):
    """Global Configs class"""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    title: str = "TEMP MCP Server"
    description: str = "MCP Server for TEMP"
    api_version: str = "0.1.0"

    base_path: str = (
        "/api/v1"  # if a BASE_PATH variable is found in the .env it will override this
    )

    host: str = "HOST"
    port: int = int(os.getenv("PORT", "8000"))
    hostname: str = "HOSTNAME"

    backend_cors_origins: List[str] = json.loads(
        os.getenv("BACKEND_CORS_ORIGINS", "[]")
    )
    reload: bool = True
    debug: bool = False

    commit_id: str = ""
    branch_name: str = ""
    build_time: str = ""
    tag: str = ""

    encryption_algorithm: str = "RS256"
    enterprise_auth_public_key: str = "ENTERPRISE_AUTH_PUBLIC_KEY"
    enterprise_base_url: str = "ENTERPRISE_BASE_URL"
    enterprise_llm_headers: List[str] = [
        "traceparent",
        "x-client-id",
        "x-project-id",
        "x-portfolio-id",
        "x-workspace-id",
    ]

    skip_paths: List[str] = ["/docs", "/openapi.json"]

    @property
    def app(self) -> Dict[str, str]:
        """app details

        Returns:
            Dict[str, str]: {name=name, description=description, version=version}
        """
        app_details = {}
        project_config = toml.load("pyproject.toml")["project"]
        app_details["name"] = self.title
        app_details["description"] = project_config["description"]
        app_details["version"] = project_config["version"]
        return app_details


@lru_cache
def get_settings() -> GlobalConfigs:
    """caching GlobalConfigs"""
    return GlobalConfigs()


settings = get_settings()

__all__ = ["settings"]
