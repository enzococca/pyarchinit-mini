"""Stratigraphic edges from us_table.rapporti, layered on an s3dgraphy.Graph.

s3dgraphy's PyArchInitImporter does not map ``rapporti`` (mapping ``relations``
is empty until s3Dgraphy#26 lands), so mini keeps its codec and adds the edges.
Normalisation is unchanged from the former S3DProjector: inverse → forward with
endpoint swap, symmetric dedup, inverse dedup, per-canonical transitive reduction.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

from .rapporti_codec import INVERSE_PAIRS, REVERSE_TO_FORWARD, SYMMETRIC, parse_rapporti
from .strat_graph import pyarchinit_attrs, stratigraphic_nodes

STRATIGRAPHIC_EDGE_TYPES = frozenset(INVERSE_PAIRS) | SYMMETRIC


@dataclass(frozen=True)
class StratEdge:
    source_id: str
    target_id: str
    canonical: str


class NodeIndex:
    def __init__(self) -> None:
        self.by_area_us: Dict[Tuple[str, str], str] = {}
        self.by_us: Dict[str, str] = {}
        self.by_id_us: Dict[int, str] = {}

    @classmethod
    def from_graph(cls, graph) -> "NodeIndex":
        idx = cls()
        for node in stratigraphic_nodes(graph):
            a = pyarchinit_attrs(node)
            if not a:
                continue
            us = str(a["us"])
            idx.by_area_us[(a.get("area") or "", us)] = node.node_id
            idx.by_us.setdefault(us, node.node_id)
            if a.get("id_us") is not None:
                idx.by_id_us[int(a["id_us"])] = node.node_id
        return idx

    def resolve(self, us: str, area: Optional[str]) -> Optional[str]:
        if area:
            hit = self.by_area_us.get((area, str(us)))
            if hit:
                return hit
        return self.by_us.get(str(us))


def build_stratigraphic_edges(rapporti_rows: Iterable[Tuple[str, Optional[str]]], *, site: str,
                              index: NodeIndex) -> List[StratEdge]:
    seen = set()
    edges: List[StratEdge] = []
    for source_id, raw in rapporti_rows:
        if not raw or not str(raw).strip():
            continue
        for rap in parse_rapporti(raw, current_site=site):
            target_id = index.resolve(rap.target_us, rap.target_area)
            if target_id is None:
                continue
            canonical, src, tgt = rap.canonical, source_id, target_id
            if canonical in REVERSE_TO_FORWARD:
                canonical = REVERSE_TO_FORWARD[canonical]
                src, tgt = tgt, src
            key = (canonical, tuple(sorted((src, tgt)))) if canonical in SYMMETRIC else (canonical, src, tgt)
            if key in seen:
                continue
            seen.add(key)
            edges.append(StratEdge(src, tgt, canonical))
    return _transitive_reduction(_drop_redundant_inverses(edges))


def _drop_redundant_inverses(edges: List[StratEdge]) -> List[StratEdge]:
    forward = {(e.canonical, e.source_id, e.target_id) for e in edges if e.canonical not in SYMMETRIC}
    kept: List[StratEdge] = []
    for e in edges:
        if e.canonical not in SYMMETRIC:
            inv = INVERSE_PAIRS.get(e.canonical)
            if inv is not None and (inv, e.target_id, e.source_id) in forward and e.canonical > inv:
                continue
        kept.append(e)
    return kept


def _transitive_reduction(edges: List[StratEdge]) -> List[StratEdge]:
    try:
        import networkx as nx
    except ImportError:
        return edges
    by_canon: Dict[str, List[StratEdge]] = {}
    for e in edges:
        by_canon.setdefault(e.canonical, []).append(e)
    reduced: List[StratEdge] = []
    for canon, group in by_canon.items():
        if canon in SYMMETRIC:
            reduced.extend(group)
            continue
        dg = nx.DiGraph()
        dg.add_edges_from((e.source_id, e.target_id) for e in group)
        try:
            keep = set(nx.transitive_reduction(dg).edges())
        except nx.NetworkXError:
            reduced.extend(group)
            continue
        reduced.extend(e for e in group if (e.source_id, e.target_id) in keep)
    return reduced


def add_stratigraphic_edges(graph, edges: Iterable[StratEdge]) -> int:
    added = 0
    for e in edges:
        edge_id = f"{e.source_id}__{e.canonical}__{e.target_id}"
        if graph.find_edge_by_id(edge_id) is None:
            graph.add_edge(edge_id, e.source_id, e.target_id, e.canonical)
            added += 1
    return added
