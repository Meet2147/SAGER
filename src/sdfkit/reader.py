from __future__ import annotations

from docintelligence.sdf.service import load_sdf
from .models import SDFAtom, SDFDocument, SDFEdge
from .query import atoms_on_page, query_document, role_distribution


def open_sdf(path: str) -> SDFDocument:
    payload = load_sdf(path)
    atoms = [SDFAtom(**atom) for atom in payload.get("atoms", [])]
    edges = [SDFEdge(**edge) for edge in payload.get("edges", [])]
    document = SDFDocument(path, payload, atoms, edges)
    document.atoms_on_page = lambda page: atoms_on_page(document, page)
    document.role_distribution = lambda: role_distribution(document)
    document.query = lambda text, top_k=5: query_document(document, text, top_k=top_k)
    return document
