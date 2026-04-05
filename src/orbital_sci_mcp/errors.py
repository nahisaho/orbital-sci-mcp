from __future__ import annotations

from pydantic import BaseModel, Field


class StructuredToolError(BaseModel):
    code: str
    message: str
    details: dict | None = None
    remediation: str | None = None
    retryable: bool = Field(default=False)


class ToolExecutionException(Exception):
    def __init__(self, error: StructuredToolError) -> None:
        super().__init__(error.message)
        self.error = error


def internal_error(message: str, details: dict | None = None) -> StructuredToolError:
    return StructuredToolError(
        code="INTERNAL_ERROR",
        message=message,
        details=details,
        retryable=False,
    )


def unsupported_operation(message: str, details: dict | None = None) -> StructuredToolError:
    return StructuredToolError(
        code="UNSUPPORTED_OPERATION",
        message=message,
        details=details,
        retryable=False,
    )
