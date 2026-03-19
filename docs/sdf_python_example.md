# Python Example: Retrieve from SDF

## 1. Create an SDF file from a processed SAGER artifact

```bash
python3 scripts/create_sdf.py data/processed/archive19_unique/archive19_unique_2017_de_public_transport_118NP8.json
```

This creates:

```text
data/processed/archive19_unique/archive19_unique_2017_de_public_transport_118NP8.sdf
```

## 2. Query the SDF file

```bash
python3 scripts/query_sdf.py data/processed/archive19_unique/archive19_unique_2017_de_public_transport_118NP8.sdf "public transport ticket"
```

## 3. Python code example

```python
from docintelligence.sdf.service import query_sdf

result = query_sdf(
    "data/processed/archive19_unique/archive19_unique_2017_de_public_transport_118NP8.sdf",
    "public transport ticket"
)

for item in result["results"]:
    print(item["page"], item["role_label"], item["text"])
```

## 4. What this demonstrates

This shows the intended workflow:

1. process a PDF with SAGER
2. create an `.sdf` derivative file
3. retrieve evidence directly from the `.sdf` file without reparsing the original PDF
