from __future__ import annotations

import types

import pytest

from orbital_sci_mcp.adapters.mattergen import MatterGenAdapter
from orbital_sci_mcp.errors import ToolExecutionException
from orbital_sci_mcp.models import ExecutionContext


def _ctx() -> ExecutionContext:
    return ExecutionContext(
        request_id="req-mg",
        tool_name="mattergen_generate_material",
        transport="stdio",
        timeout_seconds=120,
    )


# --- INPUT_VALIDATION_FAILED: no prompt nor constraints ---


def test_rejects_empty_input() -> None:
    adapter = MatterGenAdapter()
    validated = adapter.validate_input({})
    with pytest.raises(ToolExecutionException) as exc_info:
        adapter.execute(validated, _ctx())
    assert exc_info.value.error.code == "INPUT_VALIDATION_FAILED"


# --- UNSUPPORTED_OPERATION: import fails ---


def test_import_failure(monkeypatch) -> None:
    adapter = MatterGenAdapter()
    validated = adapter.validate_input({"prompt": "stable perovskite"})

    import builtins

    real_import = builtins.__import__

    def block_mattergen(name, *args, **kwargs):
        if "mattergen" in name:
            raise ImportError("no mattergen")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", block_mattergen)

    with pytest.raises(ToolExecutionException) as exc_info:
        adapter.execute(validated, _ctx())
    assert exc_info.value.error.code == "UNSUPPORTED_OPERATION"


# --- success: generate with prompt ---


def test_generate_success(monkeypatch) -> None:
    adapter = MatterGenAdapter()
    validated = adapter.validate_input(
        {"prompt": "stable perovskite", "sample_count": 2}
    )

    class FakeStructure:
        formula = "BaTiO3"
        num_sites = 5

        class lattice:
            class matrix:
                @staticmethod
                def tolist():
                    return [[4, 0, 0], [0, 4, 0], [0, 0, 4]]

        class _site:
            specie = "Ba"

            class frac_coords:
                @staticmethod
                def tolist():
                    return [0.0, 0.0, 0.0]

        sites = [_site, _site]

    def fake_generate(**kwargs):
        return [FakeStructure(), FakeStructure(), FakeStructure()]

    _inject_fake_mattergen(monkeypatch, fake_generate)

    result = adapter.execute(validated, _ctx())
    assert result["returned_count"] == 2
    assert result["requested_count"] == 2
    assert len(result["generated_candidates"]) == 2
    assert result["generated_candidates"][0]["formula"] == "BaTiO3"


# --- success: generate with constraints ---


def test_generate_with_constraints(monkeypatch) -> None:
    adapter = MatterGenAdapter()
    validated = adapter.validate_input(
        {
            "constraints": {
                "pretrained_name": "mattergen_base",
                "properties_to_condition_on": {"bandgap": 1.5},
            },
            "sample_count": 1,
        }
    )

    class FakeStructure:
        formula = "Si"
        num_sites = 2

        class lattice:
            class matrix:
                @staticmethod
                def tolist():
                    return [[5, 0, 0], [0, 5, 0], [0, 0, 5]]

        sites = []

    def fake_generate(**kwargs):
        assert kwargs["properties_to_condition_on"] == {"bandgap": 1.5}
        return [FakeStructure()]

    _inject_fake_mattergen(monkeypatch, fake_generate)

    result = adapter.execute(validated, _ctx())
    assert result["returned_count"] == 1
    assert result["constraints"]["properties_to_condition_on"] == {"bandgap": 1.5}


# --- helper ---


def _inject_fake_mattergen(monkeypatch, fake_generate_fn):
    import builtins

    real_import = builtins.__import__

    def patched_import(name, *args, **kwargs):
        if name == "mattergen.scripts.generate":
            mod = types.ModuleType("mattergen.scripts.generate")
            mod.main = fake_generate_fn
            return mod
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", patched_import)
