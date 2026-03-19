from __future__ import annotations

import networkx as nx

from docintelligence.core.models import ContextProgram, EvidenceAtom, TaskType
from docintelligence.indexing.service import rank_atoms


def build_context_program(query: str, task_type: TaskType | None) -> ContextProgram:
    lowered = query.lower()
    inferred = task_type
    if inferred is None:
        if any(term in lowered for term in ["table", "revenue", "amount"]):
            inferred = TaskType.TABLE_LOOKUP
        elif any(term in lowered for term in ["clause", "termination", "liability"]):
            inferred = TaskType.CLAUSE_EXTRACTION
        else:
            inferred = TaskType.FACT_LOOKUP

    if inferred == TaskType.TABLE_LOOKUP:
        return ContextProgram(
            task_type=inferred,
            seed_modes=["lexical", "structure"],
            expand_edges=["adjacent", "contains"],
            max_hops=2,
            verification=["numeric_consistency", "support_subgraph"],
        )
    if inferred == TaskType.CLAUSE_EXTRACTION:
        return ContextProgram(
            task_type=inferred,
            seed_modes=["lexical"],
            expand_edges=["contains", "adjacent"],
            max_hops=2,
            verification=["support_subgraph"],
        )
    return ContextProgram(
        task_type=inferred,
        seed_modes=["lexical"],
        expand_edges=["adjacent"],
        max_hops=1,
        verification=["support_subgraph"],
    )


def assemble_context(
    query: str,
    atoms: list[EvidenceAtom],
    graph: nx.DiGraph,
    program: ContextProgram,
    limit: int = 4,
) -> list[EvidenceAtom]:
    ranked = rank_atoms(query, atoms)
    selected: dict[str, EvidenceAtom] = {}

    for atom in ranked[:limit]:
        selected[atom.atom_id] = atom
        frontier = {atom.atom_id}
        for _ in range(program.max_hops):
            next_frontier: set[str] = set()
            for node in frontier:
                for neighbor in graph.successors(node):
                    edge = graph.edges[node, neighbor]["edge"]
                    if edge.edge_type in program.expand_edges:
                        next_frontier.add(neighbor)
                for neighbor in graph.predecessors(node):
                    edge = graph.edges[neighbor, node]["edge"]
                    if edge.edge_type in program.expand_edges:
                        next_frontier.add(neighbor)
            frontier = next_frontier
            for node in frontier:
                selected[node] = graph.nodes[node]["atom"]

    return sorted(selected.values(), key=lambda atom: atom.reading_order)
