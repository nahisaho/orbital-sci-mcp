from __future__ import annotations

from pydantic import BaseModel

from ..errors import ToolExecutionException, unsupported_operation
from ..models import ExecutionContext
from ..schemas.materials import MaterialStructureInput
from .base import BaseAdapter
from .utils import atoms_to_dict, material_input_to_atoms, to_serializable


class MatterSimAdapter(BaseAdapter):
    package_names = ["mattersim", "ase"]
    backend_name = "mattersim"

    def validate_input(self, payload: dict) -> BaseModel:
        return MaterialStructureInput.model_validate(payload)

    def execute(self, validated_input: BaseModel, context: ExecutionContext) -> dict:
        payload = validated_input.model_dump()
        if not payload.get("structure_text") and not (payload.get("atomic_numbers") and payload.get("positions")):
            self._ensure_required_fields(validated_input, ["structure_text"])
        atoms = material_input_to_atoms(payload)
        try:
            from mattersim.forcefield import MatterSimCalculator
        except Exception as exc:
            raise ToolExecutionException(
                unsupported_operation(
                    "MatterSim backend API could not be resolved.",
                    details={"expected": "mattersim.forcefield.MatterSimCalculator", "reason": str(exc)},
                )
            ) from exc

        atoms.calc = MatterSimCalculator()
        if context.tool_name == "mattersim_predict_energy":
            return {
                "energy": atoms.get_potential_energy(),
                "forces": to_serializable(atoms.get_forces()),
                "stress": to_serializable(atoms.get_stress()),
                "structure": atoms_to_dict(atoms),
            }
        if context.tool_name == "mattersim_relax_structure":
            from ase.optimize import BFGS

            options = payload.get("calculator_options", {})
            optimizer = BFGS(atoms, logfile=None)
            optimizer.run(fmax=options.get("fmax", 0.05), steps=options.get("steps", 50))
            return {
                "energy": atoms.get_potential_energy(),
                "relaxed_structure": atoms_to_dict(atoms),
            }
        self.raise_unsupported(
            f"Unsupported MatterSim operation: {context.tool_name}",
            details={"tool_name": context.tool_name},
        )
