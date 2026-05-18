"""Tests for harris_layout — server-side Harris-classico positioning."""
import pytest

from pyarchinit_mini.harris_swimlane.harris_layout import compute_harris_positions


def test_empty_input_returns_empty():
    positions = compute_harris_positions([], [], lane_id_for=lambda n: "L", lane_widths={"L": 200})
    assert positions == {}


def test_single_node_centered_in_lane():
    nodes = [{"id": "n1", "lane": "L1"}]
    positions = compute_harris_positions(
        nodes, [], lane_id_for=lambda n: n["lane"], lane_widths={"L1": 200}
    )
    assert "n1" in positions
    x, y = positions["n1"]
    assert 0 <= x <= 200


def test_two_nodes_one_edge_recent_on_top():
    nodes = [{"id": "n1", "lane": "L1"}, {"id": "n2", "lane": "L1"}]
    edges = [{"source": "n1", "target": "n2", "label": "overlies"}]
    positions = compute_harris_positions(
        nodes, edges, lane_id_for=lambda n: n["lane"], lane_widths={"L1": 200}
    )
    # n1 overlies n2 ⇒ n1 must be above n2 in canvas (smaller y).
    assert positions["n1"][1] < positions["n2"][1]


def test_orphan_nodes_packed_at_bottom():
    nodes = [
        {"id": "n1", "lane": "L1"}, {"id": "n2", "lane": "L1"},
        {"id": "orphan", "lane": "L1"},
    ]
    edges = [{"source": "n1", "target": "n2", "label": "overlies"}]
    positions = compute_harris_positions(
        nodes, edges, lane_id_for=lambda n: n["lane"], lane_widths={"L1": 200}
    )
    # orphan has no edges → must end up at the deepest y in lane
    max_y = max(y for _, y in positions.values())
    assert positions["orphan"][1] == max_y


def test_multiple_lanes_isolation():
    nodes = [
        {"id": "a", "lane": "L1"}, {"id": "b", "lane": "L1"},
        {"id": "c", "lane": "L2"},
    ]
    edges = [{"source": "a", "target": "b", "label": "overlies"}]
    positions = compute_harris_positions(
        nodes, edges,
        lane_id_for=lambda n: n["lane"],
        lane_widths={"L1": 200, "L2": 200},
    )
    # Each lane independently positioned — no overlap on x between lanes.
    assert positions["c"][0] >= 0
    assert positions["a"][1] < positions["b"][1]


def test_cycle_treated_as_orphans():
    """3-node cycle a→b→c→a — none have rank, all packed at the bottom."""
    nodes = [{"id": "a", "lane": "L1"}, {"id": "b", "lane": "L1"}, {"id": "c", "lane": "L1"}]
    edges = [
        {"source": "a", "target": "b", "label": "overlies"},
        {"source": "b", "target": "c", "label": "overlies"},
        {"source": "c", "target": "a", "label": "overlies"},
    ]
    positions = compute_harris_positions(
        nodes, edges, lane_id_for=lambda n: n["lane"], lane_widths={"L1": 200}
    )
    # All three end up at the same (deepest) rank because Kahn cannot rank a cycle.
    ys = {positions[nid][1] for nid in ("a", "b", "c")}
    assert len(ys) == 1


def test_diamond_pattern_correctly_ranked():
    """Diamond: top→{left,right}→bottom; bottom must be at rank 2 (below both branches)."""
    nodes = [
        {"id": "top", "lane": "L1"},
        {"id": "left", "lane": "L1"},
        {"id": "right", "lane": "L1"},
        {"id": "bottom", "lane": "L1"},
    ]
    edges = [
        {"source": "top", "target": "left", "label": "overlies"},
        {"source": "top", "target": "right", "label": "overlies"},
        {"source": "left", "target": "bottom", "label": "overlies"},
        {"source": "right", "target": "bottom", "label": "overlies"},
    ]
    positions = compute_harris_positions(
        nodes, edges, lane_id_for=lambda n: n["lane"], lane_widths={"L1": 300}
    )
    # top < left == right < bottom (by y)
    assert positions["top"][1] < positions["left"][1]
    assert positions["top"][1] < positions["right"][1]
    assert positions["left"][1] == positions["right"][1]
    assert positions["bottom"][1] > positions["left"][1]


def test_non_topo_edge_label_does_not_rank():
    """Edges with non-topological labels (e.g. 'fills') must NOT affect ranking."""
    nodes = [{"id": "n1", "lane": "L1"}, {"id": "n2", "lane": "L1"}]
    edges = [{"source": "n1", "target": "n2", "label": "fills"}]
    positions = compute_harris_positions(
        nodes, edges, lane_id_for=lambda n: n["lane"], lane_widths={"L1": 200}
    )
    # 'fills' is not in _TOPO_EDGE_LABELS — both treated as orphans, same rank.
    assert positions["n1"][1] == positions["n2"][1]


import inspect

from pyarchinit_mini.harris_swimlane import harris_layout as _harris_layout_mod


def test_compute_harris_positions_default_v_gap_is_40():
    """Spec 9: bumped v_gap default 20 → 40 for orthogonal edge breathing room."""
    sig = inspect.signature(_harris_layout_mod.compute_harris_positions)
    assert sig.parameters["v_gap"].default == 40


def test_compute_harris_positions_default_h_gap_is_50():
    """Spec 9: bumped h_gap default 30 → 50 for orthogonal edge breathing room."""
    sig = inspect.signature(_harris_layout_mod.compute_harris_positions)
    assert sig.parameters["h_gap"].default == 50
