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
