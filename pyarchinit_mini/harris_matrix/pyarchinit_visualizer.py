#!/usr/bin/env python3
"""
PyArchInit-style Harris Matrix visualizer using Graphviz
Based on the original PyArchInit plugin approach
"""

import os
import tempfile
import networkx as nx
from typing import Dict, List, Any, Optional, Tuple
from graphviz import Digraph

class PyArchInitMatrixVisualizer:
    """
    Harris Matrix visualizer that replicates PyArchInit plugin behavior
    Uses Graphviz with hierarchical orthogonal layout and period/area grouping
    """
    
    def __init__(self):
        self.default_settings = {
            'dpi': '300',  # Good resolution without excessive file size
            'rankdir': 'TB',
            'splines': 'ortho',
            'ranksep': '1.0',  # Optimized spacing between ranks
            'nodesep': '0.4',  # Optimized spacing between nodes
            'pad': '0.1',      # Minimal padding to maximize space usage
            'size': '40,40!',   # Force size to fill canvas (! forces exact size)
            'ratio': 'fill',   # Fill entire space instead of compress
            # Node styles
            'us_shape': 'box',
            'us_style': 'filled',
            'us_color': 'lightblue',
            'us_fillcolor': 'lightblue',
            'us_penwidth': '1',
            # Edge styles for different relationships
            'normal_edge_style': 'solid',
            'normal_edge_color': 'black',
            'normal_arrowhead': 'normal',
            'normal_arrowsize': '1',
            'normal_penwidth': '1',
            # Negative relationships (cuts)
            'negative_shape': 'diamond',
            'negative_color': 'red',
            'negative_fillcolor': 'pink',
            'negative_edge_style': 'dashed',
            'negative_edge_color': 'red',
            'negative_arrowhead': 'vee',
            # Contemporary relationships
            'contemp_shape': 'ellipse',
            'contemp_color': 'green',
            'contemp_fillcolor': 'lightgreen',
            'contemp_edge_style': 'dotted',
            'contemp_edge_color': 'green',
            'contemp_arrowhead': 'none',
            # Include legend
            'show_legend': True,
            'show_periods': True
        }
    
    def get_dot_source(self, graph: nx.DiGraph, grouping: str = 'period_area',
                      settings: Optional[Dict] = None) -> str:
        """
        Get DOT source for GraphML conversion

        Args:
            graph: NetworkX directed graph with US nodes and relationships
            grouping: 'period_area', 'period', 'area', 'none'
            settings: Optional style settings override

        Returns:
            DOT source code as string
        """
        # Merge settings
        current_settings = {**self.default_settings}
        if settings:
            current_settings.update(settings)

        # Create Graphviz Digraph
        G = self._create_digraph(graph, grouping, current_settings)

        # Return DOT source
        return G.source

    def create_matrix(self, graph: nx.DiGraph, grouping: str = 'period_area',
                     settings: Optional[Dict] = None, output_path: Optional[str] = None) -> str:
        """
        Create Harris Matrix using PyArchInit approach

        Args:
            graph: NetworkX directed graph with US nodes and relationships
            grouping: 'period_area', 'period', 'area', 'none'
            settings: Optional style settings override
            output_path: Optional output file path

        Returns:
            Path to generated file
        """

        # Merge settings
        current_settings = {**self.default_settings}
        if settings:
            current_settings.update(settings)

        # Create Graphviz Digraph
        G = self._create_digraph(graph, grouping, current_settings)
        
        # Generate output
        if output_path is None:
            output_path = tempfile.mktemp(suffix='.png')

        try:
            # Use standard PNG format (compatible with all Graphviz installations)
            G.render(output_path, format='png', cleanup=True)
            return output_path + '.png'
        except Exception as e:
            print(f"Error rendering matrix to PNG: {e}")
            # Fallback to saving DOT source
            dot_path = output_path.replace('.png', '.dot')
            with open(dot_path, 'w') as f:
                f.write(G.source)
            print(f"Saved DOT file instead: {dot_path}")
            return dot_path

    def _create_digraph(self, graph: nx.DiGraph, grouping: str, settings: Dict) -> Digraph:
        """
        Create Graphviz Digraph from NetworkX graph

        Args:
            graph: NetworkX directed graph with US nodes and relationships
            grouping: 'period_area', 'period', 'area', 'none'
            settings: Style settings

        Returns:
            Graphviz Digraph object
        """
        # Always use dot engine to preserve hierarchical structure and clusters
        # Even for large graphs - the optimization in get_matrix_statistics() already speeds up processing
        num_nodes = len(graph.nodes())
        engine = 'dot'

        if num_nodes > 500:
            print(f"ℹ️  Large graph ({num_nodes} nodes) - using optimized dot layout with hierarchical structure")

        # Create Graphviz Digraph
        G = Digraph(engine=engine, strict=False)

        # dot-specific attributes for hierarchical layout
        # For large graphs, use more compact spacing
        if num_nodes > 500:
            nodesep = "0.3"  # Compact spacing for large graphs
            ranksep = "0.5"  # Compact rank spacing
        else:
            nodesep = settings['nodesep']
            ranksep = settings['ranksep']

        # IMPORTANT: Graphviz dot with orthogonal splines requires xlabel instead of label
        # Error: "Warning: Orthogonal edges do not currently handle edge labels. Try using xlabels."
        # Solution: Track if we're using ortho splines to use xlabel instead of label for edges
        splines = settings['splines']
        use_xlabel = (splines == 'ortho')  # Use xlabel for edge labels with orthogonal splines

        if use_xlabel and grouping != 'none':
            print(f"ℹ️  Using xlabel for edge labels (required for orthogonal splines with clusters)")

        G.attr(
            rankdir=settings['rankdir'],
            viewport="",
            ratio=settings.get('ratio', 'auto'),
            compound='true',
            pad=settings['pad'],
            nodesep=nodesep,
            ranksep=ranksep,
            splines=splines,
            dpi=settings['dpi'],
            size=settings.get('size', '20,30'),  # Limit max size
            bgcolor='white'
        )

        # Categorize relationships like PyArchInit
        sequence_relations = []  # Normal stratigraphic relationships
        negative_relations = []  # Cuts relationships
        contemporary_relations = []  # Same/contemporary relationships

        us_rilevanti = set()  # Relevant US (those in relationships)

        # Extract and categorize relationships
        for source, target in graph.edges():
            edge_data = graph.get_edge_data(source, target)
            rel_type = edge_data.get('relationship', edge_data.get('type', 'sopra'))

            us_rilevanti.add(source)
            us_rilevanti.add(target)

            if rel_type in ['taglia', 'cuts', 'tagliato da', 'cut by']:
                negative_relations.append((source, target, rel_type))
            elif rel_type in ['uguale a', 'si lega a', 'same as', 'connected to']:
                contemporary_relations.append((source, target, rel_type))
            else:
                sequence_relations.append((source, target, rel_type))

        # Group nodes if requested
        if settings['show_periods'] and grouping != 'none':
            self._create_period_subgraphs(G, graph, grouping, us_rilevanti, settings)
        else:
            self._create_simple_nodes(G, graph, us_rilevanti, settings)

        # Add edges with proper styling (use xlabel for orthogonal splines)
        self._add_sequence_edges(G, graph, sequence_relations, settings, use_xlabel)
        self._add_negative_edges(G, graph, negative_relations, settings, use_xlabel)
        self._add_contemporary_edges(G, graph, contemporary_relations, settings, use_xlabel)

        # Add temporal ordering constraints (most recent above, oldest below)
        self._add_temporal_ordering(G, graph, us_rilevanti)

        # Add legend if requested
        if settings['show_legend']:
            self._add_legend(G, settings)

        return G

    def _create_period_subgraphs(self, G: Digraph, graph: nx.DiGraph, grouping: str, 
                               us_rilevanti: set, settings: Dict):
        """Create subgraphs grouped by periods and areas (PyArchInit style)"""
        
        # Group US by period, phase, and area
        groups = {}
        
        for node in us_rilevanti:
            if node not in graph.nodes:
                continue
                
            node_data = graph.nodes[node]
            
            # Extract grouping information
            periodo = node_data.get('period_initial', node_data.get('periodo_iniziale', 'Sconosciuto'))
            fase = node_data.get('phase_initial', node_data.get('fase_iniziale', '0'))
            area = node_data.get('area', 'A')
            datazione = node_data.get('datazione', periodo)
            sito = node_data.get('sito', 'Site')
            
            # Create group key based on grouping type
            if grouping == 'period_area':
                group_key = f"{sito}_{area}_{periodo}_{fase}"
            elif grouping == 'period':
                group_key = f"{sito}_{periodo}_{fase}"
            elif grouping == 'area':
                group_key = f"{sito}_{area}"
            else:
                group_key = "default"
            
            if group_key not in groups:
                groups[group_key] = {
                    'nodes': [],
                    'sito': sito,
                    'area': area,
                    'periodo': periodo,
                    'fase': fase,
                    'datazione': datazione
                }
            
            groups[group_key]['nodes'].append(node)
        
        # Create subgraphs for each group
        cluster_num = 0
        for group_key, group_data in groups.items():
            if not group_data['nodes']:
                continue
            
            cluster_name = f"cluster_{cluster_num}"
            
            # Determine label based on grouping
            if grouping == 'period_area':
                label = f"{group_data['datazione']}\\nArea {group_data['area']}\\nFase {group_data['fase']}"
                color = 'lightblue'
                style = 'filled,dashed'
            elif grouping == 'period':
                label = f"{group_data['datazione']}\\nFase {group_data['fase']}"
                color = 'lightyellow'
                style = 'filled'
            elif grouping == 'area':
                label = f"Area {group_data['area']}"
                color = 'lightgreen'
                style = 'filled,rounded'
            else:
                label = group_data['sito']
                color = 'lightgray'
                style = 'filled'
            
            # Create subgraph
            with G.subgraph(name=cluster_name) as cluster:
                cluster.attr(
                    label=label,
                    style=style,
                    fillcolor=color,
                    color='black',
                    penwidth='1.5',
                    fontsize='12',
                    fontname='Arial Bold',
                    rank='same'
                )
                
                # Add nodes to subgraph
                for node in group_data['nodes']:
                    self._add_single_node(cluster, graph, node, settings)
            
            cluster_num += 1
    
    def _create_simple_nodes(self, G: Digraph, graph: nx.DiGraph, us_rilevanti: set, settings: Dict):
        """Create nodes without grouping"""
        for node in us_rilevanti:
            if node in graph.nodes:
                self._add_single_node(G, graph, node, settings)
    
    def _add_single_node(self, G: Digraph, graph: nx.DiGraph, node: int, settings: Dict):
        """Add a single US node with PyArchInit styling"""
        node_data = graph.nodes[node] if node in graph.nodes else {}
        
        # Create label like PyArchInit
        us_type = node_data.get('unita_tipo', 'US')
        description = node_data.get('d_interpretativa', node_data.get('description', ''))
        period = node_data.get('periodo_iniziale', '')
        phase = node_data.get('fase_iniziale', '')
        
        # Truncate long descriptions
        if description and len(description) > 30:
            description = description[:30] + '...'
        
        # Build label
        label_parts = [f"{us_type}{node}"]
        if description:
            label_parts.append(description.replace(' ', '_'))
        if period:
            label_parts.append(f"{period}-{phase}")
        
        label = '\\n'.join(label_parts)
        
        # Determine node style based on formation type
        formation = node_data.get('formazione', node_data.get('formation', ''))
        if formation == 'Naturale':
            fillcolor = 'lightgreen'
            shape = 'ellipse'
        elif formation == 'Antropica':
            fillcolor = settings['us_fillcolor']
            shape = settings['us_shape']
        else:
            fillcolor = 'lightgray'
            shape = settings['us_shape']
        
        # Add node
        G.node(
            str(node),
            label=label,
            shape=shape,
            style=settings['us_style'],
            fillcolor=fillcolor,
            color=settings['us_color'],
            penwidth=settings['us_penwidth'],
            fontname='Arial',
            fontsize='10'
        )

    def _get_edge_label_for_unit(self, graph: nx.DiGraph, node: int, rel_type: str = '') -> str:
        """
        Get edge label based on Extended Matrix Framework unit type

        Extended Matrix Framework Rules:
        - US and USM: Use traditional textual labels (e.g., "Copre", "Coperto da", etc.)
        - USVA, USVB, USVC, TU, USD, CON, VSF, SF: Use single symbols (> and <)
        - Extractor, Combiner, DOC, property: Use double symbols (>> and <<)

        Args:
            graph: NetworkX graph containing node data
            node: Node ID (US number)
            rel_type: Relationship type (e.g., "Copre", "Taglia", "Uguale a")

        Returns:
            - rel_type for US/USM (traditional labels)
            - '>' for standard Extended Matrix units
            - '>>' for special Extended Matrix units
        """
        # Get node data if available
        if node not in graph.nodes:
            # Default: if we don't have node data, use traditional label
            return rel_type if rel_type else '>'

        node_data = graph.nodes[node]
        unita_tipo = node_data.get('unita_tipo', 'US')

        # US and USM use traditional textual relationship labels
        if unita_tipo in ['US', 'USM']:
            return rel_type if rel_type else 'Copre'

        # Units that use double symbols (>> and <<)
        double_symbol_units = ['Extractor', 'Combiner', 'DOC', 'property']

        # Special units use double symbols
        if unita_tipo in double_symbol_units:
            return '>>'

        # Other Extended Matrix units use single symbol
        return '>'

    def _add_sequence_edges(self, G: Digraph, graph: nx.DiGraph, relations: List[Tuple], settings: Dict, use_xlabel: bool = False):
        """Add normal stratigraphic sequence edges with Extended Matrix symbols"""
        for source, target, rel_type in relations:
            # Determine edge label based on unit type
            # Extended Matrix Framework specification:
            # - US/USM: Use textual labels (Copre, Coperto da, etc.)
            # - USVA, USVB, USVC, TU, USD, CON, VSF, SF: Use > and <
            # - Extractor, Combiner, DOC, property: Use >> and <<
            edge_label = self._get_edge_label_for_unit(graph, source, rel_type)

            # Use xlabel for orthogonal splines, label otherwise
            edge_params = {
                'xlabel' if use_xlabel else 'label': edge_label,
                'style': settings['normal_edge_style'],
                'color': settings['normal_edge_color'],
                'arrowhead': settings['normal_arrowhead'],
                'arrowsize': settings['normal_arrowsize'],
                'penwidth': settings['normal_penwidth']
            }

            G.edge(str(source), str(target), **edge_params)
    
    def _add_negative_edges(self, G: Digraph, graph: nx.DiGraph, relations: List[Tuple], settings: Dict, use_xlabel: bool = False):
        """Add negative (cuts) relationship edges with Extended Matrix symbols"""
        for source, target, rel_type in relations:
            # Determine edge label based on unit type
            edge_label = self._get_edge_label_for_unit(graph, source, rel_type)

            # Use xlabel for orthogonal splines, label otherwise
            edge_params = {
                'xlabel' if use_xlabel else 'label': edge_label,
                'style': settings['negative_edge_style'],
                'color': settings['negative_edge_color'],
                'arrowhead': settings['negative_arrowhead'],
                'arrowsize': settings['normal_arrowsize'],
                'penwidth': settings['normal_penwidth']
            }

            G.edge(str(source), str(target), **edge_params)

    def _add_contemporary_edges(self, G: Digraph, graph: nx.DiGraph, relations: List[Tuple], settings: Dict, use_xlabel: bool = False):
        """Add contemporary/equivalent relationship edges with Extended Matrix symbols"""
        for source, target, rel_type in relations:
            # Determine edge label based on unit type
            edge_label = self._get_edge_label_for_unit(graph, source, rel_type)

            # Use xlabel for orthogonal splines, label otherwise
            edge_params = {
                'xlabel' if use_xlabel else 'label': edge_label,
                'style': settings['contemp_edge_style'],
                'color': settings['contemp_edge_color'],
                'arrowhead': settings['contemp_arrowhead'],
                'arrowsize': settings['normal_arrowsize'],
                'penwidth': settings['normal_penwidth'],
                'constraint': 'false'  # Don't affect layout
            }

            G.edge(str(source), str(target), **edge_params)
    
    def _add_temporal_ordering(self, G: Digraph, graph: nx.DiGraph, us_rilevanti: set):
        """Add temporal ordering constraints to ensure chronological sequence"""
        
        # Group US by period (oldest to most recent)
        period_groups = {}
        
        for node in us_rilevanti:
            if node not in graph.nodes:
                continue
                
            node_data = graph.nodes[node]
            periodo = node_data.get('period_initial', node_data.get('periodo_iniziale', 5))  # Default to most recent if unknown
            
            # Convert to int to ensure proper ordering
            try:
                periodo_num = int(periodo)
            except (ValueError, TypeError):
                periodo_num = 5  # Default to most recent
            
            if periodo_num not in period_groups:
                period_groups[periodo_num] = []
            period_groups[periodo_num].append(node)
        
        # Create invisible edges to enforce temporal ordering
        # Most recent periods (higher numbers) should be at the top
        # Oldest periods (lower numbers) should be at the bottom
        sorted_periods = sorted(period_groups.keys(), reverse=True)  # Most recent first
        
        # Add invisible edges between periods to enforce chronological ordering
        for i in range(len(sorted_periods) - 1):
            current_period = sorted_periods[i]    # More recent period
            next_period = sorted_periods[i + 1]   # Older period
            
            # Take representative US from each period for ordering
            if period_groups[current_period] and period_groups[next_period]:
                recent_us = period_groups[current_period][0]  # Representative US from recent period
                older_us = period_groups[next_period][0]      # Representative US from older period
                
                # Add invisible edge to force recent US above older US
                G.edge(
                    str(recent_us), str(older_us),
                    style='invis',      # Invisible edge
                    constraint='true',  # Affects layout
                    weight='10'         # Strong constraint
                )
    
    def _add_legend(self, G: Digraph, settings: Dict):
        """Add legend like PyArchInit"""
        with G.subgraph(name='cluster_legend') as legend:
            legend.attr(
                rank='max',
                fillcolor='white',
                label='Legenda / Legend',
                fontcolor='black',
                fontsize='16',
                style='filled',
                color='black'
            )
            
            # Legend nodes and edges
            legend.node('leg_normal', 
                       label='Ante/Post',
                       shape=settings['us_shape'],
                       fillcolor=settings['us_fillcolor'],
                       style='filled')
            
            legend.node('leg_negative',
                       label='Taglia/Cuts',
                       shape=settings['negative_shape'],
                       fillcolor=settings['negative_fillcolor'],
                       style='filled')
            
            legend.node('leg_contemp',
                       label='Uguale/Same',
                       shape=settings['contemp_shape'],
                       fillcolor=settings['contemp_fillcolor'],
                       style='filled')
            
            # Legend edges
            legend.edge('leg_normal', 'leg_negative',
                       style=settings['normal_edge_style'],
                       arrowhead=settings['normal_arrowhead'],
                       color=settings['normal_edge_color'])
            
            legend.edge('leg_negative', 'leg_contemp',
                       style=settings['negative_edge_style'],
                       arrowhead=settings['negative_arrowhead'],
                       color=settings['negative_edge_color'])
    
    def export_multiple_formats(self, graph: nx.DiGraph, base_filename: str,
                               grouping: str = 'period_area') -> Dict[str, str]:
        """Export matrix in multiple formats"""
        exports = {}
        
        formats = ['png', 'svg', 'pdf']
        
        for fmt in formats:
            try:
                output_path = f"{base_filename}_{grouping}"
                
                # Create Graphviz source
                temp_dot = self.create_matrix(graph, grouping, output_path=output_path)
                
                if temp_dot.endswith('.dot'):
                    # Load and render in different formats
                    from graphviz import Source
                    with open(temp_dot, 'r') as f:
                        dot_source = f.read()
                    
                    graph_obj = Source(dot_source)
                    final_path = f"{output_path}.{fmt}"
                    graph_obj.render(final_path, format=fmt, cleanup=True)
                    exports[fmt] = f"{final_path}.{fmt}"
                else:
                    exports[fmt] = temp_dot
                    
            except Exception as e:
                print(f"Failed to export {fmt}: {e}")
        
        return exports