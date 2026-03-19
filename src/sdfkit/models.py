from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SDFAtom:
    atom_id: str
    doc_id: str
    page: int
    atom_type: str
    text: str
    reading_order: int
    parser_source: str
    confidence: float
    role_label: str | None
    bbox: dict[str, float] | None = None


@dataclass(frozen=True)
class SDFEdge:
    source: str
    target: str
    edge_type: str
    weight: float


class SDFDocument:
    def __init__(self, path: str, payload: dict[str, Any], atoms: list[SDFAtom], edges: list[SDFEdge]):
        self.path = Path(path)
        self.payload = payload
        self.format = payload.get("format", "SDF")
        self.version = payload.get("version", "unknown")
        self.method = payload.get("method", {})
        self.source = payload.get("source", {})
        self.stats = payload.get("stats", {})
        self.annotations = payload.get("annotations", {})
        self.atoms = atoms
        self.edges = edges

    @property
    def doc_id(self) -> str:
        return self.source.get("doc_id", self.path.stem)

    @property
    def page_count(self) -> int:
        return int(self.source.get("page_count", 0))
