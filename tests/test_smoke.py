from __future__ import annotations

import importlib.util
from argparse import Namespace

import pytest

from orbital_sci_mcp.cli import main
from orbital_sci_mcp.config import AppConfig
from orbital_sci_mcp.server import create_server


def test_cli_main_configures_logging_and_runs_server(monkeypatch) -> None:
    captured: dict[str, AppConfig] = {}

    monkeypatch.setattr(
        "orbital_sci_mcp.cli.parse_args",
        lambda: Namespace(
            transport="http",
            host="0.0.0.0",
            port=7100,
            name="Smoke Test Server",
            compact_mode=True,
            log_level="debug",
            enable_domain=["materials"],
            enable_tool=None,
            disable_tool=["bioemu_sample_ensemble"],
            default_timeout=45,
        ),
    )

    def fake_configure_logging(level: str, transport: str) -> None:
        captured["logging"] = AppConfig(log_level=level, transport=transport)

    def fake_run_server(config: AppConfig) -> None:
        captured["server"] = config

    monkeypatch.setattr("orbital_sci_mcp.cli.configure_logging", fake_configure_logging)
    monkeypatch.setattr("orbital_sci_mcp.cli.run_server", fake_run_server)

    main()

    assert captured["logging"].log_level == "debug"
    assert captured["logging"].transport == "http"
    assert captured["server"].server_name == "Smoke Test Server"
    assert captured["server"].compact_mode is True
    assert captured["server"].enabled_domains == ["materials"]
    assert captured["server"].disabled_tools == ["bioemu_sample_ensemble"]
    assert captured["server"].default_timeout == 45


def test_create_server_with_fastmcp_when_installed() -> None:
    if importlib.util.find_spec("fastmcp") is None:
        pytest.skip("fastmcp is not installed in this environment")

    server = create_server(AppConfig(compact_mode=True))

    assert server is not None
