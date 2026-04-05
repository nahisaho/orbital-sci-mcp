from __future__ import annotations

from abc import ABC, abstractmethod
import importlib
from importlib.util import find_spec
from typing import Any

from pydantic import BaseModel

from ..errors import StructuredToolError, ToolExecutionException, unsupported_operation
from ..models import AvailabilityResult, ExecutionContext, ToolExecutionResponse


class BaseAdapter(ABC):
    package_names: list[str] = []
    backend_name: str = "unknown"
    gpu_required: bool = False

    def tool_name(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def validate_input(self, payload: dict) -> BaseModel:
        raise NotImplementedError

    def check_availability(self) -> AvailabilityResult:
        missing = [package for package in self.package_names if find_spec(package) is None]
        if missing:
            return AvailabilityResult(
                available=False,
                status="dependency_missing",
                missing_packages=missing,
                message="Optional dependencies are not installed.",
            )
        if self.gpu_required and not self._is_gpu_available():
            return AvailabilityResult(
                available=False,
                status="gpu_unavailable",
                gpu_required=True,
                gpu_available=False,
                message="This backend requires a CUDA-capable GPU.",
            )
        return AvailabilityResult(available=True, status="available")

    @abstractmethod
    def execute(self, validated_input: BaseModel, context: ExecutionContext) -> Any:
        raise NotImplementedError

    def normalize_output(self, raw_result: Any, context: ExecutionContext) -> ToolExecutionResponse:
        return ToolExecutionResponse(
            success=True,
            data=raw_result,
            metadata={
                "request_id": context.request_id,
                "tool_name": context.tool_name,
                "backend": self.backend_name,
                "availability_status": "available",
            },
        )

    def raise_unsupported(self, message: str, details: dict | None = None) -> None:
        raise ToolExecutionException(unsupported_operation(message, details=details))

    def _is_gpu_available(self) -> bool:
        if find_spec("torch") is None:
            return False
        torch = importlib.import_module("torch")
        return bool(torch.cuda.is_available())

    def _ensure_required_fields(self, payload: BaseModel, field_names: list[str]) -> None:
        values = payload.model_dump()
        missing = []
        for field_name in field_names:
            value = values.get(field_name)
            if value is None or value == "" or value == []:
                missing.append(field_name)
        if missing:
            raise ToolExecutionException(
                StructuredToolError(
                    code="INPUT_VALIDATION_FAILED",
                    message="Required input fields are missing.",
                    details={"missing_fields": missing},
                    remediation=f"Provide values for: {', '.join(missing)}",
                    retryable=False,
                )
            )

    def build_unavailable_response(
        self, context: ExecutionContext, availability: AvailabilityResult
    ) -> ToolExecutionResponse:
        packages = ", ".join(availability.missing_packages) or "required package"
        error_code = "GPU_UNAVAILABLE" if availability.status == "gpu_unavailable" else "DEPENDENCY_MISSING"
        error = StructuredToolError(
            code=error_code,
            message=availability.message or "Backend is unavailable.",
            details=availability.model_dump(),
            remediation=(
                "Run on a machine with CUDA available."
                if availability.status == "gpu_unavailable"
                else f"Install the missing dependencies: {packages}"
            ),
            retryable=False,
        )
        return ToolExecutionResponse(
            success=False,
            error=error,
            metadata={
                "request_id": context.request_id,
                "tool_name": context.tool_name,
                "backend": self.backend_name,
                "availability_status": availability.status,
            },
        )
