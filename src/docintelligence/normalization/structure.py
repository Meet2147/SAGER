from __future__ import annotations

import re

from docintelligence.core.models import AtomType, EvidenceAtom


FIGURE_PATTERN = re.compile(r"^(figure|fig\.)\s+\d+", re.IGNORECASE)
TABLE_PATTERN = re.compile(r"^table\s+\d+", re.IGNORECASE)
FOOTNOTE_PATTERN = re.compile(r"^\d+[\]\).]?\s{1,}")
CITATION_PATTERN = re.compile(
    r"(\bet al\.\b|\bdoi:\b|\(\d{4}\)|\b\d{4}\b.*\bpp?\.\b)",
    re.IGNORECASE,
)


def infer_structure(atom: EvidenceAtom) -> EvidenceAtom:
    text = atom.text.strip()
    lowered = text.lower()

    atom_type = atom.atom_type
    role_label = atom.role_label or "body"

    if "table of contents" in lowered:
        atom_type = AtomType.SECTION
        role_label = "table_of_contents"
    elif FIGURE_PATTERN.match(text):
        atom_type = AtomType.CAPTION
        role_label = "figure_caption"
    elif TABLE_PATTERN.match(text):
        atom_type = AtomType.TABLE_HEADER
        role_label = "table_caption"
    elif FOOTNOTE_PATTERN.match(text) and len(text) > 40:
        atom_type = AtomType.FOOTNOTE
        role_label = "footnote"
    elif CITATION_PATTERN.search(text):
        atom_type = AtomType.CITATION
        role_label = "citation"
    elif _looks_like_heading(text):
        atom_type = AtomType.SECTION
        role_label = "heading"
    elif _looks_like_table_row(text):
        atom_type = AtomType.TABLE_CELL
        role_label = "table_row"

    confidence = atom.confidence
    if role_label in {"heading", "figure_caption", "table_caption"}:
        confidence = min(1.0, max(confidence, 0.82))

    return atom.model_copy(
        update={
            "atom_type": atom_type,
            "role_label": role_label,
            "confidence": confidence,
        }
    )


def _looks_like_heading(text: str) -> bool:
    words = text.split()
    if not words:
        return False
    if len(words) <= 12 and text.isupper():
        return True
    if len(text) <= 90 and text.endswith(":"):
        return True
    if len(words) <= 10 and sum(word[:1].isupper() for word in words) >= max(2, len(words) - 1):
        return True
    return False


def _looks_like_table_row(text: str) -> bool:
    if len(text) < 12:
        return False
    digit_count = sum(ch.isdigit() for ch in text)
    separator_count = text.count("  ") + text.count("\t")
    return digit_count >= 3 and separator_count >= 1
