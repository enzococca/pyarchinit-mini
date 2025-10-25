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

    def export_to_json(self, graph: 's3dgraphy.Graph',
                      output_path: str) -> str:
        """
        Export s3dgraphy graph to JSON format v1.5 specification

        Args:
            graph: s3dgraphy Graph object
            output_path: Path to output JSON file

        Returns:
            Path to the generated JSON file
        """
        # Build s3Dgraphy v1.5 JSON structure
        json_data = {
            "version": "1.5",
            "context": {
                "absolute_time_Epochs": {}
            },
            "graphs": {}
        }

        # Extract unique periods/epochs from nodes
        epochs = {}
        epoch_counter = 1

        for node in graph.nodes:
            if hasattr(node, 'attributes') and 'period' in node.attributes:
                period_name = node.attributes['period']
                if period_name and period_name not in epochs:
                    epoch_id = f"epoch_{epoch_counter:02d}"
                    epochs[period_name] = {
                        "id": epoch_id,
                        "name": period_name,
                        "start": None,  # Can be enriched with actual dates
                        "end": None,
                        "color": self._generate_epoch_color(epoch_counter)
                    }
                    epoch_counter += 1

        # Add epochs to context
        for period_name, epoch_data in epochs.items():
            json_data["context"]["absolute_time_Epochs"][epoch_data["id"]] = {
                "name": epoch_data["name"],
                "start": epoch_data["start"],
                "end": epoch_data["end"],
                "color": epoch_data["color"]
            }

        # Build graph structure
        graph_data = {
            "id": graph.graph_id,
            "name": graph.name,
            "description": graph.description,
            "defaults": {
                "license": "CC-BY-NC-ND",
                "authors": [f"pyarchinit_export_{datetime.now().strftime('%Y%m%d')}"],
                "embargo_until": None
            },
            "nodes": {
                "authors": {},
                "stratigraphic": {
                    "US": {},
                    "USVs": {},
                    "SF": {}
                },
                "epochs": {},
                "groups": {},
                "properties": {},
                "documents": {},
                "extractors": {},
                "combiners": {},
                "links": {},
                "geo": {}
            },
            "edges": {
                "is_before": [],
                "has_same_time": [],
                "has_data_provenance": [],
                "has_author": [],
                "has_first_epoch": [],
                "survive_in_epoch": [],
                "is_in_activity": [],
                "has_property": [],
                "has_timebranch": [],
                "has_linked_resource": []
            }
        }

        # Organize nodes by category
        for node in graph.nodes:
            node_data = {
                "name": node.name,
                "description": node.description
            }

            # Add all custom attributes
            if hasattr(node, 'attributes') and node.attributes:
                for key, value in node.attributes.items():
                    if key not in ['name', 'description']:
                        node_data[key] = value

            # Categorize node by unit_type
            unit_type = node.attributes.get('unit_type', 'US') if hasattr(node, 'attributes') else 'US'

            # Map unit types to s3Dgraphy categories
            if unit_type in ['USVA', 'USVB', 'USVC', 'USD']:
                graph_data["nodes"]["stratigraphic"]["USVs"][node.node_id] = node_data
            elif unit_type in ['SF', 'VSF']:
                graph_data["nodes"]["stratigraphic"]["SF"][node.node_id] = node_data
            elif unit_type == 'DOC':
                graph_data["nodes"]["documents"][node.node_id] = node_data
            elif unit_type == 'Extractor':
                graph_data["nodes"]["extractors"][node.node_id] = node_data
            elif unit_type == 'Combiner':
                graph_data["nodes"]["combiners"][node.node_id] = node_data
            else:
                # Default to US category
                graph_data["nodes"]["stratigraphic"]["US"][node.node_id] = node_data

        # Organize edges by type
        for edge in graph.edges:
            edge_data = {
                "from": edge.edge_source,
                "to": edge.edge_target
            }

            # Add edge attributes
            if hasattr(edge, 'attributes') and edge.attributes:
                edge_data.update(edge.attributes)

            # Map edge types to s3Dgraphy categories
            edge_type = edge.edge_type if hasattr(edge, 'edge_type') else 'generic_connection'

            if edge_type == 'is_before' or edge_data.get('stratigraphic_relation') in ['COVERS', 'CUTS', 'FILLS']:
                graph_data["edges"]["is_before"].append(edge_data)
            elif edge_type == 'has_same_time' or edge_data.get('stratigraphic_relation') in ['EQUAL_TO', 'BONDS_TO']:
                graph_data["edges"]["has_same_time"].append(edge_data)
            else:
                # Add to generic connection or appropriate category
                if 'is_before' not in graph_data["edges"]:
                    graph_data["edges"]["is_before"] = []
                graph_data["edges"]["is_before"].append(edge_data)

        # Add graph to graphs collection
        json_data["graphs"][graph.graph_id] = graph_data

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        return output_path

    def _generate_epoch_color(self, epoch_number: int) -> str:
        """Generate color for epoch based on number"""
        colors = [
            "#FFD700",  # Gold
            "#FF6347",  # Tomato
            "#4169E1",  # Royal Blue
            "#32CD32",  # Lime Green
            "#FF1493",  # Deep Pink
            "#00CED1",  # Dark Turquoise
            "#FF8C00",  # Dark Orange
            "#9370DB",  # Medium Purple
            "#20B2AA",  # Light Sea Green
            "#DC143C",  # Crimson
        ]
        return colors[(epoch_number - 1) % len(colors)]

    def export_to_heriverse_json(self, graph: 's3dgraphy.Graph',
                                  output_path: str,
                                  site_name: str = "Archaeological Site",
                                  creator_id: str = None,
                                  resource_path: str = None) -> str:
        """
        Export s3dgraphy graph to Heriverse/ATON JSON format

        This format includes:
        - Full CouchDB/scene wrapper with metadata
        - environment, scenegraph, multigraph sections
        - Additional node categories: USVn, semantic_shapes, representation_models, panorama_models
        - Additional edge types: generic_connection, changed_from, contrasts_with

        Args:
            graph: s3dgraphy Graph object
            output_path: Path to output JSON file
            site_name: Name of the archaeological site
            creator_id: Creator user ID (default: generated)
            resource_path: Base URL for uploaded resources (default: placeholder)

        Returns:
            Path to the generated JSON file
        """
        import uuid

        # Generate UUIDs for scene
        scene_id = f"scene:{uuid.uuid4()}"
        if not creator_id:
            creator_id = f"user:{uuid.uuid4()}"
        if not resource_path:
            resource_path = f"https://server/uploads/{uuid.uuid4()}"

        # Extract unique periods/epochs from nodes
        epochs = {}
        epoch_counter = 1

        for node in graph.nodes:
            if hasattr(node, 'attributes') and 'period' in node.attributes:
                period_name = node.attributes['period']
                if period_name and period_name not in epochs:
                    epoch_id = f"epoch_{epoch_counter:02d}"
                    epochs[period_name] = {
                        "id": epoch_id,
                        "name": period_name,
                        "start": None,
                        "end": None,
                        "color": self._generate_epoch_color(epoch_counter)
                    }
                    epoch_counter += 1

        # Build context with absolute_time_Epochs
        context = {"absolute_time_Epochs": {}}
        for period_name, epoch_data in epochs.items():
            context["absolute_time_Epochs"][epoch_data["id"]] = {
                "name": epoch_data["name"],
                "start": epoch_data["start"],
                "end": epoch_data["end"],
                "color": epoch_data["color"]
            }

        # Build multigraph structure (s3Dgraphy v1.5 with Heriverse extensions)
        graph_data = {
            "id": graph.graph_id,
            "name": graph.name,
            "description": graph.description,
            "defaults": {
                "license": "CC-BY-NC-ND",
                "authors": [f"pyarchinit_heriverse_export_{datetime.now().strftime('%Y%m%d')}"],
                "embargo_until": None
            },
            "nodes": {
                "authors": {},
                "stratigraphic": {
                    "US": {},
                    "USVs": {},
                    "USVn": {},  # Heriverse: Virtual negative units
                    "SF": {}
                },
                "epochs": {},
                "groups": {},
                "properties": {},
                "documents": {},
                "extractors": {},
                "combiners": {},
                "links": {},
                "geo": {},
                "semantic_shapes": {},        # Heriverse: 3D proxy models (GLB)
                "representation_models": {},  # Heriverse: Full 3D models (GLTF)
                "panorama_models": {}         # Heriverse: Panoramic images
            },
            "edges": {
                "is_before": [],
                "has_same_time": [],
                "has_data_provenance": [],
                "has_author": [],
                "has_first_epoch": [],
                "survive_in_epoch": [],
                "is_in_activity": [],
                "has_property": [],
                "has_timebranch": [],
                "has_linked_resource": [],
                "generic_connection": [],  # Heriverse: Generic paradata connections
                "changed_from": [],        # Heriverse: Stratigraphic evolution
                "contrasts_with": []       # Heriverse: Conflicting interpretations
            }
        }

        # Organize nodes by category
        for node in graph.nodes:
            node_data = {
                "name": node.name,
                "description": node.description
            }

            # Add all custom attributes
            if hasattr(node, 'attributes') and node.attributes:
                for key, value in node.attributes.items():
                    if key not in ['name', 'description']:
                        node_data[key] = value

            # Categorize node by unit_type
            unit_type = node.attributes.get('unit_type', 'US') if hasattr(node, 'attributes') else 'US'

            # Map unit types to Heriverse categories
            if unit_type in ['USVA', 'USVB', 'USVC', 'USD']:
                graph_data["nodes"]["stratigraphic"]["USVs"][node.node_id] = node_data
            elif unit_type == 'USVn':
                # Heriverse: Virtual negative units (separate category)
                graph_data["nodes"]["stratigraphic"]["USVn"][node.node_id] = node_data
            elif unit_type in ['SF', 'VSF']:
                graph_data["nodes"]["stratigraphic"]["SF"][node.node_id] = node_data
            elif unit_type == 'DOC':
                graph_data["nodes"]["documents"][node.node_id] = node_data
            elif unit_type == 'Extractor':
                graph_data["nodes"]["extractors"][node.node_id] = node_data
            elif unit_type == 'Combiner':
                graph_data["nodes"]["combiners"][node.node_id] = node_data
            else:
                # Default to US category
                graph_data["nodes"]["stratigraphic"]["US"][node.node_id] = node_data

                # Heriverse: Auto-generate semantic_shape placeholder for each US
                # In production, these would link to actual 3D models
                shape_id = f"shape_{node.node_id}"
                graph_data["nodes"]["semantic_shapes"][shape_id] = {
                    "name": f"3D Model for {node.name}",
                    "description": f"Proxy 3D model",
                    "url": f"{resource_path}/models/{node.node_id}.glb",
                    "format": "glb",
                    "us_reference": node.node_id
                }

        # Organize edges by type
        for edge in graph.edges:
            edge_data = {
                "from": edge.edge_source,
                "to": edge.edge_target
            }

            # Add edge attributes
            if hasattr(edge, 'attributes') and edge.attributes:
                edge_data.update(edge.attributes)

            # Map edge types to Heriverse categories
            edge_type = edge.edge_type if hasattr(edge, 'edge_type') else 'generic_connection'
            strat_rel = edge_data.get('stratigraphic_relation', '')

            if edge_type == 'is_before' or strat_rel in ['COVERS', 'CUTS', 'FILLS']:
                graph_data["edges"]["is_before"].append(edge_data)
            elif edge_type == 'has_same_time' or strat_rel in ['EQUAL_TO', 'BONDS_TO']:
                graph_data["edges"]["has_same_time"].append(edge_data)
            elif edge_type == 'changed_from':
                graph_data["edges"]["changed_from"].append(edge_data)
            elif edge_type == 'contrasts_with':
                graph_data["edges"]["contrasts_with"].append(edge_data)
            else:
                # Generic connection for paradata
                graph_data["edges"]["generic_connection"].append(edge_data)

        # Build full Heriverse JSON structure with CouchDB/scene wrapper
        heriverse_data = {
            "_id": scene_id,
            "_rev": "1-" + uuid.uuid4().hex[:32],  # CouchDB revision format
            "type": "scene",
            "creator": creator_id,
            "resource_path": resource_path,
            "title": graph.name,
            "description": graph.description,
            "resource_json": {
                "title": graph.name,
                "environment": {
                    "mainpano": {
                        "url": "s"  # Placeholder for main panorama
                    },
                    "lightprobes": {
                        "auto": "true"
                    },
                    "mainlight": {
                        "direction": ["0.0", "0.0", "0.0"]
                    }
                },
                "viewpoints": {},
                "scenegraph": {
                    "nodes": {},
                    "edges": {
                        ".": []  # Root scenegraph edges
                    }
                },
                "multigraph": {
                    "version": "1.5",
                    "context": context,
                    "graphs": {
                        graph.graph_id: graph_data
                    }
                }
            },
            "wapp": "heriverse",
            "thumbnail": "",
            "tag": [],
            "categories": [],
            "visibility": "public",
            "created_at": datetime.now().strftime("%-m/%-d/%Y, %-I:%M:%S %p")
        }

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(heriverse_data, f, indent=2, ensure_ascii=False)

        return output_path

    def import_graphml_to_json(self, graphml_path: str, output_json_path: str,
                               site_name: str = "Archaeological Site") -> str:
        """
        Import PyArchInit GraphML and convert to s3Dgraphy JSON v1.5

        Args:
            graphml_path: Path to input GraphML file (PyArchInit native export)
            output_json_path: Path to output JSON file
            site_name: Name of the archaeological site

        Returns:
            Path to the generated JSON file
        """
        import xml.etree.ElementTree as ET

        # Parse GraphML
        tree = ET.parse(graphml_path)
        root = tree.getroot()

        ns = {'g': 'http://graphml.graphdrawing.org/xmlns'}

        # Extract nodes and edges from GraphML
        nodes_data = []
        edges_data = []

        # Find key definitions to map data fields
        keys = {}
        for key in root.findall('.//g:key', ns):
            key_id = key.get('id')
            key_name = key.get('attr.name')
            keys[key_id] = key_name

        # Extract nodes
        for node in root.findall('.//g:node', ns):
            node_id = node.get('id')
            node_dict = {'id': node_id}

            # Extract data fields
            for data in node.findall('g:data', ns):
                key_id = data.get('key')
                key_name = keys.get(key_id, key_id)
                node_dict[key_name] = data.text

            # Parse label to extract unit type and number (e.g., "US12" → type="US", number="12")
            label = node_dict.get('label', node_id)
            import re
            match = re.match(r'([A-Z]+)(\d+)', label)
            if match:
                node_dict['unit_type'] = match.group(1)
                node_dict['us_number'] = match.group(2)

            nodes_data.append(node_dict)

        # Extract edges
        for edge in root.findall('.//g:edge', ns):
            edge_dict = {
                'source': edge.get('source'),
                'target': edge.get('target')
            }

            # Extract edge data
            for data in edge.findall('g:data', ns):
                key_id = data.get('key')
                key_name = keys.get(key_id, key_id)
                edge_dict[key_name] = data.text

            edges_data.append(edge_dict)

        # Convert to s3dgraphy format
        graph_id = f"{site_name}_stratigraphy"
        graph_name = f"{site_name} Stratigraphy (from GraphML)"
        graph_description = f"Imported from GraphML on {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        # Build s3Dgraphy JSON v1.5 structure
        json_data = {
            "version": "1.5",
            "context": {
                "absolute_time_Epochs": {}
            },
            "graphs": {
                graph_id: {
                    "id": graph_id,
                    "name": graph_name,
                    "description": graph_description,
                    "defaults": {
                        "license": "CC-BY-NC-ND",
                        "authors": [f"graphml_import_{datetime.now().strftime('%Y%m%d')}"],
                        "embargo_until": None
                    },
                    "nodes": {
                        "authors": {},
                        "stratigraphic": {
                            "US": {},
                            "USVs": {},
                            "SF": {}
                        },
                        "epochs": {},
                        "groups": {},
                        "properties": {},
                        "documents": {},
                        "extractors": {},
                        "combiners": {},
                        "links": {},
                        "geo": {}
                    },
                    "edges": {
                        "is_before": [],
                        "has_same_time": [],
                        "has_data_provenance": [],
                        "has_author": [],
                        "has_first_epoch": [],
                        "survive_in_epoch": [],
                        "is_in_activity": [],
                        "has_property": [],
                        "has_timebranch": [],
                        "has_linked_resource": []
                    }
                }
            }
        }

        # Categorize nodes
        for node_data in nodes_data:
            node_id = node_data['id']
            unit_type = node_data.get('unit_type', 'US')

            # Remove internal fields
            clean_data = {k: v for k, v in node_data.items() if k not in ['id']}

            # Map to categories
            if unit_type in ['USVA', 'USVB', 'USVC', 'USD']:
                json_data["graphs"][graph_id]["nodes"]["stratigraphic"]["USVs"][node_id] = clean_data
            elif unit_type in ['SF', 'VSF']:
                json_data["graphs"][graph_id]["nodes"]["stratigraphic"]["SF"][node_id] = clean_data
            elif unit_type == 'DOC':
                json_data["graphs"][graph_id]["nodes"]["documents"][node_id] = clean_data
            elif unit_type == 'Extractor':
                json_data["graphs"][graph_id]["nodes"]["extractors"][node_id] = clean_data
            elif unit_type == 'Combiner':
                json_data["graphs"][graph_id]["nodes"]["combiners"][node_id] = clean_data
            else:
                json_data["graphs"][graph_id]["nodes"]["stratigraphic"]["US"][node_id] = clean_data

        # Categorize edges
        for edge_data in edges_data:
            edge_obj = {
                "from": edge_data['source'],
                "to": edge_data['target']
            }

            # Add other attributes
            for k, v in edge_data.items():
                if k not in ['source', 'target']:
                    edge_obj[k] = v

            # Determine edge type from label or attributes
            edge_label = edge_data.get('label', '').lower()

            if 'cover' in edge_label or 'cut' in edge_label or 'fill' in edge_label:
                json_data["graphs"][graph_id]["edges"]["is_before"].append(edge_obj)
            elif 'uguale' in edge_label or 'same' in edge_label or 'lega' in edge_label:
                json_data["graphs"][graph_id]["edges"]["has_same_time"].append(edge_obj)
            else:
                json_data["graphs"][graph_id]["edges"]["is_before"].append(edge_obj)

        # Write JSON
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        return output_json_path

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
