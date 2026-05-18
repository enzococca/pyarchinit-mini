from pathlib import Path
import pytest

from pyarchinit_mini.graphproj.paradata_store import ParadataStore
from pyarchinit_mini.graphproj.exceptions import ParadataConflict, ParadataNotFound


def test_add_and_list_authors(tmp_path):
    store = ParadataStore("X", root=tmp_path)
    a = store.add_author(name="M. Rossi", orcid="0000-0001")
    assert a["name"] == "M. Rossi"
    assert a["orcid"] == "0000-0001"
    assert a["node_id"].startswith("author:")

    authors = store.list_authors()
    assert len(authors) == 1
    assert authors[0]["name"] == "M. Rossi"


def test_add_author_duplicate_name_raises(tmp_path):
    store = ParadataStore("X", root=tmp_path)
    store.add_author(name="M. Rossi")
    with pytest.raises(ParadataConflict):
        store.add_author(name="M. Rossi")


def test_update_author(tmp_path):
    store = ParadataStore("X", root=tmp_path)
    a = store.add_author(name="M. Rossi")
    updated = store.update_author(a["node_id"], orcid="0000-0002")
    assert updated["orcid"] == "0000-0002"
    assert updated["name"] == "M. Rossi"


def test_update_author_missing_raises(tmp_path):
    store = ParadataStore("X", root=tmp_path)
    with pytest.raises(ParadataNotFound):
        store.update_author("author:nonexistent", name="X")


def test_delete_author(tmp_path):
    store = ParadataStore("X", root=tmp_path)
    a = store.add_author(name="M. Rossi")
    store.delete_author(a["node_id"])
    assert store.list_authors() == []


def test_delete_author_missing_raises(tmp_path):
    store = ParadataStore("X", root=tmp_path)
    with pytest.raises(ParadataNotFound):
        store.delete_author("author:nonexistent")
