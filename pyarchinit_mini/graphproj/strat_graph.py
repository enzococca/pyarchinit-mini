"""The s3dgraphy.Graph contract mini uses everywhere (spec §4).

A projected or imported graph is a plain ``s3dgraphy.Graph``. On top of what
``PyArchInitImporter`` produces, mini adds:

* ``node.attributes["pyarchinit"]`` on every stratigraphic node: the row-level
  facts the swimlane editor, the yEd writer and the DB write-back need and the
  importer does not keep (us number, area, unit type, period/phase, …).
* ``graph.attributes["swimlane"]``: the period rows (lanes) for the editor.

The legacy keys ``unit_type``, ``family`` and ``EMid`` stay on the node for the
ingestor and older callers.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from s3dgraphy.graph import Graph
from s3dgraphy.nodes.base_node import Node
from s3dgraphy.nodes.stratigraphic_node import StratigraphicNode
from s3dgraphy.utils.utils import apply_legacy_kind, get_stratigraphic_node_class

PYARCHINIT_KEY = "pyarchinit"
SWIMLANE_KEY = "swimlane"
FALLBACK_ROW: Dict[str, Any] = {
    "row_id": "row_0", "label": "Periodo 1", "periodo": None, "fase": None,
    "datazione": None, "is_fallback": True,
}


def new_graph(site: str) -> Graph:
    return Graph(
        graph_id=f"strat:{site}",
        name=f"{site} stratigraphic graph",
        description="Projected from PyArchInit-Mini DB",
    )


def new_strat_node(*, node_id: str, name: str, unit_type: str, description: str = "") -> StratigraphicNode:
    kind = (unit_type or "US").strip() or "US"
    cls = get_stratigraphic_node_class(kind)
    node = cls(node_id=node_id, name=name, description=description or "")
    apply_legacy_kind(node, kind)
    return node


def is_stratigraphic(node: Node) -> bool:
    return isinstance(node, StratigraphicNode)


def stratigraphic_nodes(graph: Graph) -> List[Node]:
    return [n for n in graph.nodes if is_stratigraphic(n)]


def stratigraphic_edges(graph: Graph) -> list:
    ids = {n.node_id for n in stratigraphic_nodes(graph)}
    return [e for e in graph.edges if e.edge_source in ids and e.edge_target in ids]


def pyarchinit_attrs(node: Node) -> Dict[str, Any]:
    attrs = node.attributes if getattr(node, "attributes", None) is not None else {}
    return attrs.get(PYARCHINIT_KEY) or {}


def set_pyarchinit_attrs(
    node: Node, *, us: str, unit_type: str, sito: str,
    area: Optional[str] = None, description: Optional[str] = None,
    periodo: Optional[str] = None, fase: Optional[str] = None,
    row_id: str = "row_0", sub_group: Optional[str] = None,
    node_uuid: Optional[str] = None, id_us: Optional[int] = None,
    family: Optional[str] = None,
) -> Node:
    if getattr(node, "attributes", None) is None:
        node.attributes = {}
    node.attributes[PYARCHINIT_KEY] = {
        "id_us": id_us, "sito": sito, "area": area, "us": str(us),
        "unit_type": unit_type or "US", "description": description,
        "periodo": periodo, "fase": fase, "row_id": row_id,
        "sub_group": sub_group, "node_uuid": node_uuid,
    }
    node.attributes["unit_type"] = unit_type or "US"
    node.attributes["family"] = family or "unknown"
    node.attributes["EMid"] = node_uuid or ""
    return node


def set_swimlane(graph: Graph, *, site: str, group_by: str, rows: List[Dict[str, Any]]) -> None:
    graph.attributes[SWIMLANE_KEY] = {"site": site, "group_by": group_by, "rows": list(rows)}


def get_swimlane(graph: Graph) -> Dict[str, Any]:
    stored = (graph.attributes or {}).get(SWIMLANE_KEY)
    if stored:
        return stored
    site = graph.graph_id.split(":", 1)[1] if ":" in (graph.graph_id or "") else (graph.graph_id or "")
    return {"site": site, "group_by": "none", "rows": []}
