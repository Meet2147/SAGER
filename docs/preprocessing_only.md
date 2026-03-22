# SAGER Preprocessing-Only Pipeline

This runner executes only these stages:

1. Receive document
2. Run OCR, layout, VLM, and table parsers
3. Normalize parser outputs into evidence atoms
4. Add metadata: coordinates, role, confidence, provenance
5. Construct evidence graph
6. Build semantic, structural, and spatial indexes

In the current prototype, the parser stage is implemented with `pypdf` text extraction plus placeholder parser provenance so the pipeline stays runnable on a directory of PDFs.

## Run

```bash
python3 scripts/run_sager_preprocessing.py "/path/to/pdf-directory" --dataset-name office_batch
```

Optional output directory:

```bash
python3 scripts/run_sager_preprocessing.py "/path/to/pdf-directory" --dataset-name office_batch --output-dir data/preprocessed
```

## Outputs

For a dataset named `office_batch`, the script writes:

- `data/preprocessed/office_batch/manifest.json`
- `data/preprocessed/office_batch/documents/*.json`
- `data/preprocessed/office_batch/indexes/semantic_index.json`
- `data/preprocessed/office_batch/indexes/structural_index.json`
- `data/preprocessed/office_batch/indexes/spatial_index.json`

## Artifact structure

Each document artifact contains:

- `doc_id`
- `source_path`
- `pipeline_stages`
- `page_count`
- `atom_count`
- `edge_count`
- `atoms`
- `edges`

## Notes

- This runner intentionally stops before query-time retrieval and answer generation.
- The semantic index stores top TF-IDF terms per document.
- The structural index groups atoms by role, type, and page.
- The spatial index groups atoms by page region using their bounding boxes.
