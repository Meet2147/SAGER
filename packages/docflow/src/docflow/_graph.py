from __future__ import annotations

import networkx as nx

from docflow._core import EvidenceAtom, EvidenceEdge


def build_graph(atoms: list[EvidenceAtom]) -> tuple[nx.DiGraph, list[EvidenceEdge]]:
    graph = nx.DiGraph()
    edges: list[EvidenceEdge] = []
    ordered = sorted(atoms, key=lambda atom: atom.reading_order)

    for atom in ordered:
        graph.add_node(atom.atom_id, atom=atom)

    for current, nxt in zip(ordered, ordered[1:]):
        edge = EvidenceEdge(source=current.atom_id, target=nxt.atom_id, edge_type="adjacent")
        graph.add_edge(edge.source, edge.target, edge=edge)
        edges.append(edge)

    current_section: EvidenceAtom | None = None
    for atom in ordered:
        if atom.role_label == "heading":
            current_section = atom
            continue
        if current_section is not None:
            edge = EvidenceEdge(source=current_section.atom_id, target=atom.atom_id, edge_type="contains")
            graph.add_edge(edge.source, edge.target, edge=edge)
            edges.append(edge)

    return graph, edges
