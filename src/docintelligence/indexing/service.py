from __future__ import annotations

from docintelligence.core.models import EvidenceAtom


def lexical_score(query: str, atom: EvidenceAtom) -> int:
    query_terms = {term.lower() for term in query.split() if term.strip()}
    atom_terms = {term.lower().strip(".,:;()") for term in atom.text.split()}
    return len(query_terms & atom_terms)


def rank_atoms(query: str, atoms: list[EvidenceAtom]) -> list[EvidenceAtom]:
    return sorted(atoms, key=lambda atom: (lexical_score(query, atom), atom.confidence), reverse=True)
