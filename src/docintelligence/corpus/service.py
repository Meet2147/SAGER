from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from sklearn.preprocessing import normalize

from docintelligence.core.models import (
    AtomSupport,
    CorpusHit,
    CorpusQueryRequest,
    CorpusQueryResponse,
    DocumentDetailResponse,
    ProcessedDocument,
)
from docintelligence.corpus.index_store import index_exists, load_index
from docintelligence.graph.service import build_graph
from docintelligence.normalization.structure import infer_structure
from docintelligence.retrieval.service import assemble_context, build_context_program
from docintelligence.verification.service import verify_context


ROOT = Path(__file__).resolve().parents[3]
PROCESSED_DIR = ROOT / "data" / "processed"


@lru_cache(maxsize=1)
def load_processed_documents() -> list[ProcessedDocument]:
    documents: list[ProcessedDocument] = []
    for path in sorted(PROCESSED_DIR.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        document = ProcessedDocument.model_validate(payload)
        enriched_atoms = [infer_structure(atom) for atom in document.atoms]
        documents.append(document.model_copy(update={"atoms": enriched_atoms, "atom_count": len(enriched_atoms)}))
    return documents


def corpus_stats() -> dict[str, int]:
    documents = load_processed_documents()
    return {
        "document_count": len(documents),
        "atom_count": sum(doc.atom_count for doc in documents),
        "edge_count": sum(doc.edge_count for doc in documents),
    }


@lru_cache(maxsize=1)
def load_or_build_index() -> dict[str, object]:
    if index_exists():
        return load_index()
    from docintelligence.corpus.indexer import build_persistent_index

    return build_persistent_index()


def rebuild_index() -> dict[str, object]:
    load_or_build_index.cache_clear()
    from docintelligence.corpus.indexer import build_persistent_index

    return build_persistent_index()


def query_corpus(request: CorpusQueryRequest) -> CorpusQueryResponse:
    documents = {document.doc_id: document for document in load_processed_documents()}
    index = load_or_build_index()
    doc_vectorizer = index["doc_vectorizer"]
    doc_matrix = index["doc_matrix"]
    atom_vectorizer = index["atom_vectorizer"]
    atom_matrix = index["atom_matrix"]
    doc_records = index["doc_records"]
    atom_records = index["atom_records"]

    doc_query = normalize(doc_vectorizer.transform([request.query]))
    atom_query = normalize(atom_vectorizer.transform([request.query]))
    doc_scores = (doc_matrix @ doc_query.T).toarray().ravel()
    atom_scores = (atom_matrix @ atom_query.T).toarray().ravel()

    top_doc_scores: dict[str, float] = {}
    for idx, record in enumerate(doc_records):
        top_doc_scores[record["doc_id"]] = float(doc_scores[idx])

    # Use top atom matches to boost documents whose specific evidence atoms align strongly.
    for idx in atom_scores.argsort()[-200:]:
        atom_record = atom_records[int(idx)]
        boost = float(atom_scores[int(idx)]) * 0.35
        doc_id = atom_record["doc_id"]
        top_doc_scores[doc_id] = top_doc_scores.get(doc_id, 0.0) + boost

    ranked = sorted(top_doc_scores.items(), key=lambda item: item[1], reverse=True)

    hits: list[CorpusHit] = []
    program = build_context_program(request.query, request.task_type)
    for doc_id, score in ranked:
        if score <= 0:
            continue
        document = documents[doc_id]

        graph, _edges = build_graph(document.atoms)
        context_atoms = assemble_context(
            request.query,
            document.atoms,
            graph,
            program,
        )
        verification = verify_context(request.query, context_atoms)
        if not verification.support_atom_ids:
            continue

        hits.append(
            CorpusHit(
                doc_id=document.doc_id,
                source_path=document.source_path,
                page_count=document.page_count,
                score=round(score, 2),
                support_atom_ids=verification.support_atom_ids,
                snippet=verification.answer[:280],
                verification_status=verification.verification_status,
                support_pages=sorted({atom.page for atom in context_atoms[:3]}),
                top_structure_labels=_top_structure_labels(document),
            )
        )
        if len(hits) >= request.top_k:
            break

    return CorpusQueryResponse(
        query=request.query,
        total_docs=len(documents),
        returned_hits=len(hits),
        hits=hits,
    )


def get_document_detail(doc_id: str, sample_size: int = 25) -> DocumentDetailResponse | None:
    for document in load_processed_documents():
        if document.doc_id != doc_id:
            continue
        return DocumentDetailResponse(
            doc_id=document.doc_id,
            source_path=document.source_path,
            page_count=document.page_count,
            atom_count=document.atom_count,
            edge_count=document.edge_count,
            sample_atoms=[
                AtomSupport(
                    atom_id=atom.atom_id,
                    page=atom.page,
                    atom_type=atom.atom_type,
                    role_label=atom.role_label,
                    text=atom.text,
                    confidence=atom.confidence,
                )
                for atom in document.atoms[:sample_size]
            ],
        )
    return None


def _top_structure_labels(document: ProcessedDocument) -> list[str]:
    counts: dict[str, int] = {}
    for atom in document.atoms:
        label = atom.role_label or "body"
        counts[label] = counts.get(label, 0) + 1
    return [label for label, _count in sorted(counts.items(), key=lambda item: item[1], reverse=True)[:4]]
