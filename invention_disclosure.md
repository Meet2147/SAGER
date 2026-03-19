# Invention Disclosure Draft

## Title

Adaptive Evidence Graph Construction and Verified Context Assembly for Multimodal Document Intelligence

## Field

This invention relates to document intelligence, information extraction, information retrieval, multimodal machine learning, and computer systems for grounded question answering and structured extraction from complex documents.

## Problem

Most document AI systems still rely on one of two weak patterns:

- flat OCR text followed by field extraction
- chunk-based RAG over sectioned or sliding-window text

These patterns fail on real enterprise documents because such documents contain:

- complex layouts
- tables and formulas
- figures and captions
- footnotes and appendices
- cross-page dependencies
- ambiguous reading order
- mixed scanned and digital content

Even strong modern parsers do not solve the whole problem, because the downstream retrieval layer often collapses the document into fixed chunks that lose structure, provenance, and confidence information.

## Summary of invention

The invention introduces a system that transforms one or more documents into a **multimodal evidence graph** made of evidence atoms and relationships between them. For a given query or extraction task, the system generates a **context assembly program** that gathers the best supporting evidence by traversing and filtering the graph instead of selecting static chunks.

The invention further verifies any answer or structured extraction against a supporting evidence subgraph and can selectively reprocess uncertain document regions using alternate parsing configurations.

## Key components

### 1. Multi-parser ingestion

The system receives a document and applies multiple analysis processes, such as:

- OCR
- layout analysis
- vision-language parsing
- table extraction
- formula extraction
- metadata extraction

### 2. Evidence atom generation

Outputs are normalized into evidence atoms, each having:

- content
- atom type
- page identifier
- coordinates
- reading-order sequence
- parser source
- parser confidence
- semantic representation
- document-role label

### 3. Evidence graph construction

Atoms are connected using relationships including:

- containment
- adjacency
- spatial proximity
- row/column table relationships
- caption-object linkage
- citation-reference linkage
- semantic similarity
- contradiction indicators

### 4. Multi-resolution indexing

The graph is indexed across multiple levels:

- document landmarks
- section-level summaries
- evidence atoms
- graph neighborhoods
- layout regions

### 5. Context assembly program

For each query, the system predicts:

- query type
- evidence type requirements
- traversal depth
- ranking strategy
- verification policy

It then executes a context assembly program to produce a query-specific evidence set.

### 6. Verified generation or extraction

The system generates:

- answers
- extracted fields
- normalized records
- summaries
- compliance findings

Each output is accompanied by supporting evidence references and may be rejected, revised, or escalated if support is inadequate.

### 7. Selective reprocessing

If relevant atoms are low-confidence, structurally inconsistent, or contradictory across parsers, the system reprocesses only the implicated pages or regions using alternate models, settings, or resolutions.

## Example embodiments

### Embodiment 1: Contract review

The system identifies indemnity clauses, termination provisions, and liability caps by traversing section, definition, and cross-reference edges. It verifies each extracted clause against source spans and rejects unsupported summaries.

### Embodiment 2: Financial statement intelligence

The system extracts line items from tables and footnotes, linking cell values to captions, reporting periods, and explanatory notes. Query answers cite both the numeric cell and supporting narrative context.

### Embodiment 3: Scientific paper mining

The system associates claims in the body text with tables, figures, captions, formulas, and references, producing evidence-backed extraction of methods, results, and confidence qualifiers.

### Embodiment 4: Patent analytics

The system builds cross-document evidence graphs linking claim terminology, embodiments, prior-art citations, and figure references to support grounded novelty analysis.

## Technical advantages

Compared with fixed chunk retrieval and flat OCR pipelines, the invention can provide:

- improved fidelity to document structure
- better retrieval of cross-page and cross-modal evidence
- lower unsupported-answer rates
- better auditability through provenance links
- targeted compute use via selective reprocessing
- improved performance on tables, figures, footnotes, and dense technical layouts

## Novelty hypothesis

The likely inventive combination is not any single parser or embedding method. The likely inventive combination is:

- multimodal evidence atom normalization
- graph-based representation with structural and semantic edges
- query-conditioned context assembly
- provenance-aware verification
- uncertainty-triggered selective reprocessing

This combination appears materially more specific and defensible than generic RAG, semantic chunking, or document OCR workflows.

## Draft claim themes

1. A method for building evidence atoms from outputs of multiple document-analysis models and linking the atoms into an evidence graph.
2. A method for generating a query-conditioned context assembly program that traverses the evidence graph differently based on query type.
3. A method for verifying generated outputs against a connected evidence subgraph satisfying confidence and provenance criteria.
4. A method for selective reprocessing of document regions based on uncertainty detected in graph nodes relevant to a task.
5. A system implementing the above methods across single-document and multi-document workflows.

## Implementation sketch

### Data model

- `Document`
- `Page`
- `EvidenceAtom`
- `Edge`
- `ParserRun`
- `ContextProgram`
- `SupportSubgraph`

### Retrieval flow

1. Parse document with one or more parsers.
2. Normalize parser outputs into atoms.
3. Build graph and indexes.
4. Classify query.
5. Execute context assembly program.
6. Generate output.
7. Verify support.
8. If support is weak, selectively reprocess and retry.

## What to show in a prototype

- Baseline versus evidence-graph retrieval on long and layout-heavy documents.
- Improvement in table and footnote extraction accuracy.
- Reduction in unsupported answers.
- Lower cost than full-document reprocessing by using selective re-extraction.

## Filing recommendation

Prepare this as a provisional filing candidate and add:

- architecture diagram
- flowchart
- sample data schema
- 3 or more detailed embodiments
- benchmark results

## Practical note

This draft is a technical invention memo, not legal advice. Before filing, a patent attorney should run a formal prior-art search and convert this material into jurisdiction-specific claims.
