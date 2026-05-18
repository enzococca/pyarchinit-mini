import pytest
from pyarchinit_mini.harris_swimlane.compound_layout import (
    derive_row_id,
    initial_node_position,
    compute_row_positions,
)
from pyarchinit_mini.harris_swimlane.row_provider import Row


def test_derive_row_id_period_and_phase():
    assert derive_row_id("Period 1", "a") == "row_period-1_a"


def test_derive_row_id_period_only():
    assert derive_row_id("Roman Imperial", None) == "row_roman-imperial"


def test_derive_row_id_unassigned():
    assert derive_row_id(None, None) == "_unassigned"


def test_initial_node_position_returns_xy():
    row = Row(row_id="row_p1_a", period_name="P1", phase_name="a",
              start_date=100, end_date=200, color="#FF0000", source="period_table")
    pos = initial_node_position(row, index_in_row=0)
    assert "x" in pos and "y" in pos
    assert isinstance(pos["x"], (int, float))
    assert isinstance(pos["y"], (int, float))


def test_initial_node_position_spaces_nodes_horizontally():
    row = Row(row_id="r", period_name="P", phase_name=None,
              start_date=None, end_date=None, color="#000", source="period_table")
    p0 = initial_node_position(row, 0)
    p1 = initial_node_position(row, 1)
    assert p1["x"] > p0["x"]


def test_compute_row_positions_recent_at_top():
    rows = [
        Row("r1", "P1", "a", 100, 200, "#000", "period_table"),
        Row("r2", "P2", "a", 200, 300, "#111", "period_table"),
        Row("r3", "P3", "a", 300, 400, "#222", "period_table"),
    ]
    positions = compute_row_positions(rows)
    assert positions["r3"][1] < positions["r2"][1] < positions["r1"][1]


def test_compute_row_positions_handles_nulls():
    rows = [
        Row("r_none", "P", None, None, None, "#000", "fallback_distinct"),
        Row("r_p1", "P1", "a", 100, 200, "#111", "period_table"),
    ]
    positions = compute_row_positions(rows)
    assert positions["r_p1"][1] != positions["r_none"][1]
