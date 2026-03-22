from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer

from docflow.adapters import parse_document
from docflow._graph import build_graph
from docflow._normalize import normalize_atoms
from docflow.models import DocumentRecord, FlowContext


def scan_documents(context: FlowContext, config: dict[str, object]) -> list[str]:
    source_dir = _resolve_path(context, str(config["source_dir"]))
    file_types = {value.lower().lstrip(".") for value in config.get("file_types", ["pdf"])}
    if source_dir.is_file():
        paths = [str(source_dir)] if source_dir.suffix.lower().lstrip(".") in file_types else []
        return paths

    paths = [
        str(path)
        for path in sorted(source_dir.rglob("*"))
        if path.is_file() and path.suffix.lower().lstrip(".") in file_types
    ]
    return paths


def parse_documents(context: FlowContext, config: dict[str, object], inputs: list[object]) -> list[DocumentRecord]:
    dataset_name = _render(str(config.get("dataset_name", "docflow")), context)
    records: list[DocumentRecord] = []
    parse_errors: list[dict[str, str]] = context.store.setdefault("parse_errors", [])
    for input_value in inputs:
        for path in _as_sequence(input_value):
            try:
                records.append(parse_document(path, dataset_name=dataset_name))
            except Exception as exc:
                parse_errors.append({"path": str(path), "error": str(exc)})
    return records


def normalize_atoms_step(context: FlowContext, config: dict[str, object], inputs: list[object]) -> list[DocumentRecord]:
    records = _flatten_records(inputs)
    for record in records:
        record.atoms = normalize_atoms(record.atoms)
    return records


def enrich_metadata(context: FlowContext, config: dict[str, object], inputs: list[object]) -> list[DocumentRecord]:
    records = _flatten_records(inputs)
    for record in records:
        for atom in record.atoms:
            atom.parser_source = f"{atom.parser_source}+docflow"
            atom.confidence = min(1.0, max(atom.confidence, 0.76))
            if atom.role_label is None:
                atom.role_label = "body"
    return records


def build_evidence_graph_step(context: FlowContext, config: dict[str, object], inputs: list[object]) -> list[DocumentRecord]:
    records = _flatten_records(inputs)
    for record in records:
        _graph, edges = build_graph(record.atoms)
        record.edges = edges
    return records


def build_indexes(context: FlowContext, config: dict[str, object], inputs: list[object]) -> dict[str, object]:
    records = _flatten_records(inputs)
    semantic = _semantic_index(records)
    structural = _structural_index(records)
    spatial = _spatial_index(records)
    return {"semantic": semantic, "structural": structural, "spatial": spatial}


def write_outputs(context: FlowContext, config: dict[str, object], inputs: list[object]) -> dict[str, object]:
    output_dir = _resolve_path(context, str(config.get("output_dir", "docflow_runs/default")))
    output_dir.mkdir(parents=True, exist_ok=True)

    records = _flatten_records(inputs[:-1]) if len(inputs) > 1 else _flatten_records(inputs)
    indexes = inputs[-1] if inputs and isinstance(inputs[-1], dict) and {"semantic", "structural", "spatial"} <= set(inputs[-1]) else {}

    docs_dir = output_dir / "documents"
    indexes_dir = output_dir / "indexes"
    text_dir = output_dir / "text"
    docs_dir.mkdir(parents=True, exist_ok=True)
    indexes_dir.mkdir(parents=True, exist_ok=True)
    text_dir.mkdir(parents=True, exist_ok=True)

    for record in records:
        payload = {
            "doc_id": record.doc_id,
            "source_path": record.source_path,
            "file_type": record.file_type,
            "page_count": record.page_count,
            "atom_count": len(record.atoms),
            "edge_count": len(record.edges),
            "atoms": [atom.model_dump(mode="json") for atom in record.atoms],
            "edges": [edge.model_dump(mode="json") for edge in record.edges],
        }
        (docs_dir / f"{record.doc_id}.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
        (text_dir / f"{record.doc_id}.txt").write_text(_record_to_plain_text(record), encoding="utf-8")

    manifest = {
        "document_count": len(records),
        "error_count": len(context.store.get("parse_errors", [])),
        "documents": [
            {
                "doc_id": record.doc_id,
                "source_path": record.source_path,
                "file_type": record.file_type,
                "page_count": record.page_count,
                "atom_count": len(record.atoms),
                "edge_count": len(record.edges),
            }
            for record in records
        ],
        "errors": context.store.get("parse_errors", []),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    if indexes:
        for name, payload in indexes.items():
            (indexes_dir / f"{name}_index.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    return {"output_dir": str(output_dir), "manifest_path": str(output_dir / "manifest.json")}


STEP_REGISTRY = {
    "scan_documents": scan_documents,
    "parse_documents": parse_documents,
    "normalize_atoms": normalize_atoms_step,
    "enrich_metadata": enrich_metadata,
    "build_evidence_graph": build_evidence_graph_step,
    "build_indexes": build_indexes,
    "write_outputs": write_outputs,
}


def _resolve_path(context: FlowContext, raw: str) -> Path:
    expanded = _render(raw, context)
    path = Path(expanded).expanduser()
    return path if path.is_absolute() else (context.root_dir / path).resolve()


def _render(value: str, context: FlowContext) -> str:
    rendered = value
    for key, val in context.variables.items():
        rendered = rendered.replace("${" + key + "}", str(val))
    for key, val in context.inputs.items():
        rendered = rendered.replace("${inputs." + key + "}", str(val))
    return rendered


def _flatten_records(inputs: list[object]) -> list[DocumentRecord]:
    records: list[DocumentRecord] = []
    for input_value in inputs:
        for item in _as_sequence(input_value):
            if isinstance(item, DocumentRecord):
                records.append(item)
    return records


def _as_sequence(value: object) -> list[object]:
    if isinstance(value, list):
        return value
    return [value]


def _semantic_index(records: list[DocumentRecord]) -> dict[str, object]:
    texts = ["\n".join(atom.text for atom in record.atoms if atom.text.strip()) for record in records]
    if not any(texts):
        return {"kind": "semantic", "documents": []}
    vectorizer = TfidfVectorizer(lowercase=True, stop_words="english", ngram_range=(1, 2), min_df=1, max_features=3000)
    matrix = vectorizer.fit_transform(texts)
    feature_names = vectorizer.get_feature_names_out()
    documents: list[dict[str, object]] = []
    for idx, record in enumerate(records):
        row = matrix[idx].toarray()[0]
        top_terms = [feature_names[pos] for pos in row.argsort()[::-1][:10] if row[pos] > 0]
        documents.append({"doc_id": record.doc_id, "top_terms": top_terms})
    return {"kind": "semantic", "documents": documents}


def _structural_index(records: list[DocumentRecord]) -> dict[str, object]:
    roles: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in records:
        for atom in record.atoms:
            roles[atom.role_label or "body"].append({"doc_id": record.doc_id, "atom_id": atom.atom_id, "page": atom.page})
    return {"kind": "structural", "roles": dict(sorted(roles.items()))}


def _spatial_index(records: list[DocumentRecord]) -> dict[str, object]:
    docs: dict[str, dict[str, list[dict[str, object]]]] = {}
    for record in records:
        pages: dict[str, list[dict[str, object]]] = defaultdict(list)
        for atom in record.atoms:
            bbox = atom.bbox.model_dump() if atom.bbox else None
            pages[f"page_{atom.page}"].append({"atom_id": atom.atom_id, "bbox": bbox})
        docs[record.doc_id] = dict(pages)
    return {"kind": "spatial", "documents": docs}


def _record_to_plain_text(record: DocumentRecord) -> str:
    atoms = sorted(record.atoms, key=lambda atom: (atom.page, atom.reading_order, atom.atom_id))
    pages: dict[int, list[str]] = defaultdict(list)
    previous_page = None
    previous_role = None

    for atom in atoms:
        text = " ".join(atom.text.split())
        if not text:
            continue

        lines = pages[atom.page]
        if previous_page is not None and atom.page != previous_page and lines:
            lines.append("")

        current_role = atom.role_label or "body"
        if lines and _needs_spacing(previous_role, current_role):
            lines.append("")

        lines.append(text)
        previous_page = atom.page
        previous_role = current_role

    page_blocks = [_collapse_blank_lines(pages[page]) for page in sorted(pages)]
    text = "\n\n".join(block for block in page_blocks if block).strip()
    return f"{text}\n" if text else ""


def _needs_spacing(previous_role: str | None, current_role: str) -> bool:
    prev = previous_role or "body"
    if current_role in {"heading", "table_caption", "figure_caption"}:
        return True
    return prev in {"heading", "table_caption", "figure_caption"} and current_role == "body"


def _collapse_blank_lines(lines: list[str]) -> str:
    collapsed: list[str] = []
    for line in lines:
        if line == "" and (not collapsed or collapsed[-1] == ""):
            continue
        collapsed.append(line)
    return "\n".join(collapsed).strip()
