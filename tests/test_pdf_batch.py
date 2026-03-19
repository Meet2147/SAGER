from pathlib import Path

from docintelligence.ingestion.service import ingest_pdf


def test_ingest_pdf_reads_workspace_pdf() -> None:
    pdf_dir = Path(__file__).resolve().parents[1] / "Pdf"
    sample_pdf = sorted(pdf_dir.glob("*.pdf"))[0]

    doc_id, page_count, atoms = ingest_pdf(str(sample_pdf))

    assert doc_id
    assert page_count >= 1
    assert atoms
