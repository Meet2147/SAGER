from fastapi.testclient import TestClient

from docintelligence.api.main import app


def test_end_to_end_pipeline() -> None:
    client = TestClient(app)

    ingest_response = client.post(
        "/ingest",
        json={
            "doc_id": "contract-1",
            "parser_name": "demo-parser",
            "text": "Termination:\nThe agreement may terminate with 30 days notice.\nLiability is capped at fees paid.",
        },
    )
    assert ingest_response.status_code == 200
    assert ingest_response.json()["atom_count"] == 3

    query_response = client.post("/query", json={"query": "termination notice clause"})
    assert query_response.status_code == 200
    payload = query_response.json()
    assert payload["verification_status"] == "supported"
    assert payload["support_atom_ids"]
