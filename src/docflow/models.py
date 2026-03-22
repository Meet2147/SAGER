from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from docintelligence.core.models import EvidenceAtom, EvidenceEdge


@dataclass
class DocumentRecord:
    doc_id: str
    source_path: str
    file_type: str
    page_count: int
    atoms: list[EvidenceAtom] = field(default_factory=list)
    edges: list[EvidenceEdge] = field(default_factory=list)


@dataclass
class FlowContext:
    root_dir: Path
    flow_dir: Path
    inputs: dict[str, Any]
    variables: dict[str, Any]
    store: dict[str, Any] = field(default_factory=dict)
