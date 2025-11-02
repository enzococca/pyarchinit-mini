"""
Proxy Generator

Generates proxy metadata for Blender 3D objects from stratigraphic data.
Combines GraphML, US data, and periodization to create complete proxy definitions.
"""

import logging
import math
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
import json

from .graphml_parser import GraphMLParser


logger = logging.getLogger(__name__)


# ============================================================================
# Period Color Mapping
# ============================================================================

PERIOD_COLORS = {
    "Paleolithic": (0.6, 0.5, 0.4, 1.0),  # Grigio-bruno
    "Neolithic": (0.7, 0.6, 0.3, 1.0),  # Giallo-bruno
    "Copper Age": (0.85, 0.55, 0.3, 1.0),  # Rame
    "Bronze Age": (0.8, 0.6, 0.4, 1.0),  # Arancio-bruno
    "Iron Age": (0.5, 0.4, 0.3, 1.0),  # Bruno scuro
    "Archaic": (0.7, 0.5, 0.4, 1.0),  # Bruno-rossastro
    "Classical": (0.9, 0.8, 0.6, 1.0),  # Giallo chiaro
    "Hellenistic": (0.7, 0.7, 0.8, 1.0),  # Grigio-azzurro
    "Roman": (0.8, 0.2, 0.2, 1.0),  # Rosso mattone
    "Late Roman": (0.7, 0.3, 0.3, 1.0),  # Rosso scuro
    "Byzantine": (0.6, 0.4, 0.6, 1.0),  # Viola
    "Medieval": (0.4, 0.4, 0.5, 1.0),  # Grigio
    "Renaissance": (0.8, 0.7, 0.5, 1.0),  # Beige dorato
    "Modern": (0.3, 0.3, 0.3, 1.0),  # Grigio scuro
    "Unknown": (0.5, 0.5, 0.5, 0.5),  # Grigio trasparente
}


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class ProxyMetadata:
    """Complete proxy metadata for Blender"""

    # Identification
    proxy_id: str
    us_id: int
    graphml_node_id: str
    site_id: Optional[int]
    build_session_id: str

    # Stratigraphic data
    stratigraphic_data: Dict[str, Any]

    # Chronology
    chronology: Dict[str, Any]

    # Relationships
    relationships: Dict[str, List[int]]

    # Blender properties
    blender_properties: Dict[str, Any]

    # Visualization state
    visualization: Dict[str, Any]

    # Media references
    media: List[Dict[str, Any]]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict"""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


class ProxyGenerator:
    """
    Generates proxy metadata for Blender 3D visualization

    Takes stratigraphic data from GraphML + database and generates
    complete proxy definitions with positioning, materials, and metadata.
    """

    def __init__(
        self,
        graphml_parser: GraphMLParser,
        positioning: str = "graphml",
        layer_spacing: float = 0.5,
        grid_spacing: float = 3.0,
        auto_color: bool = True,
        auto_material: bool = True,
    ):
        """
        Initialize proxy generator

        Args:
            graphml_parser: GraphMLParser instance
            positioning: Positioning algorithm ("graphml", "grid", "force_directed")
            layer_spacing: Z-axis spacing between layers (Blender units)
            grid_spacing: X-Y grid spacing (Blender units)
            auto_color: Auto-assign colors based on periods
            auto_material: Auto-assign materials based on formation
        """
        self.parser = graphml_parser
        self.positioning = positioning
        self.layer_spacing = layer_spacing
        self.grid_spacing = grid_spacing
        self.auto_color = auto_color
        self.auto_material = auto_material

    def generate_proxy(
        self, us_id: int, build_session_id: str
    ) -> Optional[ProxyMetadata]:
        """
        Generate complete proxy metadata for a single US

        Args:
            us_id: US ID
            build_session_id: Build session UUID

        Returns:
            ProxyMetadata or None if US not found
        """
        # Get complete US data from parser
        us_data = self.parser.get_us_data_with_graphml(us_id)

        if "error" in us_data:
            logger.warning(f"Cannot generate proxy for US {us_id}: {us_data['error']}")
            return None

        # Extract components
        stratigraphic_data = us_data["stratigraphic_data"]
        graphml_data = us_data.get("graphml_data", {})
        relationships = us_data["relationships"]
        chronology = us_data["chronology"]

        # Calculate 3D properties
        location = self._calculate_location(us_id, graphml_data)
        scale = self._calculate_scale(stratigraphic_data)
        rotation = (0.0, 0.0, 0.0)

        # Get material and color
        color = self._get_period_color(chronology["period_name"])
        material_name = self._get_material_name(
            chronology["period_name"], stratigraphic_data.get("formazione", "")
        )

        # Create proxy metadata
        proxy = ProxyMetadata(
            proxy_id=f"proxy_us_{us_id}",
            us_id=us_id,
            graphml_node_id=graphml_data.get("id", f"n{us_id}"),
            site_id=None,  # TODO: Extract from stratigraphic_data
            build_session_id=build_session_id,
            stratigraphic_data=stratigraphic_data,
            chronology=chronology,
            relationships=relationships,
            blender_properties={
                "object_name": f"Proxy_US_{us_id}",
                "object_type": "MESH",
                "geometry": "CUBE",
                "location": {"x": location[0], "y": location[1], "z": location[2]},
                "rotation": {"x": rotation[0], "y": rotation[1], "z": rotation[2]},
                "scale": {"x": scale[0], "y": scale[1], "z": scale[2]},
                "material": {
                    "name": material_name,
                    "base_color": list(color),
                    "roughness": 0.7,
                    "metallic": 0.0,
                    "alpha": 1.0,
                },
                "layer": chronology["period_code"].lower(),
                "collection": f"Site_Stratigraphy",
                "parent": None,
            },
            visualization={
                "visible": True,
                "opacity": 1.0,
                "highlight": False,
                "selected": False,
                "color_override": None,
                "wireframe": False,
                "bounding_box": False,
                "label_visible": True,
                "label_text": f"US {us_id} - {chronology['period_name']}",
            },
            media=[],  # TODO: Query media_table
        )

        return proxy

    def generate_all_proxies(
        self, us_ids: List[int], build_session_id: str
    ) -> List[ProxyMetadata]:
        """
        Generate proxies for multiple US

        Args:
            us_ids: List of US IDs
            build_session_id: Build session UUID

        Returns:
            List of ProxyMetadata
        """
        proxies = []

        for us_id in us_ids:
            proxy = self.generate_proxy(us_id, build_session_id)
            if proxy:
                proxies.append(proxy)

        logger.info(f"Generated {len(proxies)} proxies for {len(us_ids)} US")
        return proxies

    # ========================================================================
    # Positioning Algorithms
    # ========================================================================

    def _calculate_location(
        self, us_id: int, graphml_data: Dict[str, Any]
    ) -> Tuple[float, float, float]:
        """
        Calculate 3D location for proxy

        Returns:
            (x, y, z) tuple
        """
        # Z-axis: Based on stratigraphic depth
        z = self._calculate_z_position(us_id)

        # X-Y: Based on positioning algorithm
        if self.positioning == "graphml" and "position" in graphml_data:
            x, y = self._position_from_graphml(graphml_data["position"])
        elif self.positioning == "force_directed":
            x, y = self._position_force_directed(us_id)
        else:  # grid (default fallback)
            x, y = self._position_grid(us_id)

        return (x, y, z)

    def _calculate_z_position(self, us_id: int) -> float:
        """
        Calculate Z position based on stratigraphic depth

        Bottom (oldest) = 0, top (newest) = higher Z
        """
        depth_levels = self.parser.get_depth_levels()
        us_depth = depth_levels.get(us_id, 0)
        max_depth = max(depth_levels.values()) if depth_levels else 0

        # Invert: oldest at Z=0, newest at top
        z_position = (max_depth - us_depth) * self.layer_spacing

        return z_position

    def _position_from_graphml(
        self, graphml_position: Dict[str, float]
    ) -> Tuple[float, float]:
        """Position from GraphML coordinates (scaled)"""
        # Scale GraphML coordinates (typically in pixels) to Blender units
        # Using smaller scale factor for yFiles/yEd coordinates which can be very large
        x = graphml_position.get("x", 0) * 0.001  # 1000 px = 1 Blender unit
        y = graphml_position.get("y", 0) * 0.001
        return (x, y)

    def _position_grid(self, us_id: int) -> Tuple[float, float]:
        """Position on regular grid"""
        topo_order = self.parser.get_topological_order()

        try:
            index = topo_order.index(us_id)
        except ValueError:
            index = us_id  # Fallback

        # Ensure we have at least 1 column to avoid division by zero
        num_items = max(len(topo_order), 1)
        cols = max(math.ceil(math.sqrt(num_items)), 1)

        x = (index % cols) * self.grid_spacing
        y = (index // cols) * self.grid_spacing

        return (x, y)

    def _position_force_directed(self, us_id: int) -> Tuple[float, float]:
        """Position using NetworkX spring layout"""
        import networkx as nx

        if not self.parser.graph:
            return self._position_grid(us_id)

        # Calculate spring layout
        pos = nx.spring_layout(self.parser.graph, k=2.0, iterations=50)

        # Find node for this US
        us_node = self.parser._find_node_by_us_id(us_id)
        if not us_node or us_node not in pos:
            return self._position_grid(us_id)

        # Scale to Blender units
        x, y = pos[us_node]
        return (x * 10.0, y * 10.0)

    # ========================================================================
    # Scale Calculation
    # ========================================================================

    def _calculate_scale(
        self, stratigraphic_data: Dict[str, Any]
    ) -> Tuple[float, float, float]:
        """
        Calculate proxy scale from US dimensions

        Returns:
            (x, y, z) scale tuple
        """
        # Default scale
        default_scale = (1.0, 1.0, 0.3)

        # Extract dimensions
        lunghezza = stratigraphic_data.get("lunghezza_max")
        larghezza = stratigraphic_data.get("larghezza_media")
        altezza_max = stratigraphic_data.get("altezza_max")
        altezza_min = stratigraphic_data.get("altezza_min")

        if altezza_max is not None and altezza_min is not None:
            altezza = altezza_max - altezza_min
        else:
            altezza = None

        # Use dimensions if available
        if lunghezza and larghezza and altezza:
            scale_x = larghezza
            scale_y = lunghezza
            scale_z = max(altezza, 0.1)  # Min 0.1 to avoid flat proxies
            return (scale_x, scale_y, scale_z)

        return default_scale

    # ========================================================================
    # Material & Color
    # ========================================================================

    def _get_period_color(self, period_name: str) -> Tuple[float, float, float, float]:
        """Get color for period"""
        if not self.auto_color:
            return (0.5, 0.5, 0.5, 1.0)  # Gray

        # Try exact match
        if period_name in PERIOD_COLORS:
            return PERIOD_COLORS[period_name]

        # Try partial match
        for known_period, color in PERIOD_COLORS.items():
            if known_period.lower() in period_name.lower():
                return color

        # Default to Unknown
        return PERIOD_COLORS["Unknown"]

    def _get_material_name(self, period_name: str, formation: str) -> str:
        """Generate material name"""
        if not self.auto_material:
            return "Default_Stratigraphic"

        # Clean names
        period_clean = period_name.replace(" ", "_")
        formation_clean = formation.replace(" ", "_") if formation else "Generic"

        return f"{period_clean}_{formation_clean}"

    # ========================================================================
    # Export
    # ========================================================================

    def export_proxies_json(
        self, proxies: List[ProxyMetadata], output_path: str
    ) -> bool:
        """
        Export proxies to JSON file

        Args:
            proxies: List of ProxyMetadata
            output_path: Output file path

        Returns:
            True if successful
        """
        try:
            data = {
                "proxies": [proxy.to_dict() for proxy in proxies],
                "statistics": {
                    "total_proxies": len(proxies),
                    "periods": self._get_period_stats(proxies),
                    "relationships": self._get_relationship_stats(proxies),
                },
            }

            with open(output_path, "w") as f:
                json.dump(data, f, indent=2)

            logger.info(f"Exported {len(proxies)} proxies to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error exporting proxies: {e}", exc_info=True)
            return False

    def _get_period_stats(self, proxies: List[ProxyMetadata]) -> Dict[str, int]:
        """Get period statistics"""
        stats = {}
        for proxy in proxies:
            period = proxy.chronology.get("period_name", "Unknown")
            stats[period] = stats.get(period, 0) + 1
        return stats

    def _get_relationship_stats(self, proxies: List[ProxyMetadata]) -> Dict[str, int]:
        """Get relationship statistics"""
        stats = {}
        for proxy in proxies:
            for rel_type, us_list in proxy.relationships.items():
                if us_list:
                    stats[rel_type] = stats.get(rel_type, 0) + len(us_list)
        return stats


# ============================================================================
# Helper Functions
# ============================================================================


def generate_proxies_for_site(
    graphml_filepath: str,
    db_session,
    us_ids: List[int],
    build_session_id: str,
    positioning: str = "graphml",
) -> List[ProxyMetadata]:
    """
    Quick helper to generate proxies for a site

    Args:
        graphml_filepath: Path to GraphML file
        db_session: Database session
        us_ids: List of US IDs
        build_session_id: Build session UUID
        positioning: Positioning algorithm

    Returns:
        List of ProxyMetadata
    """
    # Load GraphML
    parser = GraphMLParser(db_session)
    if not parser.load_graphml(graphml_filepath):
        raise ValueError(f"Failed to load GraphML: {graphml_filepath}")

    # Generate proxies
    generator = ProxyGenerator(parser, positioning=positioning)
    proxies = generator.generate_all_proxies(us_ids, build_session_id)

    return proxies
