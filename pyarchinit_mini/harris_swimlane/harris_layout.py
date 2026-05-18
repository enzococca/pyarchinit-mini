"""Harris-classico positioning algorithm — server-side, deterministic.

Each lane gets a sub-graph layout: nodes connected by stratigraphic edges
(``overlies``, ``is_after``) are ranked top→bottom so the most recent
(no incoming edges) is at the top of the lane and the oldest is at the
bottom. Orphan nodes (no edges) sit at the deepest y in their lane.

Output is consumed by ``SwimlaneState.load`` and ``yed_writer`` so the
editor canvas and the exported yEd file produce identical geometry.
"""
from __future__ import annotations

from collections import defaultdict, deque
from typing import Callable


_TOPO_EDGE_LABELS = frozenset({"overlies", "is_after"})


def compute_harris_positions(
    nodes: list[dict],
    edges: list[dict],
    *,
    lane_id_for: Callable[[dict], str],
    lane_widths: dict[str, int],
    node_w: int = 80,
    node_h: int = 30,
    h_gap: int = 50,
    v_gap: int = 40,
) -> dict[str, tuple[float, float]]:
    """Compute (x, y) for every node, confined within its lane.

    Args:
        nodes: list of {"id", "lane", ...}.
        edges: list of {"source", "target", "label"}.
        lane_id_for: callable returning the lane id for a node.
        lane_widths: lane_id → pixel width (used to clamp x within lane).
        node_w / node_h: pixel dims for layout spacing.
        h_gap / v_gap: spacing between sibling nodes.

    Returns:
        {node_id: (x, y)} with global canvas coordinates (lane x-offsets
        baked in by the caller's lane_widths order).
    """
    if not nodes:
        return {}

    # Group nodes by lane.
    lane_nodes: dict[str, list[dict]] = defaultdict(list)
    for n in nodes:
        lane_nodes[lane_id_for(n)].append(n)

    # Index edges only those participating in topological order.
    topo_edges_by_lane: dict[str, list[tuple[str, str]]] = defaultdict(list)
    node_to_lane = {n["id"]: lane_id_for(n) for n in nodes}
    for e in edges:
        if e.get("label") not in _TOPO_EDGE_LABELS:
            continue
        s_lane = node_to_lane.get(e["source"])
        t_lane = node_to_lane.get(e["target"])
        if s_lane and s_lane == t_lane:
            topo_edges_by_lane[s_lane].append((e["source"], e["target"]))

    positions: dict[str, tuple[float, float]] = {}
    x_offset = 0.0
    for lane_id, ns in lane_nodes.items():
        width = lane_widths.get(lane_id, 200)
        sub_positions = _layout_lane(ns, topo_edges_by_lane[lane_id], width,
                                     node_w, node_h, h_gap, v_gap)
        for nid, (x_local, y_local) in sub_positions.items():
            positions[nid] = (x_offset + x_local, y_local)
        x_offset += width + h_gap

    return positions


def _layout_lane(
    nodes: list[dict], edges: list[tuple[str, str]], lane_width: int,
    node_w: int, node_h: int, h_gap: int, v_gap: int,
) -> dict[str, tuple[float, float]]:
    """Layout one lane: ranked top→bottom by topological order, orphans last."""
    in_edges: dict[str, list[str]] = defaultdict(list)
    out_edges: dict[str, list[str]] = defaultdict(list)
    node_ids = {n["id"] for n in nodes}
    for s, t in edges:
        if s in node_ids and t in node_ids:
            in_edges[t].append(s)
            out_edges[s].append(t)

    # Determine which nodes are truly orphans (no topo edges at all).
    connected_ids = {nid for nid in node_ids if in_edges.get(nid) or out_edges.get(nid)}
    orphan_ids = node_ids - connected_ids

    # Kahn's algorithm — assign rank to each connected node.
    rank: dict[str, int] = {}
    queue = deque(nid for nid in connected_ids if not in_edges.get(nid))
    while queue:
        nid = queue.popleft()
        r = max((rank[p] + 1 for p in in_edges.get(nid, [])), default=0)
        rank[nid] = r
        for nxt in out_edges.get(nid, []):
            # Re-enqueue only when all parents have a rank already.
            if all(p in rank for p in in_edges.get(nxt, [])):
                if nxt not in rank:
                    queue.append(nxt)

    # Nodes not in rank (cycles / true orphans) get the deepest rank.
    max_rank = max(rank.values(), default=0)
    orphan_rank = max_rank + 1
    ranked: dict[int, list[str]] = defaultdict(list)
    for n in nodes:
        nid = n["id"]
        if nid in orphan_ids:
            r = orphan_rank
        else:
            r = rank.get(nid, orphan_rank)
        ranked[r].append(nid)

    positions: dict[str, tuple[float, float]] = {}
    for r in sorted(ranked.keys()):
        siblings = ranked[r]
        row_w = len(siblings) * node_w + (len(siblings) - 1) * h_gap
        start_x = max((lane_width - row_w) / 2.0, 0.0)
        y = r * (node_h + v_gap)
        for i, nid in enumerate(siblings):
            x = start_x + i * (node_w + h_gap)
            positions[nid] = (x, y)
    return positions
