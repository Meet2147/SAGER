# Provisional Patent Draft

## Title

Adaptive Evidence Graph Construction, Query-Conditioned Context Assembly, and Verified Output Generation for Multimodal Document Intelligence

## Cross-Reference

This draft is based on the invention materials in [patent_plan.md](/Users/meetjethwa/Development/PatentIdeas/DocIntelligence/patent_plan.md), [invention_disclosure.md](/Users/meetjethwa/Development/PatentIdeas/DocIntelligence/invention_disclosure.md), and [patent_package.md](/Users/meetjethwa/Development/PatentIdeas/DocIntelligence/patent_package.md).

## Field of the Invention

The present disclosure relates to document intelligence systems and, more particularly, to computer-implemented methods and systems for extracting, indexing, retrieving, and verifying information from complex multimodal documents.

## Background

Enterprise and technical documents are difficult for conventional information systems to process accurately because the relevant information is not stored as clean linear text. Instead, such information is frequently distributed across:

- paragraphs and section hierarchies
- tables and table headers
- footnotes and appendices
- figures and captions
- formulas and symbols
- cross-references and citations
- scanned and digitally generated regions within the same file

Traditional document processing pipelines frequently depend on optical character recognition followed by flat text extraction. More recent retrieval systems frequently divide the resulting text into fixed windows or semantically grouped chunks and then apply embedding-based retrieval. While useful, such approaches often lose spatial information, parser provenance, local confidence, and inter-element relationships. This can result in unsupported answers, incorrect field extraction, and poor performance on layout-heavy or cross-page tasks.

Accordingly, there remains a need for a document-intelligence architecture that preserves multimodal structure, supports task-aware retrieval, and verifies outputs against underlying evidence.

## Summary of the Invention

In one aspect, the disclosure provides a computer-implemented method that receives a document, obtains outputs from multiple document-analysis processes, and converts those outputs into normalized evidence atoms carrying extracted content and associated metadata. The evidence atoms are linked into an evidence graph using structural, spatial, semantic, and reference-based relationships.

In another aspect, a task input such as a question, extraction request, or analysis request is used to generate a context assembly program. The context assembly program specifies how the evidence graph should be traversed, filtered, and ranked to produce a task-specific context set. An output is then generated from the task-specific context set.

In another aspect, the output is verified against a supporting evidence subgraph before being accepted, returned, or stored. If the supporting evidence is inadequate, contradictory, or low-confidence, the system selectively reprocesses only relevant document regions using an alternate parser configuration and updates the evidence graph.

The disclosed architecture therefore improves grounded extraction and question answering while limiting unnecessary reprocessing cost.

## Brief Description of the Figures

### Figure 1

System architecture showing multi-parser ingestion, evidence atom normalization, evidence graph construction, indexing, context assembly, generation, verification, and selective reprocessing.

### Figure 2

Process flow showing document ingestion, atomization, graph construction, context assembly, output generation, support verification, and region-level reprocessing.

### Figure 3

Data model showing relationships among documents, pages, parser runs, evidence atoms, edges, context programs, and support subgraphs.

## Detailed Description

### 1. Definitions

For purposes of this disclosure:

- "evidence atom" refers to a normalized unit of extracted document information
- "evidence graph" refers to a graph linking evidence atoms through one or more relationship types
- "context assembly program" refers to a task-conditioned specification for retrieving and traversing evidence atoms
- "support subgraph" refers to a subset of the evidence graph that supports a generated output

### 2. Document ingestion and parser coordination

A document may be received in digital, scanned, image-based, or mixed form. One or more parser engines may be invoked, including OCR engines, layout analysis models, table extraction models, vision-language models, formula extraction models, and metadata extractors.

Different parser engines may produce overlapping or conflicting interpretations. Rather than collapsing these outputs immediately into a single text stream, the system preserves parser identity and confidence as part of a downstream representation.

### 3. Evidence atom normalization

Parser outputs are normalized into evidence atoms. Each evidence atom may include:

- a content field
- an atom type
- a page identifier
- coordinates or a bounding region
- a reading-order index
- a parser identifier
- a parser confidence score
- a role label
- an embedding reference or semantic representation

Atom types may include text spans, section headers, clauses, table cells, table headers, captions, figure references, formulas, citations, key-value pairs, or layout zones.

### 4. Evidence graph construction

The evidence graph may include one or more of:

- containment edges
- adjacency edges
- spatial proximity edges
- table row and column edges
- caption-to-figure edges
- citation and cross-reference edges
- semantic similarity edges
- contradiction edges

The graph may be maintained at multiple levels of granularity, including document level, page level, section level, and atom level.

### 5. Indexing

The system may maintain multiple indexes over the evidence graph, including:

- semantic vector indexes
- structural path indexes
- spatial indexes
- reference indexes
- landmark or summary indexes

Such indexes may support coarse routing, fine retrieval, or graph expansion.

### 6. Context assembly

Upon receiving a task input, the system may determine a task type and generate a context assembly program. The task type may include factual lookup, clause extraction, table retrieval, cross-page synthesis, or cross-document comparison.

The context assembly program may specify:

- seed retrieval modes
- graph edge types to traverse
- expansion depth
- ranking criteria
- stopping conditions
- verification requirements

In this way, the system can adapt retrieval to the structure of the task instead of relying on fixed chunk boundaries.

### 7. Output generation and verification

The task-specific context set is supplied to an extraction or generation engine to produce a structured output, answer, summary, or finding. A verification engine then identifies a support subgraph and determines whether the output satisfies support constraints.

Support constraints may include:

- minimum parser confidence
- minimum provenance diversity
- structural consistency
- spatial consistency
- absence of contradiction

Outputs failing such constraints may be rejected, flagged, or revised.

### 8. Selective reprocessing

When support is insufficient or contradictory, the system may identify one or more implicated pages or regions and selectively reprocess those pages or regions using one or more alternate parser configurations. The updated results are merged into or replace portions of the evidence graph, and the task may be rerun.

This selective reprocessing reduces cost compared with rerunning the entire pipeline for the full document.

## Example Embodiments

### Embodiment 1: Contract analysis

The system extracts clause spans, definition terms, schedules, and notice provisions. For a task concerning termination rights, the system traverses defined-term edges, clause edges, and cross-reference edges to gather the relevant evidence. The output includes the extracted clause text and linked support regions.

### Embodiment 2: Financial report analysis

The system extracts tables, headers, numeric cells, reporting periods, and supporting note text. For a task asking for revenue by segment, the system assembles context from the relevant table cells, associated headers, and adjacent footnote text.

### Embodiment 3: Scientific literature mining

The system links claims in body text to figures, captions, formulas, and result tables. For a task asking for reported outcomes and confidence qualifiers, the system returns only outputs supported by a connected subgraph spanning the relevant text and table evidence.

### Embodiment 4: Multi-document patent intelligence

The system links claims, embodiments, figures, and technical features across a target patent document and prior-art references, thereby enabling grounded novelty analysis and evidence tracing.

## Advantages

The disclosed architecture may provide one or more of the following technical advantages:

- improved preservation of document structure
- improved retrieval over tables, figures, and footnotes
- improved support tracing and auditability
- reduced unsupported-answer rates
- reduced compute cost through selective reprocessing

## Numbered Claims

### Claim 1

A computer-implemented method for document intelligence, the method comprising:
receiving a digital document;
generating a plurality of evidence atoms from outputs of a plurality of document-analysis processes;
constructing an evidence graph connecting the plurality of evidence atoms according to one or more structural, spatial, semantic, or reference relationships;
receiving a task input associated with the digital document;
determining, based on the task input, a context assembly program;
executing the context assembly program over the evidence graph to generate a task-specific context set;
generating an output based on the task-specific context set; and
verifying the output using support constraints associated with the plurality of evidence atoms.

### Claim 2

The method of claim 1, wherein each evidence atom includes page coordinates.

### Claim 3

The method of claim 1, wherein each evidence atom includes a reading-order position.

### Claim 4

The method of claim 1, wherein each evidence atom includes parser provenance and a confidence score.

### Claim 5

The method of claim 1, wherein the evidence graph includes containment edges, adjacency edges, and table-structure edges.

### Claim 6

The method of claim 1, wherein the context assembly program is selected based on a predicted task type.

### Claim 7

The method of claim 1, wherein the task-specific context set is generated by combining graph traversal with semantic retrieval.

### Claim 8

The method of claim 1, wherein verifying the output includes identifying a connected support subgraph.

### Claim 9

The method of claim 8, wherein the connected support subgraph is evaluated based on confidence, provenance, and contradiction criteria.

### Claim 10

The method of claim 1, further comprising:
detecting insufficient support, contradiction, or low confidence among evidence atoms relevant to the output;
selecting one or more document regions associated with the evidence atoms;
reprocessing the selected one or more document regions using an alternate document-analysis configuration; and
updating the evidence graph using results of the reprocessing.

### Claim 11

The method of claim 10, wherein fewer than all pages of the digital document are reprocessed.

### Claim 12

A document-intelligence system comprising:
one or more parser interfaces;
an evidence atom normalizer;
an evidence graph builder;
an index manager;
a query router configured to generate a context assembly program; and
a verification engine configured to validate an output using a supporting evidence subgraph.

### Claim 13

The system of claim 12, wherein the index manager maintains both a semantic index and a structural index.

### Claim 14

The system of claim 12, wherein the evidence graph spans multiple documents.

### Claim 15

A non-transitory computer-readable medium storing instructions that, when executed by one or more processors, cause the one or more processors to perform the method of any one of claims 1-11.

## Filing Notes

This draft should be reviewed and expanded by counsel before filing. In particular, counsel should:

- broaden alternative language around parser engines and model types
- tune claim dependencies for the target jurisdiction
- run a formal prior-art search
- decide whether to split continuation opportunities around reprocessing and verification
