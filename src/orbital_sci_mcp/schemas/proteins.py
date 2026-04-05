from __future__ import annotations

from pydantic import Field

from .common import CommonToolInput


class ProteinSequenceInput(CommonToolInput):
    sequence: str | None = None
    fasta_text: str | None = None
    sample_count: int = 1
    random_seed: int | None = None
    inference_options: dict = Field(default_factory=dict)
