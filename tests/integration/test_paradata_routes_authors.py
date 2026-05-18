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


def test_post_then_list_authors(client):
    r = client.post(
        "/api/v1/paradata/Volterra/authors",
        json={"name": "M. Rossi", "orcid": "0000-0001"},
    )
    assert r.status_code == 201
    body = r.get_json()
    assert body["name"] == "M. Rossi"
    assert body["orcid"] == "0000-0001"

    r2 = client.get("/api/v1/paradata/Volterra/authors")
    assert r2.status_code == 200
    authors = r2.get_json()
    assert len(authors) == 1
    assert authors[0]["name"] == "M. Rossi"


def test_put_author(client):
    r = client.post("/api/v1/paradata/Volterra/authors", json={"name": "M. Rossi"})
    node_id = r.get_json()["node_id"]
    r2 = client.put(
        f"/api/v1/paradata/Volterra/authors/{node_id}",
        json={"orcid": "0000-0002"},
    )
    assert r2.status_code == 200
    assert r2.get_json()["orcid"] == "0000-0002"


def test_delete_author(client):
    r = client.post("/api/v1/paradata/Volterra/authors", json={"name": "M. Rossi"})
    node_id = r.get_json()["node_id"]
    r2 = client.delete(f"/api/v1/paradata/Volterra/authors/{node_id}")
    assert r2.status_code == 204
    r3 = client.get("/api/v1/paradata/Volterra/authors")
    assert r3.get_json() == []


def test_post_duplicate_returns_409(client):
    client.post("/api/v1/paradata/Volterra/authors", json={"name": "M. Rossi"})
    r = client.post("/api/v1/paradata/Volterra/authors", json={"name": "M. Rossi"})
    assert r.status_code == 409
    body = r.get_json()
    assert body["error"] == "duplicate"


def test_put_unknown_returns_404(client):
    r = client.put(
        "/api/v1/paradata/Volterra/authors/author:bogus",
        json={"name": "X"},
    )
    assert r.status_code == 404


def test_post_missing_name_returns_400(client):
    r = client.post("/api/v1/paradata/Volterra/authors", json={})
    assert r.status_code == 400
    body = r.get_json()
    assert body["error"] == "validation"
