from __future__ import annotations

from tempfile import TemporaryDirectory

from pydantic import BaseModel

from ..errors import ToolExecutionException, unsupported_operation
from ..models import ExecutionContext
from ..schemas.materials import MaterialGenerationInput
from .base import BaseAdapter


class MatterGenAdapter(BaseAdapter):
    package_names = ["mattergen"]
    backend_name = "mattergen"

    def validate_input(self, payload: dict) -> BaseModel:
        return MaterialGenerationInput.model_validate(payload)

    def execute(self, validated_input: BaseModel, context: ExecutionContext) -> dict:
        payload = validated_input.model_dump()
        if not payload.get("prompt") and not payload.get("constraints"):
            self._ensure_required_fields(validated_input, ["prompt"])
        try:
            from mattergen.scripts.generate import main as generate_materials
        except Exception as exc:
            raise ToolExecutionException(
                unsupported_operation(
                    "MatterGen backend API could not be resolved.",
                    details={"expected": "mattergen.scripts.generate.main", "reason": str(exc)},
                )
            ) from exc

        constraints = payload.get("constraints") or {}
        sample_count = max(int(payload.get("sample_count", 1)), 1)
        batch_size = min(sample_count, 16)
        num_batches = max((sample_count + batch_size - 1) // batch_size, 1)
        pretrained_name = constraints.get("pretrained_name") or "mattergen_base"
        model_path = constraints.get("model_path")
        properties_to_condition_on = constraints.get("properties_to_condition_on") or {}
        target_compositions = constraints.get("target_compositions")
        diffusion_guidance_factor = constraints.get("diffusion_guidance_factor")

        with TemporaryDirectory(prefix="mattergen-") as output_dir:
            structures = generate_materials(
                output_path=output_dir,
                pretrained_name=None if model_path else pretrained_name,
                model_path=model_path,
                batch_size=batch_size,
                num_batches=num_batches,
                properties_to_condition_on=properties_to_condition_on,
                diffusion_guidance_factor=diffusion_guidance_factor,
                target_compositions=target_compositions,
            )

            serialized = []
            for structure in structures[:sample_count]:
                serialized.append(
                    {
                        "formula": getattr(structure, "formula", None),
                        "num_sites": getattr(structure, "num_sites", None),
                        "lattice": structure.lattice.matrix.tolist() if hasattr(structure, "lattice") else None,
                        "species": [str(site.specie) for site in getattr(structure, "sites", [])],
                        "frac_coords": [site.frac_coords.tolist() for site in getattr(structure, "sites", [])],
                    }
                )

        return {
            "generated_candidates": serialized,
            "returned_count": len(serialized),
            "requested_count": sample_count,
            "constraints": constraints,
        }
