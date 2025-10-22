"""
S3D Converter - Convert PyArchInit data to s3dgraphy graphs
"""

import os
import sys
import json
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    import s3dgraphy
    import networkx as nx
    S3D_AVAILABLE = True
except ImportError:
    S3D_AVAILABLE = False
    print("[S3D] Warning: s3dgraphy not installed. Run: pip install s3dgraphy")


class S3DConverter:
    """Convert PyArchInit stratigraphic data to s3dgraphy format"""

    def __init__(self):
        """Initialize S3D converter"""
        if not S3D_AVAILABLE:
            raise ImportError("s3dgraphy is not installed. Install with: pip install s3dgraphy")

    def create_graph_from_us(self, us_list: List[Dict[str, Any]],
                            site_name: str = "Archaeological Site") -> 's3dgraphy.Graph':
        """
        Create s3dgraphy graph from PyArchInit US data

        Args:
            us_list: List of US dictionaries from PyArchInit
            site_name: Name of the archaeological site

        Returns:
            s3dgraphy Graph object
        """
        # Create graph with required graph_id parameter
        graph_id = f"{site_name}_stratigraphy"
        graph_name = f"{site_name} Stratigraphy"
        graph_description = f"Stratigraphic graph exported from PyArchInit-Mini on {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        graph = s3dgraphy.Graph(
            graph_id=graph_id,
            name=graph_name,
            description=graph_description
        )

        # Add custom metadata
        graph.metadata = {
            "name": graph_name,
            "created": datetime.now().isoformat(),
            "source": "PyArchInit-Mini",
            "site": site_name
        }

        # Map US IDs to node IDs (strings)
        us_node_ids = {}

        # Add all US as nodes
        for us in us_list:
            us_number = str(us.get('us', ''))
            sito = us.get('sito', site_name)
            area = us.get('area', '')

            # Create unique node ID
            node_id = f"{sito}_{us_number}"
            if area:
                node_id = f"{sito}_{area}_{us_number}"

            # Node name and description
            node_name = f"US {us_number}"
            node_description = us.get('d_stratigrafica', '') or us.get('d_interpretativa', '') or f"Stratigraphic Unit {us_number}"

            # Create s3dgraphy Node
            node = s3dgraphy.Node(node_id, node_name, node_description)

            # Add attributes to node
            node.add_attribute("us_number", us_number)
            node.add_attribute("site", sito)
            if area:
                node.add_attribute("area", area)

            # Add all other US properties as attributes
            if us.get('unita_tipo'):
                node.add_attribute("unit_type", str(us.get('unita_tipo')))
            if us.get('d_stratigrafica'):
                node.add_attribute("description_strat", str(us.get('d_stratigrafica')))
            if us.get('d_interpretativa'):
                node.add_attribute("description_interp", str(us.get('d_interpretativa')))
            if us.get('interpretazione'):
                node.add_attribute("interpretation", str(us.get('interpretazione')))
            if us.get('anno_scavo'):
                node.add_attribute("excavation_year", str(us.get('anno_scavo')))
            if us.get('scavato'):
                node.add_attribute("excavated", str(us.get('scavato')))
            if us.get('periodo_iniziale'):
                node.add_attribute("period", str(us.get('periodo_iniziale')))
            if us.get('fase_iniziale'):
                node.add_attribute("phase", str(us.get('fase_iniziale')))

            # Add node to graph
            graph.add_node(node)
            us_node_ids[node_id] = node_id

        # Add stratigraphic relationships as edges
        edge_counter = 0

        # Relationship type mapping (Italian → English)
        relationship_mapping = {
            'copre': 'COVERS',
            'coperto da': 'COVERED_BY',
            'coperta da': 'COVERED_BY',
            'taglia': 'CUTS',
            'tagliato da': 'CUT_BY',
            'tagliata da': 'CUT_BY',
            'riempie': 'FILLS',
            'riempito da': 'FILLED_BY',
            'riempita da': 'FILLED_BY',
            'si lega a': 'BONDS_TO',
            'si appoggia a': 'LEANS_AGAINST',
            'gli si appoggia': 'LEANED_AGAINST_BY',
            'uguale a': 'EQUAL_TO',
            'si appoggia': 'LEANS_AGAINST',
        }

        for us in us_list:
            us_number = str(us.get('us', ''))
            sito = us.get('sito', site_name)
            area = us.get('area', '')

            # Source node ID
            source_id = f"{sito}_{us_number}"
            if area:
                source_id = f"{sito}_{area}_{us_number}"

            if source_id not in us_node_ids:
                continue

            # Get the "rapporti" field which contains all relationships as text
            rapporti = us.get('rapporti', '')
            if not rapporti or not str(rapporti).strip():
                continue

            # Parse rapporti string: "copre 1002, taglia 1005; coperto da 1001"
            # Split by both comma and semicolon
            rapporti_str = str(rapporti)
            relations = [r.strip() for r in rapporti_str.replace(';', ',').split(',')]

            for relation in relations:
                if not relation:
                    continue

                # Try to parse relationship: "verb US_number"
                # Examples: "copre 1002", "Si appoggia a 1001", "coperto da 1003"
                relation_lower = relation.lower().strip()

                # Find matching relationship type
                edge_type = None
                target_us = None

                for italian_rel, english_rel in relationship_mapping.items():
                    if relation_lower.startswith(italian_rel):
                        edge_type = english_rel
                        # Extract target US number (everything after the relationship verb)
                        target_us_str = relation_lower[len(italian_rel):].strip()
                        # Remove any non-digit characters from the start
                        target_us = ''.join(c for c in target_us_str if c.isdigit() or c in ['.', '-'])
                        if target_us:
                            target_us = target_us.split()[0] if ' ' in target_us else target_us
                        break

                if not edge_type or not target_us:
                    # Couldn't parse this relation, skip it
                    continue

                # Target node ID
                target_id = f"{sito}_{target_us}"
                if area:
                    target_id = f"{sito}_{area}_{target_us}"

                if target_id in us_node_ids:
                    # Create unique edge ID
                    edge_counter += 1
                    edge_id = f"edge_{edge_counter}_{edge_type}_{source_id}_to_{target_id}"

                    # s3dgraphy uses "is_before" for chronological sequence
                    # We store the specific relationship type as attribute
                    s3d_edge_type = "is_before" if edge_type in ['COVERS', 'CUTS', 'FILLS'] else "generic_connection"

                    # Create edge
                    edge = graph.add_edge(edge_id, source_id, target_id, s3d_edge_type)

                    # Add relationship type as attribute for detailed semantics
                    edge.attributes['stratigraphic_relation'] = edge_type
                    edge.attributes['relation_label'] = edge_type.replace('_', ' ').title()

        return graph

    def _convert_to_networkx(self, graph: 's3dgraphy.Graph') -> 'nx.DiGraph':
        """
        Convert s3dgraphy Graph to NetworkX DiGraph for export

        Args:
            graph: s3dgraphy Graph object

        Returns:
            NetworkX DiGraph
        """
        nx_graph = nx.DiGraph()

        # Add graph-level metadata
        nx_graph.graph['name'] = graph.name
        nx_graph.graph['description'] = graph.description
        nx_graph.graph['graph_id'] = graph.graph_id

        # Add nodes with all their attributes
        for node in graph.nodes:
            node_attrs = {
                'name': node.name,
                'description': node.description,
                'node_type': node.node_type if hasattr(node, 'node_type') else 'Node',
            }
            # Add custom attributes
            if hasattr(node, 'attributes') and node.attributes:
                node_attrs.update(node.attributes)

            nx_graph.add_node(node.node_id, **node_attrs)

        # Add edges with their attributes
        for edge in graph.edges:
            edge_attrs = {
                'edge_id': edge.edge_id,
                'edge_type': edge.edge_type,
                'label': edge.label if hasattr(edge, 'label') else edge.edge_type,
            }
            # Add custom edge attributes (like stratigraphic_relation)
            if hasattr(edge, 'attributes') and edge.attributes:
                edge_attrs.update(edge.attributes)

            nx_graph.add_edge(edge.edge_source, edge.edge_target, **edge_attrs)

        return nx_graph

    def export_to_graphml(self, graph: 's3dgraphy.Graph',
                         output_path: str) -> str:
        """
        Export s3dgraphy graph to GraphML format with yEd compatible labels

        Args:
            graph: s3dgraphy Graph object
            output_path: Path to output GraphML file

        Returns:
            Path to the generated GraphML file
        """
        # Convert to NetworkX graph
        nx_graph = self._convert_to_networkx(graph)

        # Add yEd-specific node labels
        for node_id, node_data in nx_graph.nodes(data=True):
            # Create label from us_number or name
            label_text = node_data.get('us_number', node_data.get('name', node_id))
            node_data['label'] = f"US {label_text}" if node_data.get('us_number') else label_text

        # Add yEd-specific edge labels
        for source, target, edge_data in nx_graph.edges(data=True):
            if 'relation_label' in edge_data:
                edge_data['label'] = edge_data['relation_label']

        # Export to GraphML using NetworkX
        nx.write_graphml(nx_graph, output_path, encoding='utf-8', prettyprint=True)

        # Post-process to add yEd formatting
        self._add_yed_formatting(output_path, graph)

        return output_path

    def _add_yed_formatting(self, graphml_path: str, graph: 's3dgraphy.Graph'):
        """Add yEd-specific formatting to GraphML file"""
        import xml.etree.ElementTree as ET

        # Parse GraphML
        ET.register_namespace('', 'http://graphml.graphdrawing.org/xmlns')
        ET.register_namespace('y', 'http://www.yworks.com/xml/graphml')
        ET.register_namespace('yed', 'http://www.yworks.com/xml/yed/3')

        tree = ET.parse(graphml_path)
        root = tree.getroot()

        ns = {
            'g': 'http://graphml.graphdrawing.org/xmlns',
            'y': 'http://www.yworks.com/xml/graphml'
        }

        # Find all nodes and add yEd NodeLabel with text
        for node in root.findall('.//g:node', ns):
            node_id = node.get('id')

            # Find the label data element
            label_elem = node.find('.//g:data[@key="d17"]', ns)  # name field
            us_number_elem = node.find('.//g:data[@key="d15"]', ns)  # us_number field

            if us_number_elem is not None and us_number_elem.text:
                label_text = f"US {us_number_elem.text.strip()}"
            elif label_elem is not None and label_elem.text:
                label_text = label_elem.text.strip()
            else:
                continue

            # Find yEd graphics element
            graphics = node.find('.//y:ShapeNode/y:NodeLabel', ns)
            if graphics is not None:
                graphics.set('hasText', 'true')
                graphics.text = label_text

        # Find all edges and add yEd EdgeLabel with text
        for edge in root.findall('.//g:edge', ns):
            # Find the relation_label data element
            label_elem = edge.find('.//g:data[@key="d22"]', ns)  # relation_label field

            if label_elem is not None and label_elem.text:
                label_text = label_elem.text.strip()

                # Find or create yEd graphics element
                graphics = edge.find('.//y:PolyLineEdge', ns)
                if graphics is not None:
                    # Add EdgeLabel if doesn't exist
                    edge_label = graphics.find('y:EdgeLabel', ns)
                    if edge_label is None:
                        edge_label = ET.SubElement(graphics, '{http://www.yworks.com/xml/graphml}EdgeLabel')
                    edge_label.text = label_text

        # Write back
        tree.write(graphml_path, encoding='utf-8', xml_declaration=True)

    def export_to_json(self, graph: 's3dgraphy.Graph',
                      output_path: str) -> str:
        """
        Export s3dgraphy graph to JSON format using NetworkX node-link format

        Args:
            graph: s3dgraphy Graph object
            output_path: Path to output JSON file

        Returns:
            Path to the generated JSON file
        """
        # Convert to NetworkX graph
        nx_graph = self._convert_to_networkx(graph)

        # Export to JSON using NetworkX node-link format
        json_data = nx.node_link_data(nx_graph, edges='edges')

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        return output_path

    def get_graph_statistics(self, graph: 's3dgraphy.Graph') -> Dict[str, Any]:
        """
        Get statistics about the stratigraphic graph

        Args:
            graph: s3dgraphy Graph object

        Returns:
            Dictionary with graph statistics
        """
        stats = {
            "total_nodes": len(graph.nodes),
            "total_edges": len(graph.edges),
            "node_types": {},
            "edge_types": {},
            "metadata": graph.metadata if hasattr(graph, 'metadata') else {}
        }

        # Count nodes by type
        for node in graph.nodes:
            node_type = getattr(node, 'node_type', 'unknown')
            stats["node_types"][node_type] = stats["node_types"].get(node_type, 0) + 1

        # Count edges by type
        for edge in graph.edges:
            edge_type = getattr(edge, 'edge_type', 'unknown')
            stats["edge_types"][edge_type] = stats["edge_types"].get(edge_type, 0) + 1

        return stats
