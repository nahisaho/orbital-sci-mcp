from __future__ import annotations

from pydantic import Field

from .common import CommonToolInput


class MoleculeInput(CommonToolInput):
    smiles: str | None = None
    molecule_block: str | None = None
    conformer_count: int = 1
    target_property: str | None = None
    generation_options: dict = Field(default_factory=dict)
    inference_options: dict = Field(default_factory=dict)
