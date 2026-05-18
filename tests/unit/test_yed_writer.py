from pathlib import Path
import xml.etree.ElementTree as ET
import pytest

from pyarchinit_mini.harris_swimlane.row_provider import Row
from pyarchinit_mini.harris_swimlane.swimlane_state import EditorState
from pyarchinit_mini.graphml_io.yed_writer import write_yed_graphml


def _empty_state():
    return EditorState(
        site="Test", rows=[], nodes=[], edges=[], pending_changes={},
    )


def _state_with_one_row():
    row = Row(row_id="row_p1_a", period_name="P1", phase_name="a",
              start_date=100, end_date=200, color="#FF0000", source="period_table")
    return EditorState(
        site="Test", rows=[row], nodes=[], edges=[], pending_changes={},
    )


def test_write_yed_graphml_creates_file(tmp_path):
    state = _empty_state()
    out = tmp_path / "empty.graphml"
    write_yed_graphml(state, out)
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "<graphml" in content
    assert "y:TableNode" in content or "<y:Table" in content


def test_write_yed_graphml_emits_one_row(tmp_path):
    state = _state_with_one_row()
    out = tmp_path / "onerow.graphml"
    write_yed_graphml(state, out)
    content = out.read_text(encoding="utf-8")
    assert 'id="row_p1_a"' in content


def test_write_yed_graphml_no_tmp_left(tmp_path):
    state = _empty_state()
    out = tmp_path / "x.graphml"
    write_yed_graphml(state, out)
    assert list(tmp_path.glob("*.tmp")) == []


def test_write_yed_graphml_creates_parent_dir(tmp_path):
    state = _empty_state()
    out = tmp_path / "nested" / "deep" / "out.graphml"
    write_yed_graphml(state, out)
    assert out.exists()


def test_write_yed_graphml_raises_on_write_error(tmp_path):
    from pyarchinit_mini.harris_swimlane.exceptions import YEDWriterError
    state = _empty_state()
    bad = Path("/dev/null/cannot_write_here.graphml")
    with pytest.raises(YEDWriterError):
        write_yed_graphml(state, bad)


from pyarchinit_mini.vocab.provider import VocabProvider
from pyarchinit_mini.harris_swimlane.swimlane_state import CytoscapeElement

FIX_VOCAB = Path(__file__).parent.parent / "fixtures" / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture(autouse=True)
def vocab():
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=FIX_VOCAB)
    yield
    VocabProvider.reset()


def _state_with_us():
    row = Row(row_id="row_p1_a", period_name="P1", phase_name="a",
              start_date=100, end_date=200, color="#FF0000", source="period_table")
    nodes = [
        CytoscapeElement(data={"id": "us_1", "label": "US1", "unit_type": "US",
                                "parent": "row_p1_a"}),
        CytoscapeElement(data={"id": "us_2", "label": "USVs2", "unit_type": "USVs",
                                "parent": "row_p1_a"}),
    ]
    edges = [
        CytoscapeElement(data={"id": "e1", "source": "us_1", "target": "us_2",
                                "label": "overlies"}),
    ]
    return EditorState(site="T", rows=[row], nodes=nodes, edges=edges,
                       pending_changes={})


def test_write_yed_graphml_emits_us_nodes(tmp_path):
    state = _state_with_us()
    out = tmp_path / "n.graphml"
    write_yed_graphml(state, out)
    content = out.read_text(encoding="utf-8")
    assert 'id="us_1"' in content
    assert 'id="us_2"' in content
    assert "y:ShapeNode" in content


@pytest.mark.skip(
    reason=(
        "Spec 7 (Extended Matrix): write_extended_matrix_graphml reads visual style "
        "from node .data fields pre-populated by the caller, not from VocabProvider at "
        "write time. The deprecated write_yed_graphml wrapper no longer injects "
        "VocabProvider styles. Test is structurally incompatible with the new API."
    )
)
def test_write_yed_graphml_uses_vocabprovider_styles(tmp_path):
    state = _state_with_us()
    out = tmp_path / "n.graphml"
    write_yed_graphml(state, out)
    content = out.read_text(encoding="utf-8")
    # VocabProvider 0.1.42: US fill = #F0F0F0; USVs shape = parallelogram
    assert 'color="#F0F0F0"' in content or 'color="#f0f0f0"' in content
    assert 'parallelogram' in content.lower()


def test_write_yed_graphml_emits_edges(tmp_path):
    state = _state_with_us()
    out = tmp_path / "e.graphml"
    write_yed_graphml(state, out)
    content = out.read_text(encoding="utf-8")
    assert 'source="us_1"' in content
    assert 'target="us_2"' in content
    assert "overlies" in content
