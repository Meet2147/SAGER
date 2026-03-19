from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from docintelligence.core.models import BBox, EvidenceAtom, IngestRequest


def ingest_text(request: IngestRequest) -> list[EvidenceAtom]:
    atoms: list[EvidenceAtom] = []
    for idx, raw_line in enumerate(line.strip() for line in request.text.splitlines() if line.strip()):
        atom_type = "section" if raw_line.endswith(":") else "text"
        atoms.append(
            EvidenceAtom(
                atom_id=f"{request.doc_id}-atom-{idx}",
                doc_id=request.doc_id,
                page=1,
                atom_type=atom_type,
                text=raw_line,
                bbox=BBox(x0=0, y0=idx * 20, x1=400, y1=(idx * 20) + 16),
                reading_order=idx,
                parser_source=request.parser_name,
                confidence=0.85 if atom_type == "section" else 0.75,
                role_label="heading" if atom_type == "section" else "body",
            )
        )
    return atoms


def extract_pdf_text(pdf_path: str) -> tuple[int, list[str]]:
    reader = PdfReader(pdf_path)
    page_texts: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        page_texts.append(text)
    return len(reader.pages), page_texts


def ingest_pdf(pdf_path: str) -> tuple[str, int, list[EvidenceAtom]]:
    source = Path(pdf_path)
    doc_id = source.stem.replace(" ", "_")
    page_count, page_texts = extract_pdf_text(str(source))
    atoms: list[EvidenceAtom] = []

    for page_index, page_text in enumerate(page_texts, start=1):
        lines = [line.strip() for line in page_text.splitlines() if line.strip()]
        for line_index, raw_line in enumerate(lines):
            atom_type = "section" if raw_line.endswith(":") else "text"
            atom_id = f"{doc_id}-p{page_index}-a{line_index}"
            atoms.append(
                EvidenceAtom(
                    atom_id=atom_id,
                    doc_id=doc_id,
                    page=page_index,
                    atom_type=atom_type,
                    text=raw_line,
                    bbox=BBox(x0=0, y0=line_index * 20, x1=400, y1=(line_index * 20) + 16),
                    reading_order=((page_index - 1) * 10000) + line_index,
                    parser_source="pypdf",
                    confidence=0.7 if raw_line else 0.0,
                    role_label="heading" if atom_type == "section" else "body",
                )
            )

    return doc_id, page_count, atoms
