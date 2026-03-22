# Publishing `docflow`

From the repository root:

```bash
cd /Users/meetjethwa/Development/PatentIdeas/DocIntelligence/packages/docflow
python3 -m pip install -e '.[dev]'
python3 -m build
python3 -m twine check dist/*
```

This package exposes:

- the `docflow` Python package
- the `docflow` CLI entrypoint

Example local usage:

```bash
docflow run ../../docflow/examples/document_preprocess.flow.dag.yaml --source-dir /path/to/documents --output-dir /tmp/docflow_run --trace
```

Supported input file types:

- `pdf`
- `docx`
- `doc`
- `xlsx`
- `xls`
- `msg`

Notes:

- `.doc` support uses OLE text extraction as a pragmatic fallback, not a full fidelity Word layout parser.
- `.msg` support depends on `extract-msg`.
- `.xls` support depends on `xlrd`.
