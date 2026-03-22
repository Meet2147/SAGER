from __future__ import annotations

from pathlib import Path

from docflow import adapters


def test_parse_document_routes_supported_suffixes(monkeypatch: object, tmp_path: Path) -> None:
    called: list[str] = []

    def fake_parser(path: Path, doc_id: str) -> tuple[int, list[object]]:
        called.append(path.suffix.lower())
        return 1, []

    monkeypatch.setattr(adapters, "_parse_pdf", fake_parser)
    monkeypatch.setattr(adapters, "_parse_docx", fake_parser)
    monkeypatch.setattr(adapters, "_parse_doc", fake_parser)
    monkeypatch.setattr(adapters, "_parse_xlsx", fake_parser)
    monkeypatch.setattr(adapters, "_parse_xls", fake_parser)
    monkeypatch.setattr(adapters, "_parse_msg", fake_parser)

    for suffix in [".pdf", ".docx", ".doc", ".xlsx", ".xls", ".msg"]:
        path = tmp_path / f"sample{suffix}"
        path.write_bytes(b"placeholder")
        record = adapters.parse_document(path)
        assert record.file_type == suffix.lstrip(".")

    assert called == [".pdf", ".docx", ".doc", ".xlsx", ".xls", ".msg"]
