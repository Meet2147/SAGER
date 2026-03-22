from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class AtomType(str, Enum):
    TEXT = "text"
    SECTION = "section"
    TABLE_CELL = "table_cell"
    TABLE_HEADER = "table_header"
    CAPTION = "caption"
    FOOTNOTE = "footnote"
    CITATION = "citation"


class BBox(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float


class EvidenceAtom(BaseModel):
    atom_id: str
    doc_id: str
    page: int
    atom_type: AtomType
    text: str
    bbox: BBox | None = None
    reading_order: int = 0
    parser_source: str
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    role_label: str | None = None


class EvidenceEdge(BaseModel):
    source: str
    target: str
    edge_type: str
    weight: float = 1.0
