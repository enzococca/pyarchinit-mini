"""PR2 gate: yed_writer output must match golden fixture for canonical Volterra state."""
from pathlib import Path
import xml.etree.ElementTree as ET
import pytest

from pyarchinit_mini.vocab.provider import VocabProvider
from pyarchinit_mini.harris_swimlane.row_provider import Row
from pyarchinit_mini.harris_swimlane.swimlane_state import EditorState, CytoscapeElement
from pyarchinit_mini.graphml_io.yed_writer import write_yed_graphml

FIX = Path(__file__).parent.parent / "fixtures"
GOLDEN = FIX / "yed_graphml_outputs" / "volterra_baseline.graphml"
VOCAB_FIX = FIX / "s3dgraphy_jsons" / "0.1.42"


@pytest.fixture(autouse=True)
def vocab():
    VocabProvider.reset()
    VocabProvider.instance(json_config_dir=VOCAB_FIX)
    yield
    VocabProvider.reset()


def _build_volterra_state():
    rows = [
        Row("row_medieval_b", "Medieval", "b", 1200, 1500, "#9642B7", "period_table"),
        Row("row_medieval_a", "Medieval", "a", 600, 1200, "#7204CB", "period_table"),
        Row("row_late-antiquity_a", "Late Antiquity", "a", 300, 600, "#20ADB7", "period_table"),
        Row("row_roman_b", "Roman", "b", 100, 300, "#65C3E4", "period_table"),
        Row("row_roman_a", "Roman", "a", -27, 100, "#FA9639", "period_table"),
    ]
    nodes = [
        CytoscapeElement(data={"id": "us_1", "label": "US1", "unit_type": "US", "parent": "row_roman_a"}),
        CytoscapeElement(data={"id": "us_2", "label": "US2", "unit_type": "US", "parent": "row_roman_b"}),
        CytoscapeElement(data={"id": "us_3", "label": "USVs3", "unit_type": "USVs", "parent": "row_medieval_a"}),
    ]
    edges = [
        CytoscapeElement(data={"id": "e1", "source": "us_2", "target": "us_1", "label": "overlies"}),
    ]
    return EditorState(site="Volterra", rows=rows, nodes=nodes, edges=edges, pending_changes={})


def test_yed_writer_output_matches_golden(tmp_path):
    state = _build_volterra_state()
    out = tmp_path / "v.graphml"
    write_yed_graphml(state, out)
    actual = out.read_text(encoding="utf-8")
    golden = GOLDEN.read_text(encoding="utf-8")
    assert actual == golden, (
        "yed_writer output diverged from golden. "
        "If intentional, regenerate the baseline."
    )


def test_yed_writer_row_count_matches_golden():
    tree = ET.parse(GOLDEN)
    rows = tree.findall(".//{http://www.yworks.com/xml/graphml}Row")
    assert len(rows) == 5


def test_yed_writer_node_count_matches_golden():
    tree = ET.parse(GOLDEN)
    ns = {"g": "http://graphml.graphdrawing.org/xmlns"}
    nodes = tree.findall(".//g:graph[@id='swimlane_root:']/g:node", ns)
    assert len(nodes) == 3
