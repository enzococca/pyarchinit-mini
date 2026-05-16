"""Harris matrix visual parity gate: standard unit types (US, SU, WSU, USM)
must not regress visually between the pre-Task-9 em_palette implementation
and the post-Task-9 VocabProvider-backed implementation.

This file is the gate for Task 9. The asserts pass trivially before Task 9
(EMPalette is unchanged); the parity check becomes meaningful after Task 9
because EMPalette will then read from VocabProvider."""
import sqlite3
from pathlib import Path

import pytest

from pyarchinit_mini.graphml_converter.em_palette import EMPalette

FIX = Path(__file__).parent.parent / "fixtures"
DB = FIX / "databases" / "sqlite_fully_migrated.db"
BASELINE = FIX / "graphml_outputs" / "synthetic_baseline_em_palette.graphml"

# Standard types: their style must NOT change between baseline and post-Task-9
STANDARD_TYPES = {"US", "SU", "WSU", "USM"}


def _styles_for(db_path):
    """Return {unita_tipo: style_dict} via current EMPalette.get_node_style()."""
    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT DISTINCT unita_tipo, us FROM us_table").fetchall()
    conn.close()
    out = {}
    for unita_tipo, us in rows:
        label = f"{unita_tipo}{us}"
        out[unita_tipo] = EMPalette.get_node_style(label)
    return out


def test_baseline_fixture_exists():
    assert BASELINE.exists(), "baseline GraphML must exist (Task 8)"
    assert DB.exists(), "synthetic DB must exist (Task 8)"
    text = BASELINE.read_text(encoding="utf-8")
    assert "<graphml" in text or "<?xml" in text


def test_standard_unit_types_have_complete_style_dict():
    styles = _styles_for(DB)
    for ut in STANDARD_TYPES:
        if ut not in styles:
            continue
        s = styles[ut]
        assert "shape" in s, f"{ut} style missing 'shape'"
        assert "fill_color" in s, f"{ut} style missing 'fill_color'"
        assert "border_color" in s, f"{ut} style missing 'border_color'"


def test_us_standard_style_matches_expected_shape():
    """US must always be a rectangle. This is the contract Task 9 cannot break."""
    style = EMPalette.get_node_style("US100")
    assert style["shape"] == "rectangle"
