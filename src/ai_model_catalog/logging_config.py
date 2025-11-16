from __future__ import annotations

import logging
import os
from pathlib import Path

_SILENT = logging.CRITICAL + 1
_LEVEL_MAP = {"0": _SILENT, "1": logging.INFO, "2": logging.DEBUG}


def configure_logging() -> None:
    """
    Configure root logging from env:
      - LOG_LEVEL: "0" (silent, default), "1" (info), "2" (debug).
      - LOG_FILE: filesystem path. If missing or level==0, no logging is emitted.
    """
    level_str = (os.getenv("LOG_LEVEL") or "0").strip()
    level = _LEVEL_MAP.get(level_str, _SILENT)

    root = logging.getLogger()
    # avoid duplicate handlers if called more than once
    for h in list(root.handlers):
        root.removeHandler(h)
    root.setLevel(level)

    path = os.getenv("LOG_FILE")
    if not path:
        return  # no log file specified

    # For LOG_LEVEL=0, create empty log file if LOG_FILE is specified
    if level == _SILENT:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.touch()  # Create empty file
        return

    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    fh = logging.FileHandler(p, encoding="utf-8")
    fh.setLevel(level)
    fh.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s %(levelname)s %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    root.addHandler(fh)
