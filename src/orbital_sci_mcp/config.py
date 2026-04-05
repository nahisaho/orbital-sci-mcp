from __future__ import annotations

import os
from typing import Literal

from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    server_name: str = Field(default="Orbital Sci MCP Server")
    transport: Literal["stdio", "http"] = Field(default="stdio")
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=7000)
    log_level: str = Field(default="info")
    compact_mode: bool = Field(default=False)
    enabled_domains: list[str] = Field(default_factory=list)
    enabled_tools: list[str] = Field(default_factory=list)
    disabled_tools: list[str] = Field(default_factory=list)
    optional_dependency_policy: Literal["warn", "strict"] = Field(default="warn")
    default_timeout: int = Field(default=300)

    @classmethod
    def from_env(cls) -> "AppConfig":
        enabled_domains = _split_csv(os.getenv("ORBITAL_SCI_MCP_ENABLED_DOMAINS", ""))
        enabled_tools = _split_csv(os.getenv("ORBITAL_SCI_MCP_ENABLED_TOOLS", ""))
        disabled_tools = _split_csv(os.getenv("ORBITAL_SCI_MCP_DISABLED_TOOLS", ""))
        return cls(
            transport=os.getenv("ORBITAL_SCI_MCP_TRANSPORT", "stdio"),
            host=os.getenv("ORBITAL_SCI_MCP_HOST", "127.0.0.1"),
            port=int(os.getenv("ORBITAL_SCI_MCP_PORT", "7000")),
            log_level=os.getenv("ORBITAL_SCI_MCP_LOG_LEVEL", "info"),
            compact_mode=os.getenv("ORBITAL_SCI_MCP_COMPACT_MODE", "false").lower()
            in {"1", "true", "yes", "on"},
            enabled_domains=enabled_domains,
            enabled_tools=enabled_tools,
            disabled_tools=disabled_tools,
            default_timeout=int(os.getenv("ORBITAL_SCI_MCP_DEFAULT_TIMEOUT", "300")),
        )


def _split_csv(raw_value: str) -> list[str]:
    return [item.strip() for item in raw_value.split(",") if item.strip()]
