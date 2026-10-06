"""yEd TableNode writer reads the projected s3dgraphy.Graph contract."""
from pyarchinit_mini.graphproj.graphml_writer import write_graphml
from pyarchinit_mini.graphproj.strat_graph import FALLBACK_ROW, new_graph, new_strat_node, set_swimlane
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
    assert text.count("<y:Row ") == len(ROWS)


def test_yed_output_has_node_labels_and_italian_edge_label():
    text = write_graphml(_graph()).decode("utf-8")
    assert ">1<" in text and ">2<" in text
    assert "Copre" in text


def test_yed_output_carries_node_uuid():
    uid = "0192aaaa-1111-7222-8333-444455556666"
    text = write_graphml(_graph(node_uuid=uid)).decode("utf-8")
    assert uid in text


def test_empty_graph_writes_single_fallback_row():
    text = write_graphml(new_graph("S")).decode("utf-8")
    # yed_writer does not serialise row labels, so assert the single row id instead
    assert '<y:Row id="row_0"' in text
    assert text.count("<y:Row ") == 1


def test_row_with_datazione_emits_epochs_payload():
    rows = [{"row_id": "r0", "label": "P", "periodo": "P", "fase": None,
             "datazione": "sec. I a.C.", "is_fallback": False}]
    g = make_graph(site="S", rows=rows, nodes=[{"id": "n1", "us": "1", "row_id": "r0"}])
    assert "sec. I a.C." in write_graphml(g).decode("utf-8")


def test_node_with_unknown_row_id_is_still_written():
    rows = [{"row_id": "row_0", "label": "P", "periodo": "P", "fase": None,
             "datazione": None, "is_fallback": False}]
    g = make_graph(site="S", rows=rows, nodes=[{"id": "n1", "us": "77", "row_id": "row_99"}])
    text = write_graphml(g).decode("utf-8")
    assert ">77<" in text
    assert text.count("<y:Row ") == 1


def test_node_without_contract_and_none_description():
    g = new_graph("S")
    g.add_node(new_strat_node(node_id="x", name="US7", unit_type="US"))
    set_swimlane(g, site="S", group_by="none", rows=[dict(FALLBACK_ROW)])
    text = write_graphml(g).decode("utf-8")
    assert "US7" in text
    assert "None" not in text
