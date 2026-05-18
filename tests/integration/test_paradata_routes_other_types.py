from pathlib import Path
import pytest

from pyarchinit_mini.vocab.provider import VocabProvider

FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX)
    from flask import Flask
    from pyarchinit_mini.web_interface.paradata_routes import paradata_bp
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(paradata_bp)
    yield app.test_client()
    VocabProvider.reset()


@pytest.mark.parametrize("kind,body", [
    ("licenses", {"name": "CC-BY", "url": "https://creativecommons.org/..."}),
    ("embargoes", {"label": "Until 2030", "until": "2030-01-01"}),
    ("documents", {"title": "Report 2024", "uri": "https://example.org/report"}),
    ("epochs", {"name": "Roman", "start": -27, "end": 476}),
])
def test_crud_round_trip(client, kind, body):
    r = client.post(f"/api/v1/paradata/Volterra/{kind}", json=body)
    assert r.status_code == 201, f"{kind} POST failed: {r.data}"
    created = r.get_json()
    node_id = created["node_id"]

    r2 = client.get(f"/api/v1/paradata/Volterra/{kind}")
    assert any(item["node_id"] == node_id for item in r2.get_json())

    r3 = client.delete(f"/api/v1/paradata/Volterra/{kind}/{node_id}")
    assert r3.status_code == 204

    r4 = client.get(f"/api/v1/paradata/Volterra/{kind}")
    assert r4.get_json() == []


def test_unknown_kind_returns_404(client):
    r = client.get("/api/v1/paradata/Volterra/widgets")
    assert r.status_code == 404


def test_missing_required_field_returns_400(client):
    r = client.post("/api/v1/paradata/Volterra/licenses", json={})  # missing 'name'
    assert r.status_code == 400


def test_put_updates_existing(client):
    r = client.post("/api/v1/paradata/Volterra/licenses", json={"name": "CC-BY"})
    node_id = r.get_json()["node_id"]
    r2 = client.put(
        f"/api/v1/paradata/Volterra/licenses/{node_id}",
        json={"url": "https://new"},
    )
    assert r2.status_code == 200
    assert r2.get_json()["url"] == "https://new"
