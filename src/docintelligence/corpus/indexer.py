from __future__ import annotations

from collections import Counter

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

from docintelligence.core.models import ProcessedDocument
from docintelligence.corpus.index_store import save_index
from docintelligence.corpus.service import load_processed_documents


def build_persistent_index() -> dict[str, object]:
    documents = load_processed_documents()
    doc_texts = [_document_text(document) for document in documents]
    atom_texts = [atom.text for document in documents for atom in document.atoms]

    doc_vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        min_df=2,
        max_features=40000,
    )
    atom_vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        min_df=2,
        max_features=60000,
    )

    doc_matrix = normalize(doc_vectorizer.fit_transform(doc_texts))
    atom_matrix = normalize(atom_vectorizer.fit_transform(atom_texts))

    atom_records: list[dict[str, object]] = []
    structure_counts: dict[str, Counter[str]] = {}
    atom_offset = 0
    for document in documents:
        counts = Counter(atom.role_label or "body" for atom in document.atoms)
        structure_counts[document.doc_id] = counts
        for atom in document.atoms:
            atom_records.append(
                {
                    "doc_id": document.doc_id,
                    "atom_id": atom.atom_id,
                    "page": atom.page,
                    "text": atom.text,
                    "role_label": atom.role_label,
                    "atom_type": atom.atom_type.value,
                    "confidence": atom.confidence,
                    "atom_index": atom_offset,
                    "source_path": document.source_path,
                }
            )
            atom_offset += 1

    payload = {
        "doc_vectorizer": doc_vectorizer,
        "doc_matrix": doc_matrix,
        "atom_vectorizer": atom_vectorizer,
        "atom_matrix": atom_matrix,
        "doc_records": [
            {
                "doc_id": document.doc_id,
                "source_path": document.source_path,
                "page_count": document.page_count,
                "atom_count": document.atom_count,
                "edge_count": document.edge_count,
                "extracted_text_chars": document.extracted_text_chars,
                "top_structure_labels": [label for label, _count in structure_counts[document.doc_id].most_common(4)],
            }
            for document in documents
        ],
        "atom_records": atom_records,
    }
    index_path = save_index(payload)
    payload["index_path"] = str(index_path)
    return payload


def _document_text(document: ProcessedDocument) -> str:
    weighted_lines: list[str] = []
    for atom in document.atoms:
        text = atom.text.strip()
        if not text:
            continue
        weight = 3 if atom.role_label == "heading" else 2 if atom.role_label in {"figure_caption", "table_caption"} else 1
        weighted_lines.extend([text] * weight)
    return "\n".join(weighted_lines)
