from __future__ import annotations

import logging
import sys


def configure_logging(level: str = "info", transport: str = "stdio") -> None:
    logger = logging.getLogger()
    logger.handlers.clear()
    handler = logging.StreamHandler(sys.stderr if transport == "stdio" else sys.stdout)
    handler.setFormatter(logging.Formatter("%(levelname)s %(name)s %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(level.upper())
