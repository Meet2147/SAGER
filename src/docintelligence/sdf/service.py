from __future__ import annotations

import json
import tempfile
from collections import Counter
from pathlib import Path

from docintelligence.core.models import EvidenceAtom, EvidenceEdge, ProcessedDocument
from docintelligence.graph.service import build_graph
from docintelligence.ingestion.service import ingest_pdf
from docintelligence.indexing.service import lexical_score
from docintelligence.normalization.service import normalize_atoms


def convert_processed_json_to_sdf(processed_json_path: str, output_path: str | None = None) -> Path:
    source_path = Path(processed_json_path)
    payload = _load_json_with_fallbacks(source_path)
    if "atoms" not in payload or "edges" not in payload:
        raise ValueError(
            f"{source_path} does not look like a processed SAGER artifact. "
            "Expected top-level 'atoms' and 'edges' fields."
        )
    document = ProcessedDocument.model_validate(payload)

    role_distribution = Counter(atom.role_label or "body" for atom in document.atoms)

    sdf_payload = {
        "format": "SDF",
        "version": "0.1",
        "method": {
            "name": "SAGER",
            "expanded": "Structure-Aware Graph Evidence Retrieval",
        },
        "source": {
            "path": document.source_path,
            "doc_id": document.doc_id,
            "page_count": document.page_count,
        },
        "stats": {
            "atom_count": document.atom_count,
            "edge_count": document.edge_count,
            "extracted_text_chars": document.extracted_text_chars,
        },
        "atoms": [atom.model_dump() for atom in document.atoms],
        "edges": [edge.model_dump() for edge in document.edges],
        "annotations": {
            "role_distribution": dict(role_distribution),
            "notes": [
                "Generated from SAGER processed artifact.",
                "Intended as a retrieval-native derivative document format.",
            ],
        },
    }

    out_path = Path(output_path) if output_path else source_path.with_suffix(".sdf")
    out_path.write_text(json.dumps(sdf_payload, indent=2), encoding="utf-8")
    return out_path


def convert_pdf_to_sdf(pdf_path: str, output_path: str | None = None) -> Path:
    source_path = Path(pdf_path)
    doc_id, page_count, raw_atoms = ingest_pdf(str(source_path))
    atoms = normalize_atoms(raw_atoms)
    _graph, edges = build_graph(atoms)

    payload = {
        "doc_id": doc_id,
        "source_path": str(source_path),
        "page_count": page_count,
        "atom_count": len(atoms),
        "edge_count": len(edges),
        "extracted_text_chars": sum(len(atom.text) for atom in atoms),
        "atoms": [atom.model_dump() for atom in atoms],
        "edges": [edge.model_dump() for edge in edges],
    }

    temp_json = Path(tempfile.gettempdir()) / f"{source_path.stem}.processed.json"
    temp_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    try:
        return convert_processed_json_to_sdf(str(temp_json), output_path)
    finally:
        if temp_json.exists():
            temp_json.unlink()


def load_sdf(path: str) -> dict[str, object]:
    return _load_json_with_fallbacks(Path(path))


def query_sdf(path: str, query: str, top_k: int = 5) -> dict[str, object]:
    sdf = load_sdf(path)
    atoms = [EvidenceAtom.model_validate(atom) for atom in sdf["atoms"]]
    edges = [EvidenceEdge.model_validate(edge) for edge in sdf["edges"]]

    ranked = sorted(
        atoms,
        key=lambda atom: (lexical_score(query, atom), atom.confidence),
        reverse=True,
    )
    top_atoms = ranked[:top_k]
    support_ids = {atom.atom_id for atom in top_atoms}

    # Pull directly connected neighbors to demonstrate graph-aware retrieval over SDF.
    for edge in edges:
        if edge.source in support_ids and edge.target not in support_ids and len(top_atoms) < top_k + 3:
            neighbor = next((atom for atom in atoms if atom.atom_id == edge.target), None)
            if neighbor is not None:
                top_atoms.append(neighbor)
                support_ids.add(neighbor.atom_id)

    return {
        "format": sdf["format"],
        "doc_id": sdf["source"]["doc_id"],
        "query": query,
        "results": [
            {
                "atom_id": atom.atom_id,
                "page": atom.page,
                "role_label": atom.role_label,
                "text": atom.text,
                "confidence": atom.confidence,
            }
            for atom in top_atoms
        ],
    }


def _load_json_with_fallbacks(path: Path) -> dict[str, object]:
    encodings = ["utf-8", "utf-8-sig", "cp1252", "latin-1"]
    last_error: Exception | None = None
    for encoding in encodings:
        try:
            return json.loads(path.read_text(encoding=encoding))
        except UnicodeDecodeError as error:
            last_error = error
            continue
        except json.JSONDecodeError as error:
            # The bytes were decodable, but the file is not valid JSON.
            raise ValueError(f"{path} is not valid JSON: {error}") from error

    raise ValueError(f"Unable to decode JSON file {path}: {last_error}") from last_error
