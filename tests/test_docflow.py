from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from docflow.runner import run_flow


def test_docflow_example_runs_on_pdf_directory(tmp_path: Path, sample_pdf: Path) -> None:
    source_dir = tmp_path / "inputs"
    source_dir.mkdir()
    pdf_path = source_dir / "example.pdf"
    pdf_path.write_bytes(sample_pdf.read_bytes())

    flow_path = Path(__file__).resolve().parents[1] / "docflow" / "examples" / "document_preprocess.flow.dag.yaml"
    output_dir = tmp_path / "docflow_out"
    result = run_flow(flow_path, inputs={"source_dir": str(source_dir), "output_dir": str(output_dir)})

    final_output = result["final_output"]
    assert result["flow_type"] == "standard"
    assert result["orchestration"] == "dag"
    assert Path(final_output["manifest_path"]).exists()

    manifest = json.loads(Path(final_output["manifest_path"]).read_text(encoding="utf-8"))
    assert manifest["document_count"] == 1
    assert manifest["error_count"] == 0
    assert (output_dir / "indexes" / "semantic_index.json").exists()
    assert (output_dir / "text" / "docflow_demo__example.txt").exists()


def test_docflow_txt_export_writes_document_text(tmp_path: Path, sample_pdf: Path) -> None:
    source_dir = tmp_path / "inputs"
    source_dir.mkdir()
    pdf_path = source_dir / "example.pdf"
    pdf_path.write_bytes(sample_pdf.read_bytes())

    flow_path = Path(__file__).resolve().parents[1] / "docflow" / "examples" / "document_preprocess.flow.dag.yaml"
    output_dir = tmp_path / "docflow_out"
    export_path = tmp_path / "example.txt"
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "run_docflow.py"
    subprocess.run(
        [
            sys.executable,
            str(script_path),
            str(flow_path),
            "--source-dir",
            str(source_dir),
            "--output-dir",
            str(output_dir),
            "--export-format",
            "txt",
            "--export-path",
            str(export_path),
        ],
        check=True,
    )

    text = export_path.read_text(encoding="utf-8")
    assert "flow_name:" not in text
    assert isinstance(text, str)


def test_docflow_skips_bad_pdf_and_records_error(tmp_path: Path, sample_pdf: Path) -> None:
    source_dir = tmp_path / "inputs"
    source_dir.mkdir()
    (source_dir / "good.pdf").write_bytes(sample_pdf.read_bytes())
    (source_dir / "bad.pdf").write_bytes(b"not a real pdf")

    flow_path = Path(__file__).resolve().parents[1] / "docflow" / "examples" / "document_preprocess.flow.dag.yaml"
    output_dir = tmp_path / "docflow_out"
    result = run_flow(flow_path, inputs={"source_dir": str(source_dir), "output_dir": str(output_dir)})

    final_output = result["final_output"]
    manifest = json.loads(Path(final_output["manifest_path"]).read_text(encoding="utf-8"))
    assert manifest["document_count"] == 1
    assert manifest["error_count"] == 1
    assert manifest["errors"][0]["path"].endswith("bad.pdf")


def test_compile_flow_graph_includes_flow_type_and_orchestration() -> None:
    from docflow.runner import compile_flow_graph

    flow_path = Path(__file__).resolve().parents[1] / "docflow" / "examples" / "document_preprocess.flow.dag.yaml"
    graph = compile_flow_graph(flow_path)
    assert graph["flow_type"] == "standard"
    assert graph["orchestration"] == "dag"
