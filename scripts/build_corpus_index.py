from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from docintelligence.corpus.indexer import build_persistent_index


def main() -> None:
    payload = build_persistent_index()
    print(
        json.dumps(
            {
                "index_path": payload["index_path"],
                "document_count": len(payload["doc_records"]),
                "atom_count": len(payload["atom_records"]),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
