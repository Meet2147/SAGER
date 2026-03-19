from pathlib import Path

from docintelligence.sdf.service import convert_processed_json_to_sdf, load_sdf


def test_sdf_roundtrip_from_processed_json(tmp_path: Path) -> None:
    processed = Path("data/processed/archive19_unique/archive19_unique_2017_de_public_transport_118NP8.json")
    target = tmp_path / "sample.sdf"

    sdf_path = convert_processed_json_to_sdf(str(processed), str(target))
    payload = load_sdf(str(sdf_path))

    assert payload["format"] == "SDF"
    assert payload["method"]["name"] == "SAGER"
    assert payload["atoms"]
