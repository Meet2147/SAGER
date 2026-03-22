from __future__ import annotations

from pathlib import Path

from docflow.visualizer import render_flow_html


def test_render_flow_html_creates_visual_output(tmp_path: Path) -> None:
    flow_path = Path(__file__).resolve().parents[1] / "docflow" / "examples" / "document_preprocess.flow.dag.yaml"
    output_path = tmp_path / "flow.html"
    created = render_flow_html(flow_path, output_path)

    html = created.read_text(encoding="utf-8")
    assert created == output_path
    assert "document_preprocess" in html
    assert "normalize_atoms" in html
    assert "build_evidence_graph" in html
