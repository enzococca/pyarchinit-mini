from pathlib import Path
import pytest

from pyarchinit_mini.vocab.provider import VocabProvider
from pyarchinit_mini.s3d_integration.s3d_converter import S3DConverter

FIX = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture(autouse=True)
def reset_provider():
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX)
    yield
    VocabProvider.reset()


def test_italian_rapporti_parsed_via_vocab():
    """Smoke: rapporti string ('copre 2, taglia 3') produces edges in the graph."""
    conv = S3DConverter()
    us_list = [
        {"sito": "S", "us": 1, "rapporti": "copre 2, taglia 3"},
        {"sito": "S", "us": 2, "rapporti": ""},
        {"sito": "S", "us": 3, "rapporti": ""},
    ]
    g = conv.create_graph_from_us(us_list, site_name="S")
    nodes = list(g.nodes)
    edges = list(g.edges)
    assert len(nodes) >= 3  # s3dgraphy may add extra system nodes (e.g. GeoPositionNode)
    assert len(edges) >= 1


def test_coperto_da_parsed_as_is_after():
    """Compound alias 'coperto da' must map to is_after (and not to 'covers')."""
    conv = S3DConverter()
    us_list = [
        {"sito": "S", "us": 10, "rapporti": "coperto da 20"},
        {"sito": "S", "us": 20, "rapporti": ""},
    ]
    g = conv.create_graph_from_us(us_list, site_name="S")
    edges = list(g.edges)
    assert len(edges) == 1
    e = edges[0]
    # The legacy code used uppercase 'COVERED_BY' attribute; new code maps via vocab.
    # Either UPPERCASE legacy code OR s3dgraphy canonical name is acceptable;
    # what MUST hold: the edge attribute reflects "is_after" semantics, not "covers".
    rel = (e.attributes.get("stratigraphic_relation") or "").lower()
    assert "is_after" in rel or "covered" in rel
    assert "covers" != rel  # NOT the inverse


def test_usvs_node_categorized_via_vocab_family():
    """USVs should get family='virtual' attribute via VocabProvider lookup."""
    conv = S3DConverter()
    us_list = [
        {"sito": "S", "us": 10, "unita_tipo": "USVs", "rapporti": ""},
        {"sito": "S", "us": 11, "unita_tipo": "US", "rapporti": ""},
    ]
    g = conv.create_graph_from_us(us_list, site_name="S")
    # Find the USVs node by its semantic id suffix
    usvs_node = next((n for n in g.nodes if "10" in n.node_id), None)
    assert usvs_node is not None
    assert getattr(usvs_node, "attributes", {}).get("family") == "virtual"


def test_us_node_categorized_as_real():
    conv = S3DConverter()
    us_list = [
        {"sito": "S", "us": 5, "unita_tipo": "US", "rapporti": ""},
    ]
    g = conv.create_graph_from_us(us_list, site_name="S")
    us_node = next((n for n in g.nodes if "5" in n.node_id), None)
    assert us_node is not None
    assert getattr(us_node, "attributes", {}).get("family") == "real"
