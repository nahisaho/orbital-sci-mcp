from __future__ import annotations

from pydantic import Field

from .common import CommonToolInput


class MaterialStructureInput(CommonToolInput):
    structure_text: str | None = None
    structure_format: str | None = None
    atomic_numbers: list[int] = Field(default_factory=list)
    positions: list[list[float]] = Field(default_factory=list)
    lattice: list[list[float]] = Field(default_factory=list)
    calculator_options: dict = Field(default_factory=dict)


class MaterialGenerationInput(CommonToolInput):
    prompt: str | None = None
    constraints: dict = Field(default_factory=dict)
    sample_count: int = 1
