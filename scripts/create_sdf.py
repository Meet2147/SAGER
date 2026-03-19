from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from docintelligence.sdf.service import convert_pdf_to_sdf, convert_processed_json_to_sdf


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python3 scripts/create_sdf.py <processed_json_or_pdf> [output.sdf]")

    source = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    source_path = Path(source)

    if source_path.suffix.lower() == ".pdf":
        sdf_path = convert_pdf_to_sdf(source, output_path)
    else:
        sdf_path = convert_processed_json_to_sdf(source, output_path)
    print(sdf_path)


if __name__ == "__main__":
    main()
