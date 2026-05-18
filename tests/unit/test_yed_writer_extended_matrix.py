"""Tests for yed_writer rewrite — Extended Matrix byte-compat."""
from pathlib import Path
import pytest

from pyarchinit_mini.harris_swimlane.swimlane_state import EditorState, CytoscapeElement
from pyarchinit_mini.graphml_io.yed_writer import write_extended_matrix_graphml


@pytest.fixture
def minimal_state():
    return EditorState(
        site="TestSite", rows=[], nodes=[], edges=[],
        pending_changes={}, group_by="period_phase",
    )


def test_emits_38_key_definitions(tmp_path, minimal_state):
    out = tmp_path / "out.graphml"
    write_extended_matrix_graphml(
        minimal_state, site_meta={"sito": "TestSite"}, epochs=[], out=out,
    )
    xml = out.read_text(encoding="utf-8")
    # Count <key declarations
    assert xml.count("<key ") >= 38
    # Specific keys present
    for k in ("d0", "d4", "d6", "d8", "d16", "d31", "d37"):
        assert f'id="{k}"' in xml


def test_root_graphml_namespace(tmp_path, minimal_state):
    out = tmp_path / "out.graphml"
    write_extended_matrix_graphml(
        minimal_state, site_meta={"sito": "TestSite"}, epochs=[], out=out,
    )
    xml = out.read_text(encoding="utf-8")
    assert 'xmlns="http://graphml.graphdrawing.org/xmlns"' in xml
    assert 'xmlns:y="http://www.yworks.com/xml/graphml"' in xml


def test_emits_table_node_root(tmp_path):
    from pyarchinit_mini.harris_swimlane.row_provider import Row
    rows = [
        Row(row_id="row_p1_a", period_name="Period01", phase_name="a",
            start_date=0, end_date=100, color="#FFAAAA", source="period_table"),
        Row(row_id="row_p2_a", period_name="Period02", phase_name="a",
            start_date=100, end_date=200, color="#AAFFAA", source="period_table"),
    ]
    state = EditorState(site="TestSite", rows=rows, nodes=[], edges=[],
                       pending_changes={}, group_by="period_phase")
    out = tmp_path / "out.graphml"
    write_extended_matrix_graphml(state, site_meta={"sito": "TestSite"}, epochs=[], out=out)
    xml = out.read_text(encoding="utf-8")
    assert 'yfiles.foldertype="group"' in xml
    assert 'configuration="YED_TABLE_NODE"' in xml
    assert '<y:Row id="row_p1_a"' in xml
    assert '<y:Row id="row_p2_a"' in xml


def test_emits_us_node_with_keys(tmp_path):
    from pyarchinit_mini.harris_swimlane.row_provider import Row
    rows = [Row(row_id="row_p1_a", period_name="P1", phase_name="a",
               start_date=0, end_date=100, color="#FFAAAA", source="period_table")]
    nodes = [CytoscapeElement(
        data={
            "id": "us_42", "label": "US42", "parent": "row_p1_a",
            "unit_type": "US", "color": "#F0F0F0",
            "shape": "rectangle", "border_color": "#540909", "border_style": "solid",
            "us": 42, "us_number": 42,
            "node_uuid": "uuid-42",
            "period": "1", "phase": "a",
            "description": "test strato",
            "area": "A",
            "datazione": "II sec",
            "file_path": "",
        },
        position={"x": 100, "y": 50},
    )]
    state = EditorState(site="TestSite", rows=rows, nodes=nodes, edges=[],
                       pending_changes={}, group_by="period_phase")
    out = tmp_path / "out.graphml"
    write_extended_matrix_graphml(state, site_meta={"sito": "TestSite"}, epochs=[], out=out)
    xml = out.read_text(encoding="utf-8")
    assert '<node id="us_42"' in xml
    assert '<data key="d6">42</data>' in xml
    assert '<data key="d7">A</data>' in xml
    assert '<data key="d8">TestSite</data>' in xml
    assert '<data key="d9">US</data>' in xml
    assert '<data key="d16">' in xml and 'uuid-42' in xml
    assert '<y:ShapeNode>' in xml


def test_cdata_injection_resilience(tmp_path):
    """rapporti or node_uuid containing ']]>' must not break XML parsing."""
    from pyarchinit_mini.harris_swimlane.row_provider import Row
    import xml.etree.ElementTree as ET
    rows = [Row(row_id="row_p1_a", period_name="P1", phase_name="a",
               start_date=0, end_date=100, color="#FFAAAA", source="period_table")]
    nodes = [CytoscapeElement(
        data={
            "id": "us_evil", "label": "USevil", "parent": "row_p1_a",
            "unit_type": "US", "us": 99, "us_number": 99,
            "node_uuid": "uuid-with-]]>-injection-attempt",
            "rapporti": "copre 1 ]]> evil",
            "period": "1", "phase": "a",
        },
        position={"x": 0, "y": 0},
    )]
    state = EditorState(site="TestSite", rows=rows, nodes=nodes, edges=[],
                       pending_changes={}, group_by="period_phase")
    out = tmp_path / "out.graphml"
    write_extended_matrix_graphml(state, site_meta={"sito": "TestSite"}, epochs=[], out=out)
    # Must parse as valid XML (no CDATA injection breaking it)
    tree = ET.parse(str(out))
    assert tree is not None
