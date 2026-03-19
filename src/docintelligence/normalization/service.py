from __future__ import annotations

from docintelligence.core.models import EvidenceAtom
from docintelligence.normalization.structure import infer_structure


def normalize_atoms(atoms: list[EvidenceAtom]) -> list[EvidenceAtom]:
    normalized: list[EvidenceAtom] = []
    for atom in atoms:
        stripped = atom.model_copy(update={"text": atom.text.strip()})
        normalized.append(infer_structure(stripped))
    return normalized
