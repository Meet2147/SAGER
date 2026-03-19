# DocIntelligence

Prototype scaffold and patent materials for a document-intelligence system built around adaptive evidence graphs, query-conditioned context assembly, and verified outputs.

## Documents

- [Patent plan](/Users/meetjethwa/Development/PatentIdeas/DocIntelligence/patent_plan.md)
- [Invention disclosure](/Users/meetjethwa/Development/PatentIdeas/DocIntelligence/invention_disclosure.md)
- [Patent package](/Users/meetjethwa/Development/PatentIdeas/DocIntelligence/patent_package.md)
- [Provisional draft](/Users/meetjethwa/Development/PatentIdeas/DocIntelligence/docs/patent/provisional_draft.md)
- [Prototype roadmap](/Users/meetjethwa/Development/PatentIdeas/DocIntelligence/prototype_roadmap.md)

## Prototype

The code scaffold focuses on:

- evidence atom normalization
- evidence graph construction
- rule-based context assembly
- simple support verification

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pytest
uvicorn docintelligence.api.main:app --reload
```

## Batch PDF processing

Process the workspace corpus in `Pdf/` into JSON artifacts and a manifest:

```bash
python3 scripts/process_pdfs.py
```

Outputs:

- `data/processed/*.json`
- `data/manifests/pdf_manifest.json`

Query the processed corpus from the CLI:

```bash
python3 scripts/query_corpus.py "humanitarian data"
```

Build or refresh the persistent corpus index:

```bash
python3 scripts/build_corpus_index.py
```

Run the UI:

```bash
uvicorn docintelligence.api.main:app --reload
```

## Layout

```text
docs/
  diagrams/
  patent/
src/docintelligence/
  api/
  core/
  graph/
  indexing/
  ingestion/
  normalization/
  retrieval/
  verification/
tests/
```
