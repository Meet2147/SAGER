from __future__ import annotations

import re
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from pypdf import PdfReader

try:
    import extract_msg
except ImportError:  # pragma: no cover - exercised when optional dependency is absent
    extract_msg = None

try:
    import olefile
except ImportError:  # pragma: no cover - exercised when optional dependency is absent
    olefile = None

try:
    import xlrd
except ImportError:  # pragma: no cover - exercised when optional dependency is absent
    xlrd = None

from docintelligence.core.models import BBox, EvidenceAtom

from docflow.models import DocumentRecord


WORD_NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
SHEET_NS = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def parse_document(path: str | Path, dataset_name: str = "docflow") -> DocumentRecord:
    source = Path(path).expanduser().resolve()
    file_type = source.suffix.lower().lstrip(".")
    doc_id = f"{dataset_name}__{source.stem.replace(' ', '_')}"

    if file_type == "pdf":
        page_count, atoms = _parse_pdf(source, doc_id)
    elif file_type == "docx":
        page_count, atoms = _parse_docx(source, doc_id)
    elif file_type == "doc":
        page_count, atoms = _parse_doc(source, doc_id)
    elif file_type in {"xlsx", "xlsm"}:
        page_count, atoms = _parse_xlsx(source, doc_id)
    elif file_type == "xls":
        page_count, atoms = _parse_xls(source, doc_id)
    elif file_type == "msg":
        page_count, atoms = _parse_msg(source, doc_id)
    else:
        raise ValueError(f"Unsupported document type: {source.suffix}")

    return DocumentRecord(
        doc_id=doc_id,
        source_path=str(source),
        file_type=file_type,
        page_count=page_count,
        atoms=atoms,
    )


def _parse_pdf(path: Path, doc_id: str) -> tuple[int, list[EvidenceAtom]]:
    reader = PdfReader(str(path))
    atoms: list[EvidenceAtom] = []
    for page_index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        for line_index, line in enumerate(lines):
            atoms.append(
                _make_atom(
                    doc_id=doc_id,
                    page=page_index,
                    line_index=line_index,
                    text=line,
                    parser_source="pypdf",
                    role_label="body",
                )
            )
    return len(reader.pages), atoms


def _parse_docx(path: Path, doc_id: str) -> tuple[int, list[EvidenceAtom]]:
    atoms: list[EvidenceAtom] = []
    with ZipFile(path) as archive:
        xml_bytes = archive.read("word/document.xml")
    root = ET.fromstring(xml_bytes)
    paragraphs = []
    for paragraph in root.findall(".//w:p", WORD_NS):
        texts = [node.text for node in paragraph.findall(".//w:t", WORD_NS) if node.text]
        merged = "".join(texts).strip()
        if merged:
            paragraphs.append(merged)

    for line_index, line in enumerate(paragraphs):
        atoms.append(
            _make_atom(
                doc_id=doc_id,
                page=1,
                line_index=line_index,
                text=line,
                parser_source="docx-xml",
                role_label="body",
            )
        )
    return 1, atoms


def _parse_xlsx(path: Path, doc_id: str) -> tuple[int, list[EvidenceAtom]]:
    atoms: list[EvidenceAtom] = []
    with ZipFile(path) as archive:
        shared_strings = _read_shared_strings(archive)
        sheet_names = sorted(name for name in archive.namelist() if name.startswith("xl/worksheets/sheet") and name.endswith(".xml"))
        for sheet_index, sheet_name in enumerate(sheet_names, start=1):
            root = ET.fromstring(archive.read(sheet_name))
            row_index = 0
            for row in root.findall(".//a:sheetData/a:row", SHEET_NS):
                values = []
                for cell in row.findall("a:c", SHEET_NS):
                    cell_type = cell.attrib.get("t")
                    value_node = cell.find("a:v", SHEET_NS)
                    if value_node is None or value_node.text is None:
                        continue
                    raw = value_node.text
                    if cell_type == "s":
                        values.append(shared_strings[int(raw)] if raw.isdigit() and int(raw) < len(shared_strings) else raw)
                    else:
                        values.append(raw)
                merged = " | ".join(value.strip() for value in values if value.strip())
                if not merged:
                    continue
                atoms.append(
                    _make_atom(
                        doc_id=doc_id,
                        page=sheet_index,
                        line_index=row_index,
                        text=merged,
                        parser_source="xlsx-xml",
                        role_label="table_row",
                    )
                )
                row_index += 1
    return max(1, len({atom.page for atom in atoms}) or 1), atoms


def _parse_xls(path: Path, doc_id: str) -> tuple[int, list[EvidenceAtom]]:
    if xlrd is None:
        raise ImportError("Parsing .xls files requires the 'xlrd' package.")
    workbook = xlrd.open_workbook(str(path))
    atoms: list[EvidenceAtom] = []
    for sheet_index in range(workbook.nsheets):
        sheet = workbook.sheet_by_index(sheet_index)
        line_index = 0
        for row_index in range(sheet.nrows):
            values = [str(value).strip() for value in sheet.row_values(row_index) if str(value).strip()]
            merged = " | ".join(values)
            if not merged:
                continue
            atoms.append(
                _make_atom(
                    doc_id=doc_id,
                    page=sheet_index + 1,
                    line_index=line_index,
                    text=merged,
                    parser_source="xlrd",
                    role_label="table_row",
                )
            )
            line_index += 1
    return max(1, workbook.nsheets), atoms


def _parse_doc(path: Path, doc_id: str) -> tuple[int, list[EvidenceAtom]]:
    if olefile is None:
        raise ImportError("Parsing .doc files requires the 'olefile' package.")
    if not olefile.isOleFile(str(path)):
        raise ValueError(f"{path.name} is not a valid OLE .doc file")

    paragraphs: list[str] = []
    with olefile.OleFileIO(str(path)) as ole:
        for stream_name in ole.listdir(streams=True, storages=False):
            try:
                raw = ole.openstream(stream_name).read()
            except OSError:
                continue
            paragraphs.extend(_extract_text_lines_from_binary(raw))

    deduped = _dedupe_preserving_order(paragraphs)
    atoms = [
        _make_atom(
            doc_id=doc_id,
            page=1,
            line_index=index,
            text=line,
            parser_source="olefile-doc",
            role_label="body",
        )
        for index, line in enumerate(deduped)
    ]
    return 1, atoms


def _parse_msg(path: Path, doc_id: str) -> tuple[int, list[EvidenceAtom]]:
    if extract_msg is None:
        raise ImportError("Parsing .msg files requires the 'extract-msg' package.")
    message = extract_msg.Message(str(path))
    try:
        body_parts = [
            ("Subject", message.subject or ""),
            ("Sender", getattr(message, "sender", "") or ""),
            ("To", getattr(message, "to", "") or ""),
            ("Cc", getattr(message, "cc", "") or ""),
            ("Date", str(getattr(message, "date", "") or "")),
            ("Body", message.body or ""),
        ]
    finally:
        message.close()

    lines: list[str] = []
    for label, value in body_parts:
        value = value.strip()
        if not value:
            continue
        if label == "Body":
            lines.extend(line.strip() for line in value.splitlines() if line.strip())
        else:
            lines.append(f"{label}: {value}")

    atoms = [
        _make_atom(
            doc_id=doc_id,
            page=1,
            line_index=index,
            text=line,
            parser_source="extract-msg",
            role_label="body",
        )
        for index, line in enumerate(lines)
    ]
    return 1, atoms


def _read_shared_strings(archive: ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    values: list[str] = []
    for si in root.findall(".//a:si", SHEET_NS):
        texts = [node.text for node in si.findall(".//a:t", SHEET_NS) if node.text]
        values.append("".join(texts))
    return values


def _extract_text_lines_from_binary(raw: bytes) -> list[str]:
    utf16 = [
        _clean_binary_line(match.decode("utf-16le", errors="ignore"))
        for match in re.findall(rb"(?:[\x20-\x7E]\x00){4,}", raw)
    ]
    latin = [
        _clean_binary_line(match.decode("latin-1", errors="ignore"))
        for match in re.findall(rb"[\x20-\x7E]{4,}", raw)
    ]
    return [line for line in utf16 + latin if line]


def _clean_binary_line(text: str) -> str:
    normalized = " ".join(text.replace("\x00", " ").split())
    return normalized if len(normalized) >= 4 else ""


def _dedupe_preserving_order(lines: list[str]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for line in lines:
        if line in seen:
            continue
        seen.add(line)
        deduped.append(line)
    return deduped


def _make_atom(
    doc_id: str,
    page: int,
    line_index: int,
    text: str,
    parser_source: str,
    role_label: str,
) -> EvidenceAtom:
    atom_type = "section" if text.endswith(":") else "text"
    return EvidenceAtom(
        atom_id=f"{doc_id}-p{page}-a{line_index}",
        doc_id=doc_id,
        page=page,
        atom_type=atom_type,
        text=text,
        bbox=BBox(x0=0, y0=line_index * 20, x1=400, y1=(line_index * 20) + 16),
        reading_order=((page - 1) * 10000) + line_index,
        parser_source=parser_source,
        confidence=0.72,
        role_label="heading" if atom_type == "section" else role_label,
    )
