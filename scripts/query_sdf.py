from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from docintelligence.sdf.service import query_sdf


def main() -> None:
    if len(sys.argv) < 3:
        raise SystemExit("Usage: python3 scripts/query_sdf.py <file.sdf> '<query>'")

    sdf_path = sys.argv[1]
    query = sys.argv[2]
    result = query_sdf(sdf_path, query)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
