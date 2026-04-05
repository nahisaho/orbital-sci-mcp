from __future__ import annotations

import argparse

from .config import AppConfig
from .logging_config import configure_logging
from .server import run_server


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Orbital Sci MCP server.")
    parser.add_argument("--transport", choices=["stdio", "http"], default=None)
    parser.add_argument("--host", default=None)
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--name", default=None)
    parser.add_argument("--compact-mode", action="store_true")
    parser.add_argument("--log-level", default=None)
    parser.add_argument("--enable-domain", action="append", default=None)
    parser.add_argument("--enable-tool", action="append", default=None)
    parser.add_argument("--disable-tool", action="append", default=None)
    parser.add_argument("--default-timeout", type=int, default=None)
    return parser.parse_args()


def build_config(args: argparse.Namespace) -> AppConfig:
    config = AppConfig.from_env()
    updates = {}
    if args.transport is not None:
        updates["transport"] = args.transport
    if args.host is not None:
        updates["host"] = args.host
    if args.port is not None:
        updates["port"] = args.port
    if args.name is not None:
        updates["server_name"] = args.name
    if args.log_level is not None:
        updates["log_level"] = args.log_level
    if args.compact_mode:
        updates["compact_mode"] = True
    if args.enable_domain is not None:
        updates["enabled_domains"] = args.enable_domain
    if args.enable_tool is not None:
        updates["enabled_tools"] = args.enable_tool
    if args.disable_tool is not None:
        updates["disabled_tools"] = args.disable_tool
    if args.default_timeout is not None:
        updates["default_timeout"] = args.default_timeout
    return config.model_copy(update=updates)


def main() -> None:
    args = parse_args()
    config = build_config(args)
    configure_logging(level=config.log_level, transport=config.transport)
    run_server(config)


if __name__ == "__main__":
    main()