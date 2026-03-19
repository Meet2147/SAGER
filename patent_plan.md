# Patent Plan: Adaptive Evidence Graphs for Multimodal Document Intelligence

## Short thesis

Plain RAG, fixed chunking, and vector search are no longer strong enough as a patent core by themselves. The stronger patent direction is a **document-intelligence system that converts raw documents into multimodal evidence graphs and dynamically assembles query-specific context programs instead of retrieving static chunks**.

This plan is built around a candidate invention family:

**Adaptive Evidence Graph Retrieval and Verified Extraction for Complex Documents**

## Why this is a better direction than standard RAG

The recent literature shows three clear shifts:

1. Document extraction is moving from OCR-only pipelines toward layout-aware and VLM-based parsing.
2. Retrieval is moving beyond naive fixed chunking toward hierarchical, chunk-free, or context-preserving retrieval.
3. High-value document intelligence now depends on provenance, structural grounding, and extraction confidence rather than text similarity alone.

That means a stronger patent should not claim:

- "use RAG on documents"
- "chunk documents semantically"
- "embed sections and retrieve top-k"

Those are too exposed to prior art.

It should instead claim a specific technical architecture that:

- creates fine-grained evidence units from multimodal document structure
- stores them in a graph with spatial, logical, semantic, and citation relationships
- uses query-conditioned assembly of context from the graph rather than fixed chunks
- verifies outputs using provenance and cross-view consistency
- reprocesses uncertain regions adaptively with specialized parsers

## Research landscape and what it suggests

### 1. Extraction frontier: structure-aware and VLM-driven parsing

- Docling Technical Report (Aug 19, 2024) describes a modular document conversion system using layout analysis and table structure recognition, showing that robust document intelligence now begins with structured parsing, not plain OCR.
  Source: https://research.ibm.com/publications/docling-technical-report
- Docling AAAI 2025 paper emphasizes unified richly structured representations across formats and efficient extensibility for downstream AI systems.
  Source: https://research.ibm.com/publications/docling-an-efficient-open-source-toolkit-for-ai-driven-document-conversion
- olmOCR (Feb 2025) pushes PDF extraction with a VLM tuned for reading order and structured content preservation at scale, reinforcing that linearized text alone is insufficient unless tied to document structure.
  Source: https://spacefrontiers.org/r/10.48550/arxiv.2502.18443
- PaddleOCR-VL (Oct 16, 2025) reports strong multilingual page-level and element-level parsing for text, tables, formulas, and charts using a compact VLM, suggesting production-grade multimodal parsing is becoming a baseline expectation.
  Source: https://www.catalyzex.com/author/Cheng%20Cui

Patent implication:
The novelty is unlikely to be "extract document text with AI." The better angle is what happens **after** extraction and how multiple parsing views are fused into a retrieval-ready evidence representation.

### 2. Chunking is being replaced or weakened by richer retrieval schemes

- RAPTOR (Jan 31, 2024) introduces tree-organized retrieval via recursive clustering and summarization, directly addressing the weakness of retrieving only short contiguous chunks.
  Source: https://arxiv.gg/abs/2401.18059
- Late Chunking (Sep 7, 2024) shows that chunk representations improve when chunking happens after full-context encoding, preserving surrounding context.
  Source: https://axi.lims.ac.uk/paper/2409.04701
- Grounding Language Model with Chunking-Free In-Context Retrieval, ACL 2024, explicitly argues that conventional chunking breaks semantic coherence and proposes chunk-free evidence retrieval from encoded document states.
  Source: https://aclanthology.org/2024.acl-long.71/
- Landmark Embedding, ACL 2024, proposes chunking-free embedding for long-context retrieval and position-aware learning over coherent long context.
  Source: https://aclanthology.org/2024.acl-long.180/
- ChunkRAG (Oct 25, 2024) and MoC (Mar 2025) show that even when chunking remains, the field is moving toward learned, adaptive, and query-sensitive chunk policies rather than fixed windows.
  Sources:
  https://spacefrontiers.org/r/10.48550/arxiv.2410.19572
  https://scixplorer.org/abs/2025arXiv250309600Z/abstract

Patent implication:
Do not anchor the invention on "contextual chunking" alone. Anchor it on **dynamic evidence assembly over multimodal document graphs**, where chunks may be only one fallback representation among several.

### 3. Benchmark pressure is shifting toward faithful structure preservation

- OCRBench and olmOCR-Bench show the field is increasingly evaluating extraction systems on structured fidelity, reading order, and machine-verifiable correctness, not just token overlap.
  Sources:
  https://paperswithcode.com/dataset/ocrbench
  https://www.alphaxiv.org/benchmarks/allen-institute-for-ai/olmocr-bench

Patent implication:
Claims that incorporate verification, provenance, and structure-faithful extraction are better aligned with where the field is going.

## Proposed invention

## Working title

**Systems and Methods for Adaptive Evidence Graph Construction and Query-Conditioned Context Assembly for Multimodal Documents**

## Core idea

Instead of converting a document into flat text chunks, the system converts each document into a set of **evidence atoms** and a connected **evidence graph**.

Each evidence atom may represent:

- a text span
- a table cell or table region
- a formula
- a figure caption
- a chart element
- a detected key-value pair
- a citation mention
- a title, section, paragraph, footnote, or clause
- a layout zone or page region

Each atom carries:

- textual content
- page coordinates
- reading-order position
- parser provenance
- confidence score
- document role label
- semantic embedding
- parent-child relationships
- adjacency and cross-reference links

The system then builds multiple linked indexes:

- a semantic vector index
- a structural path index
- a spatial/layout index
- a citation/reference index
- a summary/landmark index for coarse routing

At query time, the system does not just retrieve chunks. It performs:

1. query intent classification
2. evidence-type prediction
3. graph expansion over relevant atom types
4. dynamic context assembly using a "context program"
5. answer or extraction generation with provenance
6. verification and optional reprocessing of uncertain regions

## The real novelty candidates

The best patentable hooks are likely here:

### A. Evidence atoms are multimodal and provenance-bearing

The system stores every extracted unit with parser source, confidence, page geometry, and role metadata, enabling retrieval to reason over structure and reliability, not just text similarity.

### B. Context is assembled by graph traversal policies, not fixed chunks

The system generates a query-specific context program that decides:

- which atom types are relevant
- how far to expand in the graph
- whether to prioritize section context, table neighborhoods, definitions, citations, or adjacent layout zones
- which retrieval mode to apply first: landmark, graph, semantic, or parser-specific

### C. Uncertainty triggers adaptive re-extraction

If the highest-value evidence is low-confidence or contradictory across parsers, the system selectively reprocesses only those page regions using a different parser or higher-resolution model.

### D. Answer generation is paired with evidence verification

Before outputting structured data or an answer, the system checks whether the answer is supported by a connected evidence subgraph satisfying thresholds for:

- provenance diversity
- structural consistency
- spatial consistency
- extraction confidence
- contradiction absence

### E. The graph supports both retrieval and downstream extraction workflows

The same representation powers:

- question answering
- clause extraction
- contract comparison
- table-to-schema extraction
- compliance review
- patent prior-art mining
- regulatory evidence tracing

This helps position the invention as infrastructure, not a one-off application.

## Candidate system architecture

### Stage 1: Multi-parser ingestion

Input documents are processed by one or more engines:

- OCR engine
- layout detector
- VLM-based parser
- table structure parser
- formula parser
- chart parser
- metadata extractor

### Stage 2: Evidence atomization

The system converts outputs into normalized evidence atoms with:

- content
- type
- coordinates
- page number
- reading-order index
- parser identity
- confidence
- embeddings

### Stage 3: Evidence graph construction

Edges encode:

- adjacency in reading order
- section containment
- spatial overlap or proximity
- table row/column/cell relations
- caption-to-figure association
- citation-to-reference linkage
- defined-term linkage
- semantic similarity
- contradiction or inconsistency markers

### Stage 4: Multi-resolution indexing

The graph is indexed through:

- coarse landmarks or summaries
- medium-grain section representations
- fine-grain evidence atoms
- graph neighborhoods
- learned query-to-index routing

### Stage 5: Query-conditioned context assembly

A controller chooses the retrieval strategy based on the query class:

- factual lookup
- comparative lookup
- table aggregation
- definition seeking
- clause extraction
- cross-page reasoning
- cross-document evidence fusion

The controller creates a context program that may combine:

- landmark retrieval
- graph traversal
- semantic nearest neighbors
- layout-neighborhood expansion
- contradiction checks
- parser escalation

### Stage 6: Verified output generation

Outputs can be:

- extracted fields
- normalized JSON
- cited answers
- audit trails
- evidence-linked summaries

Each output is linked to a minimal supporting evidence subgraph.

## Why this can be patentable

On a practical basis, this proposal has a better patent posture because it is:

- more specific than generic RAG
- more technical than "use AI to read documents"
- more system-oriented than a single model claim
- more defensible because it combines representation, indexing, routing, verification, and adaptive reprocessing

The likely novelty is in the **combination and control logic**, especially if the claims emphasize:

- evidence-atom normalization from multiple parsers
- graph-based context assembly tied to query intent
- confidence-triggered selective re-extraction
- output verification against a connected evidence subgraph

## Draft claim strategy

These are product-strategy claim ideas, not legal claims.

### Independent claim concept 1: method claim

A computer-implemented method comprising:

- receiving a document
- generating multimodal evidence atoms from at least two document-analysis processes
- constructing an evidence graph linking atoms by structural and semantic relationships
- selecting, based on a query, a context assembly program
- traversing the evidence graph according to the context assembly program to create a query-specific context set
- generating an output based on the query-specific context set
- verifying the output against provenance and confidence constraints associated with the evidence graph

### Independent claim concept 2: adaptive reprocessing

A method wherein low-confidence or conflicting evidence atoms trigger selective re-analysis of only corresponding document regions using a second parser configuration, after which the evidence graph and context set are updated.

### Independent claim concept 3: system claim

A document-intelligence system comprising:

- parser interfaces
- an evidence atom normalizer
- an evidence graph builder
- a multi-resolution index manager
- a query router configured to generate context assembly programs
- a verification engine configured to validate outputs using supporting evidence subgraphs

### Dependent claim themes

- table-aware graph edges
- layout-aware expansion thresholds
- citation-linked evidence validation
- cross-document graph merge
- human feedback modifying traversal policies
- policy-specific handling for legal, financial, scientific, or patent documents
- evidence compression into verifiable summaries

## What to avoid because prior art risk is high

- pure semantic chunking
- static hierarchical chunking by headings
- vector embeddings over document sections
- OCR plus table extraction as the main invention
- "RAG with metadata filters"
- simple GraphRAG without adaptive re-extraction or provenance verification

## Strong commercialization wedges

The best verticals for this patent family are:

- contracts and legal review
- patent and prior-art analysis
- financial filings and due diligence
- regulatory compliance
- medical and scientific literature mining
- enterprise knowledge extraction from PDFs and scanned archives

Why these matter:

- They need exact evidence, not approximate answers.
- They contain tables, footnotes, formulas, appendices, and cross-references.
- They reward provenance and auditability.

## Recommended patent filing path

### Phase 1: invention disclosure now

Prepare a disclosure with:

- problem statement
- technical background
- concrete architecture
- retrieval and verification flow
- 3 to 5 embodiments
- example use cases
- 10 to 20 draft claim concepts
- diagrams

### Phase 2: prototype evidence

Build a prototype showing that the system beats a fixed-chunk baseline on:

- field extraction accuracy
- evidence fidelity
- table/question answering
- cross-page answer grounding
- hallucination or unsupported-answer rate

### Phase 3: provisional filing

File a provisional around the full architecture, then branch continuations later into:

- adaptive region reprocessing
- graph-based context assembly
- evidence-subgraph verification
- domain-specialized extraction policies

## Suggested experiments before filing

Run comparisons against:

- fixed window chunking
- semantic chunking
- late chunking
- hierarchical section retrieval
- chunk-free retrieval baseline if feasible

Measure:

- exact field extraction F1
- support coverage
- unsupported answer rate
- page/region reprocessing cost
- latency versus fidelity tradeoff

## Recommended patent package from this work

You should likely build one core family and reserve two follow-ons:

1. **Core family**
   Adaptive evidence graph construction and query-conditioned context assembly.
2. **Follow-on family**
   Confidence-triggered selective reprocessing of document regions.
3. **Follow-on family**
   Verified output generation using minimal supporting evidence subgraphs.

## Final recommendation

If the goal is a meaningful patent in document intelligence, the best move is not to patent "RAG for documents" or "contextual chunking." The stronger move is to patent a **multimodal, provenance-aware, graph-based document intelligence architecture that dynamically assembles and verifies evidence for each task**.

That is closer to where the research frontier is moving, and it gives you a more defensible story for novelty, technical effect, and business value.

## References

- Docling Technical Report (IBM Research, Aug 19, 2024): https://research.ibm.com/publications/docling-technical-report
- Docling: An Efficient Open-Source Toolkit for AI-driven Document Conversion (IBM Research, AAAI 2025): https://research.ibm.com/publications/docling-an-efficient-open-source-toolkit-for-ai-driven-document-conversion
- olmOCR: Unlocking Trillions of Tokens in PDFs with Vision Language Models (Feb 2025): https://spacefrontiers.org/r/10.48550/arxiv.2502.18443
- PaddleOCR-VL: Boosting Multilingual Document Parsing via a 0.9B Ultra-Compact Vision-Language Model (Oct 16, 2025): https://www.catalyzex.com/author/Cheng%20Cui
- RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval (Jan 31, 2024): https://arxiv.gg/abs/2401.18059
- Late Chunking: Contextual Chunk Embeddings Using Long-Context Embedding Models (Sep 7, 2024): https://axi.lims.ac.uk/paper/2409.04701
- Grounding Language Model with Chunking-Free In-Context Retrieval (ACL 2024): https://aclanthology.org/2024.acl-long.71/
- Landmark Embedding: A Chunking-Free Embedding Method For Retrieval Augmented Long-Context Large Language Models (ACL 2024): https://aclanthology.org/2024.acl-long.180/
- ChunkRAG: Novel LLM-Chunk Filtering Method for RAG Systems (Oct 25, 2024): https://spacefrontiers.org/r/10.48550/arxiv.2410.19572
- MoC: Mixtures of Text Chunking Learners for Retrieval-Augmented Generation System (Mar 2025): https://scixplorer.org/abs/2025arXiv250309600Z/abstract
- OCRBench dataset page: https://paperswithcode.com/dataset/ocrbench
- olmOCR-Bench benchmark page (Feb 25, 2025): https://www.alphaxiv.org/benchmarks/allen-institute-for-ai/olmocr-bench
