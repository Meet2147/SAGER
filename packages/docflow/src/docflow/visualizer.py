from __future__ import annotations

import json
from pathlib import Path

from docflow.runner import compile_flow_graph


def render_flow_html(flow_path: str | Path, output_path: str | Path | None = None) -> Path:
    graph = compile_flow_graph(flow_path)
    output = Path(output_path) if output_path else Path(flow_path).with_suffix(".html")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(_build_html(graph), encoding="utf-8")
    return output


def _build_html(graph: dict[str, object]) -> str:
    graph_json = json.dumps(graph)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{graph["flow_name"]} - DocFlow</title>
  <style>
    :root {{
      --bg: #f4f0e8;
      --panel: #fffdf8;
      --ink: #1f3548;
      --muted: #61758a;
      --line: #8fa4b5;
      --accent: #d45047;
      --accent-soft: #f9dfdb;
      --shadow: rgba(31, 53, 72, 0.12);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "Avenir Next", "Helvetica Neue", Arial, sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(212,80,71,0.10), transparent 26%),
        radial-gradient(circle at right center, rgba(31,53,72,0.08), transparent 20%),
        var(--bg);
    }}
    .page {{
      padding: 28px;
      min-height: 100vh;
    }}
    .hero {{
      background: var(--panel);
      border: 2px solid var(--ink);
      border-radius: 24px;
      padding: 22px 24px;
      box-shadow: 0 18px 40px var(--shadow);
      margin-bottom: 22px;
    }}
    .hero h1 {{
      margin: 0 0 8px;
      font-size: 32px;
    }}
    .hero p {{
      margin: 0;
      color: var(--muted);
      font-size: 15px;
    }}
    .layout {{
      display: grid;
      grid-template-columns: minmax(780px, 1fr) 320px;
      gap: 20px;
      align-items: start;
    }}
    .canvas-wrap {{
      background: var(--panel);
      border: 2px solid var(--ink);
      border-radius: 24px;
      box-shadow: 0 18px 40px var(--shadow);
      overflow: auto;
      padding: 18px;
    }}
    .sidebar {{
      background: var(--panel);
      border: 2px solid var(--ink);
      border-radius: 24px;
      box-shadow: 0 18px 40px var(--shadow);
      padding: 18px;
      position: sticky;
      top: 20px;
    }}
    .sidebar h2 {{
      margin: 0 0 14px;
      font-size: 20px;
    }}
    .sidebar h3 {{
      margin: 18px 0 10px;
      font-size: 13px;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: var(--muted);
    }}
    .sidebar pre {{
      white-space: pre-wrap;
      word-break: break-word;
      font-size: 12px;
      background: #f7f3ea;
      border-radius: 12px;
      padding: 12px;
      margin: 0;
      max-height: 260px;
      overflow: auto;
    }}
    .stat {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      padding: 9px 0;
      border-bottom: 1px solid #e8ddd0;
      font-size: 14px;
    }}
    .stat:last-child {{
      border-bottom: 0;
    }}
    #canvas {{
      position: relative;
      min-height: 760px;
    }}
    #edges {{
      position: absolute;
      inset: 0;
      overflow: visible;
      pointer-events: none;
    }}
    .node {{
      position: absolute;
      width: 240px;
      min-height: 122px;
      background: linear-gradient(180deg, #fffdf9 0%, #fff8ef 100%);
      border: 2px solid var(--ink);
      border-radius: 22px;
      box-shadow: 0 14px 30px rgba(31,53,72,0.10);
      padding: 16px;
      cursor: pointer;
      transition: transform 120ms ease, box-shadow 120ms ease, border-color 120ms ease;
    }}
    .node:hover {{
      transform: translateY(-2px);
      box-shadow: 0 18px 34px rgba(31,53,72,0.16);
    }}
    .node.active {{
      border-color: var(--accent);
      box-shadow: 0 18px 34px rgba(212,80,71,0.24);
    }}
    .node.final {{
      background: linear-gradient(180deg, #fff3f1 0%, #fff9f7 100%);
    }}
    .pill {{
      display: inline-flex;
      align-items: center;
      border-radius: 999px;
      padding: 5px 10px;
      background: var(--accent-soft);
      color: var(--accent);
      font-size: 12px;
      font-weight: 700;
      margin-bottom: 10px;
    }}
    .node h3 {{
      margin: 0 0 6px;
      font-size: 20px;
      line-height: 1.1;
    }}
    .node p {{
      margin: 0;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.4;
    }}
    .empty {{
      color: var(--muted);
      font-size: 13px;
    }}
    @media (max-width: 1120px) {{
      .layout {{
        grid-template-columns: 1fr;
      }}
      .sidebar {{
        position: static;
      }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <section class="hero">
      <h1>{graph["flow_name"]}</h1>
      <p>DocFlow visual DAG view inspired by prompt-style flow builders. Click any node to inspect its step, inputs, and config.</p>
    </section>
    <section class="layout">
      <div class="canvas-wrap">
        <div id="canvas">
          <svg id="edges"></svg>
        </div>
      </div>
      <aside class="sidebar">
        <h2>Node Details</h2>
        <div class="stat"><span>Flow</span><strong>{graph["flow_name"]}</strong></div>
        <div class="stat"><span>Nodes</span><strong id="node-count"></strong></div>
        <div class="stat"><span>Edges</span><strong id="edge-count"></strong></div>
        <div class="stat"><span>Final Node</span><strong id="final-node"></strong></div>
        <h3>Selected</h3>
        <div id="selected-name" class="empty">Click a node</div>
        <h3>Step</h3>
        <div id="selected-step" class="empty">No node selected</div>
        <h3>Depends On</h3>
        <div id="selected-deps" class="empty">No node selected</div>
        <h3>Config</h3>
        <pre id="selected-config">{{}}</pre>
      </aside>
    </section>
  </div>
  <script>
    const graph = {graph_json};
    const canvas = document.getElementById("canvas");
    const edgesSvg = document.getElementById("edges");
    const columnWidth = 300;
    const rowHeight = 170;
    const cardWidth = 240;
    const cardHeight = 122;
    const marginX = 40;
    const marginY = 32;

    document.getElementById("node-count").textContent = graph.nodes.length;
    document.getElementById("edge-count").textContent = graph.edges.length;
    document.getElementById("final-node").textContent = graph.final_node || "n/a";

    const columns = new Map();
    for (const node of graph.nodes) {{
      if (!columns.has(node.depth)) columns.set(node.depth, []);
      columns.get(node.depth).push(node);
    }}

    const maxRows = Math.max(...Array.from(columns.values(), value => value.length), 1);
    const maxDepth = Math.max(...graph.nodes.map(node => node.depth), 0);
    canvas.style.width = `${{marginX * 2 + (maxDepth + 1) * columnWidth}}px`;
    canvas.style.height = `${{marginY * 2 + maxRows * rowHeight}}px`;
    edgesSvg.setAttribute("width", canvas.style.width);
    edgesSvg.setAttribute("height", canvas.style.height);

    const positions = new Map();
    for (const [depth, nodes] of columns.entries()) {{
      nodes.forEach((node, index) => {{
        const x = marginX + depth * columnWidth;
        const y = marginY + index * rowHeight;
        positions.set(node.id, {{ x, y }});

        const div = document.createElement("button");
        div.className = "node" + (graph.final_node === node.id ? " final" : "");
        div.style.left = `${{x}}px`;
        div.style.top = `${{y}}px`;
        div.dataset.nodeId = node.id;
        div.innerHTML = `
          <span class="pill">${{node.step}}</span>
          <h3>${{node.id}}</h3>
          <p>${{node.depends_on.length ? "Depends on: " + node.depends_on.join(", ") : "Start node"}}</p>
        `;
        div.addEventListener("click", () => selectNode(node.id));
        canvas.appendChild(div);
      }});
    }}

    for (const edge of graph.edges) {{
      const from = positions.get(edge.source);
      const to = positions.get(edge.target);
      if (!from || !to) continue;

      const startX = from.x + cardWidth;
      const startY = from.y + cardHeight / 2;
      const endX = to.x;
      const endY = to.y + cardHeight / 2;
      const midX = startX + (endX - startX) / 2;

      const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
      path.setAttribute("d", `M ${{startX}} ${{startY}} C ${{midX}} ${{startY}}, ${{midX}} ${{endY}}, ${{endX}} ${{endY}}`);
      path.setAttribute("stroke", "#8fa4b5");
      path.setAttribute("stroke-width", "3");
      path.setAttribute("fill", "none");
      path.setAttribute("stroke-linecap", "round");
      edgesSvg.appendChild(path);

      const arrow = document.createElementNS("http://www.w3.org/2000/svg", "polygon");
      arrow.setAttribute("points", `${{endX}},${{endY}} ${{endX - 11}},${{endY - 6}} ${{endX - 11}},${{endY + 6}}`);
      arrow.setAttribute("fill", "#8fa4b5");
      edgesSvg.appendChild(arrow);
    }}

    function selectNode(nodeId) {{
      const node = graph.nodes.find(item => item.id === nodeId);
      if (!node) return;
      document.querySelectorAll(".node").forEach(el => el.classList.toggle("active", el.dataset.nodeId === nodeId));
      document.getElementById("selected-name").textContent = node.id;
      document.getElementById("selected-step").textContent = node.step;
      document.getElementById("selected-deps").textContent = node.depends_on.length ? node.depends_on.join(", ") : "None";
      document.getElementById("selected-config").textContent = JSON.stringify(node.config || {{}}, null, 2);
    }}

    if (graph.nodes.length) {{
      selectNode(graph.nodes[0].id);
    }}
  </script>
</body>
</html>
"""
