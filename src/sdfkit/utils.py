from __future__ import annotations

from pathlib import Path


def is_sdf_file(path: str) -> bool:
    return Path(path).suffix.lower() == ".sdf"
