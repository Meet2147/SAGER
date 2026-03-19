from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from docintelligence.core.models import (
    CorpusQueryRequest,
    CorpusQueryResponse,
    DocumentDetailResponse,
    IngestRequest,
    QueryRequest,
    QueryResponse,
)
from docintelligence.corpus.index_store import INDEX_PATH
from docintelligence.corpus.indexer import build_persistent_index
from docintelligence.corpus.service import corpus_stats, get_document_detail, query_corpus, rebuild_index
from docintelligence.graph.service import build_graph
from docintelligence.ingestion.service import ingest_pdf, ingest_text
from docintelligence.normalization.service import normalize_atoms
from docintelligence.retrieval.service import assemble_context, build_context_program
from docintelligence.verification.service import verify_context

app = FastAPI(title="DocIntelligence Prototype")
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[3] / "templates"))

STATE: dict[str, object] = {
    "atoms": [],
    "graph": None,
}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def search_ui(request: Request):
    return templates.TemplateResponse("search.html", {"request": request})


@app.get("/corpus/stats")
def get_corpus_stats() -> dict[str, int]:
    stats = corpus_stats()
    stats["index_exists"] = int(INDEX_PATH.exists())
    return stats


@app.post("/corpus/rebuild-index")
def rebuild_corpus_index() -> dict[str, object]:
    payload = rebuild_index()
    return {
        "index_path": payload["index_path"],
        "document_count": len(payload["doc_records"]),
        "atom_count": len(payload["atom_records"]),
    }


@app.get("/corpus/document/{doc_id}", response_model=DocumentDetailResponse)
def get_corpus_document(doc_id: str) -> DocumentDetailResponse:
    detail = get_document_detail(doc_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Document not found.")
    return detail


@app.post("/ingest")
def ingest(request: IngestRequest) -> dict[str, object]:
    raw_atoms = ingest_text(request)
    atoms = normalize_atoms(raw_atoms)
    graph, edges = build_graph(atoms)
    STATE["atoms"] = atoms
    STATE["graph"] = graph
    return {
        "doc_id": request.doc_id,
        "atom_count": len(atoms),
        "edge_count": len(edges),
    }


@app.post("/ingest-pdf")
def ingest_pdf_file(payload: dict[str, str]) -> dict[str, object]:
    path = payload.get("path")
    if not path:
        raise HTTPException(status_code=400, detail="Missing PDF path.")

    doc_id, page_count, raw_atoms = ingest_pdf(path)
    atoms = normalize_atoms(raw_atoms)
    graph, edges = build_graph(atoms)
    STATE["atoms"] = atoms
    STATE["graph"] = graph
    return {
        "doc_id": doc_id,
        "page_count": page_count,
        "atom_count": len(atoms),
        "edge_count": len(edges),
    }


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest) -> QueryResponse:
    atoms = STATE["atoms"]
    graph = STATE["graph"]
    if not atoms or graph is None:
        raise HTTPException(status_code=400, detail="No document ingested yet.")

    program = build_context_program(request.query, request.task_type)
    context_atoms = assemble_context(request.query, atoms, graph, program)
    return verify_context(request.query, context_atoms)


@app.post("/query-corpus", response_model=CorpusQueryResponse)
def query_processed_corpus(request: CorpusQueryRequest) -> CorpusQueryResponse:
    return query_corpus(request)
