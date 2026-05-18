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
