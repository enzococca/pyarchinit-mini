from pathlib import Path
import pytest

from pyarchinit_mini.vocab.provider import VocabProvider

FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture
def client():
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX)
    from flask import Flask
    from pyarchinit_mini.web_interface.vocab_routes import vocab_bp
    app = Flask(__name__)
    app.register_blueprint(vocab_bp)
    yield app.test_client()
    VocabProvider.reset()


def test_get_unit_types_returns_json_array(client):
    r = client.get("/api/v1/vocab/unit-types?lang=it")
    assert r.status_code == 200
    data = r.get_json()
    assert isinstance(data, list)
    assert any(t["abbreviation"] == "US" for t in data)


def test_get_unit_types_filter_by_family(client):
    r = client.get("/api/v1/vocab/unit-types?family=real")
    assert r.status_code == 200
    data = r.get_json()
    for t in data:
        assert t["family"] == "real" or t["family"] is None


def test_get_unit_type_single(client):
    r = client.get("/api/v1/vocab/unit-types/US?lang=en")
    assert r.status_code == 200
    data = r.get_json()
    assert data["abbreviation"] == "US"


def test_get_unit_type_not_found_returns_404_with_suggestions(client):
    r = client.get("/api/v1/vocab/unit-types/ZZZ_UNKNOWN")
    assert r.status_code == 404
    data = r.get_json()
    assert "suggestions" in data


def test_get_visual_style_returns_style_dict(client):
    r = client.get("/api/v1/vocab/visual-style/US")
    assert r.status_code == 200
    data = r.get_json()
    assert data["shape"] == "rectangle"


def test_get_edge_types(client):
    r = client.get("/api/v1/vocab/edge-types")
    assert r.status_code == 200
    assert isinstance(r.get_json(), list)


def test_etag_present_on_unit_types(client):
    r = client.get("/api/v1/vocab/unit-types")
    assert r.headers.get("ETag") is not None
