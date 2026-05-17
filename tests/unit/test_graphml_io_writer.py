from pathlib import Path
import pytest

import s3dgraphy
from pyarchinit_mini.graphml_io.writer import write_graphml


def test_write_graphml_produces_file(tmp_path):
    g = s3dgraphy.Graph(graph_id="test", name="Test", description="d")
    g.add_node(s3dgraphy.Node("n1", "Node 1", "first"))
    g.add_node(s3dgraphy.Node("n2", "Node 2", "second"))
    g.add_edge("e1", "n1", "n2", "is_after")

    out = tmp_path / "out.graphml"
    write_graphml(g, out)

    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "<graphml" in content or "<?xml" in content


def test_write_graphml_creates_parent_dir(tmp_path):
    g = s3dgraphy.Graph(graph_id="test", name="Test", description="d")
    out = tmp_path / "nested" / "dir" / "out.graphml"
    write_graphml(g, out)
    assert out.exists()


def test_write_graphml_raises_graphml_write_error_on_bad_graph(tmp_path):
    """If the underlying exporter raises, we wrap it in GraphMLWriteError."""
    from pyarchinit_mini.graphproj.exceptions import GraphMLWriteError
    # Pass something that's not a graph — should trip the exporter
    with pytest.raises(GraphMLWriteError):
        write_graphml("not a graph", tmp_path / "bad.graphml")
