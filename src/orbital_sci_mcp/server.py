from __future__ import annotations

from typing import Any

from .config import AppConfig
from .execution import ExecutionService
from .registry import ToolRegistry, create_default_registry
from .tools.discovery import build_get_tool_info, build_list_tools, build_search_tools
from .tools.execution_tools import build_execute_tool, build_individual_tool


def _load_fastmcp() -> Any:
    from fastmcp import FastMCP

    return FastMCP


def create_server(config: AppConfig, registry: ToolRegistry | None = None):
    fastmcp_cls = _load_fastmcp()
    registry = registry or create_default_registry()
    registry.configure(
        enabled_domains=config.enabled_domains,
        enabled_tools=config.enabled_tools,
        disabled_tools=config.disabled_tools,
    )
    execution_service = ExecutionService(
        registry=registry,
        transport=config.transport,
        default_timeout=config.default_timeout,
    )
    server = fastmcp_cls(config.server_name)

    server.tool(name="list_tools")(build_list_tools(registry, config.compact_mode))
    server.tool(name="get_tool_info")(build_get_tool_info(registry))
    server.tool(name="search_tools")(build_search_tools(registry))
    server.tool(name="execute_tool")(build_execute_tool(execution_service))

    if not config.compact_mode:
        for spec in registry.list_all():
            server.tool(name=spec.name)(build_individual_tool(registry, execution_service, spec.name))

    return server


def run_server(config: AppConfig, registry: ToolRegistry | None = None) -> None:
    server = create_server(config=config, registry=registry)
    if config.transport == "stdio":
        server.run(transport="stdio")
        return
    server.run(transport="streamable-http", host=config.host, port=config.port)
