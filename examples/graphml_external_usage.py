"""
Complete example of using PyArchInit-Mini GraphML Converter as an external API.

This example demonstrates how to create a Harris Matrix diagram from scratch
using NetworkX and export it to yEd-compatible GraphML with full EM_palette
styling and archaeological metadata.

Requirements:
    pip install pyarchinit-mini networkx

Features demonstrated:
    - Creating a NetworkX DiGraph with stratigraphic relationships
    - Adding archaeological metadata (d_stratigrafica, d_interpretativa, unita_tipo)
    - Generating DOT format from the graph
    - Converting to GraphML with EM_palette colors
    - Proper node descriptions visible in yEd

Author: PyArchInit Team
License: GPL v2
"""

import networkx as nx
from pyarchinit_mini.graphml_converter import convert_dot_content_to_graphml
import tempfile


def create_harris_matrix_graph():
    """
    Create a sample Harris Matrix as a NetworkX DiGraph.

    Graph structure represents stratigraphic relationships:
    - Nodes: Stratigraphic Units (US) with metadata
    - Edges: Stratigraphic relationships (copre, taglia, uguale a, etc.)

    Returns:
        nx.DiGraph: Graph with stratigraphic data
    """
    graph = nx.DiGraph()

    # Add US nodes with full archaeological metadata
    # Each node must have these attributes for proper GraphML export:
    #   - d_stratigrafica: Stratigraphic description
    #   - d_interpretativa: Archaeological interpretation
    #   - unita_tipo: Unit type (US, USM, USD, USV, USV/s)
    #   - period_initial: Chronological period
    #   - area: Archaeological area/sector (optional)

    # US 1001 - Modern topsoil (US type)
    graph.add_node(1001,
        d_stratigrafica='Humus - Strato superficiale di humus',
        d_interpretativa='Interpretazione: strato superficiale. Contesto moderno.',
        unita_tipo='US',
        period_initial='Moderno',
        area='Settore A')

    # US 1002 - Medieval fill (US type)
    graph.add_node(1002,
        d_stratigrafica='Riempimento - Riempimento di fossa',
        d_interpretativa='Interpretazione: deposito di riempimento. Contesto medievale.',
        unita_tipo='US',
        period_initial='Medievale',
        area='Settore A')

    # US 1003 - Medieval wall (USM - masonry type)
    graph.add_node(1003,
        d_stratigrafica='Muro - Struttura muraria in opus incertum',
        d_interpretativa='Interpretazione: muro perimetrale. Contesto medievale.',
        unita_tipo='USM',  # Masonry unit - gets red border
        period_initial='Medievale',
        area='Settore A')

    # US 1004 - Cut for wall foundation (USV - virtual negative)
    graph.add_node(1004,
        d_stratigrafica='Taglio - Interfaccia di taglio per fondazione',
        d_interpretativa='Interpretazione: taglio di fondazione. Contesto medievale.',
        unita_tipo='USV',  # Virtual US negative - gets green border, hexagon
        period_initial='Medievale',
        area='Settore A')

    # US 1005 - Roman floor (US type)
    graph.add_node(1005,
        d_stratigrafica='Pavimento - Superficie pavimentale in opus signinum',
        d_interpretativa='Interpretazione: pavimento. Contesto romano imperiale.',
        unita_tipo='US',
        period_initial='Romano Imperiale',
        area='Settore A')

    # US 1006 - Documentary unit (USD - documentary type)
    graph.add_node(1006,
        d_stratigrafica='Documentazione - Unità documentaria per foto di dettaglio',
        d_interpretativa='Interpretazione: unità di documentazione fotografica.',
        unita_tipo='USD',  # Documentary US - gets orange border
        period_initial='Romano Imperiale',
        area='Settore A')

    # Add stratigraphic relationships (edges)
    # Each edge should have:
    #   - relationship: Type (copre, taglia, uguale a, si lega a)
    #   - certainty: certain or uncertain (optional)

    # Contemporary relationships (no arrow in GraphML)
    graph.add_edge(1001, 1002, relationship='copre', certainty='certain')
    graph.add_edge(1002, 1003, relationship='si lega a', certainty='certain')  # No arrow

    # Negative relationships (dashed line in GraphML)
    graph.add_edge(1003, 1004, relationship='taglia', certainty='certain')  # Dashed

    # Normal stratigraphic relationships (arrow in GraphML)
    graph.add_edge(1004, 1005, relationship='copre', certainty='certain')
    graph.add_edge(1005, 1006, relationship='copre', certainty='certain')

    return graph


def generate_dot_from_graph(graph, grouping='period'):
    """
    Generate Graphviz DOT content from NetworkX graph.

    This function creates a DOT file that the GraphML converter can process.
    It applies EM_palette styles based on unita_tipo and includes all metadata.

    Args:
        graph: NetworkX DiGraph with stratigraphic data
        grouping: Grouping mode ('period_area', 'period', 'area', 'none')

    Returns:
        str: DOT file content
    """
    # EM_palette node styles based on unita_tipo
    # From Extended Matrix palette v.1.4
    US_STYLES = {
        'US': {'shape': 'box', 'fillcolor': '#FFFFFF', 'color': '#9B3333', 'penwidth': '4.0'},
        'USM': {'shape': 'box', 'fillcolor': '#FFFFFF', 'color': '#9B3333', 'penwidth': '4.0'},
        'TSU': {'shape': 'box', 'fillcolor': '#FFFFFF', 'color': '#9B3333', 'penwidth': '4.0'},  # dashed border
        'USD': {'shape': 'box', 'fillcolor': '#FFFFFF', 'color': '#D86400', 'penwidth': '4.0'},
        'USV': {'shape': 'hexagon', 'fillcolor': '#000000', 'color': '#31792D', 'penwidth': '4.0'},
        'USV/s': {'shape': 'trapezium', 'fillcolor': '#000000', 'color': '#248FE7', 'penwidth': '4.0'},
        'Series US': {'shape': 'ellipse', 'fillcolor': '#FFFFFF', 'color': '#9B3333', 'penwidth': '4.0'},
        'Series USV': {'shape': 'ellipse', 'fillcolor': '#000000', 'color': '#31792D', 'penwidth': '4.0'},
        'SF': {'shape': 'octagon', 'fillcolor': '#FFFFFF', 'color': '#D8BD30', 'penwidth': '4.0'},
        'VSF': {'shape': 'octagon', 'fillcolor': '#000000', 'color': '#B19F61', 'penwidth': '4.0'},
    }

    dot_lines = ['digraph {', '\trankdir=BT']  # Bottom-to-top layout

    # Add nodes with EM_palette styling
    for node in graph.nodes():
        node_data = graph.nodes[node]

        # Extract metadata
        d_strat = node_data.get('d_stratigrafica', '')
        d_interp = node_data.get('d_interpretativa', '')
        unita_tipo = node_data.get('unita_tipo', 'US')
        periodo = node_data.get('period_initial', 'Sconosciuto')

        # Build node description (will appear in yEd Description field)
        desc_parts = []
        if d_strat:
            desc_parts.append(d_strat)
        if d_interp:
            desc_parts.append(d_interp)
        node_description = ' - '.join(desc_parts) if desc_parts else ''

        # Clean for DOT format
        desc_clean = d_strat.replace(' ', '_').replace(',', '').replace('"', '')[:30]
        periodo_clean = periodo.replace(' ', '-')

        # Node ID format required by GraphML converter
        node_id = f'US_{node}_{desc_clean}_{periodo_clean}'
        label = f'US{node}_{periodo_clean}'

        # Get style for this unit type
        style = US_STYLES.get(unita_tipo, US_STYLES['US'])

        # Build node attributes
        attrs = [
            f'label="{label}"',
            f'shape={style["shape"]}',
            f'fillcolor="{style["fillcolor"]}"',
            f'color="{style["color"]}"',
            f'penwidth={style["penwidth"]}',
            'style=filled'
        ]

        # Add tooltip with description (optional, not used in final GraphML)
        if node_description:
            desc_escaped = node_description.replace('"', '\\"').replace('\n', '\\n')
            attrs.append(f'tooltip="{desc_escaped}"')

        dot_lines.append(f'\t"{node_id}" [{", ".join(attrs)}]')

    # Add edges with PyArchInit convention
    for source, target in graph.edges():
        edge_data = graph.get_edge_data(source, target)
        rel_type = edge_data.get('relationship', 'sopra')

        # Build source and target IDs
        source_data = graph.nodes[source]
        target_data = graph.nodes[target]

        source_desc = source_data.get('d_stratigrafica', '')[:30].replace(' ', '_').replace(',', '')
        target_desc = target_data.get('d_stratigrafica', '')[:30].replace(' ', '_').replace(',', '')

        source_periodo = source_data.get('period_initial', 'Sconosciuto').replace(' ', '-')
        target_periodo = target_data.get('period_initial', 'Sconosciuto').replace(' ', '-')

        source_id = f'US_{source}_{source_desc}_{source_periodo}'
        target_id = f'US_{target}_{target_desc}_{target_periodo}'

        # Determine edge style based on relationship type
        edge_attrs = []
        rel_lower = rel_type.lower()

        if 'uguale' in rel_lower or 'lega' in rel_lower:
            # Contemporary: no arrow
            edge_attrs.append('dir=none')
        elif 'taglia' in rel_lower or 'cut' in rel_lower:
            # Negative: dashed with arrow
            edge_attrs.append('style=dashed')
            edge_attrs.append('arrowhead=normal')
        else:
            # Normal stratigraphic: arrow
            edge_attrs.append('arrowhead=normal')

        # Add relationship as tooltip (not visible label)
        if rel_type:
            edge_attrs.append(f'tooltip="{rel_type}"')

        edge_attr_str = ', '.join(edge_attrs)
        dot_lines.append(f'\t"{source_id}" -> "{target_id}" [{edge_attr_str}]')

    # Add period label nodes (required for period grouping)
    periods = set()
    for node in graph.nodes():
        periodo = graph.nodes[node].get('period_initial', 'Sconosciuto')
        periods.add(periodo.replace(' ', '-'))

    for periodo in sorted(periods):
        dot_lines.append(f'\t"Periodo : {periodo}" [shape=plaintext]')

    dot_lines.append('}')
    return '\n'.join(dot_lines)


def main():
    """Main function demonstrating complete workflow."""

    print("=== PyArchInit-Mini GraphML Converter - External API Example ===\n")

    # Step 1: Create Harris Matrix graph
    print("Step 1: Creating Harris Matrix graph...")
    graph = create_harris_matrix_graph()
    print(f"  ✓ Created graph with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")
    print(f"  Nodes: {list(graph.nodes())}")
    print()

    # Step 2: Generate DOT content
    print("Step 2: Generating DOT content...")
    dot_content = generate_dot_from_graph(graph, grouping='period')
    print(f"  ✓ Generated DOT ({len(dot_content)} characters)")
    print()

    # Step 3: Convert to GraphML
    print("Step 3: Converting to GraphML...")
    graphml_content = convert_dot_content_to_graphml(dot_content)
    print(f"  ✓ Converted to GraphML ({len(graphml_content)} characters)")
    print()

    # Step 4: Post-process to add descriptions (like web_interface/app.py does)
    print("Step 4: Adding node descriptions to GraphML...")
    import re
    import xml.dom.minidom as minidom

    # Clean labels (remove period suffix from labels)
    graphml_content = re.sub(r'(>US\d+)_[^<]+(</y:NodeLabel>)', r'\1\2', graphml_content)

    # Build description map
    description_map = {}
    for node in graph.nodes():
        node_data = graph.nodes[node]
        d_strat = node_data.get('d_stratigrafica', '')
        d_interp = node_data.get('d_interpretativa', '')
        desc_parts = []
        if d_strat:
            desc_parts.append(d_strat)
        if d_interp:
            desc_parts.append(d_interp)
        if desc_parts:
            description_map[node] = ' - '.join(desc_parts)

    # Parse and modify GraphML
    dom = minidom.parseString(graphml_content)
    descriptions_added = 0

    for shape_node in dom.getElementsByTagName('y:ShapeNode'):
        labels = shape_node.getElementsByTagName('y:NodeLabel')
        if not labels or not labels[0].firstChild:
            continue

        label_text = labels[0].firstChild.nodeValue
        match = re.match(r'US(\d+)', label_text)
        if not match:
            continue

        us_number = int(match.group(1))

        if us_number in description_map:
            data_element = shape_node.parentNode
            node_element = data_element.parentNode

            # Find or create <data key="d5"> (description field)
            existing_desc = None
            for child in node_element.childNodes:
                if child.nodeType == child.ELEMENT_NODE and child.tagName == 'data':
                    if child.getAttribute('key') == 'd5':
                        existing_desc = child
                        break

            description_text = description_map[us_number]
            if existing_desc:
                if existing_desc.firstChild:
                    existing_desc.firstChild.nodeValue = description_text
                else:
                    text_node = dom.createTextNode(description_text)
                    existing_desc.appendChild(text_node)
                descriptions_added += 1

    graphml_content = dom.toxml()
    print(f"  ✓ Added {descriptions_added} node descriptions")
    print()

    # Step 5: Save to file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.graphml', delete=False, encoding='utf-8') as f:
        f.write(graphml_content)
        output_file = f.name

    print(f"Step 5: Saved GraphML file")
    print(f"  ✓ File: {output_file}")
    print(f"  ✓ Size: {len(graphml_content)} bytes")
    print()

    # Summary
    print("=== Summary ===")
    print(f"GraphML file ready: {output_file}")
    print()
    print("To view in yEd Graph Editor:")
    print("  1. Download yEd from https://www.yworks.com/products/yed")
    print("  2. Open the .graphml file")
    print("  3. Click on nodes to see descriptions in Properties panel")
    print("  4. EM_palette colors are automatically applied:")
    print("     - US/USM: Red border (#9B3333)")
    print("     - USD: Orange border (#D86400)")
    print("     - USV: Green border (#31792D), hexagon")
    print("     - USV/s: Blue border (#248FE7), trapezium")
    print()
    print("Node descriptions contain:")
    print("  d_stratigrafica - d_interpretativa")
    print()
    print("Edges follow PyArchInit convention:")
    print("  - Contemporary (si lega a): No arrow")
    print("  - Stratigraphic (copre): Arrow")
    print("  - Negative (taglia): Dashed arrow")


if __name__ == '__main__':
    main()
