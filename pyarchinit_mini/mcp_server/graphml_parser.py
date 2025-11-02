"""
GraphML Parser

Parses GraphML files and extracts stratigraphic metadata,
combining GraphML data with database US records.
"""

import logging
import networkx as nx
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from ..models.us import US
from ..models.harris_matrix import Periodizzazione
from ..models.datazione import Datazione


logger = logging.getLogger(__name__)


class GraphMLParser:
    """
    GraphML Parser for stratigraphic data

    Parses GraphML files created by Extended Matrix and combines
    with database US records to generate complete metadata.
    """

    def __init__(self, db_session):
        """
        Initialize parser

        Args:
            db_session: Database session for querying US data
        """
        self.db_session = db_session
        self.graph: Optional[nx.DiGraph] = None
        self.graphml_path: Optional[str] = None

    def load_graphml(self, filepath: str) -> bool:
        """
        Load GraphML file (supports both standard GraphML and yFiles format)

        Args:
            filepath: Path to GraphML file

        Returns:
            True if loaded successfully
        """
        try:
            if not Path(filepath).exists():
                logger.error(f"GraphML file not found: {filepath}")
                return False

            # Try loading with NetworkX first
            try:
                self.graph = nx.read_graphml(filepath)
                self.graphml_path = filepath
                logger.info(
                    f"Loaded GraphML (standard): {len(self.graph.nodes())} nodes, "
                    f"{len(self.graph.edges())} edges"
                )
                return True
            except nx.NetworkXError:
                # If NetworkX fails, try parsing yFiles nested graph manually
                logger.info("Standard GraphML read failed, trying yFiles format...")
                return self._load_yfiles_graphml(filepath)

        except Exception as e:
            logger.error(f"Error loading GraphML: {e}", exc_info=True)
            return False

    def _load_yfiles_graphml(self, filepath: str) -> bool:
        """
        Load yFiles GraphML with nested graphs (TableNode format)

        Args:
            filepath: Path to yFiles GraphML file

        Returns:
            True if loaded successfully
        """
        import xml.etree.ElementTree as ET

        try:
            tree = ET.parse(filepath)
            root = tree.getroot()

            # Create empty graph
            self.graph = nx.DiGraph()

            # Find main graph and nested graph (namespace-agnostic)
            main_graph = None
            nested_graph = None

            for child in list(root):
                if 'graph' in child.tag and child.get('id') == 'G':
                    main_graph = child

                    # Look for table_node_group node with nested graph
                    for node in list(main_graph):
                        if 'node' in node.tag and node.get('id') == 'table_node_group':
                            for subelem in list(node):
                                if 'graph' in subelem.tag:
                                    nested_graph = subelem
                                    break
                            break
                    break

            if nested_graph is None:
                logger.error("No nested graph found in yFiles GraphML")
                return False

            # Key mapping for data attributes
            node_key_map = {
                'd4': 'label',
                'd5': 'extended_label',
                'd7': 'description',
                'd8': 'period',
                'd9': 'area',
                'd10': 'formation',
                'd11': 'unita_tipo',
                'd12': 'interpretation'
            }

            edge_key_map = {
                'd15': 'label',
                'd16': 'relationship',
                'd17': 'certainty',
                'd18': 'url',
                'd19': 'description'
            }

            # Extract nodes from nested graph
            for node in list(nested_graph):
                if 'node' not in node.tag:
                    continue

                node_id = node.get('id', '')
                # Remove table_node_group:: prefix if present
                clean_id = node_id.replace('table_node_group::', '')

                # Extract data attributes
                node_attrs = {}
                for data in list(node):
                    if 'data' not in data.tag:
                        continue

                    key = data.get('key', '')
                    value = data.text or ''

                    if key in node_key_map:
                        node_attrs[node_key_map[key]] = value

                # Add node to graph
                self.graph.add_node(clean_id, **node_attrs)

            # Extract edges from main graph (edges are at graph G level, not nested)
            if main_graph is not None:
                for edge in list(main_graph):
                    if 'edge' not in edge.tag:
                        continue

                    source = edge.get('source', '').replace('table_node_group::', '')
                    target = edge.get('target', '').replace('table_node_group::', '')

                    # Extract edge attributes
                    edge_attrs = {}
                    for data in list(edge):
                        if 'data' not in data.tag:
                            continue

                        key = data.get('key', '')
                        value = data.text or ''

                        if key in edge_key_map:
                            edge_attrs[edge_key_map[key]] = value

                    # Add edge to graph
                    if source and target:
                        self.graph.add_edge(source, target, **edge_attrs)

            self.graphml_path = filepath
            logger.info(
                f"Loaded GraphML (yFiles): {len(self.graph.nodes())} nodes, "
                f"{len(self.graph.edges())} edges"
            )
            return True

        except Exception as e:
            logger.error(f"Error parsing yFiles GraphML: {e}", exc_info=True)
            return False

    def parse_node(self, node_id: str) -> Dict[str, Any]:
        """
        Parse single GraphML node

        Args:
            node_id: Node ID in GraphML

        Returns:
            Dict with node data
        """
        if not self.graph:
            raise ValueError("No GraphML loaded")

        if node_id not in self.graph.nodes():
            raise ValueError(f"Node {node_id} not found in GraphML")

        node_data = self.graph.nodes[node_id]

        # Extract basic attributes
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
                "x": float(node_data.get("x", 0)),
                "y": float(node_data.get("y", 0)),
            }

        # Parse US ID from label (e.g., "US 5" -> 5)
        node_info["us_id"] = self._extract_us_id(node_info["label"])

        return node_info

    def parse_all_nodes(self) -> List[Dict[str, Any]]:
        """
        Parse all GraphML nodes

        Returns:
            List of node dicts
        """
        if not self.graph:
            raise ValueError("No GraphML loaded")

        return [self.parse_node(node_id) for node_id in self.graph.nodes()]

    def parse_edges(self) -> List[Dict[str, Any]]:
        """
        Parse all GraphML edges (relationships)

        Returns:
            List of edge dicts
        """
        if not self.graph:
            raise ValueError("No GraphML loaded")

        edges = []
        for source, target in self.graph.edges():
            edge_data = self.graph.edges[source, target]

            edge_info = {
                "source": source,
                "target": target,
                "relationship": edge_data.get("relationship", ""),
                "certainty": edge_data.get("certainty", "certain"),
            }

            # Extract US IDs from source/target
            source_label = self.graph.nodes[source].get("label", source)
            target_label = self.graph.nodes[target].get("label", target)
            edge_info["source_us_id"] = self._extract_us_id(source_label)
            edge_info["target_us_id"] = self._extract_us_id(target_label)

            edges.append(edge_info)

        return edges

    def get_relationships_for_us(self, us_id: int) -> Dict[str, List[int]]:
        """
        Get all stratigraphic relationships for a US

        Args:
            us_id: US ID

        Returns:
            Dict with relationship types as keys, US ID lists as values
        """
        if not self.graph:
            raise ValueError("No GraphML loaded")

        relationships = {
            "covers": [],
            "covered_by": [],
            "fills": [],
            "filled_by": [],
            "cuts": [],
            "cut_by": [],
            "equals": [],
            "contemporaneous_with": [],
        }

        # Find node for this US
        us_node = self._find_node_by_us_id(us_id)
        if not us_node:
            return relationships

        # Parse outgoing edges (this US → other US)
        for _, target in self.graph.out_edges(us_node):
            edge_data = self.graph.edges[us_node, target]
            relationship = edge_data.get("relationship", "").lower()

            target_label = self.graph.nodes[target].get("label", "")
            target_us_id = self._extract_us_id(target_label)

            if target_us_id and relationship in relationships:
                relationships[relationship].append(target_us_id)

        # Parse incoming edges (other US → this US)
        for source, _ in self.graph.in_edges(us_node):
            edge_data = self.graph.edges[source, us_node]
            relationship = edge_data.get("relationship", "").lower()

            source_label = self.graph.nodes[source].get("label", "")
            source_us_id = self._extract_us_id(source_label)

            # Infer inverse relationship
            inverse_rel = self._get_inverse_relationship(relationship)

            if source_us_id and inverse_rel in relationships:
                relationships[inverse_rel].append(source_us_id)

        return relationships

    def get_us_data_with_graphml(self, us_id: int) -> Dict[str, Any]:
        """
        Get complete US data combining database + GraphML

        Args:
            us_id: US ID

        Returns:
            Complete US data dict
        """
        # Query database for US record
        # Note: US.us is the US number field (e.g., "1001"), not id_us (primary key)
        us_record = self.db_session.query(US).filter(US.us == str(us_id)).first()

        if not us_record:
            logger.warning(f"US {us_id} not found in database")
            return {"error": f"US {us_id} not found"}

        # Get GraphML node data
        us_node = self._find_node_by_us_id(us_id)
        graphml_data = {}
        if us_node:
            graphml_data = self.parse_node(us_node)

        # Get relationships
        relationships = self.get_relationships_for_us(us_id)

        # Get periodization data
        period_data = self._get_period_data(us_record)

        # Combine all data
        complete_data = {
            "us_id": us_id,
            "stratigraphic_data": self._extract_us_fields(us_record),
            "graphml_data": graphml_data,
            "relationships": relationships,
            "chronology": period_data,
        }

        return complete_data

    def get_all_us_with_graphml(
        self, site_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all US data with GraphML metadata

        Args:
            site_id: Optional site ID filter

        Returns:
            List of complete US data dicts
        """
        # Query all US
        query = self.db_session.query(US)
        if site_id:
            # Note: US table doesn't have site_id FK directly
            # Would need to filter by sito name if needed
            pass

        us_records = query.all()

        # Get complete data for each US
        complete_data = []
        for us_record in us_records:
            data = self.get_us_data_with_graphml(us_record.id_us)
            if "error" not in data:
                complete_data.append(data)

        return complete_data

    def get_topological_order(self) -> List[int]:
        """
        Get US IDs in topological order (bottom to top)

        Returns:
            List of US IDs ordered stratigraphically
        """
        if not self.graph:
            raise ValueError("No GraphML loaded")

        try:
            # Topological sort
            topo_order = list(nx.topological_sort(self.graph))

            # Extract US IDs
            us_ids = []
            for node in topo_order:
                label = self.graph.nodes[node].get("label", "")
                us_id = self._extract_us_id(label)
                if us_id:
                    us_ids.append(us_id)

            return us_ids

        except nx.NetworkXError as e:
            logger.error(f"Error computing topological order: {e}")
            # Graph has cycles - return nodes in arbitrary order
            us_ids = []
            for node in self.graph.nodes():
                label = self.graph.nodes[node].get("label", "")
                us_id = self._extract_us_id(label)
                if us_id:
                    us_ids.append(us_id)
            return us_ids

    def get_depth_levels(self) -> Dict[int, int]:
        """
        Get depth level for each US (0 = oldest/bottom)

        Returns:
            Dict mapping US ID → depth level
        """
        topo_order = self.get_topological_order()

        # Assign depth levels
        depth_levels = {}
        for idx, us_id in enumerate(topo_order):
            depth_levels[us_id] = idx

        return depth_levels

    # ========================================================================
    # Private Helper Methods
    # ========================================================================

    def _extract_us_id(self, label: str) -> Optional[int]:
        """Extract US ID from label like 'US 5'"""
        try:
            if label.upper().startswith("US "):
                return int(label.split()[1])
        except (IndexError, ValueError):
            pass
        return None

    def _find_node_by_us_id(self, us_id: int) -> Optional[str]:
        """Find GraphML node ID for given US ID"""
        if not self.graph:
            return None

        for node_id in self.graph.nodes():
            label = self.graph.nodes[node_id].get("label", "")
            if self._extract_us_id(label) == us_id:
                return node_id

        return None

    def _get_inverse_relationship(self, relationship: str) -> str:
        """Get inverse stratigraphic relationship"""
        inverses = {
            "covers": "covered_by",
            "covered_by": "covers",
            "fills": "filled_by",
            "filled_by": "fills",
            "cuts": "cut_by",
            "cut_by": "cuts",
            "equals": "equals",
            "contemporaneous_with": "contemporaneous_with",
        }
        return inverses.get(relationship, relationship)

    def _extract_us_fields(self, us_record: US) -> Dict[str, Any]:
        """Extract all relevant fields from US database record"""
        return {
            "sito": us_record.sito,
            "area": us_record.area,
            "us": us_record.us,
            "definizione_stratigrafica": us_record.d_stratigrafica,
            "descrizione": us_record.descrizione,
            "interpretazione": us_record.interpretazione,
            "formazione": us_record.formazione,
            "consistenza": us_record.consistenza,
            "colore": us_record.colore,
            "inclusi": us_record.inclusi,
            "unita_tipo": us_record.unita_tipo,
            "settore": us_record.settore,
            "quad_par": us_record.quad_par,
            "ambient": us_record.ambient,
            "quota_relativa": float(us_record.quota_relativa) if us_record.quota_relativa else None,
            "quota_abs": float(us_record.quota_abs) if us_record.quota_abs else None,
            "lunghezza_max": (
                float(us_record.lunghezza_max) if us_record.lunghezza_max else None
            ),
            "altezza_max": (
                float(us_record.altezza_max) if us_record.altezza_max else None
            ),
            "altezza_min": (
                float(us_record.altezza_min) if us_record.altezza_min else None
            ),
            "profondita_max": (
                float(us_record.profondita_max) if us_record.profondita_max else None
            ),
            "profondita_min": (
                float(us_record.profondita_min) if us_record.profondita_min else None
            ),
            "larghezza_media": (
                float(us_record.larghezza_media)
                if us_record.larghezza_media
                else None
            ),
        }

    def _get_period_data(self, us_record: US) -> Dict[str, Any]:
        """Get periodization data for US"""
        # Query periodizzazione table
        period_record = (
            self.db_session.query(Periodizzazione)
            .filter(
                Periodizzazione.sito == us_record.sito,
                Periodizzazione.area == us_record.area,
                Periodizzazione.us == us_record.us,
            )
            .first()
        )

        if not period_record:
            return {
                "period_name": "Unknown",
                "period_code": "UNK",
                "dating_start": None,
                "dating_end": None,
            }

        # Query datazioni table for period details
        period_detail = None
        if period_record.periodo:
            period_detail = (
                self.db_session.query(Datazione)
                .filter(Datazione.sito == us_record.sito)
                .filter(Datazione.periodo.ilike(f"%{period_record.periodo}%"))
                .first()
            )

        period_data = {
            "period_id": period_record.id if period_record else None,
            "period_name": period_record.periodo if period_record else "Unknown",
            "period_code": (
                period_record.periodo[:3].upper() if period_record.periodo else "UNK"
            ),
            "fase": period_record.fase if period_record else None,
            "datazione_estesa": (
                period_record.datazione_estesa if period_record else None
            ),
            "cron_iniziale": period_record.cron_iniziale if period_record else None,
            "cron_finale": period_record.cron_finale if period_record else None,
            "affidabilita": period_record.affidabilita if period_record else None,
            "motivazione": period_record.motivazione if period_record else None,
        }

        # Add dating range if available from datazioni table
        if period_detail:
            period_data["dating_start"] = period_detail.cron_iniz
            period_data["dating_end"] = period_detail.cron_fin

        return period_data


# ============================================================================
# Helper Functions
# ============================================================================


def parse_graphml_file(filepath: str, db_session) -> GraphMLParser:
    """
    Quick helper to parse GraphML file

    Args:
        filepath: Path to GraphML file
        db_session: Database session

    Returns:
        Loaded GraphMLParser instance
    """
    parser = GraphMLParser(db_session)
    if not parser.load_graphml(filepath):
        raise ValueError(f"Failed to load GraphML: {filepath}")
    return parser
