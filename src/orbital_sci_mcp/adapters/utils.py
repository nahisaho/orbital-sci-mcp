from __future__ import annotations

from io import StringIO
from typing import Any


def material_input_to_atoms(payload: dict):
    from ase import Atoms
    from ase.io import read

    structure_text = payload.get("structure_text")
    structure_format = payload.get("structure_format")
    atomic_numbers = payload.get("atomic_numbers") or []
    positions = payload.get("positions") or []
    lattice = payload.get("lattice") or []

    if structure_text:
        return read(StringIO(structure_text), format=structure_format or "cif")

    if atomic_numbers and positions:
        kwargs: dict[str, Any] = {"numbers": atomic_numbers, "positions": positions}
        if lattice:
            kwargs["cell"] = lattice
            kwargs["pbc"] = True
        return Atoms(**kwargs)

    raise ValueError("Either structure_text or atomic_numbers with positions must be provided.")


def atoms_to_dict(atoms) -> dict:
    positions = getattr(atoms, "positions", None)
    cell = getattr(atoms, "cell", None)
    return {
        "atomic_numbers": list(getattr(atoms, "numbers", [])),
        "positions": positions.tolist() if hasattr(positions, "tolist") else [],
        "lattice": cell.tolist() if hasattr(cell, "tolist") else [],
        "pbc": list(atoms.pbc) if hasattr(atoms, "pbc") else [],
    }


def to_serializable(value):
    return value.tolist() if hasattr(value, "tolist") else value