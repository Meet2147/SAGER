# docflow-sager

![DocFlow Logo](https://raw.githubusercontent.com/Meet2147/SAGER/main/assets/docflow_logo.png)

`docflow-sager` is a document-native workflow engine for preprocessing files into structured evidence artifacts, plain-text exports, and downstream indexes.

The package name on PyPI is `docflow-sager`, while the Python import stays:

```python
import docflow
```

## What It Does

DocFlow is designed for document pipelines in the same way PromptFlow is designed for prompt pipelines.

Instead of chaining prompt nodes, DocFlow chains document-processing steps such as:

- scanning files
- parsing documents
- normalizing parser output into evidence atoms
- enriching metadata
- constructing an evidence graph
- building semantic, structural, and spatial indexes
- exporting structured outputs

It is a strong fit for:

- document intelligence
- preprocessing large file corpora
- evidence-aware retrieval pipelines
- text extraction and indexing workflows
- AI-ready document transformation

## Supported Input Types

DocFlow currently supports:

- `pdf`
- `docx`
- `doc`
- `xlsx`
- `xls`
- `msg`

Implementation notes:

- `pdf` uses `pypdf`
- `docx` uses Open XML parsing
- `doc` uses OLE-based text extraction as a pragmatic fallback
- `xlsx` uses Open XML parsing
- `xls` uses `xlrd`
- `msg` uses `extract-msg`

## Installation

```bash
pip install docflow-sager
```

## Quick Start

### Python API

```python
from docflow import run_flow

result = run_flow(
    "document_preprocess.flow.dag.yaml",
    inputs={
        "source_dir": "/path/to/documents",
        "output_dir": "/tmp/docflow_run",
    },
)

print(result["flow_name"])
print(result["final_output"])
```

### CLI

The package exposes a `docflow` command-line entrypoint.

Run a flow:

```bash
docflow run document_preprocess.flow.dag.yaml --source-dir /path/to/documents --output-dir /tmp/docflow_run --trace
```

Inspect the compiled graph:

```bash
docflow graph document_preprocess.flow.dag.yaml
```

## Example Flow

```yaml
name: document_preprocess
variables:
  dataset_name: docflow_demo
  output_dir: docflow_runs/demo

nodes:
  - name: scan
    step: scan_documents
    config:
      source_dir: ${inputs.source_dir}
      file_types: [pdf, docx, doc, xlsx, xls, msg]

  - name: parse
    step: parse_documents
    depends_on: [scan]
    config:
      dataset_name: ${dataset_name}

  - name: normalize
    step: normalize_atoms
    depends_on: [parse]

  - name: metadata
    step: enrich_metadata
    depends_on: [normalize]

  - name: graph
    step: build_evidence_graph
    depends_on: [metadata]

  - name: indexes
    step: build_indexes
    depends_on: [graph]

  - name: write
    step: write_outputs
    depends_on: [graph, indexes]
    config:
      output_dir: ${output_dir}

outputs:
  final_node: write
```

## Output Structure

A typical DocFlow run writes:

- `documents/*.json`
- `text/*.txt`
- `indexes/semantic_index.json`
- `indexes/structural_index.json`
- `indexes/spatial_index.json`
- `manifest.json`

The manifest records:

- processed document count
- parse error count
- per-document stats
- skipped-file error details

## Core Concepts

### Evidence Atoms

Each extracted line or structured unit becomes an evidence atom containing:

- document id
- page number
- text
- reading order
- parser provenance
- confidence
- role label

### Evidence Graph

DocFlow constructs lightweight graph edges between atoms, including:

- adjacency in reading order
- containment under headings

This makes the outputs better suited for downstream retrieval and reasoning than plain flattened text alone.

### Multi-Format Exports

DocFlow outputs can later be exported or indexed as:

- plain text
- JSON
- CSV
- XLSX
- SDF-compatible structured artifacts

## Notes and Limitations

- `.doc` support is text-oriented, not layout-faithful
- `.msg` support focuses on message metadata and body extraction
- malformed PDFs are skipped and logged in the manifest instead of aborting the full batch
- parser quality depends on the underlying format adapter

## Package Identity

- PyPI package: `docflow-sager`
- Python import: `docflow`
- CLI command: `docflow`

## Repository

Source repository:

[https://github.com/Meet2147/SAGER](https://github.com/Meet2147/SAGER)
