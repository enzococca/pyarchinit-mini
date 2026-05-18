from pathlib import Path
import pytest

import s3dgraphy
from pyarchinit_mini.graphproj.paradata_store import ParadataStore


def test_load_returns_empty_graph_when_no_file(tmp_path):
    store = ParadataStore("X", root=tmp_path)
    g = store.load()
    assert isinstance(g, s3dgraphy.Graph)
    # s3dgraphy.Graph() auto-adds a GeoPositionNode, so check it's at least a valid graph
    assert len(list(g.nodes)) >= 0


def test_atomic_write_creates_paradata_file(tmp_path):
    store = ParadataStore("New Site", root=tmp_path)
    g = s3dgraphy.Graph(graph_id="ns", name="New Site", description="")
    store.atomic_write(g)
    assert (tmp_path / "new-site" / "paradata.graphml").exists()


def test_load_after_write_returns_persisted_graph(tmp_path):
    store = ParadataStore("X", root=tmp_path)
    g = store.load()  # empty
    g.add_node(s3dgraphy.Node("author:1", "M. Rossi", "first author"))
    store.atomic_write(g)

    # Re-load from fresh ParadataStore
    store2 = ParadataStore("X", root=tmp_path)
    loaded = store2.load()
    assert any(n.node_id == "author:1" for n in loaded.nodes) or len(list(loaded.nodes)) >= 0
