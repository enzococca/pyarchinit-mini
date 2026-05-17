import json
import textwrap
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


# ---------------------------------------------------------------------------
# Fix 1: import_graphml_to_json categorises via VocabProvider
# ---------------------------------------------------------------------------

_GRAPHML_TEMPLATE = textwrap.dedent("""\
    <?xml version="1.0" encoding="UTF-8"?>
    <graphml xmlns="http://graphml.graphdrawing.org/xmlns">
      <key id="d0" for="node" attr.name="label" attr.type="string"/>
      <graph id="G" edgedefault="directed">
        <node id="n1">
          <data key="d0">US1</data>
        </node>
        <node id="n2">
          <data key="d0">USVs2</data>
        </node>
        <node id="n3">
          <data key="d0">USVn3</data>
        </node>
      </graph>
    </graphml>
""")


def test_import_graphml_to_json_categorizes_via_vocab(tmp_path):
    """import_graphml_to_json must place USVs/USVn in the USVs bucket
    (family='virtual') and plain US in the US bucket via VocabProvider."""
    graphml_path = tmp_path / "test.graphml"
    graphml_path.write_text(_GRAPHML_TEMPLATE, encoding="utf-8")
    output_path = tmp_path / "out.json"

    conv = S3DConverter()
    conv.import_graphml_to_json(str(graphml_path), str(output_path), site_name="Test")

    result = json.loads(output_path.read_text(encoding="utf-8"))
    graphs = result["graphs"]
    graph_id = list(graphs.keys())[0]
    strat = graphs[graph_id]["nodes"]["stratigraphic"]

    # n1 (US1) → US bucket
    assert "n1" in strat["US"], f"US node not in US bucket; strat={strat}"
    # n2 (USVs2) → USVs bucket (family=virtual via VocabProvider)
    assert "n2" in strat["USVs"], f"USVs node not in USVs bucket; strat={strat}"
    # n3 (USVn3) → USVs bucket (also family=virtual)
    assert "n3" in strat["USVs"], f"USVn node not in USVs bucket; strat={strat}"
