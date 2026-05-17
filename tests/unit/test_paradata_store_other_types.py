import pytest
from pyarchinit_mini.graphproj.paradata_store import ParadataStore
from pyarchinit_mini.graphproj.exceptions import ParadataNotFound


def test_license_crud(tmp_path):
    store = ParadataStore("X", root=tmp_path)
    l = store.add_license(name="CC-BY-NC-ND", url="https://creativecommons.org/...")
    assert l["name"] == "CC-BY-NC-ND"
    assert l["url"] == "https://creativecommons.org/..."
    assert l["node_id"].startswith("license:")

    listed = store.list_licenses()
    assert len(listed) == 1
    assert listed[0]["name"] == "CC-BY-NC-ND"

    upd = store.update_license(l["node_id"], url="https://newurl")
    assert upd["url"] == "https://newurl"

    store.delete_license(l["node_id"])
    assert store.list_licenses() == []


def test_embargo_crud(tmp_path):
    store = ParadataStore("X", root=tmp_path)
    e = store.add_embargo(label="Until 2030", until="2030-01-01")
    assert e["label"] == "Until 2030"
    assert e["until"] == "2030-01-01"
    assert e["node_id"].startswith("embargo:")
    assert len(store.list_embargoes()) == 1

    upd = store.update_embargo(e["node_id"], until="2031-01-01")
    assert upd["until"] == "2031-01-01"

    store.delete_embargo(e["node_id"])
    assert store.list_embargoes() == []


def test_document_crud(tmp_path):
    store = ParadataStore("X", root=tmp_path)
    d = store.add_document(title="Excavation Report 2024", uri="https://example.org/report")
    assert d["title"] == "Excavation Report 2024"
    assert d["uri"] == "https://example.org/report"
    assert d["node_id"].startswith("document:")

    upd = store.update_document(d["node_id"], uri="https://example.org/new")
    assert upd["uri"] == "https://example.org/new"

    store.delete_document(d["node_id"])
    assert store.list_documents() == []


def test_epoch_crud(tmp_path):
    store = ParadataStore("X", root=tmp_path)
    e = store.add_epoch(name="Roman Imperial", start=-27, end=476)
    assert e["name"] == "Roman Imperial"
    assert e["start"] == -27
    assert e["end"] == 476

    upd = store.update_epoch(e["node_id"], end=500)
    assert upd["end"] == 500

    store.delete_epoch(e["node_id"])
    assert store.list_epochs() == []


def test_update_unknown_raises_not_found(tmp_path):
    store = ParadataStore("X", root=tmp_path)
    with pytest.raises(ParadataNotFound):
        store.update_license("license:bogus", name="X")


def test_delete_unknown_raises_not_found(tmp_path):
    store = ParadataStore("X", root=tmp_path)
    with pytest.raises(ParadataNotFound):
        store.delete_document("document:bogus")
