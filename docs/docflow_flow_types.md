# DocFlow Flow Types

This note maps PromptFlow's flow ideas to a document-native DocFlow model.

Reference inspiration:

- PromptFlow concepts page: `Flex flow`, `DAG flow`, and the higher-level categories `standard/chat/evaluation`.

## 1. Orchestration Styles

DocFlow should support two orchestration styles:

### A. DAG Flow

File: `flow.dag.yaml`

Use when the document pipeline is visually structured and node-based.

Best for:

- ingestion pipelines
- extraction pipelines
- indexing pipelines
- export pipelines
- UI-first authoring in the VS Code extension

### B. Flex Flow

File: `flow.flex.yaml`

Use when the document workflow needs Python-first orchestration instead of purely declarative DAG nodes.

Best for:

- conditional routing by file type
- fallback parser logic
- loops over pages or attachments
- advanced branching
- mixed orchestration with custom Python code

This is the closest DocFlow analogue to PromptFlow's `flex flow`.

## 2. Product-Level Flow Types

Beyond orchestration style, DocFlow should classify flows by purpose.

### A. Standard Flow

Purpose:
General document processing.

Typical steps:

- scan documents
- parse documents
- normalize atoms
- enrich metadata
- build graph
- build indexes
- write outputs

This is the default DocFlow type.

### B. Extraction Flow

Purpose:
Extract structured outputs from documents.

Typical outputs:

- clauses
- sections
- tables
- entities
- invoice fields
- policy terms
- citations

Best for:

- document IE
- compliance extraction
- finance/legal workflows

### C. Indexing Flow

Purpose:
Prepare documents for search and retrieval.

Typical outputs:

- text exports
- atom stores
- vector indexes
- structural indexes
- spatial indexes
- SDF files

Best for:

- RAG pipelines
- enterprise search
- semantic retrieval

### D. Retrieval Flow

Purpose:
Run query-time document retrieval over prepared artifacts.

Typical steps:

- load indexes
- route query
- retrieve atoms
- expand graph context
- verify support
- return grounded results

Best for:

- search applications
- grounded Q&A
- evidence-based retrieval

### E. Conversion Flow

Purpose:
Convert source documents into target artifacts.

Typical conversions:

- PDF -> TXT
- PDF -> JSON
- PDF -> SDF
- DOCX -> SDF
- MSG -> JSON

Best for:

- data pipeline handoff
- interoperability
- batch conversions

### F. Evaluation Flow

Purpose:
Evaluate document-processing quality.

Typical checks:

- parse success rate
- extraction accuracy
- retrieval precision/recall
- citation grounding
- structural classification quality

This is the closest DocFlow analogue to PromptFlow's `evaluation flow`.

### G. Review Flow

Purpose:
Human-in-the-loop validation and correction.

Typical steps:

- load extracted results
- surface low-confidence atoms
- request review
- capture fixes
- regenerate final artifacts

Best for:

- legal review
- finance review
- annotation workflows

### H. Monitoring Flow

Purpose:
Observe production document pipelines over time.

Typical outputs:

- failure reports
- parser drift detection
- quality alerts
- format coverage reports
- malformed file logs

Best for:

- operations
- reliability
- regression detection

## 3. Recommended First-Class DocFlow Types

If we want a clean first version, the best set is:

1. `standard`
2. `extraction`
3. `indexing`
4. `conversion`
5. `evaluation`

Then in a second phase:

6. `retrieval`
7. `review`
8. `monitoring`

## 4. Best Mapping to PromptFlow

PromptFlow:

- `DAG flow`
- `Flex flow`
- `standard`
- `chat`
- `evaluation`

DocFlow:

- `DAG flow`
- `Flex flow`
- `standard`
- `extraction`
- `indexing`
- `conversion`
- `evaluation`
- `retrieval`

Why there is no direct `chat flow` equivalent:

PromptFlow is conversation-native.
DocFlow is document-native.

So the closest equivalent to `chat flow` in DocFlow is not chat, but:

- `retrieval flow`
- or `review flow`

depending on whether the main interaction is machine query or human validation.

## 5. Recommendation

The strongest DocFlow direction is:

- Keep `DAG` and `Flex` as orchestration styles
- Add `standard`, `extraction`, `indexing`, `conversion`, and `evaluation` as explicit flow types

That gives us a clean, scalable taxonomy without overcomplicating the first release.
