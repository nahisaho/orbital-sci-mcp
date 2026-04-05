from __future__ import annotations

import types

import pytest

from orbital_sci_mcp.adapters.mace import MaceAdapter
from orbital_sci_mcp.errors import ToolExecutionException
from orbital_sci_mcp.models import ExecutionContext


def _ctx(tool_name: str = "mace_predict_energy") -> ExecutionContext:
    return ExecutionContext(
        request_id="req-mc",
        tool_name=tool_name,
        transport="stdio",
        timeout_seconds=60,
    )


# --- INPUT_VALIDATION_FAILED: no structure ---


def test_rejects_empty_structure() -> None:
    adapter = MaceAdapter()
    validated = adapter.validate_input({})
    with pytest.raises(ToolExecutionException) as exc_info:
        adapter.execute(validated, _ctx())
    assert exc_info.value.error.code == "INPUT_VALIDATION_FAILED"


# --- UNSUPPORTED_OPERATION: import fails ---


def test_import_failure(monkeypatch) -> None:
    adapter = MaceAdapter()
    validated = adapter.validate_input(
        {"atomic_numbers": [14, 14], "positions": [[0, 0, 0], [1, 1, 1]]}
    )

    # mock atoms creation so ase is not needed
    import numpy as np

    class FakeAtoms:
        def __init__(self):
            self.calc = None
            self.numbers = [14, 14]
            self.positions = np.zeros((2, 3))
            self.cell = np.zeros((3, 3))
            self.pbc = [False, False, False]

    monkeypatch.setattr(
        "orbital_sci_mcp.adapters.mace.material_input_to_atoms",
        lambda payload: FakeAtoms(),
    )

    import builtins

    real_import = builtins.__import__

    def block_mace(name, *args, **kwargs):
        if name.startswith("mace"):
            raise ImportError("no mace")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", block_mace)

    with pytest.raises(ToolExecutionException) as exc_info:
        adapter.execute(validated, _ctx())
    assert exc_info.value.error.code == "UNSUPPORTED_OPERATION"


# --- UNSUPPORTED_OPERATION: unknown tool_name ---


def test_unsupported_tool_name(monkeypatch) -> None:
    adapter = MaceAdapter()
    validated = adapter.validate_input(
        {"atomic_numbers": [14, 14], "positions": [[0, 0, 0], [1, 1, 1]]}
    )
    _inject_fake_mace(monkeypatch, energy=-5.0, forces=[[0, 0, 0], [0, 0, 0]])

    with pytest.raises(ToolExecutionException) as exc_info:
        adapter.execute(validated, _ctx("mace_bogus"))
    assert exc_info.value.error.code == "UNSUPPORTED_OPERATION"


# --- success: predict_energy ---


def test_predict_energy_success(monkeypatch) -> None:
    adapter = MaceAdapter()
    validated = adapter.validate_input(
        {"atomic_numbers": [14, 14], "positions": [[0, 0, 0], [1.35, 1.35, 1.35]]}
    )
    _inject_fake_mace(monkeypatch, energy=-5.5, forces=[[0.1, 0.2, 0.3], [-0.1, -0.2, -0.3]])

    result = adapter.execute(validated, _ctx("mace_predict_energy"))
    assert result["energy"] == -5.5
    assert "structure" in result


# --- success: calculate_forces ---


def test_calculate_forces_success(monkeypatch) -> None:
    adapter = MaceAdapter()
    validated = adapter.validate_input(
        {"atomic_numbers": [14, 14], "positions": [[0, 0, 0], [1.35, 1.35, 1.35]]}
    )
    _inject_fake_mace(monkeypatch, energy=-5.5, forces=[[0.1, 0.2, 0.3], [-0.1, -0.2, -0.3]])

    result = adapter.execute(validated, _ctx("mace_calculate_forces"))
    assert len(result["forces"]) == 2
    assert "structure" in result


# --- helper ---


def _inject_fake_mace(monkeypatch, *, energy, forces):
    import numpy as np

    class FakeCalc:
        pass

    fake_module = types.ModuleType("mace.calculators")
    fake_module.mace_mp = lambda: FakeCalc()

    import builtins

    real_import = builtins.__import__

    def patched_import(name, *args, **kwargs):
        if name == "mace.calculators":
            return fake_module
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", patched_import)

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

    monkeypatch.setattr(
        "orbital_sci_mcp.adapters.mace.material_input_to_atoms",
        lambda payload: FakeAtoms(),
    )
