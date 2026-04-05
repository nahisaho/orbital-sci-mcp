from __future__ import annotations

import types

import pytest

from orbital_sci_mcp.adapters.mattersim import MatterSimAdapter
from orbital_sci_mcp.errors import ToolExecutionException
from orbital_sci_mcp.models import ExecutionContext


def _ctx(tool_name: str = "mattersim_predict_energy") -> ExecutionContext:
    return ExecutionContext(
        request_id="req-ms",
        tool_name=tool_name,
        transport="stdio",
        timeout_seconds=60,
    )


# --- INPUT_VALIDATION_FAILED: no structure ---


def test_rejects_empty_structure() -> None:
    adapter = MatterSimAdapter()
    validated = adapter.validate_input({})
    with pytest.raises(ToolExecutionException) as exc_info:
        adapter.execute(validated, _ctx())
    assert exc_info.value.error.code == "INPUT_VALIDATION_FAILED"


# --- UNSUPPORTED_OPERATION: import fails ---


def test_import_failure(monkeypatch) -> None:
    adapter = MatterSimAdapter()
    validated = adapter.validate_input(
        {"atomic_numbers": [14, 14], "positions": [[0, 0, 0], [1, 1, 1]]}
    )

    # mock atoms creation so ase is not needed
    monkeypatch.setattr(
        "orbital_sci_mcp.adapters.mattersim.material_input_to_atoms",
        lambda payload: _make_fake_atoms(0, [[0, 0, 0], [0, 0, 0]], [0] * 6),
    )

    import builtins

    real_import = builtins.__import__

    def block_mattersim(name, *args, **kwargs):
        if name.startswith("mattersim"):
            raise ImportError("no mattersim")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", block_mattersim)

    with pytest.raises(ToolExecutionException) as exc_info:
        adapter.execute(validated, _ctx())
    assert exc_info.value.error.code == "UNSUPPORTED_OPERATION"


# --- UNSUPPORTED_OPERATION: unknown tool_name ---


def test_unsupported_tool_name(monkeypatch) -> None:
    adapter = MatterSimAdapter()
    validated = adapter.validate_input(
        {"atomic_numbers": [14, 14], "positions": [[0, 0, 0], [1, 1, 1]]}
    )

    _inject_fake_mattersim(monkeypatch, energy=1.0, forces=[[0, 0, 0], [0, 0, 0]], stress=[0] * 6)

    with pytest.raises(ToolExecutionException) as exc_info:
        adapter.execute(validated, _ctx("mattersim_bogus"))
    assert exc_info.value.error.code == "UNSUPPORTED_OPERATION"


# --- success: predict_energy ---


def test_predict_energy_success(monkeypatch) -> None:
    adapter = MatterSimAdapter()
    validated = adapter.validate_input(
        {"atomic_numbers": [14, 14], "positions": [[0, 0, 0], [1.35, 1.35, 1.35]]}
    )

    _inject_fake_mattersim(
        monkeypatch,
        energy=-10.5,
        forces=[[0.1, 0.2, 0.3], [-0.1, -0.2, -0.3]],
        stress=[1, 2, 3, 4, 5, 6],
    )

    result = adapter.execute(validated, _ctx("mattersim_predict_energy"))
    assert result["energy"] == -10.5
    assert len(result["forces"]) == 2
    assert len(result["stress"]) == 6
    assert "structure" in result


# --- success: relax_structure ---


def test_relax_structure_success(monkeypatch) -> None:
    adapter = MatterSimAdapter()
    validated = adapter.validate_input(
        {"atomic_numbers": [14, 14], "positions": [[0, 0, 0], [1.35, 1.35, 1.35]]}
    )

    _inject_fake_mattersim(monkeypatch, energy=-11.0, forces=[[0, 0, 0], [0, 0, 0]], stress=[0] * 6)

    result = adapter.execute(validated, _ctx("mattersim_relax_structure"))
    assert result["energy"] == -11.0
    assert "relaxed_structure" in result


# --- helpers ---


def _inject_fake_mattersim(monkeypatch, *, energy, forces, stress):
    class FakeCalc:
        pass

    fake_module = types.ModuleType("mattersim.forcefield")
    fake_module.MatterSimCalculator = FakeCalc

    import builtins

    real_import = builtins.__import__

    def patched_import(name, *args, **kwargs):
        if name == "mattersim.forcefield":
            return fake_module
        if name == "ase.optimize":
            mod = types.ModuleType("ase.optimize")

            class FakeBFGS:
                def __init__(self, atoms, logfile=None):
                    pass

                def run(self, fmax=0.05, steps=50):
                    pass

            mod.BFGS = FakeBFGS
            return mod
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", patched_import)

    monkeypatch.setattr(
        "orbital_sci_mcp.adapters.mattersim.material_input_to_atoms",
        lambda payload: _make_fake_atoms(energy, forces, stress),
    )


def _make_fake_atoms(energy, forces, stress):
    import numpy as np

    class FakeAtoms:
        def __init__(self):
            self.calc = None
            self.numbers = [14, 14]
            self.positions = np.array([[0, 0, 0], [1.35, 1.35, 1.35]])
            self.cell = np.zeros((3, 3))
            self.pbc = [False, False, False]

        def get_potential_energy(self):
            return energy

        def get_forces(self):
            return np.array(forces)

        def get_stress(self):
            return np.array(stress)

    return FakeAtoms()


def _inject_fake_ase_bfgs(monkeypatch):
    class FakeBFGS:
        def __init__(self, atoms, logfile=None):
            pass

        def run(self, fmax=0.05, steps=50):
            pass

    monkeypatch.setattr("orbital_sci_mcp.adapters.mattersim.BFGS", FakeBFGS, raising=False)

    import builtins

    real_import = builtins.__import__

    def patched_import(name, *args, **kwargs):
        if name == "ase.optimize":
            mod = types.ModuleType("ase.optimize")
            mod.BFGS = FakeBFGS
            return mod
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", patched_import)
