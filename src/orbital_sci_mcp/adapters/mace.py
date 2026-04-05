from __future__ import annotations

from pydantic import BaseModel

from ..errors import ToolExecutionException, unsupported_operation
from ..models import ExecutionContext
from ..schemas.materials import MaterialStructureInput
from .base import BaseAdapter
from .utils import atoms_to_dict, material_input_to_atoms, to_serializable


class MaceAdapter(BaseAdapter):
    package_names = ["mace", "ase"]
    backend_name = "mace"

    def validate_input(self, payload: dict) -> BaseModel:
        return MaterialStructureInput.model_validate(payload)

    def execute(self, validated_input: BaseModel, context: ExecutionContext) -> dict:
        payload = validated_input.model_dump()
        if not payload.get("structure_text") and not (payload.get("atomic_numbers") and payload.get("positions")):
            self._ensure_required_fields(validated_input, ["structure_text"])
        atoms = material_input_to_atoms(payload)
        try:
            from mace.calculators import mace_mp
        except Exception as exc:
            raise ToolExecutionException(
                unsupported_operation(
                    "MACE backend API could not be resolved.",
                    details={"expected": "mace.calculators.mace_mp", "reason": str(exc)},
                )
            ) from exc

        atoms.calc = mace_mp()
        if context.tool_name == "mace_predict_energy":
            return {"energy": atoms.get_potential_energy(), "structure": atoms_to_dict(atoms)}
        if context.tool_name == "mace_calculate_forces":
            return {"forces": to_serializable(atoms.get_forces()), "structure": atoms_to_dict(atoms)}
        self.raise_unsupported(
            f"Unsupported MACE operation: {context.tool_name}",
            details={"tool_name": context.tool_name},
        )
