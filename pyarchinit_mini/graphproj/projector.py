"""GraphProjector — DB → s3dgraphy.Graph through the shared library (issue #2).

The projection itself is s3dgraphy's ``PyArchInitImporter`` (nodes, qualia,
locations, authors, documents, epochs). Mini adds what the library does not
provide yet: the stratigraphic edges from ``rapporti`` and the swimlane rows /
row-level attributes the editor needs (spec §3–§5).
"""
from __future__ import annotations

import logging
from typing import Optional

from s3dgraphy.graph import Graph
from s3dgraphy.importer.pyarchinit_importer import PyArchInitImporter
from sqlalchemy.orm import Session

from .connection_url import connection_url_from_session
from .enrich import VALID_GROUP_BY, attach_pyarchinit_attributes, load_us_rows
from .exceptions import ProjectionError
from .periods import load_period_rows
from .strat_edges import NodeIndex, add_stratigraphic_edges, build_stratigraphic_edges
from .strat_graph import set_swimlane

logger = logging.getLogger(__name__)


class GraphProjector:
    MAPPING_NAME = "pyarchinit_us_mapping"

    @staticmethod
    def populate_graph(session: Session, site: str, *, area: Optional[str] = None,
                       group_by: str = "none") -> Graph:
        if group_by not in VALID_GROUP_BY:
            raise ValueError(f"group_by must be one of {sorted(VALID_GROUP_BY)}, got {group_by!r}")
        filters = {"sito": site}
        if area:
            filters["area"] = area
        try:  # construction too: a bad mapping/URL raises ValueError there
            importer = PyArchInitImporter(
                connection_url=connection_url_from_session(session),
                mapping_name=GraphProjector.MAPPING_NAME,
                filters=filters,
            )
            graph = importer.parse()
        except Exception as exc:  # parse() wraps everything in ImportError
            raise ProjectionError(f"s3dgraphy import failed for site {site!r}: {exc}", site=site) from exc
        graph.graph_id = f"strat:{site}"
        graph.name = f"{site} stratigraphic graph"
        graph.description = "Projected from PyArchInit-Mini DB via s3dgraphy"
        for w in importer.warnings:
            logger.debug("s3dgraphy importer [%s]: %s", site, w)

        period_rows = load_period_rows(session, site)
        us_rows = load_us_rows(session, site, group_by=group_by, area=area)
        attach_pyarchinit_attributes(graph, importer, us_rows, period_rows=period_rows)

        index = NodeIndex.from_graph(graph)
        rapporti_rows = [(index.by_id_us[r.id_us], r.rapporti) for r in us_rows if r.id_us in index.by_id_us]
        add_stratigraphic_edges(graph, build_stratigraphic_edges(rapporti_rows, site=site, index=index))

        set_swimlane(graph, site=site, group_by=group_by, rows=[r.as_dict() for r in period_rows])
        return graph
