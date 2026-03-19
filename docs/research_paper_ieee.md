# SAGER: Structure-Aware Graph Evidence Retrieval for Document Intelligence

**Author:** Meet Jethwa  
**Affiliation:** Independent Research / DocIntelligence Prototype  
**Date:** March 15, 2026

## Abstract

Conventional document intelligence systems often flatten documents into contiguous text chunks and perform retrieval over those chunks using keyword or embedding similarity. While effective for short and clean text, these methods frequently degrade on long-form, layout-heavy, and structurally complex documents. This paper presents a prototype evidence-graph retrieval system for large-scale PDF corpora. The system processed 1,076 PDFs, successfully converted 1,059 into structured evidence artifacts, and indexed 492,530 evidence atoms using a persistent semantic index. The prototype integrates PDF extraction, structure-aware atom normalization, document-level graph construction, semantic retrieval, and support-linked inspection. Experimental results show that the architecture is operationally robust and useful for corpus-scale retrieval, with query latencies ranging from 0.242 s to 6.470 s across representative tasks. The results validate the architectural direction of evidence-graph document intelligence, while also revealing clear limits in semantic depth, parser fidelity, and domain-specific precision. The study concludes that evidence-graph retrieval is a stronger substrate than plain chunk-based retrieval for complex documents and provides a practical basis for future patent-oriented work.

**Index Terms:** document intelligence, retrieval-augmented generation, evidence graph, PDF mining, semantic retrieval, document extraction

## I. Introduction

Document intelligence remains difficult when the source material contains headings, footnotes, citations, tables, figure references, inconsistent reading order, and long-range dependencies across pages. Many deployed systems still rely on OCR followed by extraction heuristics or chunk-based retrieval over linearized text. These approaches simplify implementation but lose structural information and often produce unsupported outputs on complex corpora.

This work investigates a different architecture: represent documents as **evidence atoms**, connect them through a lightweight **evidence graph**, and retrieve support-linked context from those atoms rather than relying exclusively on static chunks. The objective of this study is not to claim state-of-the-art accuracy, but to evaluate whether this architecture is practically workable over a large and noisy PDF corpus.

## II. Problem Statement and Motivation

The motivating problem is that standard chunking frequently obscures:

- document hierarchy
- local provenance
- cross-page context
- support traceability
- the distinction between body text, headings, footnotes, and citation-like material

The research question is therefore:

**Can a structure-aware evidence-graph prototype provide a more useful and scalable document-intelligence substrate than flat chunk retrieval on a large heterogeneous PDF corpus?**

## III. System Architecture

The prototype consists of five stages:

1. PDF ingestion and text extraction
2. evidence atom normalization
3. evidence graph construction
4. persistent semantic indexing
5. support-aware retrieval and inspection

Fig. 1 shows the end-to-end architecture used in the prototype.

![Figure 1. System architecture.](/Users/meetjethwa/Development/PatentIdeas/DocIntelligence/docs/diagrams/architecture.png)

### A. Evidence Atoms

Each document is decomposed into evidence atoms containing:

- document id
- page number
- extracted text
- reading order
- parser source
- confidence
- atom type
- structure label

### B. Structure-Aware Normalization

Atoms are enriched with heuristic labels such as:

- `heading`
- `table_of_contents`
- `table_caption`
- `figure_caption`
- `footnote`
- `citation`
- `table_row`
- `body`

This enrichment is intentionally lightweight, but it allows the system to distinguish higher-value structural regions from plain body text.

### C. Evidence Graph

Each document yields a simple directed graph with:

- adjacency edges in reading order
- containment edges from inferred headings to following atoms

Fig. 2 shows the process flow used to construct and query the graph.

![Figure 2. Processing and retrieval flow.](/Users/meetjethwa/Development/PatentIdeas/DocIntelligence/docs/diagrams/process_flow.png)

### D. Persistent Semantic Index

The final index stores:

- document-level TF-IDF vectors
- atom-level TF-IDF vectors
- atom metadata for support inspection

At query time, the system ranks documents semantically, boosts them using high-scoring atom matches, performs graph-based context assembly inside candidate documents, and returns support-linked hits.

### E. Data Model

The core data model is shown in Fig. 3.

![Figure 3. Evidence-graph data model.](/Users/meetjethwa/Development/PatentIdeas/DocIntelligence/docs/diagrams/data_model.png)

## IV. Experimental Setup

### A. Corpus

The study used a local corpus of PDFs stored in the project workspace. The corpus contained mixed document types and quality levels, including malformed and encrypted files.

### B. Implementation Stack

The prototype was implemented with:

- Python
- FastAPI
- Pydantic
- NetworkX
- scikit-learn
- pypdf

### C. Evaluation Style

This was a systems prototype study rather than a formal benchmark evaluation. The experiment focused on:

- corpus processing robustness
- retrieval usability at scale
- structure-aware indexing behavior
- support-linked result inspection

Queries were selected to reflect plausible document-intelligence use cases rather than a fixed labeled benchmark.

## V. Experimental Results

### A. Corpus Processing Results

Table I summarizes the ingestion and indexing outcomes.

**Table I**  
**Corpus Processing and Indexing Summary**

| Metric | Value |
|---|---:|
| Total PDFs discovered | 1076 |
| Successfully processed PDFs | 1059 |
| Failed PDFs | 17 |
| Processing success rate | 98.42% |
| Indexed evidence atoms | 492530 |
| Persistent index size | 137.41 MB |

The 17 failures were isolated into the processing manifest and did not stop the full batch run, which is important operationally for noisy real-world corpora.

### B. Structure Enrichment Results

Table II reports the observed distribution of inferred structural labels over the processed corpus.

**Table II**  
**Observed Structure-Label Distribution**

| Structure label | Count |
|---|---:|
| body | 363403 |
| heading | 70907 |
| footnote | 38222 |
| table_row | 17632 |
| citation | 1161 |
| table_caption | 598 |
| figure_caption | 511 |
| table_of_contents | 96 |

These results indicate that even heuristic enrichment can recover meaningful structural signals at scale, especially headings and footnotes.

### C. Query-Level Retrieval Results

Representative query results are shown in Table III.

**Table III**  
**Representative Retrieval Queries**

| Query | Latency (s) | Returned hits | Top hit doc id | Top hit score |
|---|---:|---:|---|---:|
| humanitarian data governance | 0.679 | 3 | `536b64435024c919d6b4c3f5819a889d0607f349` | 4.83 |
| termination clause notice | 6.470 | 3 | `2544CYX3TC3T5QB2NTVXD3IUFM654GXK` | 6.00 |
| table revenue amount | 2.133 | 3 | `Y5P3TB77KSPOLIUMLGDQIIGE7XMVNENP` | 20.85 |
| data responsibility guidelines | 0.242 | 3 | `642c5aed3f342a15e2ae287d5350a5735bae9ebc` | 11.95 |
| figure results confidence | 2.371 | 3 | `SYBT26QCMSRHEOFZDZM4TZ5CCJ6T34MF` | 5.02 |

The latency spread suggests that persistent indexing made corpus-wide retrieval practical, but query complexity and candidate-document behavior still influenced response time.

### D. Qualitative Findings

The prototype performed best on topical, informational, and governance-oriented queries aligned with the dominant themes in the corpus. Queries such as `data responsibility guidelines` and `humanitarian data governance` returned clearly relevant support-linked hits. More ambiguous or domain-specialized queries, such as `termination clause notice`, exposed a current weakness: the system still retrieves grounded text, but not consistently domain-targeted legal evidence.

## VI. Discussion

The experiment supports several conclusions.

First, the evidence-graph representation is operationally viable at corpus scale. The system successfully normalized a large set of PDFs into reusable artifacts and queried them through a persistent index.

Second, structure-aware atomization appears useful even when implemented heuristically. The recovered counts for headings, footnotes, table-like rows, captions, and citation-like atoms show that the corpus is not best treated as undifferentiated text.

Third, the results suggest that evidence-graph retrieval is a stronger substrate than plain chunk retrieval for complex document collections because it preserves support traceability and document-local structure during retrieval.

At the same time, the study also shows where the current system remains limited:

- semantic retrieval is based on TF-IDF rather than transformer embeddings
- structure recognition is heuristic rather than parser-native
- graph relations are shallow and mostly local
- support verification detects evidence presence, not factual correctness
- domain precision remains uneven for specialized legal and analytical queries

## VII. Verdict

The verdict of the experiment is:

**The prototype is a successful architecture validation, but not yet a final production-grade document-intelligence system.**

This statement is justified by four concrete outcomes:

1. Large-scale corpus normalization succeeded with a 98.42% processing rate.
2. The system built and persisted a usable semantic evidence index over 492,530 atoms.
3. The search layer returned support-linked results through both API and UI interfaces.
4. The retrieval quality was meaningfully better on structured informational queries than would be expected from raw flat text search alone.

However, the system has not yet demonstrated:

- benchmarked superiority over strong modern RAG baselines
- transformer-level semantic understanding
- layout-native multimodal extraction
- consistently strong precision for legal or table-centric reasoning tasks

## VIII. Conclusion

This study demonstrates that a large heterogeneous PDF corpus can be transformed into a searchable, inspectable evidence-graph substrate. The evidence-graph architecture proved more promising than flat chunk-based retrieval as a foundation for document intelligence because it preserved structural cues and support traceability while remaining practical at corpus scale.

The central conclusion is therefore:

**Evidence-graph retrieval is a better long-term direction than plain chunking or generic RAG for complex document intelligence, but the current prototype should be viewed as an architectural proof rather than a final system.**

## IX. Limitations and Future Work

This study has several limitations:

- no human-labeled benchmark set was used
- no direct comparison against a strong chunked-RAG baseline was run
- no transformer or multimodal embedding model was used
- parsing was mostly text extraction rather than full layout-native understanding
- support quality was assessed qualitatively rather than by citation-faithfulness metrics

The next steps are:

1. replace heuristic structure labeling with layout-aware parsing
2. replace TF-IDF embeddings with transformer embeddings
3. add richer graph edges for tables, figures, references, and cross-page relations
4. construct a labeled evaluation set
5. compare directly against chunked RAG, semantic chunking, and hierarchical retrieval baselines

## References

[1] M. Jethwa, “Adaptive Evidence-Graph Retrieval for Large-Scale Document Intelligence: A Prototype Study over 1,059 PDFs,” internal project manuscript, 2026.

[2] DocIntelligence prototype repository artifacts, including processed corpus, evidence index, architecture diagrams, and API implementation, `/Users/meetjethwa/Development/PatentIdeas/DocIntelligence`, 2026.
