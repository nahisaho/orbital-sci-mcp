from __future__ import annotations

from time import time
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from .errors import StructuredToolError


class DependencyRequirement(BaseModel):
    python_packages: list[str] = Field(default_factory=list)
    gpu_required: bool = Field(default=False)
    env_vars: list[str] = Field(default_factory=list)
    artifacts: list[str] = Field(default_factory=list)


class AvailabilityResult(BaseModel):
    available: bool
    status: str
    missing_packages: list[str] = Field(default_factory=list)
    missing_env_vars: list[str] = Field(default_factory=list)
    gpu_required: bool = Field(default=False)
    gpu_available: bool | None = None
    missing_artifacts: list[str] = Field(default_factory=list)
    message: str | None = None


class ToolSpec(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    description: str
    domain: str
    tags: list[str] = Field(default_factory=list)
    maturity: str = Field(default="prototype")
    input_model: type[BaseModel]
    output_model: type[BaseModel] | None = None
    adapter_key: str
    dependency_requirements: DependencyRequirement = Field(default_factory=DependencyRequirement)
    availability_policy: str = Field(default="best-effort")


class ExecutionContext(BaseModel):
    request_id: str
    tool_name: str
    start_time: float = Field(default_factory=time)
    transport: str
    caller_metadata: dict[str, Any] = Field(default_factory=dict)
    timeout_seconds: int = Field(default=300)


class ToolExecutionResponse(BaseModel):
    success: bool
    data: Any = None
    error: StructuredToolError | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
