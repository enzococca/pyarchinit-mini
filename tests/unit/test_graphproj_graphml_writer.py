"""yEd TableNode writer reads the projected s3dgraphy.Graph contract."""
from pyarchinit_mini.graphproj.graphml_writer import write_graphml
from tests.unit.strat_graph_factory import make_graph

ROWS = [
    {"row_id": "r0", "label": "Periodo 1", "periodo": "Periodo 1", "fase": None,
     "datazione": None, "is_fallback": False},
    {"row_id": "r1", "label": "Periodo 2", "periodo": "Periodo 2", "fase": None,
     "datazione": None, "is_fallback": False},
]


def _graph(**node_extra):
    return make_graph(
        site="S", rows=ROWS,
        nodes=[
            {"id": "n1", "us": "1", "row_id": "r0", **node_extra},
            {"id": "n2", "us": "2", "row_id": "r1"},
        ],
        edges=[("n1", "n2", "overlies")],
    )


def test_yed_output_is_tablenode_graphml():
    data = write_graphml(_graph())
    assert data.startswith(b"<?xml")
    text = data.decode("utf-8")
    assert "<graphml" in text
    assert "YED_TABLE_NODE" in text
    assert text.count("<y:Row") >= 2


def test_yed_output_has_node_labels_and_italian_edge_label():
    text = write_graphml(_graph()).decode("utf-8")
    assert ">1<" in text and ">2<" in text
    assert "Copre" in text


def test_yed_output_carries_node_uuid():
    uid = "0192aaaa-1111-7222-8333-444455556666"
    text = write_graphml(_graph(node_uuid=uid)).decode("utf-8")
    assert uid in text
