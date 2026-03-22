from __future__ import annotations

import argparse
import csv
import json
import sys
import traceback
from collections import Counter, defaultdict
from pathlib import Path

from openpyxl import Workbook

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from docflow.models import DocumentRecord
from docflow.runner import FlowExecutionError, run_flow


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a DocFlow YAML DAG over a directory of documents.")
    parser.add_argument("flow", help="Path to flow.dag.yaml")
    parser.add_argument("--source-dir", required=True, help="Directory of input documents.")
    parser.add_argument("--output-dir", help="Optional override for output directory.")
    parser.add_argument("--trace", action="store_true", help="Print the full run result including per-node trace.")
    parser.add_argument(
        "--export-format",
        choices=["terminal", "json", "txt", "csv", "xlsx", "sdf"],
        default="terminal",
        help="Where to send the final DocFlow output.",
    )
    parser.add_argument("--export-path", help="Required when export-format is not terminal.")
    args = parser.parse_args()

    inputs = {"source_dir": args.source_dir}
    if args.output_dir:
        inputs["output_dir"] = args.output_dir

    try:
        result = run_flow(args.flow, inputs=inputs)
    except Exception as exc:
        print(format_error(exc), file=sys.stderr)
        raise SystemExit(1)
    payload = (
        {
            "flow_name": result["flow_name"],
            "final_output": result["final_output"],
            "trace": result.get("trace", []),
        }
        if args.trace
        else result["final_output"]
    )
    if args.export_format == "terminal":
        print(json.dumps(payload, indent=2))
        return

    if not args.export_path:
        raise SystemExit("--export-path is required when --export-format is not terminal")

    export_path = Path(args.export_path).expanduser().resolve()
    export_path.parent.mkdir(parents=True, exist_ok=True)
    write_export(payload, args.export_format, export_path, result=result)
    print(
        json.dumps(
            {
                "flow_name": result["flow_name"],
                "final_output": result["final_output"],
                "trace": result.get("trace", []),
                "export_path": str(export_path),
                "export_format": args.export_format,
            },
            indent=2,
        )
    )


def write_export(payload: object, export_format: str, export_path: Path, result: dict[str, object] | None = None) -> None:
    if export_format == "json":
        export_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return
    if export_format == "sdf":
        sdf_payload = build_sdf_payload(result or {})
        export_path.write_text(json.dumps(sdf_payload, indent=2), encoding="utf-8")
        return

    if export_format == "txt":
        export_path.write_text(build_plain_text_export(result or {}), encoding="utf-8")
        return

    rows = flatten_payload(payload)

    if export_format == "csv":
        with export_path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.writer(fh)
            writer.writerow(["key", "value"])
            writer.writerows(rows)
        return

    if export_format == "xlsx":
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "DocFlow Output"
        sheet.append(["key", "value"])
        for row in rows:
            sheet.append(list(row))
        workbook.save(export_path)
        return

    raise ValueError(f"Unsupported export format: {export_format}")


def flatten_payload(payload: object, prefix: str = "") -> list[tuple[str, str]]:
    if isinstance(payload, dict):
        rows: list[tuple[str, str]] = []
        for key, value in payload.items():
            next_prefix = f"{prefix}.{key}" if prefix else str(key)
            rows.extend(flatten_payload(value, next_prefix))
        return rows
    if isinstance(payload, list):
        rows: list[tuple[str, str]] = []
        for index, value in enumerate(payload):
            next_prefix = f"{prefix}[{index}]"
            rows.extend(flatten_payload(value, next_prefix))
        return rows
    return [(prefix or "value", "" if payload is None else str(payload))]


def build_sdf_payload(result: dict[str, object]) -> dict[str, object]:
    records = extract_document_records(result)
    if not records:
        raise ValueError("DocFlow did not produce any document records, so SDF export is unavailable.")

    atoms = [atom for record in records for atom in record.atoms]
    edges = [edge for record in records for edge in record.edges]
    role_distribution = Counter(atom.role_label or "body" for atom in atoms)
    text_chars = sum(len(atom.text) for atom in atoms)

    if len(records) == 1:
        source = {
            "path": records[0].source_path,
            "doc_id": records[0].doc_id,
            "page_count": records[0].page_count,
        }
    else:
        source = {
            "path": "docflow-batch",
            "doc_id": result.get("flow_name", "docflow_batch"),
            "page_count": sum(record.page_count for record in records),
        }

    return {
        "format": "SDF",
        "version": "0.1",
        "method": {
            "name": "DocFlow",
            "expanded": "Document Flow Processing",
        },
        "source": source,
        "stats": {
            "document_count": len(records),
            "atom_count": len(atoms),
            "edge_count": len(edges),
            "extracted_text_chars": text_chars,
        },
        "atoms": [atom.model_dump(mode="json") for atom in atoms],
        "edges": [edge.model_dump(mode="json") for edge in edges],
        "annotations": {
            "role_distribution": dict(role_distribution),
            "trace": result.get("trace", []),
            "notes": [
                "Generated from DocFlow execution.",
                "Structured for SDF-compatible inspection and downstream retrieval.",
            ],
        },
    }


def extract_document_records(result: dict[str, object]) -> list[DocumentRecord]:
    results = result.get("results", {})
    if not isinstance(results, dict):
        return []

    for node_output in reversed(list(results.values())):
        if isinstance(node_output, list) and node_output and all(isinstance(item, DocumentRecord) for item in node_output):
            return node_output
    return []


def build_plain_text_export(result: dict[str, object]) -> str:
    records = extract_document_records(result)
    if not records:
        payload = {
            "flow_name": result.get("flow_name"),
            "final_output": result.get("final_output"),
            "trace": result.get("trace", []),
        }
        rows = flatten_payload(payload)
        return "\n".join(f"{key}: {value}" for key, value in rows)

    document_blocks = [record_to_plain_text(record) for record in records]
    text = "\n\n".join(block for block in document_blocks if block.strip()).strip()
    return f"{text}\n" if text else ""


def record_to_plain_text(record: DocumentRecord) -> str:
    page_to_lines: dict[int, list[str]] = defaultdict(list)
    atoms = sorted(record.atoms, key=lambda atom: (atom.page, atom.reading_order, atom.atom_id))
    previous_page = None
    previous_role = None

    for atom in atoms:
        text = normalize_text_line(atom.text)
        if not text:
            continue

        current_lines = page_to_lines[atom.page]
        if previous_page is not None and atom.page != previous_page and current_lines:
            current_lines.append("")

        if should_insert_blank_line(previous_role, atom.role_label, current_lines):
            current_lines.append("")

        current_lines.append(text)
        previous_page = atom.page
        previous_role = atom.role_label or "body"

    page_blocks = [collapse_blank_lines(page_to_lines[page]) for page in sorted(page_to_lines)]
    return "\n\n".join(block for block in page_blocks if block)


def normalize_text_line(text: str) -> str:
    return " ".join(text.split())


def should_insert_blank_line(previous_role: str | None, current_role: str | None, current_lines: list[str]) -> bool:
    if not current_lines:
        return False
    prev = previous_role or "body"
    curr = current_role or "body"
    if curr in {"heading", "table_caption", "figure_caption"}:
        return current_lines[-1] != ""
    if prev in {"heading", "table_caption", "figure_caption"} and curr == "body":
        return current_lines[-1] != ""
    return False


def collapse_blank_lines(lines: list[str]) -> str:
    collapsed: list[str] = []
    for line in lines:
        if line == "" and (not collapsed or collapsed[-1] == ""):
            continue
        collapsed.append(line)
    return "\n".join(collapsed).strip()


def format_error(exc: Exception) -> str:
    if isinstance(exc, FlowExecutionError):
        lines = [
            "DocFlow run failed.",
            f"Failing node: {exc.node}",
            f"Step: {exc.step}",
            "",
            "Execution trace:",
        ]
        for item in exc.trace:
            lines.append(
                f"- {item['node']} [{item['status']}] {item['step']} ({item['duration_ms']} ms): {item['summary']}"
            )
        lines.extend(
            [
                "",
                "Exception:",
                "".join(traceback.format_exception(type(exc.original), exc.original, exc.original.__traceback__)).rstrip(),
            ]
        )
        return "\n".join(lines)
    return "".join(traceback.format_exception(type(exc), exc, exc.__traceback__)).rstrip()


if __name__ == "__main__":
    main()
