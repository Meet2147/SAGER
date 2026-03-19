from __future__ import annotations

from docintelligence.core.models import EvidenceAtom, QueryResponse


def verify_context(query: str, context_atoms: list[EvidenceAtom]) -> QueryResponse:
    if not context_atoms:
        return QueryResponse(
            answer="No supported answer found.",
            support_atom_ids=[],
            support_score=0.0,
            verification_status="insufficient_support",
        )

    score = round(sum(atom.confidence for atom in context_atoms[:3]) / min(len(context_atoms), 3), 2)
    answer = " ".join(atom.text for atom in context_atoms[:3])
    status = "supported" if score >= 0.7 else "insufficient_support"
    return QueryResponse(
        answer=answer,
        support_atom_ids=[atom.atom_id for atom in context_atoms[:3]],
        support_score=score,
        verification_status=status,
    )
