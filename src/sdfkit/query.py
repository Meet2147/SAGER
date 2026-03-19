from __future__ import annotations

from docintelligence.core.models import AtomType, BBox, EvidenceAtom
from docintelligence.indexing.service import lexical_score

from .models import SDFAtom, SDFDocument


def atoms_on_page(document: SDFDocument, page: int) -> list[SDFAtom]:
    return [atom for atom in document.atoms if atom.page == page]


def role_distribution(document: SDFDocument) -> dict[str, int]:
    return dict(document.annotations.get("role_distribution", {}))


def query_document(document: SDFDocument, text: str, top_k: int = 5) -> list[SDFAtom]:
    scored = sorted(
        document.atoms,
        key=lambda atom: (
            lexical_score(text, _to_evidence_atom(atom)),
            atom.confidence,
        ),
        reverse=True,
    )
    return scored[:top_k]


def _to_evidence_atom(atom: SDFAtom) -> EvidenceAtom:
    bbox = BBox(**atom.bbox) if atom.bbox else None
    atom_type = atom.atom_type if atom.atom_type in AtomType._value2member_map_ else AtomType.TEXT
    return EvidenceAtom(
        atom_id=atom.atom_id,
        doc_id=atom.doc_id,
        page=atom.page,
        atom_type=atom_type,
        text=atom.text,
        bbox=bbox,
        reading_order=atom.reading_order,
        parser_source=atom.parser_source,
        confidence=atom.confidence,
        role_label=atom.role_label,
    )
