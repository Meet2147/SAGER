from __future__ import annotations

from enum import Enum
from typing import Literal

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


class ParserRun(BaseModel):
    parser_name: str
    parser_version: str = "prototype"
    confidence_profile: str = "default"


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


class ProcessedDocument(BaseModel):
    doc_id: str
    source_path: str
    page_count: int
    atom_count: int
    edge_count: int
    extracted_text_chars: int
    atoms: list[EvidenceAtom]
    edges: list["EvidenceEdge"]


class EvidenceEdge(BaseModel):
    source: str
    target: str
    edge_type: str
    weight: float = 1.0


class TaskType(str, Enum):
    FACT_LOOKUP = "fact_lookup"
    CLAUSE_EXTRACTION = "clause_extraction"
    TABLE_LOOKUP = "table_lookup"
    CROSS_PAGE = "cross_page"


class ContextProgram(BaseModel):
    task_type: TaskType
    seed_modes: list[str]
    expand_edges: list[str]
    max_hops: int = 1
    verification: list[str]


class IngestRequest(BaseModel):
    doc_id: str = "demo-doc"
    text: str
    parser_name: str = "demo-parser"


class QueryRequest(BaseModel):
    query: str
    task_type: TaskType | None = None


class QueryResponse(BaseModel):
    answer: str
    support_atom_ids: list[str]
    support_score: float
    verification_status: Literal["supported", "insufficient_support"]


class CorpusQueryRequest(BaseModel):
    query: str
    task_type: TaskType | None = None
    top_k: int = Field(default=5, ge=1, le=20)


class CorpusHit(BaseModel):
    doc_id: str
    source_path: str
    page_count: int
    score: float
    support_atom_ids: list[str]
    snippet: str
    verification_status: Literal["supported", "insufficient_support"]
    support_pages: list[int] = []
    top_structure_labels: list[str] = []


class CorpusQueryResponse(BaseModel):
    query: str
    total_docs: int
    returned_hits: int
    hits: list[CorpusHit]


class AtomSupport(BaseModel):
    atom_id: str
    page: int
    atom_type: AtomType
    role_label: str | None = None
    text: str
    confidence: float


class DocumentDetailResponse(BaseModel):
    doc_id: str
    source_path: str
    page_count: int
    atom_count: int
    edge_count: int
    sample_atoms: list[AtomSupport]
