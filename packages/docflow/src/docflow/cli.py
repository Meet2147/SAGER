from __future__ import annotations

import argparse
import json
from pathlib import Path

from docflow.runner import compile_flow_graph, run_flow


def main() -> None:
    parser = argparse.ArgumentParser(description="Run or inspect a DocFlow DAG.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run a DocFlow DAG.")
    run_parser.add_argument("flow", help="Path to flow.dag.yaml")
    run_parser.add_argument("--source-dir", required=True, help="Input file or directory.")
    run_parser.add_argument("--output-dir", help="Optional output directory override.")
    run_parser.add_argument("--trace", action="store_true", help="Include execution trace in output.")

    graph_parser = subparsers.add_parser("graph", help="Print the compiled DocFlow graph as JSON.")
    graph_parser.add_argument("flow", help="Path to flow.dag.yaml")

    args = parser.parse_args()
    if args.command == "run":
        inputs = {"source_dir": args.source_dir}
        if args.output_dir:
            inputs["output_dir"] = args.output_dir
        result = run_flow(args.flow, inputs=inputs)
        payload = result if args.trace else result["final_output"]
        print(json.dumps(payload, indent=2))
        return

    graph = compile_flow_graph(Path(args.flow))
    print(json.dumps(graph, indent=2))


if __name__ == "__main__":
    main()
