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
    from pyarchinit_mini.web_interface.paradata_ui_routes import paradata_ui_bp
    template_folder = (
        Path(__file__).parent.parent.parent
        / "pyarchinit_mini" / "web_interface" / "templates"
    )
    app = Flask(__name__, template_folder=str(template_folder))
    app.config["TESTING"] = True
    app.secret_key = "test"
    app.register_blueprint(paradata_bp)
    app.register_blueprint(paradata_ui_bp)
    yield app.test_client()
    VocabProvider.reset()


def test_list_authors_page_renders(client):
    r = client.get("/paradata/Volterra/authors")
    assert r.status_code == 200
    # Page mentions the kind (lowercase or uppercase)
    body = r.data.decode("utf-8", errors="ignore").lower()
    assert "author" in body


def test_create_author_via_form_redirects_to_list(client):
    r = client.post(
        "/paradata/Volterra/authors/new",
        data={"name": "M. Rossi", "orcid": "0000-0001"},
        follow_redirects=False,
    )
    assert r.status_code in (302, 303)
    r2 = client.get("/paradata/Volterra/authors")
    assert b"M. Rossi" in r2.data


def test_delete_author_via_post(client):
    client.post("/paradata/Volterra/authors/new", data={"name": "X"})
    r_json = client.get("/api/v1/paradata/Volterra/authors")
    authors = r_json.get_json()
    nid = authors[0]["node_id"]
    r = client.post(
        f"/paradata/Volterra/authors/{nid}/delete",
        follow_redirects=False,
    )
    assert r.status_code in (302, 303)
    r_after = client.get("/api/v1/paradata/Volterra/authors")
    assert r_after.get_json() == []


@pytest.mark.parametrize("kind,field,value", [
    ("licenses", "name", "CC-BY"),
    ("embargoes", "label", "Until 2030"),
    ("documents", "title", "Excavation Report"),
    ("epochs", "name", "Roman"),
])
def test_list_page_renders_for_each_kind(client, kind, field, value):
    # Seed via REST API
    client.post(f"/api/v1/paradata/Volterra/{kind}", json={field: value})
    r = client.get(f"/paradata/Volterra/{kind}")
    assert r.status_code == 200
    assert value.encode() in r.data
