from __future__ import annotations

from pathlib import Path

from docintelligence.sdf.service import convert_pdf_to_sdf, convert_processed_json_to_sdf


def create_sdf(source_path: str, output_path: str | None = None) -> Path:
    path = Path(source_path)
    if path.suffix.lower() == ".pdf":
        return convert_pdf_to_sdf(source_path, output_path)
    return convert_processed_json_to_sdf(source_path, output_path)
