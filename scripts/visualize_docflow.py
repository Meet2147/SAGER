from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from docflow.visualizer import render_flow_html


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a DocFlow DAG YAML into an interactive HTML visual.")
    parser.add_argument("flow", help="Path to flow.dag.yaml")
    parser.add_argument("--output", help="Optional HTML output path.")
    args = parser.parse_args()

    html_path = render_flow_html(args.flow, args.output)
    print(html_path)


if __name__ == "__main__":
    main()
