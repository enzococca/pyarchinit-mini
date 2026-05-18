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
