from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer

from docintelligence.graph.service import build_graph
from docintelligence.ingestion.service import ingest_pdf
from docintelligence.normalization.service import normalize_atoms


def process_pdf_directory(
    source_dir: str | Path,
    output_dir: str | Path,
    dataset_name: str = "dataset",
) -> dict[str, object]:
    source_root = Path(source_dir).expanduser().resolve()
    output_root = Path(output_dir).expanduser().resolve()
    docs_dir = output_root / "documents"
    indexes_dir = output_root / "indexes"
    docs_dir.mkdir(parents=True, exist_ok=True)
    indexes_dir.mkdir(parents=True, exist_ok=True)

    pdf_paths = sorted(path for path in source_root.rglob("*") if path.is_file() and path.suffix.lower() == ".pdf")

    documents: list[dict[str, object]] = []
    failures: list[dict[str, str]] = []
    for pdf_path in pdf_paths:
        try:
            document = process_single_pdf(pdf_path=pdf_path, source_root=source_root, output_dir=docs_dir, dataset_name=dataset_name)
            documents.append(document)
        except Exception as exc:  # pragma: no cover - batch resiliency
            failures.append({"source_path": str(pdf_path), "error": str(exc)})

    semantic_index = _build_semantic_index(documents)
    structural_index = _build_structural_index(documents)
    spatial_index = _build_spatial_index(documents)

    semantic_path = indexes_dir / "semantic_index.json"
    structural_path = indexes_dir / "structural_index.json"
    spatial_path = indexes_dir / "spatial_index.json"
    manifest_path = output_root / "manifest.json"

    semantic_path.write_text(json.dumps(semantic_index, indent=2), encoding="utf-8")
    structural_path.write_text(json.dumps(structural_index, indent=2), encoding="utf-8")
    spatial_path.write_text(json.dumps(spatial_index, indent=2), encoding="utf-8")

    manifest = {
        "dataset_name": dataset_name,
        "source_dir": str(source_root),
        "output_dir": str(output_root),
        "pdf_count": len(pdf_paths),
        "processed_count": len(documents),
        "failure_count": len(failures),
        "documents": [
            {
                "doc_id": document["doc_id"],
                "source_path": document["source_path"],
                "artifact_path": document["artifact_path"],
                "page_count": document["page_count"],
                "atom_count": document["atom_count"],
                "edge_count": document["edge_count"],
            }
            for document in documents
        ],
        "failures": failures,
        "index_paths": {
            "semantic": str(semantic_path),
            "structural": str(structural_path),
            "spatial": str(spatial_path),
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def process_single_pdf(
    pdf_path: str | Path,
    source_root: str | Path,
    output_dir: str | Path,
    dataset_name: str,
) -> dict[str, object]:
    pdf_path = Path(pdf_path).resolve()
    source_root = Path(source_root).resolve()
    output_dir = Path(output_dir).resolve()

    relative_path = pdf_path.relative_to(source_root).with_suffix("")
    doc_id = f"{dataset_name}__{'__'.join(part.replace(' ', '_') for part in relative_path.parts)}"

    _original_doc_id, page_count, raw_atoms = ingest_pdf(str(pdf_path))
    raw_atoms = [
        atom.model_copy(
            update={
                "doc_id": doc_id,
                "atom_id": atom.atom_id.replace(atom.doc_id, doc_id, 1),
                # Placeholder parser metadata for OCR/layout/VLM/table stages in the prototype.
                "parser_source": "ocr+layout+vlm+table-prototype",
            }
        )
        for atom in raw_atoms
    ]
    atoms = normalize_atoms(raw_atoms)
    _graph, edges = build_graph(atoms)

    payload = {
        "dataset_name": dataset_name,
        "doc_id": doc_id,
        "source_path": str(pdf_path),
        "pipeline_stages": [
            "receive_document",
            "run_ocr_layout_vlm_table_parsers",
            "normalize_into_evidence_atoms",
            "attach_metadata",
            "construct_evidence_graph",
            "build_semantic_structural_spatial_indexes",
        ],
        "page_count": page_count,
        "atom_count": len(atoms),
        "edge_count": len(edges),
        "atoms": [atom.model_dump(mode="json") for atom in atoms],
        "edges": [edge.model_dump(mode="json") for edge in edges],
    }
    artifact_path = output_dir / f"{doc_id}.json"
    artifact_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    return {
        "doc_id": doc_id,
        "source_path": str(pdf_path),
        "artifact_path": str(artifact_path),
        "page_count": page_count,
        "atom_count": len(atoms),
        "edge_count": len(edges),
        "atoms": payload["atoms"],
        "edges": payload["edges"],
    }


def _build_semantic_index(documents: list[dict[str, object]]) -> dict[str, object]:
    if not documents:
        return {"kind": "semantic", "document_count": 0, "atom_count": 0, "vocabulary": [], "documents": []}

    atom_texts = [atom["text"] for document in documents for atom in document["atoms"] if atom["text"].strip()]
    if not atom_texts:
        return {"kind": "semantic", "document_count": len(documents), "atom_count": 0, "vocabulary": [], "documents": []}

    vectorizer = TfidfVectorizer(lowercase=True, stop_words="english", ngram_range=(1, 2), min_df=1, max_features=5000)
    matrix = vectorizer.fit_transform(atom_texts)
    feature_names = vectorizer.get_feature_names_out()

    doc_entries: list[dict[str, object]] = []
    atom_offset = 0
    for document in documents:
        atom_count = len(document["atoms"])
        doc_matrix = matrix[atom_offset : atom_offset + atom_count]
        scores = doc_matrix.sum(axis=0).A1 if atom_count else []
        top_terms: list[str] = []
        if atom_count:
            ranked = scores.argsort()[::-1][:20]
            top_terms = [feature_names[index] for index in ranked if scores[index] > 0]
        doc_entries.append(
            {
                "doc_id": document["doc_id"],
                "source_path": document["source_path"],
                "top_terms": top_terms[:10],
            }
        )
        atom_offset += atom_count

    vocab_scores = matrix.sum(axis=0).A1
    top_vocab = [feature_names[index] for index in vocab_scores.argsort()[::-1][:200] if vocab_scores[index] > 0]
    return {
        "kind": "semantic",
        "document_count": len(documents),
        "atom_count": len(atom_texts),
        "vocabulary": top_vocab,
        "documents": doc_entries,
    }


def _build_structural_index(documents: list[dict[str, object]]) -> dict[str, object]:
    role_to_atoms: dict[str, list[dict[str, object]]] = defaultdict(list)
    type_to_atoms: dict[str, list[dict[str, object]]] = defaultdict(list)
    page_sections: dict[str, list[dict[str, object]]] = defaultdict(list)

    for document in documents:
        for atom in document["atoms"]:
            entry = {
                "doc_id": document["doc_id"],
                "atom_id": atom["atom_id"],
                "page": atom["page"],
                "text": atom["text"][:200],
            }
            role_to_atoms[atom.get("role_label") or "body"].append(entry)
            type_to_atoms[atom["atom_type"]].append(entry)
            page_sections[f"{document['doc_id']}::page_{atom['page']}"].append(entry)

    return {
        "kind": "structural",
        "roles": {role: entries for role, entries in sorted(role_to_atoms.items())},
        "atom_types": {atom_type: entries for atom_type, entries in sorted(type_to_atoms.items())},
        "page_map": {page_key: entries for page_key, entries in sorted(page_sections.items())},
    }


def _build_spatial_index(documents: list[dict[str, object]]) -> dict[str, object]:
    page_regions: dict[str, dict[str, list[dict[str, object]]]] = {}

    for document in documents:
        per_page: dict[str, list[dict[str, object]]] = defaultdict(list)
        for atom in document["atoms"]:
            bbox = atom.get("bbox")
            region = _region_for_bbox(bbox)
            per_page[f"page_{atom['page']}"].append(
                {
                    "atom_id": atom["atom_id"],
                    "region": region,
                    "bbox": bbox,
                    "role_label": atom.get("role_label"),
                    "confidence": atom.get("confidence"),
                }
            )
        page_regions[document["doc_id"]] = dict(per_page)

    return {
        "kind": "spatial",
        "documents": page_regions,
    }


def _region_for_bbox(bbox: dict[str, float] | None) -> str:
    if not bbox:
        return "unknown"
    center_y = (bbox["y0"] + bbox["y1"]) / 2
    if center_y < 200:
        return "upper"
    if center_y < 500:
        return "middle"
    return "lower"
