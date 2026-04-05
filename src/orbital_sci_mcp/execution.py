from __future__ import annotations

import uuid
from time import perf_counter

from .errors import StructuredToolError, ToolExecutionException, internal_error
from .models import ExecutionContext, ToolExecutionResponse
from .registry import ToolRegistry


class ExecutionService:
    def __init__(self, registry: ToolRegistry, transport: str, default_timeout: int = 300) -> None:
        self.registry = registry
        self.transport = transport
        self.default_timeout = default_timeout

    def execute_tool(self, tool_name: str, payload: dict | None = None) -> ToolExecutionResponse:
        context = ExecutionContext(
            request_id=f"req-{uuid.uuid4()}",
            tool_name=tool_name,
            transport=self.transport,
            timeout_seconds=(payload or {}).get("timeout_seconds", self.default_timeout),
        )
        start = perf_counter()
        try:
            try:
                adapter = self.registry.create_adapter(tool_name)
            except KeyError:
                response = ToolExecutionResponse(
                    success=False,
                    error=StructuredToolError(
                        code="UNSUPPORTED_OPERATION",
                        message=f"Unknown tool: {tool_name}",
                        remediation="Use list_tools or search_tools to find a valid tool name.",
                    ),
                    metadata={"request_id": context.request_id, "tool_name": tool_name},
                )
                response.metadata["runtime_seconds"] = round(perf_counter() - start, 6)
                return response
            validated_input = adapter.validate_input(payload or {})
            availability = adapter.check_availability()
            if not availability.available:
                response = adapter.build_unavailable_response(context, availability)
            else:
                raw_result = adapter.execute(validated_input, context)
                response = adapter.normalize_output(raw_result, context)
        except ToolExecutionException as exc:
            response = ToolExecutionResponse(
                success=False,
                error=exc.error,
                metadata={"request_id": context.request_id, "tool_name": tool_name},
            )
        except Exception as exc:
            response = ToolExecutionResponse(
                success=False,
                error=internal_error(str(exc), details={"tool_name": tool_name}),
                metadata={"request_id": context.request_id, "tool_name": tool_name},
            )

        response.metadata["runtime_seconds"] = round(perf_counter() - start, 6)
        return response
