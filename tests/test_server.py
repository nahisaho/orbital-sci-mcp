from __future__ import annotations

from orbital_sci_mcp.config import AppConfig
from orbital_sci_mcp.registry import create_default_registry
from orbital_sci_mcp.server import create_server


class FakeFastMCP:
    def __init__(self, name: str) -> None:
        self.name = name
        self.registered: list[str] = []

    def tool(self, name: str):
        def decorator(func):
            self.registered.append(name)
            return func

        return decorator


def test_create_server_compact_mode_registers_only_discovery_tools(monkeypatch) -> None:
    monkeypatch.setattr("orbital_sci_mcp.server._load_fastmcp", lambda: FakeFastMCP)

    config = AppConfig(compact_mode=True)
    registry = create_default_registry()

    server = create_server(config=config, registry=registry)

    assert sorted(server.registered) == sorted(
        ["list_tools", "get_tool_info", "search_tools", "execute_tool"]
    )


def test_create_server_registers_individual_tools_when_not_compact(monkeypatch) -> None:
    monkeypatch.setattr("orbital_sci_mcp.server._load_fastmcp", lambda: FakeFastMCP)

    config = AppConfig(compact_mode=False)
    registry = create_default_registry()

    server = create_server(config=config, registry=registry)

    assert "execute_tool" in server.registered
    assert "mattersim_predict_energy" in server.registered
    assert "bioemu_sample_ensemble" in server.registered