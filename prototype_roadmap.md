# Prototype Roadmap

## Goal

Build a prototype in this workspace that demonstrates why adaptive evidence graphs outperform flat chunk-based document pipelines on layout-heavy, multi-page documents.

## Target outcome

By the end of the prototype, we should be able to show:

- evidence-backed extraction from PDFs
- graph-based retrieval over document structure
- query-specific context assembly
- provenance-linked answers or JSON outputs
- selective reprocessing of uncertain regions

## Recommended repository structure

```text
DocIntelligence/
  docs/
    patent/
  src/
    ingestion/
    parsers/
    normalization/
    graph/
    indexing/
    retrieval/
    verification/
    api/
  data/
    samples/
    processed/
  tests/
  notebooks/
```

## Phase 0: foundation

Duration: 2-4 days

Set up:

- Python project scaffolding
- dependency management
- sample document corpus
- baseline evaluation harness

Deliverables:

- simple CLI or API that ingests a PDF
- storage for raw parser outputs
- first-pass schema for `EvidenceAtom`, `Edge`, and `ParserRun`

## Phase 1: ingestion and normalization

Duration: 4-7 days

Implement:

- PDF ingestion
- OCR/layout parser adapter
- table parser adapter
- normalized atom schema

Minimum atom fields:

- `atom_id`
- `doc_id`
- `page`
- `atom_type`
- `text`
- `bbox`
- `reading_order`
- `parser_source`
- `confidence`

Success criteria:

- can parse a sample PDF into normalized atoms
- can export atoms as JSON
- can preserve page geometry and parser provenance

## Phase 2: evidence graph

Duration: 4-7 days

Implement graph construction rules for:

- adjacency edges
- containment edges
- section hierarchy edges
- table row/column/cell edges
- caption-reference edges
- citation or cross-reference edges

Success criteria:

- each document yields a graph artifact
- graph neighborhoods can be queried programmatically
- at least one visualization shows graph-connected evidence on a sample document

## Phase 3: indexing and baseline retrieval

Duration: 4-6 days

Implement:

- atom embedding generation
- vector index over atoms or atom groups
- structural lookup index
- spatial lookup utilities

Baselines to include:

- fixed-size chunk retrieval
- heading-based chunk retrieval
- evidence-atom semantic retrieval

Success criteria:

- same query can run against chunk baseline and evidence graph pipeline
- outputs are comparable in a single evaluation script

## Phase 4: context assembly engine

Duration: 5-8 days

Implement:

- task-type classifier or rule-based router
- context assembly policies
- hybrid retrieval plus graph expansion

Example task types:

- factual lookup
- clause extraction
- table lookup
- cross-page evidence synthesis

Example policy output:

```json
{
  "task_type": "table_lookup",
  "seed_modes": ["semantic", "table_header_match"],
  "expand_edges": ["same_table", "same_row", "caption_link"],
  "max_hops": 2,
  "verification": ["numeric_consistency", "header_alignment"]
}
```

Success criteria:

- query-specific context differs by task type
- system can explain why evidence atoms were selected

## Phase 5: verification and selective reprocessing

Duration: 5-8 days

Implement:

- support subgraph builder
- output confidence scoring
- contradiction detection
- targeted page or region reprocessing

Examples of reprocessing triggers:

- low-confidence OCR on selected region
- mismatch between OCR text and table parser cell value
- unsupported answer after generation

Success criteria:

- system can reject unsupported outputs
- system can retry with targeted reprocessing
- logs show reduced reprocessing scope versus full-document rerun

## Phase 6: demo application

Duration: 3-5 days

Build a simple interface:

- ingest document
- display extracted evidence atoms
- ask a question
- show answer with supporting evidence references
- show when reprocessing was triggered

Preferred outputs:

- cited answer
- extracted JSON
- support trace

## Evaluation plan

### Benchmark tasks

- extract clauses from agreements
- answer questions from financial statements
- extract table-backed values from reports
- connect claims to figures or footnotes in technical papers

### Metrics

- field extraction F1
- answer support rate
- unsupported-answer rate
- table accuracy
- latency
- number of pages or regions reprocessed

### Comparisons

- fixed chunk baseline
- semantic chunk baseline
- evidence graph without reprocessing
- full system with verification and reprocessing

## Suggested MVP technical stack

Use simple, swappable components first:

- Python
- FastAPI for service layer
- Pydantic for schemas
- NetworkX or a graph database adapter for graph logic
- a local vector store or FAISS for embeddings
- one OCR/layout parser and one table parser to start

The first version should optimize for clarity and measurement, not production scale.

## First implementation milestones

### Milestone 1

Ingest one PDF and produce normalized evidence atoms as JSON.

### Milestone 2

Construct evidence graph and run simple graph queries.

### Milestone 3

Compare chunk baseline versus atom retrieval on 10-20 hand-authored queries.

### Milestone 4

Add support-subgraph verification and visible provenance in answers.

### Milestone 5

Add targeted reprocessing for low-confidence regions.

### Milestone 6

Package a demo that clearly shows why this is better than chunk-based RAG.

## What makes the demo compelling for patent support

The demo should visibly show:

- the retrieved evidence is not just a text chunk
- tables, footnotes, and cross-references are preserved
- unsupported outputs are blocked or corrected
- reprocessing happens only where uncertainty exists

That combination helps support both technical novelty and commercial value.

## Recommended next coding step

Start with the evidence schema and ingestion pipeline first. Without a strong normalized representation, the graph, retrieval, and verification layers will be much harder to compare or patent convincingly.
