from __future__ import annotations

from contextlib import nullcontext
from pathlib import Path
from tempfile import TemporaryDirectory

from pydantic import BaseModel

from ..errors import ToolExecutionException, unsupported_operation
from ..models import ExecutionContext
from ..schemas.proteins import ProteinSequenceInput
from .base import BaseAdapter


class BioEmuAdapter(BaseAdapter):
    package_names = ["bioemu"]
    backend_name = "bioemu"
    gpu_required = True

    def validate_input(self, payload: dict) -> BaseModel:
        return ProteinSequenceInput.model_validate(payload)

    def execute(self, validated_input: BaseModel, context: ExecutionContext) -> dict:
        payload = validated_input.model_dump()
        if not payload.get("sequence") and not payload.get("fasta_text"):
            self._ensure_required_fields(validated_input, ["sequence"])
        try:
            from bioemu.sample import main as sample_structures
        except Exception as exc:
            raise ToolExecutionException(
                unsupported_operation(
                    "BioEmu backend API could not be resolved.",
                    details={"expected": "bioemu.sample.main", "reason": str(exc)},
                )
            ) from exc

        sequence = payload.get("sequence") or payload.get("fasta_text")
        sample_count = max(int(payload.get("sample_count", 1)), 1)
        inference_options = payload.get("inference_options") or {}
        output_dir_override = inference_options.get("output_dir")
        context = (
            nullcontext(str(Path(output_dir_override).expanduser().resolve()))
            if output_dir_override
            else TemporaryDirectory(prefix="bioemu-")
        )

        with context as output_dir:
            sample_structures(
                sequence=sequence,
                num_samples=sample_count,
                output_dir=output_dir,
                batch_size_100=int(inference_options.get("batch_size_100", 10)),
                model_name=inference_options.get("model_name", "bioemu-v1.1"),
                denoiser_type=inference_options.get("denoiser_type", "dpm"),
                denoiser_config=inference_options.get("denoiser_config"),
                cache_embeds_dir=inference_options.get("cache_embeds_dir"),
                cache_so3_dir=inference_options.get("cache_so3_dir"),
                msa_host_url=inference_options.get("msa_host_url"),
                filter_samples=bool(inference_options.get("filter_samples", True)),
                steering_config=inference_options.get("steering_config"),
                base_seed=payload.get("random_seed"),
            )

            output_path = Path(output_dir)
            topology_path = output_path / "topology.pdb"
            xtc_path = output_path / "samples.xtc"
            fasta_path = output_path / "sequence.fasta"
            result = {
                "requested_count": sample_count,
                "model_name": inference_options.get("model_name", "bioemu-v1.1"),
                "artifacts": {
                    "topology_pdb_exists": topology_path.exists(),
                    "samples_xtc_exists": xtc_path.exists(),
                    "sequence_fasta_exists": fasta_path.exists(),
                },
            }
            if output_dir_override:
                result.update(
                    {
                        "output_dir": str(output_path),
                        "topology_pdb": str(topology_path) if topology_path.exists() else None,
                        "samples_xtc": str(xtc_path) if xtc_path.exists() else None,
                        "sequence_fasta": str(fasta_path) if fasta_path.exists() else None,
                    }
                )
            return result
