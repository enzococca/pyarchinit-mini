"""
GraphML Resource

Provides GraphML stratigraphic graph data to Claude AI.
"""

import logging
import json
import networkx as nx
from typing import Dict, Any, Optional, List
from pathlib import Path

from .base_resource import BaseResource, ResourceDescription
from ...models.extended_matrix import ExtendedMatrix

logger = logging.getLogger(__name__)


class GraphMLResource(BaseResource):
    """
    GraphML Resource

    Provides access to GraphML stratigraphic graphs.

    URI format: resource://graphml/{graphml_id}
    URI format: resource://graphml/current (latest for site)
    URI format: resource://graphml/site/{site_id} (all graphs for site)
    """

    def __init__(self, db_session, config):
        """
        Initialize GraphML Resource

        Args:
            db_session: Database session
            config: MCP configuration
        """
        super().__init__(config)
        self.db_session = db_session

    def to_resource_description(self) -> ResourceDescription:
        """Return resource description"""
        return ResourceDescription(
            uri="resource://graphml",
            name="GraphML Stratigraphic Graph",
            description=(
                "Provides access to GraphML stratigraphic graphs containing "
                "stratigraphic units (US), relationships, and metadata. "
                "Use this resource to understand the stratigraphic sequence, "
                "relationships between units, and spatial structure for 3D modeling."
            ),
            mime_type="application/json",
        )

    async def read(self, resource_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Read GraphML resource

        Args:
            resource_id: GraphML ID, 'current', or None for list

        Returns:
            GraphML data as JSON-serializable dict

        Examples:
            read(None) -> List all GraphML files
            read("15") -> Get GraphML with ID 15
            read("current") -> Get current/latest GraphML
            read("site/1") -> Get all GraphML for site 1
        """
        try:
            if resource_id is None:
                # List all GraphML files
                return await self._list_all_graphml()

            elif resource_id == "current":
                # Get current/latest GraphML
                return await self._get_current_graphml()

            elif resource_id.startswith("site/"):
                # Get all GraphML for a specific site
                site_id = int(resource_id.split("/")[1])
                return await self._get_graphml_by_site(site_id)

            else:
                # Get specific GraphML by ID
                graphml_id = int(resource_id)
                return await self._get_graphml_by_id(graphml_id)

        except ValueError as e:
            logger.error(f"Invalid resource_id: {resource_id} - {e}")
            return self._format_error("ValidationError", str(e))
        except Exception as e:
            logger.error(f"Error reading GraphML resource: {e}", exc_info=True)
            return self._format_error("InternalError", str(e))

    async def _list_all_graphml(self) -> Dict[str, Any]:
        """List all GraphML files in database"""
        try:
            # Query all GraphML files from extended_matrix_table
            graphml_files = (
                self.db_session.query(ExtendedMatrix)
                .order_by(ExtendedMatrix.id.desc())
                .all()
            )

            return {
                "type": "graphml_list",
                "count": len(graphml_files),
                "graphml_files": [
                    {
                        "id": gml.id,
                        "filepath": gml.filepath,
                        "created_at": (
                            gml.created_at.isoformat() if gml.created_at else None
                        ),
                        "node_count": self._count_nodes(gml.filepath),
                    }
                    for gml in graphml_files
                ],
            }
        except Exception as e:
            logger.error(f"Error listing GraphML files: {e}", exc_info=True)
            return self._format_error("DatabaseError", str(e))

    async def _get_current_graphml(self) -> Dict[str, Any]:
        """Get current/latest GraphML file"""
        try:
            # Get the most recent GraphML file
            latest = (
                self.db_session.query(ExtendedMatrix)
                .order_by(ExtendedMatrix.id.desc())
                .first()
            )

            if not latest:
                return self._format_error("NotFound", "No GraphML files found")

            return await self._parse_graphml_file(latest)

        except Exception as e:
            logger.error(f"Error getting current GraphML: {e}", exc_info=True)
            return self._format_error("DatabaseError", str(e))

    async def _get_graphml_by_site(self, site_id: int) -> Dict[str, Any]:
        """Get all GraphML files for a specific site"""
        try:
            # Note: extended_matrix_table doesn't have site_id FK
            # We need to parse GraphML to filter by site
            all_graphml = (
                self.db_session.query(ExtendedMatrix)
                .order_by(ExtendedMatrix.id.desc())
                .all()
            )

            site_graphml = []
            for gml in all_graphml:
                # Parse GraphML and check site
                parsed = await self._parse_graphml_file(gml)
                if parsed.get("site_name", "").lower().find(str(site_id)) >= 0:
                    site_graphml.append(parsed)

            return {
                "type": "graphml_list_by_site",
                "site_id": site_id,
                "count": len(site_graphml),
                "graphml_files": site_graphml,
            }

        except Exception as e:
            logger.error(f"Error getting GraphML by site: {e}", exc_info=True)
            return self._format_error("DatabaseError", str(e))

    async def _get_graphml_by_id(self, graphml_id: int) -> Dict[str, Any]:
        """Get specific GraphML file by ID"""
        try:
            graphml = (
                self.db_session.query(ExtendedMatrix)
                .filter(ExtendedMatrix.id == graphml_id)
                .first()
            )

            if not graphml:
                return self._format_error(
                    "NotFound", f"GraphML with ID {graphml_id} not found"
                )

            return await self._parse_graphml_file(graphml)

        except Exception as e:
            logger.error(f"Error getting GraphML by ID: {e}", exc_info=True)
            return self._format_error("DatabaseError", str(e))

    async def _parse_graphml_file(
        self, graphml_record: ExtendedMatrix
    ) -> Dict[str, Any]:
        """
        Parse GraphML file and extract structured data

        Returns:
            Dict with nodes, edges, metadata
        """
        try:
            filepath = graphml_record.filepath

            if not filepath or not Path(filepath).exists():
                return self._format_error(
                    "FileNotFound", f"GraphML file not found: {filepath}"
                )

            # Load GraphML using NetworkX
            G = nx.read_graphml(filepath)

            # Extract nodes with attributes
            nodes = []
            for node_id in G.nodes():
                node_data = G.nodes[node_id]

                # Extract key attributes
                node_info = {
                    "id": node_id,
                    "label": node_data.get("label", node_id),
                    "extended_label": node_data.get("extended_label", ""),
                    "description": node_data.get("description", ""),
                    "period": node_data.get("period", ""),
                    "area": node_data.get("area", ""),
                    "formation": node_data.get("formation", ""),
                    "unita_tipo": node_data.get("unita_tipo", "US"),
                    "interpretation": node_data.get("interpretation", ""),
                }

                # Extract visual properties (yEd geometry)
                if "x" in node_data and "y" in node_data:
                    node_info["position"] = {
                        "x": float(node_data["x"]),
                        "y": float(node_data["y"]),
                    }

                # Parse US ID from label (e.g., "US 5" -> 5)
                label = node_info["label"]
                if label.startswith("US "):
                    try:
                        node_info["us_id"] = int(label.split(" ")[1])
                    except (IndexError, ValueError):
                        node_info["us_id"] = None

                nodes.append(node_info)

            # Extract edges with relationships
            edges = []
            for source, target in G.edges():
                edge_data = G.edges[source, target]

                edge_info = {
                    "source": source,
                    "target": target,
                    "relationship": edge_data.get("relationship", ""),
                    "certainty": edge_data.get("certainty", "certain"),
                }

                edges.append(edge_info)

            # Extract metadata
            metadata = {
                "node_count": len(nodes),
                "edge_count": len(edges),
                "site_name": G.graph.get("site_name", "Unknown"),
                "periods": list(set(n.get("period", "") for n in nodes if n.get("period"))),
                "areas": list(set(n.get("area", "") for n in nodes if n.get("area"))),
            }

            return {
                "type": "graphml_data",
                "id": graphml_record.id,
                "filepath": filepath,
                "created_at": (
                    graphml_record.created_at.isoformat()
                    if graphml_record.created_at
                    else None
                ),
                "metadata": metadata,
                "nodes": nodes,
                "edges": edges,
            }

        except Exception as e:
            logger.error(f"Error parsing GraphML file: {e}", exc_info=True)
            return self._format_error("ParseError", str(e))

    def _count_nodes(self, filepath: str) -> int:
        """Count nodes in GraphML file"""
        try:
            if not filepath or not Path(filepath).exists():
                return 0
            G = nx.read_graphml(filepath)
            return len(G.nodes())
        except Exception:
            return 0


# Stub implementations for other resources
# These will be implemented in subsequent files


class USResource(BaseResource):
    """US (Stratigraphic Units) Resource - TODO: Full implementation"""

    def __init__(self, us_service, config):
        super().__init__(config)
        self.us_service = us_service

    def to_resource_description(self) -> ResourceDescription:
        return ResourceDescription(
            uri="resource://us",
            name="Stratigraphic Units (US)",
            description="Provides access to stratigraphic unit data",
            mime_type="application/json",
        )

    async def read(self, resource_id: Optional[str] = None) -> Dict[str, Any]:
        # TODO: Implement
        return {"type": "us_data", "message": "Not yet implemented"}


class PeriodsResource(BaseResource):
    """Periods Resource - TODO: Full implementation"""

    def __init__(self, periodizzazione_service, config):
        super().__init__(config)
        self.periodizzazione_service = periodizzazione_service

    def to_resource_description(self) -> ResourceDescription:
        return ResourceDescription(
            uri="resource://periods",
            name="Chronological Periods",
            description="Provides access to chronological periods and datazioni",
            mime_type="application/json",
        )

    async def read(self, resource_id: Optional[str] = None) -> Dict[str, Any]:
        # TODO: Implement
        return {"type": "periods_data", "message": "Not yet implemented"}


class RelationshipsResource(BaseResource):
    """Relationships Resource - TODO: Full implementation"""

    def __init__(self, db_session, config):
        super().__init__(config)
        self.db_session = db_session

    def to_resource_description(self) -> ResourceDescription:
        return ResourceDescription(
            uri="resource://relationships",
            name="Stratigraphic Relationships",
            description="Provides stratigraphic relationships data",
            mime_type="application/json",
        )

    async def read(self, resource_id: Optional[str] = None) -> Dict[str, Any]:
        # TODO: Implement
        return {"type": "relationships_data", "message": "Not yet implemented"}


class SitesResource(BaseResource):
    """Sites Resource - TODO: Full implementation"""

    def __init__(self, site_service, config):
        super().__init__(config)
        self.site_service = site_service

    def to_resource_description(self) -> ResourceDescription:
        return ResourceDescription(
            uri="resource://sites",
            name="Archaeological Sites",
            description="Provides access to archaeological sites data",
            mime_type="application/json",
        )

    async def read(self, resource_id: Optional[str] = None) -> Dict[str, Any]:
        # TODO: Implement
        return {"type": "sites_data", "message": "Not yet implemented"}
