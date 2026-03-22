from __future__ import annotations

from collections import deque
from pathlib import Path
from time import perf_counter

import yaml

from docflow.models import FlowContext
from docflow.steps import STEP_REGISTRY


class FlowExecutionError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        node: str,
        step: str,
        trace: list[dict[str, object]],
        original: Exception,
    ) -> None:
        super().__init__(message)
        self.node = node
        self.step = step
        self.trace = trace
        self.original = original


def load_flow_spec(flow_path: str | Path) -> dict[str, object]:
    flow_path = Path(flow_path).expanduser().resolve()
    flow_spec = yaml.safe_load(flow_path.read_text(encoding="utf-8")) or {}
    flow_spec.setdefault("flow_type", "standard")
    flow_spec.setdefault("orchestration", _infer_orchestration_style(flow_path))
    return flow_spec


def run_flow(flow_path: str | Path, inputs: dict[str, object] | None = None) -> dict[str, object]:
    flow_path = Path(flow_path).expanduser().resolve()
    flow_spec = load_flow_spec(flow_path)
    variables = flow_spec.get("variables", {}).copy()
    if inputs:
        variables.update(inputs)
    context = FlowContext(
        root_dir=flow_path.parents[2] if len(flow_path.parents) >= 3 else flow_path.parent,
        flow_dir=flow_path.parent,
        inputs=inputs or {},
        variables=variables,
    )

    nodes = flow_spec.get("nodes", [])
    ordered_nodes = _toposort(nodes)
    results: dict[str, object] = {}
    trace: list[dict[str, object]] = []

    for node in ordered_nodes:
        node_name = node["name"]
        step_name = node["step"]
        dependencies = node.get("depends_on", [])
        dependency_outputs = [results[name] for name in dependencies]
        config = node.get("config", {})
        start = perf_counter()
        try:
            step_fn = STEP_REGISTRY[step_name]
            if step_name == "scan_documents":
                results[node_name] = step_fn(context, config)
            else:
                results[node_name] = step_fn(context, config, dependency_outputs)
            duration_ms = round((perf_counter() - start) * 1000, 2)
            trace.append(
                {
                    "node": node_name,
                    "step": step_name,
                    "depends_on": list(dependencies),
                    "status": "completed",
                    "duration_ms": duration_ms,
                    "summary": _summarize_result(results[node_name]),
                }
            )
        except Exception as exc:
            duration_ms = round((perf_counter() - start) * 1000, 2)
            trace.append(
                {
                    "node": node_name,
                    "step": step_name,
                    "depends_on": list(dependencies),
                    "status": "failed",
                    "duration_ms": duration_ms,
                    "summary": str(exc),
                }
            )
            raise FlowExecutionError(
                f"DocFlow node '{node_name}' failed in step '{step_name}': {exc}",
                node=node_name,
                step=step_name,
                trace=trace,
                original=exc,
            ) from exc

    final_node = flow_spec.get("outputs", {}).get("final_node", ordered_nodes[-1]["name"] if ordered_nodes else None)
    return {
        "flow_name": flow_spec.get("name", flow_path.stem),
        "flow_type": flow_spec.get("flow_type", "standard"),
        "orchestration": flow_spec.get("orchestration", _infer_orchestration_style(flow_path)),
        "results": results,
        "final_output": results.get(final_node),
        "trace": trace,
    }


def compile_flow_graph(flow_path: str | Path) -> dict[str, object]:
    flow_path = Path(flow_path).expanduser().resolve()
    flow_spec = load_flow_spec(flow_path)
    nodes = flow_spec.get("nodes", [])
    ordered_nodes = _toposort(nodes)
    depths = _compute_depths(nodes)
    graph_nodes: list[dict[str, object]] = []
    graph_edges: list[dict[str, str]] = []

    for node in ordered_nodes:
        name = node["name"]
        graph_nodes.append(
            {
                "id": name,
                "step": node["step"],
                "depth": depths.get(name, 0),
                "depends_on": list(node.get("depends_on", [])),
                "config": node.get("config", {}),
            }
        )
        for dependency in node.get("depends_on", []):
            graph_edges.append({"source": dependency, "target": name})

    return {
        "flow_name": flow_spec.get("name", flow_path.stem),
        "flow_type": flow_spec.get("flow_type", "standard"),
        "orchestration": flow_spec.get("orchestration", _infer_orchestration_style(flow_path)),
        "flow_path": str(flow_path),
        "nodes": graph_nodes,
        "edges": graph_edges,
        "final_node": flow_spec.get("outputs", {}).get("final_node"),
    }


def _toposort(nodes: list[dict[str, object]]) -> list[dict[str, object]]:
    node_map = {node["name"]: node for node in nodes}
    indegree = {name: 0 for name in node_map}
    edges: dict[str, list[str]] = {name: [] for name in node_map}

    for node in nodes:
        for parent in node.get("depends_on", []):
            edges[parent].append(node["name"])
            indegree[node["name"]] += 1

    queue = deque(name for name, degree in indegree.items() if degree == 0)
    ordered_names: list[str] = []
    while queue:
        name = queue.popleft()
        ordered_names.append(name)
        for child in edges[name]:
            indegree[child] -= 1
            if indegree[child] == 0:
                queue.append(child)

    if len(ordered_names) != len(nodes):
        raise ValueError("Flow graph contains a cycle or missing dependency.")
    return [node_map[name] for name in ordered_names]


def _compute_depths(nodes: list[dict[str, object]]) -> dict[str, int]:
    node_map = {node["name"]: node for node in nodes}
    depths: dict[str, int] = {}

    def resolve(name: str) -> int:
        if name in depths:
            return depths[name]
        parents = node_map[name].get("depends_on", [])
        if not parents:
            depths[name] = 0
            return 0
        depth = max(resolve(parent) for parent in parents) + 1
        depths[name] = depth
        return depth

    for node in nodes:
        resolve(node["name"])
    return depths


def _summarize_result(result: object) -> str:
    if isinstance(result, list):
        return f"{len(result)} items"
    if isinstance(result, dict):
        keys = list(result)[:4]
        return ", ".join(str(key) for key in keys) if keys else "empty object"
    if result is None:
        return "no output"
    return type(result).__name__


def _infer_orchestration_style(flow_path: Path) -> str:
    name = flow_path.name.lower()
    if ".flex." in name:
        return "flex"
    return "dag"
