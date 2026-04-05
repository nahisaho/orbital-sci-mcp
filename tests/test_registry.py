from __future__ import annotations

from orbital_sci_mcp.registry import create_default_registry


def test_registry_domain_filtering() -> None:
    registry = create_default_registry()
    registry.configure(enabled_domains=["materials"])

    tools = registry.list_all()

    assert tools
    assert all(tool.domain == "materials" for tool in tools)


def test_registry_tool_filters_disable_tool() -> None:
    registry = create_default_registry()
    registry.configure(disabled_tools=["mattersim_predict_energy"])

    names = [tool.name for tool in registry.list_all()]

    assert "mattersim_predict_energy" not in names
    assert "mace_predict_energy" in names
