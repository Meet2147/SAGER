from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path("data").resolve() / "mplconfig"))
os.environ.setdefault("XDG_CACHE_HOME", str(Path("data").resolve() / "mplconfig"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "docs" / "ieee" / "figures"


def save_processing_figure() -> None:
    labels = ["Processed", "Failed"]
    values = [1059, 17]
    colors = ["#0e7c66", "#c96b4b"]

    fig, ax = plt.subplots(figsize=(5.6, 3.3), dpi=200)
    ax.bar(labels, values, color=colors, width=0.55)
    ax.set_ylabel("PDF count")
    ax.set_title("Corpus processing outcomes")
    for idx, value in enumerate(values):
        ax.text(idx, value + 10, str(value), ha="center", va="bottom", fontsize=9)
    ax.set_ylim(0, 1150)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "processing_outcomes.png", bbox_inches="tight")
    plt.close(fig)


def save_structure_figure() -> None:
    labels = [
        "body",
        "heading",
        "footnote",
        "table_row",
        "citation",
        "table_caption",
        "figure_caption",
        "table_of_contents",
    ]
    values = [363403, 70907, 38222, 17632, 1161, 598, 511, 96]

    fig, ax = plt.subplots(figsize=(7.0, 3.8), dpi=200)
    ax.bar(labels, values, color="#355c7d")
    ax.set_ylabel("Atom count")
    ax.set_title("Observed structure-label distribution")
    ax.tick_params(axis="x", rotation=30, labelsize=8)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "structure_distribution.png", bbox_inches="tight")
    plt.close(fig)


def save_latency_figure() -> None:
    labels = [
        "humanitarian\ndata governance",
        "termination\nclause notice",
        "table revenue\namount",
        "data responsibility\nguidelines",
        "figure results\nconfidence",
    ]
    values = [0.679, 6.470, 2.133, 0.242, 2.371]

    fig, ax = plt.subplots(figsize=(7.0, 3.8), dpi=200)
    ax.bar(labels, values, color="#6c8ebf")
    ax.set_ylabel("Latency (s)")
    ax.set_title("Representative corpus-query latency")
    for idx, value in enumerate(values):
        ax.text(idx, value + 0.08, f"{value:.3f}", ha="center", va="bottom", fontsize=8)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "query_latency.png", bbox_inches="tight")
    plt.close(fig)


def save_baseline_figure() -> None:
    metrics = ["MRR@10", "Recall@10"]
    baseline = [0.167, 0.5]
    improved = [0.812, 1.0]

    x = range(len(metrics))
    width = 0.32

    fig, ax = plt.subplots(figsize=(5.6, 3.4), dpi=200)
    ax.bar([i - width / 2 for i in x], baseline, width=width, label="Lexical baseline", color="#c96b4b")
    ax.bar([i + width / 2 for i in x], improved, width=width, label="Evidence-graph index", color="#0e7c66")
    ax.set_xticks(list(x), metrics)
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("Score")
    ax.set_title("Proxy retrieval benchmark")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "baseline_comparison.png", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    save_processing_figure()
    save_structure_figure()
    save_latency_figure()
    save_baseline_figure()
    print(FIG_DIR)


if __name__ == "__main__":
    main()
