from __future__ import annotations

from argparse import Namespace

from orbital_sci_mcp.cli import build_config


def test_build_config_applies_cli_overrides() -> None:
    args = Namespace(
        transport="http",
        host="0.0.0.0",
        port=8123,
        name="Test Server",
        compact_mode=True,
        log_level="debug",
        enable_domain=["materials", "proteins"],
        enable_tool=["mattersim_predict_energy"],
        disable_tool=["bioemu_sample_ensemble"],
        default_timeout=120,
    )

    config = build_config(args)

    assert config.transport == "http"
    assert config.host == "0.0.0.0"
    assert config.port == 8123
    assert config.server_name == "Test Server"
    assert config.compact_mode is True
    assert config.log_level == "debug"
    assert config.enabled_domains == ["materials", "proteins"]
    assert config.enabled_tools == ["mattersim_predict_energy"]
    assert config.disabled_tools == ["bioemu_sample_ensemble"]
    assert config.default_timeout == 120
