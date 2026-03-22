# DocFlow

DocFlow is a small DAG runner for document-processing pipelines. It is designed to feel similar to prompt-flow orchestration, but for file-based document preprocessing.

The current prototype supports:

- `pdf` via `pypdf`
- `docx` via zipped XML parsing
- `doc` via OLE stream text extraction
- `xlsx` and `xlsm` via zipped XML parsing
- `xls` via `xlrd`
- `msg` via `extract-msg`

The output is a consistent evidence-atom and evidence-graph artifact set.

## Flow Types

DocFlow now supports explicit `flow_type` classification in YAML.

Recommended types:

- `standard`
- `extraction`
- `indexing`
- `conversion`
- `evaluation`

DocFlow also recognizes orchestration style as:

- `dag`
- `flex`

If not explicitly set, orchestration is inferred from the filename:

- `*.flow.dag.yaml` -> `dag`
- `*.flow.flex.yaml` -> `flex`

Starter templates are available in:

[`docflow/templates`](/Users/meetjethwa/Development/PatentIdeas/DocIntelligence/docflow/templates)

## Standalone package

A publishable standalone Python package skeleton also lives here:

[`packages/docflow`](/Users/meetjethwa/Development/PatentIdeas/DocIntelligence/packages/docflow)

## Visualize a flow

Render the DAG into an interactive HTML view:

```bash
python3 scripts/visualize_docflow.py docflow/examples/document_preprocess.flow.dag.yaml
```

Optional output path:

```bash
python3 scripts/visualize_docflow.py docflow/examples/document_preprocess.flow.dag.yaml --output docflow/examples/document_preprocess.visual.html
```

## Run the example flow

```bash
python3 scripts/run_docflow.py docflow/examples/document_preprocess.flow.dag.yaml --source-dir "/path/to/documents"
```

Optional override:

```bash
python3 scripts/run_docflow.py docflow/examples/document_preprocess.flow.dag.yaml --source-dir "/path/to/documents" --output-dir "/tmp/docflow_run"
```
