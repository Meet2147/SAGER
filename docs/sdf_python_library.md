# SDF Python Library

## Package

The workspace now includes a lightweight Python library:

`sdfkit`

## Import

```python
from sdfkit import open_sdf
```

## Example

```python
from sdfkit import open_sdf

doc = open_sdf("data/processed/books/books_work.sdf")

print(doc.doc_id)
print(doc.page_count)
print(doc.role_distribution())

results = doc.query("work and energy", top_k=5)
for atom in results:
    print(atom.page, atom.role_label, atom.text)
```

## What it gives you

- `open_sdf(path)` to load an SDF file
- `doc.atoms` to inspect atoms
- `doc.edges` to inspect graph edges
- `doc.atoms_on_page(page)` to browse a page
- `doc.role_distribution()` to inspect structure labels
- `doc.query(text, top_k=...)` to retrieve top evidence atoms
