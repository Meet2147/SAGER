from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from docintelligence.graph.service import build_graph
from docintelligence.ingestion.service import ingest_pdf
from docintelligence.normalization.service import normalize_atoms


def process_pdf(
    pdf_path: Path,
    output_dir: Path,
    doc_id_prefix: str = "",
    source_root: Path | None = None,
) -> dict[str, object]:
    doc_id, page_count, raw_atoms = ingest_pdf(str(pdf_path))
    if source_root is not None:
        rel = pdf_path.relative_to(source_root).with_suffix("")
        path_slug = "_".join(rel.parts).replace(" ", "_")
        doc_id = path_slug
    if doc_id_prefix:
        doc_id = f"{doc_id_prefix}_{doc_id}"
        raw_atoms = [atom.model_copy(update={"doc_id": doc_id, "atom_id": atom.atom_id.replace(atom.doc_id, doc_id, 1)}) for atom in raw_atoms]
    atoms = normalize_atoms(raw_atoms)
    graph, edges = build_graph(atoms)

    payload = {
        "doc_id": doc_id,
        "source_path": str(pdf_path),
        "page_count": page_count,
        "atom_count": len(atoms),
        "edge_count": len(edges),
        "extracted_text_chars": sum(len(atom.text) for atom in atoms),
        "atoms": [atom.model_dump() for atom in atoms],
        "edges": [edge.model_dump() for edge in edges],
    }
    out_path = output_dir / f"{doc_id}.json"
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return {
        "doc_id": doc_id,
        "source_path": str(pdf_path),
        "page_count": page_count,
        "atom_count": len(atoms),
        "edge_count": len(edges),
        "extracted_text_chars": payload["extracted_text_chars"],
        "artifact_path": str(out_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Process a PDF directory into DocIntelligence artifacts.")
    parser.add_argument("--source-dir", default=str(ROOT / "Pdf"), help="Directory to scan recursively for PDFs.")
    parser.add_argument("--dataset-name", default="default", help="Dataset name used for artifact directories and doc id prefixes.")
    args = parser.parse_args()

    source_dir = Path(args.source_dir).expanduser()
    dataset_name = args.dataset_name.strip().replace(" ", "_")
    output_dir = ROOT / "data" / "processed" / dataset_name
    manifest_path = ROOT / "data" / "manifests" / f"{dataset_name}_manifest.json"

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    manifest: list[dict[str, object]] = []
    pdf_paths = sorted(
        [
            path
            for path in source_dir.rglob("*")
            if path.is_file() and path.suffix.lower() == ".pdf"
        ]
    )
    for pdf_path in pdf_paths:
        try:
            manifest.append(
                process_pdf(
                    pdf_path,
                    output_dir=output_dir,
                    doc_id_prefix=dataset_name,
                    source_root=source_dir,
                )
            )
        except Exception as exc:  # pragma: no cover - batch resiliency path
            manifest.append(
                {
                    "source_path": str(pdf_path),
                    "error": str(exc),
                }
            )

    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    success_count = sum(1 for item in manifest if "error" not in item)
    print(f"Dataset: {dataset_name}")
    print(f"Source: {source_dir}")
    print(f"Processed {success_count}/{len(manifest)} PDFs")
    print(f"Artifacts: {output_dir}")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
