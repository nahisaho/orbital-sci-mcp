from __future__ import annotations

from ..execution import ExecutionService
from ..registry import ToolRegistry


def build_execute_tool(execution_service: ExecutionService):
    def execute_tool(tool_name: str, arguments: dict | None = None) -> dict:
        return execution_service.execute_tool(tool_name, arguments).model_dump()

    return execute_tool


def build_individual_tool(registry: ToolRegistry, execution_service: ExecutionService, tool_name: str):
    spec = registry.get(tool_name)

    def tool_function(arguments: dict | None = None) -> dict:
        return execution_service.execute_tool(spec.name, arguments).model_dump()

    tool_function.__name__ = tool_name
    tool_function.__doc__ = spec.description
    return tool_function
