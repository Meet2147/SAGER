# SDF Concept Note

## Title

SDF: SAGER Document Format

## Short definition

`.sdf` is a SAGER-native derivative document format generated after processing a source document. It is designed to store **structured evidence**, **graph relationships**, **provenance**, and **retrieval-ready metadata** in a machine-native form.

In simple terms:

- `PDF` is for visual fidelity and human reading
- `.sdf` is for evidence-aware machine retrieval and reasoning

## Why SDF exists

PDFs are good for:

- preserving layout
- preserving rendering fidelity
- distribution

PDFs are not naturally good for:

- evidence-aware retrieval
- provenance-linked AI reasoning
- graph-based document understanding
- support verification
- repeated downstream querying without reparsing

SDF is meant to solve that gap.

Instead of reparsing a PDF every time, SAGER generates an `.sdf` file once, and downstream systems retrieve from the SDF directly.

## Core idea

SAGER first processes a source document and extracts:

- evidence atoms
- structure labels
- graph edges
- confidence scores
- parser provenance
- page references
- retrieval metadata

It then stores these outputs in a standardized derivative artifact:

**SDF = SAGER Document Format**

## What SDF contains

An SDF file should contain, at minimum:

- source document metadata
- page metadata
- evidence atoms
- graph edges
- structure labels
- parser provenance
- confidence values
- optional retrieval annotations

Optional future additions:

- embeddings
- support traces
- query history
- selective reprocessing history
- domain-specific annotations

## Why SDF is more than JSON

Right now we use JSON artifacts in the prototype. SDF is a better concept because it introduces:

- a formal schema
- a formal extension
- a stable interchange contract
- a retrieval-native identity
- stronger product and patent framing

So SDF should be thought of as:

**a retrieval-native evidence document container**

not just a random serialized export.

## SDF design goals

The format should be:

- human inspectable
- machine readable
- stable
- provenance preserving
- retrieval oriented
- extensible

## Proposed file extension

`.sdf`

Expanded as:

**SAGER Document Format**

## Proposed top-level schema

```json
{
  "format": "SDF",
  "version": "0.1",
  "method": {
    "name": "SAGER",
    "expanded": "Structure-Aware Graph Evidence Retrieval"
  },
  "source": {
    "path": "...",
    "doc_id": "...",
    "page_count": 0
  },
  "stats": {
    "atom_count": 0,
    "edge_count": 0,
    "extracted_text_chars": 0
  },
  "atoms": [],
  "edges": [],
  "annotations": {
    "role_distribution": {},
    "notes": []
  }
}
```

## Atom schema

Each atom may include:

```json
{
  "atom_id": "doc-p1-a0",
  "doc_id": "doc",
  "page": 1,
  "atom_type": "text",
  "text": "Example line",
  "bbox": {"x0": 0, "y0": 0, "x1": 100, "y1": 20},
  "reading_order": 0,
  "parser_source": "pypdf",
  "confidence": 0.81,
  "role_label": "heading"
}
```

## Edge schema

Each edge may include:

```json
{
  "source": "doc-p1-a0",
  "target": "doc-p1-a1",
  "edge_type": "adjacent",
  "weight": 1.0
}
```

## Retrieval model over SDF

SDF retrieval should work like this:

1. load one or more SDF files
2. score candidate atoms
3. expand through graph relationships
4. return support-linked results

That means SDF is not just a storage format. It is also a **retrieval substrate**.

## Patent-oriented novelty angle

The strongest patent story is not simply:

- “store processed data in a file”

The stronger angle is:

- generate a machine-native derivative file from a source document
- encode evidence atoms and graph relationships in that file
- use the derivative file for subsequent retrieval and reasoning without reparsing the source
- update or partially rewrite the derivative file after selective reprocessing

That is a much more defensible system-level invention angle.

## Draft patent-style claim themes

These are not legal claims, but invention directions.

1. A method for generating an SDF derivative file from a source document, wherein the SDF file stores evidence atoms and graph relationships.
2. A method for retrieving support-linked context directly from the SDF file without reparsing the source PDF.
3. A method for selectively updating a portion of the SDF file after reprocessing uncertain regions of the source document.
4. A system in which SDF acts as the primary retrieval substrate for downstream extraction, question answering, or compliance workflows.

## Practical recommendation

SDF should be treated as:

**the machine-native evidence form of a source document after SAGER processing**

That gives it value in:

- product architecture
- research framing
- patent framing
- reusable corpus building

## Short summary

If someone asks what SDF is:

> SDF is a SAGER-native structured document format that stores evidence atoms, graph structure, provenance, and retrieval metadata so that AI systems can query documents directly in evidence form without reparsing the original PDF.
