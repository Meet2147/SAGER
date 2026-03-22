from __future__ import annotations

import json
from pathlib import Path

from docintelligence.preprocess.service import process_pdf_directory


def test_process_pdf_directory_builds_document_and_indexes(tmp_path: Path, sample_pdf: Path) -> None:
    source_dir = tmp_path / "pdfs"
    source_dir.mkdir()
    pdf_path = source_dir / "sample.pdf"
    pdf_path.write_bytes(sample_pdf.read_bytes())

    output_dir = tmp_path / "out"
    manifest = process_pdf_directory(source_dir=source_dir, output_dir=output_dir, dataset_name="demo")

    assert manifest["processed_count"] == 1
    assert manifest["failure_count"] == 0

    semantic_index = json.loads((output_dir / "indexes" / "semantic_index.json").read_text(encoding="utf-8"))
    structural_index = json.loads((output_dir / "indexes" / "structural_index.json").read_text(encoding="utf-8"))
    spatial_index = json.loads((output_dir / "indexes" / "spatial_index.json").read_text(encoding="utf-8"))

    assert semantic_index["kind"] == "semantic"
    assert structural_index["kind"] == "structural"
    assert spatial_index["kind"] == "spatial"
    assert len(list((output_dir / "documents").glob("*.json"))) == 1
