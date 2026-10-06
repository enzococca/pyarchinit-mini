"""Build contract-conformant s3dgraphy graphs for view/writer tests (no DB)."""
from pyarchinit_mini.graphproj.strat_graph import (
    FALLBACK_ROW, new_graph, new_strat_node, set_pyarchinit_attrs, set_swimlane,
)


def make_graph(site="S", group_by="none", rows=None, nodes=(), edges=()):
    g = new_graph(site)
    rows = list(rows) if rows is not None else [dict(FALLBACK_ROW)]
    set_swimlane(g, site=site, group_by=group_by, rows=rows)
    for n in nodes:
        node = new_strat_node(node_id=n["id"], name=f"{n.get('unit_type', 'US')}{n['us']}",
                              unit_type=n.get("unit_type", "US"), description=n.get("description") or "")
        set_pyarchinit_attrs(
            node, us=n["us"], unit_type=n.get("unit_type", "US"), sito=site,
            area=n.get("area"), description=n.get("description"),
            periodo=n.get("periodo"), fase=n.get("fase"),
            row_id=n.get("row_id", rows[0]["row_id"]), sub_group=n.get("sub_group"),
            node_uuid=n.get("node_uuid"), id_us=n.get("id_us"),
        )
        g.add_node(node)
    for src, tgt, canonical in edges:
        g.add_edge(f"{src}__{canonical}__{tgt}", src, tgt, canonical)
    return g
