from __future__ import annotations

import sys
from pathlib import Path

import pytest
from pypdf import PdfWriter


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


@pytest.fixture
def sample_pdf(tmp_path: Path) -> Path:
    pdf_path = tmp_path / "sample.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    writer.add_metadata({"/Title": "Sample"})
    with pdf_path.open("wb") as fh:
        writer.write(fh)
    return pdf_path
