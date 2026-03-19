from fastapi.testclient import TestClient

from docintelligence.api.main import app


def test_corpus_endpoints() -> None:
    client = TestClient(app)

    stats_response = client.get("/corpus/stats")
    assert stats_response.status_code == 200
    stats = stats_response.json()
    assert stats["document_count"] >= 1000

    query_response = client.post("/query-corpus", json={"query": "humanitarian data", "top_k": 1})
    assert query_response.status_code == 200
    payload = query_response.json()
    assert payload["returned_hits"] == 1

    doc_id = payload["hits"][0]["doc_id"]
    detail_response = client.get(f"/corpus/document/{doc_id}")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["doc_id"] == doc_id
    assert detail["sample_atoms"]
