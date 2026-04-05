from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CommonToolInput(BaseModel):
    input_format: str | None = None
    payload_version: str = Field(default="1.0")
    timeout_seconds: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
