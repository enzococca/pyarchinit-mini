"""GraphProjector — DB rows → s3dgraphy.Graph (stratigraphic layer only).

Idempotent: re-projecting the same DB state produces an identical graph
modulo per-instance object identity. Uses VocabProvider for canonical
unit_type info and EdgeRegistry to parse PyArchInit rapporti strings.
"""
from typing import Optional

import s3dgraphy
from sqlalchemy import text
from sqlalchemy.orm import Session

from pyarchinit_mini.vocab.provider import VocabProvider
from .edge_registry import EdgeRegistry


class GraphProjector:
    @staticmethod
    def populate_graph(
        session: Session,
        site: str,
        *,
        area: Optional[str] = None,
    ) -> "s3dgraphy.Graph":
        """DB rows → s3dgraphy.Graph (stratigraphic layer only).

        Reads us_table for the given site (optionally filtered by area).
        Edge typing uses EdgeRegistry (which wraps VocabProvider's
        italian_aliases). The result is idempotent: node IDs are derived
        deterministically from (sito, area, us), so re-projecting the same
        DB state always produces the same graph topology.
        """
        graph = s3dgraphy.Graph(
            graph_id=f"strat:{site}",
            name=f"{site} stratigraphic graph",
            description="Projected from PyArchInit-Mini DB",
        )

        sql = (
            "SELECT id_us, sito, area, us, unita_tipo, rapporti, node_uuid "
            "FROM us_table WHERE sito = :sito"
        )
        params: dict = {"sito": site}
        if area:
            sql += " AND area = :area"
            params["area"] = area
        sql += " ORDER BY id_us"

        rows = session.execute(text(sql), params).fetchall()

        provider = VocabProvider.instance()
        registry = EdgeRegistry()

        # First pass: build nodes and a us-number → node_id lookup.
        # us_to_node maps string us number → graph node_id for edge resolution.
        us_to_node: dict[str, str] = {}
        rows_data: list[tuple[dict, str]] = []

        for row in rows:
            row_dict = (
                dict(row._mapping)
                if hasattr(row, "_mapping")
                else dict(zip(row.keys(), row))
            )
            us_num = str(row_dict["us"])
            sito = row_dict["sito"]
            ar = row_dict["area"] or ""
            node_id = f"{sito}_{ar}_{us_num}" if ar else f"{sito}_{us_num}"

            unita_tipo = row_dict["unita_tipo"] or "US"
            ut_info = provider.get_unit_type(unita_tipo)
            family = ut_info.family if (ut_info and ut_info.family) else "unknown"

            node = s3dgraphy.Node(node_id, f"{unita_tipo}{us_num}", "")
            # s3dgraphy.Node.attributes is a dict; it exists per the 0.1.42 API.
            if not hasattr(node, "attributes") or node.attributes is None:
                node.attributes = {}
            node.attributes["unit_type"] = unita_tipo
            node.attributes["family"] = family
            node.attributes["EMid"] = row_dict["node_uuid"] or ""

            graph.add_node(node)
            us_to_node[us_num] = node_id
            rows_data.append((row_dict, node_id))

        # Second pass: create stratigraphic edges from rapporti strings.
        edge_counter = 0
        for row_dict, source_id in rows_data:
            rapporti = (row_dict["rapporti"] or "").strip()
            if not rapporti:
                continue
            for raw_token in rapporti.replace(";", ",").split(","):
                token = raw_token.strip()
                if not token:
                    continue
                edge_name, target_us = registry.parse_rapporti_token(token)
                if edge_name is None or target_us is None:
                    continue
                if target_us not in us_to_node:
                    continue
                target_id = us_to_node[target_us]
                edge_counter += 1
                graph.add_edge(f"e{edge_counter}", source_id, target_id, edge_name)

        return graph
