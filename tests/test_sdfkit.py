from sdfkit import open_sdf


def test_sdfkit_load_and_query() -> None:
    doc = open_sdf("data/processed/archive19_unique/archive19_unique_2017_de_public_transport_118NP8.sdf")

    assert doc.format == "SDF"
    assert doc.doc_id.startswith("archive19_unique_")
    assert doc.atoms
    assert doc.role_distribution()

    results = doc.query("public transport ticket", top_k=3)
    assert results
