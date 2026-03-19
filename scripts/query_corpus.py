from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from docintelligence.core.models import CorpusQueryRequest
from docintelligence.corpus.service import query_corpus


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python3 scripts/query_corpus.py '<query>'")

    request = CorpusQueryRequest(query=sys.argv[1])
    response = query_corpus(request)
    print(json.dumps(response.model_dump(), indent=2))


if __name__ == "__main__":
    main()
