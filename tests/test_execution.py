from __future__ import annotations

from orbital_sci_mcp.execution import ExecutionService
from orbital_sci_mcp.registry import create_default_registry


def test_execute_tool_returns_structured_error_for_missing_dependency() -> None:
    registry = create_default_registry()
    service = ExecutionService(registry=registry, transport="stdio")

    response = service.execute_tool(
        "bioemu_sample_ensemble",
        {"sequence": "MKTIIALSYIFCLVFADYKDDDDK"},
    )

    assert response.success is False
    assert response.error is not None
    assert response.error.code in {"DEPENDENCY_MISSING", "GPU_UNAVAILABLE"}
    assert response.metadata["tool_name"] == "bioemu_sample_ensemble"


def test_execute_tool_returns_unknown_tool_error() -> None:
    registry = create_default_registry()
    service = ExecutionService(registry=registry, transport="stdio")

    response = service.execute_tool("does_not_exist", {})

    assert response.success is False
    assert response.error is not None
    assert response.error.code == "UNSUPPORTED_OPERATION"


def test_graphormer_requires_explicit_inference_options() -> None:
    registry = create_default_registry()
    service = ExecutionService(registry=registry, transport="stdio")

    response = service.execute_tool(
        "graphormer_predict_property",
        {"smiles": "CCO"},
    )

    assert response.success is False
    assert response.error is not None
    assert response.error.code in {"DEPENDENCY_MISSING", "UNSUPPORTED_OPERATION"}


def test_graphormer_missing_required_inference_options_returns_validation_error(monkeypatch) -> None:
    registry = create_default_registry()
    service = ExecutionService(registry=registry, transport="stdio")

    original_create_adapter = registry.create_adapter

    def create_adapter_with_available_graphormer(name: str):
        adapter = original_create_adapter(name)
        if name == "graphormer_predict_property":
            monkeypatch.setattr(adapter, "check_availability", lambda: type("A", (), {"available": True})())
        return adapter

    monkeypatch.setattr(registry, "create_adapter", create_adapter_with_available_graphormer)

    response = service.execute_tool(
        "graphormer_predict_property",
        {
            "smiles": "CCO",
            "inference_options": {
                "graphormer_repo_path": "/tmp/graphormer-only",
            },
        },
    )

    assert response.success is False
    assert response.error is not None
    assert response.error.code == "INPUT_VALIDATION_FAILED"
    assert response.error.details == {
        "missing_inference_options": ["dataset_name", "dataset_source", "pretrained_model_name"]
    }


def test_dig_requires_explicit_workflow_options() -> None:
    registry = create_default_registry()
    service = ExecutionService(registry=registry, transport="stdio")

    response = service.execute_tool(
        "dig_sample_conformations",
        {"smiles": "CCO"},
    )

    assert response.success is False
    assert response.error is not None
    assert response.error.code == "UNSUPPORTED_OPERATION"


def test_dig_equilibrium_requires_explicit_workflow_options() -> None:
    registry = create_default_registry()
    service = ExecutionService(registry=registry, transport="stdio")

    response = service.execute_tool(
        "dig_predict_equilibrium",
        {},
    )

    assert response.success is False
    assert response.error is not None
    assert response.error.code == "UNSUPPORTED_OPERATION"

