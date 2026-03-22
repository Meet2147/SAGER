from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from docintelligence.preprocess.service import process_pdf_directory


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run only the SAGER preprocessing stages over a directory of PDFs."
    )
    parser.add_argument("source_dir", help="Directory to scan recursively for PDF files.")
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "data" / "preprocessed"),
        help="Directory where document artifacts and indexes will be written.",
    )
    parser.add_argument(
        "--dataset-name",
        default="sager_preprocessed",
        help="Name used to namespace the generated artifacts.",
    )
    args = parser.parse_args()

    manifest = process_pdf_directory(
        source_dir=args.source_dir,
        output_dir=Path(args.output_dir) / args.dataset_name,
        dataset_name=args.dataset_name,
    )

    print(f"Dataset: {manifest['dataset_name']}")
    print(f"Source directory: {manifest['source_dir']}")
    print(f"Processed PDFs: {manifest['processed_count']}/{manifest['pdf_count']}")
    print(f"Failures: {manifest['failure_count']}")
    print(f"Manifest: {Path(manifest['output_dir']) / 'manifest.json'}")
    print("Indexes:")
    for name, path in manifest["index_paths"].items():
        print(f"  - {name}: {path}")


if __name__ == "__main__":
    main()
