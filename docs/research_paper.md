# SAGER: Structure-Aware Graph Evidence Retrieval for Document Intelligence

## Abstract

This paper reports the design and evaluation of a prototype document-intelligence system that replaces flat chunk-based retrieval with an evidence-graph workflow over a large PDF corpus. The system processed 1,076 PDFs from a local corpus, successfully converted 1,059 documents into structured JSON artifacts, and built a persistent search index spanning 492,530 evidence atoms. The prototype combines document parsing, structure-aware atom normalization, graph construction, persistent semantic indexing, and support-based retrieval. Results show that the system can retrieve grounded evidence across a heterogeneous corpus and return support-linked document hits with sub-second to low-single-digit latency for many practical queries. The study also identifies current limitations: structure labeling is heuristic rather than parser-native, semantic retrieval uses TF-IDF rather than transformer embeddings, and verification remains support-oriented rather than truth-certified. The main conclusion is that evidence-graph document intelligence is a materially stronger direction than plain chunked RAG, but production-grade accuracy will require richer parsing and stronger embedding models.

## 1. Introduction

Document intelligence has largely been dominated by three families of systems:

- OCR followed by extraction rules
- vector search over flat document chunks
- retrieval-augmented generation over semantically chunked text

These approaches are often adequate for short, well-structured text, but they degrade on real enterprise and technical documents containing:

- tables
- headings and section hierarchies
- footnotes
- citations
- mixed reading order
- large multi-page context

This project investigated whether a more structured retrieval architecture could improve corpus usability without requiring a fully custom multimodal foundation model. The working hypothesis was that documents should be represented as **evidence atoms linked in an evidence graph**, then retrieved through a combination of semantic ranking and local graph expansion.

![Architecture](/Users/meetjethwa/Development/PatentIdeas/DocIntelligence/docs/diagrams/architecture.png)

## 2. Research Question

The central question of this experiment was:

**Can a structure-aware evidence-graph prototype provide a more useful and scalable document-intelligence substrate than flat chunk retrieval on a large heterogeneous PDF corpus?**

Sub-questions included:

- Can a large raw PDF corpus be converted into reusable evidence artifacts at scale?
- Can simple structure-aware normalization improve retrieval behavior without bespoke annotation?
- Can a persistent semantic index make corpus-wide retrieval practical?
- Do support-linked hits provide a better inspection experience than plain top-k text retrieval?

## 3. System Design

The prototype consists of five stages:

1. PDF ingestion and text extraction
2. Evidence atom normalization
3. Evidence graph construction
4. Persistent semantic indexing
5. Support-aware retrieval and inspection

### 3.1 Evidence atoms

Each processed document is decomposed into evidence atoms containing:

- document identifier
- page number
- text content
- reading order
- parser source
- confidence score
- role label
- inferred atom type

### 3.2 Structure-aware normalization

The system enriches atoms using heuristic structure inference. Atoms may be labeled as:

- `heading`
- `table_of_contents`
- `table_caption`
- `figure_caption`
- `footnote`
- `citation`
- `table_row`
- default `body`

This step is intentionally lightweight but important because it allows retrieval to weight structurally important evidence more heavily.

### 3.3 Evidence graph

For each document, a graph is built using:

- adjacency edges based on reading order
- containment edges linking headings to subsequent body atoms

This graph is still simple compared with a full multimodal graph, but it already supports context expansion beyond literal top-ranked atoms.

### 3.4 Persistent semantic index

The corpus index is stored on disk and includes:

- document-level TF-IDF vectors
- atom-level TF-IDF vectors
- atom metadata for page and structure inspection

At query time, the system:

- ranks documents semantically
- boosts documents with high-scoring atom matches
- runs graph-based context assembly inside candidate documents
- returns support-linked hits

## 4. Experimental Setup

### 4.1 Corpus

The experiment used a local corpus of PDFs in the `Pdf/` directory.

Corpus statistics:

- total PDFs discovered: `1076`
- successfully processed: `1059`
- failed due to corruption, encryption, or malformed structure: `17`
- processed evidence atoms: `492530`
- persistent index size: `137.41 MB`

### 4.2 Implementation environment

The prototype was implemented in Python with:

- FastAPI
- Pydantic
- NetworkX
- scikit-learn
- pypdf

### 4.3 Evaluation style

This was a prototype systems study, not a formal benchmark-paper evaluation. The goal was to assess:

- pipeline robustness
- retrieval usability
- corpus-scale search behavior
- support traceability

The experiment used representative queries rather than a manually labeled gold set.

## 5. Results

### 5.1 Processing results

The ingestion pipeline proved robust enough for large-batch corpus conversion:

- 98.42% of discovered PDFs were processed successfully
- malformed files were isolated into a manifest instead of breaking the run
- each successful file produced reusable JSON evidence artifacts

This is a strong operational result because one of the practical bottlenecks in document intelligence is not only retrieval quality, but also whether large messy corpora can be normalized reliably enough to query at all.

### 5.2 Structure enrichment results

The inferred structure-label distribution across the processed corpus was:

- `body`: `363403`
- `heading`: `70907`
- `footnote`: `38222`
- `table_row`: `17632`
- `citation`: `1161`
- `table_caption`: `598`
- `figure_caption`: `511`
- `table_of_contents`: `96`

This indicates that even lightweight heuristics can recover a substantial amount of useful structural signal at scale, especially headings and footnotes.

### 5.3 Query behavior

Representative query results showed the following latencies:

- `"humanitarian data governance"`: `0.623 s`
- `"termination clause notice"`: `6.022 s`
- `"table revenue amount"`: `1.591 s`
- `"data responsibility guidelines"`: `0.239 s`
- `"figure results confidence"`: `2.338 s`

These timings suggest that the persistent index makes corpus-wide retrieval practical, though complexity still varies by query and candidate-document behavior.

### 5.4 Qualitative retrieval outcomes

The strongest performance appeared on domain-aligned informational queries such as:

- humanitarian data
- data responsibility
- governance-oriented topics

For example, the query `"data responsibility guidelines"` correctly surfaced a highly relevant humanitarian-data document with a strong score and support-linked evidence.

The system also returned support-linked hits for broader queries such as `"figure results confidence"` and `"table revenue amount"`, showing that the prototype can move beyond pure keyword search and preserve some structural grounding during result assembly.

However, the query `"termination clause notice"` exposed a key limitation: the prototype returned supported results, but not clearly legal-domain-specialized results. This indicates that the current semantic layer and structure inference are still too generic for precise clause intelligence in mixed-domain corpora.

## 6. Verdict

### Short verdict

**The experiment is a success as a systems prototype, but not yet a final document-intelligence solution.**

### What succeeded

- Large-scale corpus normalization worked.
- Persistent search over more than a thousand PDFs worked.
- Evidence-atom search with graph expansion produced grounded, inspectable results.
- Structure-aware normalization improved the corpus representation meaningfully.
- A usable UI and API were built on top of the index.

### What did not fully succeed

- The semantic layer is still classical TF-IDF, not transformer-grade semantic search.
- Structure extraction is heuristic and text-based, not true layout-native document parsing.
- Graph edges are still shallow and do not capture full table, citation, and figure relations.
- Verification currently checks support presence, not factual correctness.
- Domain precision remains uneven for specialized tasks like legal clause retrieval.

## 7. Conclusion

The core conclusion of this experiment is that **evidence-graph document intelligence is a stronger practical foundation than plain chunk-based retrieval for large heterogeneous document corpora**.

Three findings support that conclusion:

1. The corpus could be processed into reusable evidence artifacts at high success rate.
2. Structure-aware atomization provided meaningful signals that improved retrieval and inspection.
3. Persistent semantic indexing made corpus-scale search feasible while keeping support traceability.

At the same time, the experiment shows that moving beyond chunked RAG is not enough by itself. To become genuinely state-of-the-art, the system will need:

- parser-native layout and table understanding
- stronger semantic embeddings
- richer graph edges
- better domain-specific routing and verification

So the right conclusion is not that the problem is solved. The right conclusion is that the project has validated the **architecture direction**.

## 8. Implications for Patent Strategy

These results strengthen the invention direction proposed earlier:

- evidence atoms are a workable unit of document representation
- graph-based context assembly is technically practical
- support-linked retrieval is commercially meaningful
- selective enrichment and indexing are differentiating components

The experiment therefore supports a patent position centered on:

- evidence-graph construction
- query-conditioned context assembly
- structure-aware retrieval
- support-based verification

rather than conventional chunking or generic RAG.

## 9. Limitations

This study has several limitations:

- No human-labeled benchmark set was used.
- No formal comparison against a strong modern RAG baseline was run.
- No transformer or multimodal embedding model was used in retrieval.
- PDF parsing relied primarily on text extraction rather than rich visual parsing.
- Support quality was evaluated qualitatively, not with a citation-faithfulness metric.

These limitations mean the current results should be interpreted as prototype validation rather than a definitive retrieval benchmark.

## 10. Future Work

The next research steps should be:

1. Replace heuristic structure inference with layout-aware parsing.
2. Upgrade semantic retrieval from TF-IDF to transformer embeddings.
3. Add richer graph relations for tables, captions, references, and cross-page links.
4. Build a labeled evaluation set for document QA and extraction.
5. Compare directly against chunked RAG, semantic chunking, and hierarchical retrieval baselines.

## 11. Final Conclusion

This experiment demonstrates that a large heterogeneous PDF corpus can be transformed into a searchable evidence-graph substrate and queried in a grounded, inspectable way. The system is not yet state-of-the-art in extraction accuracy or semantic depth, but it has validated a direction that is both technically promising and patentable.

In plain terms:

**RAG plus chunking is not the best long-term answer here. Evidence graphs plus structure-aware, support-linked retrieval look like the better path.**
