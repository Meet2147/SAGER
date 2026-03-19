from __future__ import annotations

import pickle
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
INDEX_DIR = ROOT / "data" / "index"
INDEX_PATH = INDEX_DIR / "corpus_index.pkl"


def save_index(payload: dict[str, object]) -> Path:
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    with INDEX_PATH.open("wb") as fh:
        pickle.dump(payload, fh)
    return INDEX_PATH


def load_index() -> dict[str, object]:
    with INDEX_PATH.open("rb") as fh:
        return pickle.load(fh)


def index_exists() -> bool:
    return INDEX_PATH.exists()


def cosine_scores(query_vector, matrix) -> np.ndarray:
    scores = matrix @ query_vector.T
    dense = np.asarray(scores.todense()).ravel() if hasattr(scores, "todense") else np.asarray(scores).ravel()
    return dense
