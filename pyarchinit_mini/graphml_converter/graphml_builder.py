"""
GraphML Builder - Pure Python
Constructs complete GraphML XML with yEd-compatible structures
No Graphviz dependency required
"""

import networkx as nx
from typing import Dict, List, Tuple, Optional
from xml.etree.ElementTree import Element, SubElement, ElementTree
from xml.dom import minidom

from .yed_template import YEdTemplate
from .em_palette import EMPalette
from .svg_resources import SVGResources


class GraphMLBuilder:
    """
    Builds complete GraphML XML structure with yEd compatibility
    Handles nodes, edges, groups, and Extended Matrix attributes
    """

    def __init__(self):
        """Initialize GraphML builder"""
        self.root = None
        self.graph_elem = None
        self.keys = {}

    def create_document(self, title: str = "Harris Matrix") -> Element:
        """
        Create GraphML document with yEd namespaces and keys

        Args:
            title: Graph title/description

        Returns:
            Root GraphML element
        """
        # Create root with namespaces
        self.root = YEdTemplate.create_graphml_root()

        # Create key definitions
        self.keys = YEdTemplate.create_graph_keys(self.root)

        # Create main graph element
        self.graph_elem = SubElement(self.root, 'graph')
        self.graph_elem.set('id', 'G')
        self.graph_elem.set('edgedefault', 'directed')

        # Add graph description
        if title:
            data = SubElement(self.graph_elem, 'data')
            data.set('key', self.keys['graph_description'])
            data.text = title

        return self.root

    def add_table_node_group(
        self,
        site_name: str,
        periods: List[Tuple[str, str, List]],  # (period_id, period_label, nodes)
        width: float = 1044.0,
        row_height: float = 940.0
    ) -> Tuple[Element, Element]:
        """
        Add TableNode group structure for period clustering

        Args:
            site_name: Site name for title
            periods: List of (period_id, period_label, node_list) tuples
            width: Table width
            row_height: Height of each period row

        Returns:
            Tuple of (group_node, nested_graph) elements
        """
        # Create group node for TableNode
        group_node = SubElement(self.graph_elem, 'node')
        group_node.set('id', 'table_node_group')
        group_node.set('yfiles.foldertype', 'group')

        # Add node graphics data
        data = SubElement(group_node, 'data')
        data.set('key', self.keys['node_graphics'])

        # Create TableNode structure using template
        period_rows = [(period_id, period_label) for period_id, period_label, _ in periods]
        table_node = YEdTemplate.create_table_node_header(
            parent=data,
            title=site_name,
            rows=period_rows,
            width=width,
            row_height=row_height
        )

        # Create single nested graph inside group for ALL nodes
        # (like reference file: <graph id="n0:">)
        nested_graph = SubElement(group_node, 'graph')
        nested_graph.set('id', 'table_node_group:')
        nested_graph.set('edgedefault', 'directed')

        return group_node, nested_graph

    def add_node(
        self,
        node_id: str,
        label: str,
        extended_label: str = "",
        description: str = "",
        url: str = "",
        period: str = "",
        parent_graph: Optional[Element] = None,
        y_position: float = 0.0,
        period_row: int = 0,
        **kwargs
    ) -> Element:
        """
        Add a node with Extended Matrix attributes

        Args:
            node_id: Unique node identifier
            label: Display label
            extended_label: PyArchInit Extended Matrix label
            description: Node description/tooltip
            url: File path URL
            period: Period code for grouping
            parent_graph: Parent graph element (for nested nodes)
            y_position: Y coordinate for positioning
            period_row: Period row index
            **kwargs: Additional node attributes

        Returns:
            Node element
        """
        target_graph = parent_graph if parent_graph is not None else self.graph_elem

        node = SubElement(target_graph, 'node')
        node.set('id', str(node_id))

        # Add label data
        if label:
            data = SubElement(node, 'data')
            data.set('key', self.keys['node_label'])
            data.text = label

        # Add extended label
        if extended_label:
            data = SubElement(node, 'data')
            data.set('key', self.keys['node_extended_label'])
            data.text = extended_label

        # Add description
        if description:
            data = SubElement(node, 'data')
            data.set('key', self.keys['node_description'])
            data.text = description

        # Add URL
        if url:
            data = SubElement(node, 'data')
            data.set('key', self.keys['node_url'])
            data.text = url

        # Add period
        if period:
            data = SubElement(node, 'data')
            data.set('key', self.keys['node_period'])
            data.text = period

        # Add additional attributes
        for attr_name, attr_value in kwargs.items():
            if attr_value:
                data = SubElement(node, 'data')
                # Map attribute name to key (will need key mapping logic)
                data.set('key', f'attr_{attr_name}')
                data.text = str(attr_value)

        # Add node graphics (ShapeNode structure with EM palette)
        self._add_node_graphics(node, label, description, y_position, period_row)

        return node

    def _add_node_graphics(
        self,
        node: Element,
        label: str,
        description: str = "",
        y_position: float = 0.0,
        period_row: int = 0
    ):
        """
        Add yEd node graphics (ShapeNode, SVGNode, or GenericNode) based on node type

        Args:
            node: Node element
            label: Node label text
            description: Tooltip text
            y_position: Y coordinate for positioning in TableNode
            period_row: Period row index (0-based)
        """
        # Detect node type from label prefix
        label_upper = label.upper()

        # Special nodes requiring SVGNode
        if label_upper.startswith('CON'):
            self._add_svg_node(node, label, description, y_position, refid='3', node_type='CON')
        elif label_upper.startswith('EXTRACTOR'):
            self._add_svg_node(node, label, description, y_position, refid='1', node_type='EXTRACTOR')
        elif label_upper.startswith('COMBINAR'):
            self._add_svg_node(node, label, description, y_position, refid='2', node_type='COMBINAR')
        # Special nodes requiring GenericNode (BPMN)
        elif label_upper.startswith('DOC'):
            self._add_bpmn_node(node, label, description, y_position, node_type='DOC')
        elif label_upper.startswith('PROPERTY'):
            self._add_bpmn_node(node, label, description, y_position, node_type='PROPERTY')
        # Standard ShapeNode for all other types
        else:
            self._add_shape_node(node, label, description, y_position)

    def _add_shape_node(
        self,
        node: Element,
        label: str,
        description: str,
        y_position: float
    ):
        """Add standard ShapeNode for regular US/USM/etc nodes"""
        data = SubElement(node, 'data')
        data.set('key', self.keys['node_graphics'])

        # Get Extended Matrix style for this node
        style = EMPalette.get_node_style(label)

        # Create ShapeNode
        shape_node = SubElement(data, '{http://www.yworks.com/xml/graphml}ShapeNode')

        # Geometry
        geometry = SubElement(shape_node, '{http://www.yworks.com/xml/graphml}Geometry')
        geometry.set('height', '30.0')
        geometry.set('width', '90.0')
        geometry.set('x', '0.0')
        geometry.set('y', str(y_position))

        # Fill
        fill = SubElement(shape_node, '{http://www.yworks.com/xml/graphml}Fill')
        fill.set('color', style['fill_color'])
        fill.set('transparent', 'false')

        # Border
        border = SubElement(shape_node, '{http://www.yworks.com/xml/graphml}BorderStyle')
        border.set('color', style['border_color'])
        border.set('type', 'line')
        border.set('width', style['border_width'])

        # Node Label
        node_label = SubElement(shape_node, '{http://www.yworks.com/xml/graphml}NodeLabel')
        node_label.set('alignment', 'center')
        node_label.set('autoSizePolicy', 'content')
        node_label.set('fontFamily', style['font_family'])
        node_label.set('fontSize', style['font_size'])
        node_label.set('fontStyle', style['font_style'])
        node_label.set('hasBackgroundColor', 'false')
        node_label.set('hasLineColor', 'false')
        node_label.set('height', '32.265625')
        node_label.set('horizontalTextPosition', 'center')
        node_label.set('iconTextGap', '4')
        node_label.set('modelName', 'internal')
        node_label.set('modelPosition', 'c')
        node_label.set('textColor', style['text_color'])
        node_label.set('verticalTextPosition', 'bottom')
        node_label.set('visible', 'true')
        node_label.set('xml:space', 'preserve')
        if description:
            node_label.set('configuration', 'AutoFlippingLabel')
            node_label.set('hasText', 'true')
        node_label.text = label

        # Shape
        shape = SubElement(shape_node, '{http://www.yworks.com/xml/graphml}Shape')
        shape.set('type', style['shape'])

    def _add_svg_node(
        self,
        node: Element,
        label: str,
        description: str,
        y_position: float,
        refid: str,
        node_type: str
    ):
        """Add SVGNode for CON, Extractor, Combinar"""
        data = SubElement(node, 'data')
        data.set('key', self.keys['node_graphics'])

        # Get style from palette
        style = EMPalette.get_node_style(label)

        # Format label text according to node type
        display_label = label
        if node_type == 'EXTRACTOR':
            # "Extractor_23" → "D.23"
            display_label = label.replace('Extractor', 'D.')
        elif node_type == 'COMBINAR':
            # "Combinar_45" → "C.45"
            display_label = label.replace('Combinar', 'C.')
        elif node_type == 'CON':
            # CON keeps original label but font size 0
            display_label = label

        # Create SVGNode
        svg_node = SubElement(data, '{http://www.yworks.com/xml/graphml}SVGNode')

        # Geometry (smaller for CON, standard for Extractor/Combinar)
        geometry = SubElement(svg_node, '{http://www.yworks.com/xml/graphml}Geometry')
        if node_type == 'CON':
            geometry.set('height', '26.0')
            geometry.set('width', '26.0')
        else:
            geometry.set('height', '25.0')
            geometry.set('width', '25.0')
        geometry.set('x', '0.0')
        geometry.set('y', str(y_position))

        # Fill
        fill = SubElement(svg_node, '{http://www.yworks.com/xml/graphml}Fill')
        fill.set('color', style['fill_color'])
        fill.set('transparent', 'false')

        # Border
        border = SubElement(svg_node, '{http://www.yworks.com/xml/graphml}BorderStyle')
        border.set('color', style['border_color'])
        border.set('type', 'line')
        border.set('width', style['border_width'])

        # Node Label (CON has fontSize 0 to hide text)
        node_label = SubElement(svg_node, '{http://www.yworks.com/xml/graphml}NodeLabel')
        node_label.set('alignment', 'center')
        node_label.set('autoSizePolicy', 'content')
        if node_type == 'CON':
            node_label.set('fontFamily', 'Dialog')
            node_label.set('fontSize', '0')  # Hidden label for CON
            node_label.set('fontStyle', 'plain')
            node_label.set('modelName', 'sandwich')
            node_label.set('modelPosition', 's')
        else:
            # Extractor/Combinar labels (D.1, C.2, etc)
            node_label.set('fontFamily', 'Dialog')
            node_label.set('fontSize', '10')
            node_label.set('fontStyle', 'plain')
            node_label.set('borderDistance', '0.0')
            node_label.set('modelName', 'corners')
            node_label.set('modelPosition', 'nw')
            node_label.set('underlinedText', 'true')
        node_label.set('hasBackgroundColor', 'false')
        node_label.set('hasLineColor', 'false')
        node_label.set('textColor', style['text_color'])
        node_label.set('visible', 'true')
        node_label.set('xml:space', 'preserve')
        node_label.text = display_label

        # SVGNodeProperties
        svg_props = SubElement(svg_node, '{http://www.yworks.com/xml/graphml}SVGNodeProperties')
        svg_props.set('usingVisualBounds', 'true')

        # SVGModel with refid
        svg_model = SubElement(svg_node, '{http://www.yworks.com/xml/graphml}SVGModel')
        svg_model.set('svgBoundsPolicy', '0')

        svg_content = SubElement(svg_model, '{http://www.yworks.com/xml/graphml}SVGContent')
        svg_content.set('refid', refid)

    def _add_bpmn_node(
        self,
        node: Element,
        label: str,
        description: str,
        y_position: float,
        node_type: str
    ):
        """Add GenericNode (BPMN) for DOC and property nodes"""
        data = SubElement(node, 'data')
        data.set('key', self.keys['node_graphics'])

        # Get style from palette
        style = EMPalette.get_node_style(label)

        # Format label text according to node type
        display_label = label
        if node_type == 'DOC':
            # "DOC4001" → "D.4001"
            display_label = label.replace('DOC', 'D.')
        elif node_type == 'PROPERTY':
            # Extract first word from description (e.g., "Materiale pietra dura" → "Materiale")
            # or "Material hard stone" → "Material"
            if description and description.strip():
                # Get first word from description
                display_label = description.strip().split()[0]
            else:
                # Fallback: try to extract from label
                parts = label.split('_')
                if len(parts) >= 2:
                    display_label = parts[1]  # Get "material" part
                else:
                    # Just show the number
                    display_label = label.replace('property', '').replace('PROPERTY', '')

        # Create GenericNode
        generic_node = SubElement(data, '{http://www.yworks.com/xml/graphml}GenericNode')
        if node_type == 'DOC':
            generic_node.set('configuration', 'com.yworks.bpmn.Artifact.withShadow')
        else:  # PROPERTY
            generic_node.set('configuration', 'com.yworks.bpmn.Artifact.withShadow')

        # Geometry
        geometry = SubElement(generic_node, '{http://www.yworks.com/xml/graphml}Geometry')
        if node_type == 'DOC':
            geometry.set('height', '55.0')
            geometry.set('width', '35.0')
        else:  # PROPERTY
            geometry.set('height', '30.0')
            geometry.set('width', '90.0')
        geometry.set('x', '0.0')
        geometry.set('y', str(y_position))

        # Fill
        fill = SubElement(generic_node, '{http://www.yworks.com/xml/graphml}Fill')
        fill.set('color', style['fill_color'])
        fill.set('transparent', 'false')

        # Border
        border = SubElement(generic_node, '{http://www.yworks.com/xml/graphml}BorderStyle')
        border.set('color', style['border_color'])
        border.set('type', 'line')
        border.set('width', style['border_width'])

        # Node Label
        node_label = SubElement(generic_node, '{http://www.yworks.com/xml/graphml}NodeLabel')
        node_label.set('alignment', 'center')
        node_label.set('autoSizePolicy', 'content')
        node_label.set('fontFamily', style['font_family'])
        node_label.set('fontSize', style['font_size'])
        node_label.set('fontStyle', style['font_style'])
        node_label.set('hasBackgroundColor', 'false')
        node_label.set('hasLineColor', 'false')
        node_label.set('horizontalTextPosition', 'center')
        node_label.set('iconTextGap', '4')
        node_label.set('modelName', 'internal')
        node_label.set('modelPosition', 'c')
        node_label.set('textColor', style['text_color'])
        node_label.set('verticalTextPosition', 'bottom')
        node_label.set('visible', 'true')
        node_label.set('xml:space', 'preserve')
        node_label.text = display_label

        # StyleProperties for BPMN
        style_props = SubElement(generic_node, '{http://www.yworks.com/xml/graphml}StyleProperties')

        prop1 = SubElement(style_props, '{http://www.yworks.com/xml/graphml}Property')
        prop1.set('class', 'java.awt.Color')
        prop1.set('name', 'com.yworks.bpmn.icon.line.color')
        prop1.set('value', '#000000')

        prop2 = SubElement(style_props, '{http://www.yworks.com/xml/graphml}Property')
        prop2.set('class', 'java.awt.Color')
        prop2.set('name', 'com.yworks.bpmn.icon.fill2')
        prop2.set('value', '#d4d4d4cc')

        prop3 = SubElement(style_props, '{http://www.yworks.com/xml/graphml}Property')
        prop3.set('class', 'java.awt.Color')
        prop3.set('name', 'com.yworks.bpmn.icon.fill')
        prop3.set('value', '#ffffffe6')

        if node_type == 'DOC':
            prop4 = SubElement(style_props, '{http://www.yworks.com/xml/graphml}Property')
            prop4.set('class', 'com.yworks.yfiles.bpmn.view.BPMNTypeEnum')
            prop4.set('name', 'com.yworks.bpmn.type')
            prop4.set('value', 'ARTIFACT_TYPE_DATA_OBJECT')

            prop5 = SubElement(style_props, '{http://www.yworks.com/xml/graphml}Property')
            prop5.set('class', 'com.yworks.yfiles.bpmn.view.DataObjectTypeEnum')
            prop5.set('name', 'com.yworks.bpmn.dataObjectType')
            prop5.set('value', 'DATA_OBJECT_TYPE_PLAIN')
        else:  # PROPERTY
            prop4 = SubElement(style_props, '{http://www.yworks.com/xml/graphml}Property')
            prop4.set('class', 'com.yworks.yfiles.bpmn.view.BPMNTypeEnum')
            prop4.set('name', 'com.yworks.bpmn.type')
            prop4.set('value', 'ARTIFACT_TYPE_ANNOTATION')

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        label: str = "",
        relationship: str = "",
        certainty: str = "",
        **kwargs
    ) -> Element:
        """
        Add an edge with relationship attributes

        Args:
            source_id: Source node ID
            target_id: Target node ID
            label: Edge label
            relationship: Relationship type (sopra, taglia, etc.)
            certainty: Relationship certainty
            **kwargs: Additional edge attributes

        Returns:
            Edge element
        """
        edge = SubElement(self.graph_elem, 'edge')
        edge_id = f"e_{source_id}_{target_id}"
        edge.set('id', edge_id)
        edge.set('source', str(source_id))
        edge.set('target', str(target_id))

        # Add label data
        if label:
            data = SubElement(edge, 'data')
            data.set('key', self.keys['edge_label'])
            data.text = label

        # Add relationship type
        if relationship:
            data = SubElement(edge, 'data')
            data.set('key', self.keys['edge_relationship'])
            data.text = relationship

        # Add certainty
        if certainty:
            data = SubElement(edge, 'data')
            data.set('key', self.keys['edge_certainty'])
            data.text = certainty

        # Add edge graphics (arrow styling)
        self._add_edge_graphics(edge, label, relationship)

        return edge

    def _add_edge_graphics(self, edge: Element, label: str = "", relationship: str = ""):
        """
        Add yEd edge graphics (arrows, line style) based on relationship type

        Args:
            edge: Edge element
            label: Edge label text
            relationship: Relationship type for styling
        """
        data = SubElement(edge, 'data')
        data.set('key', self.keys['edge_graphics'])

        # Create PolyLineEdge
        poly_line = SubElement(data, '{http://www.yworks.com/xml/graphml}PolyLineEdge')

        # Path (auto-routed by yEd)
        path = SubElement(poly_line, '{http://www.yworks.com/xml/graphml}Path')
        path.set('sx', '0.0')
        path.set('sy', '0.0')
        path.set('tx', '0.0')
        path.set('ty', '0.0')

        # Determine line style and arrows based on relationship type
        rel = relationship.lower() if relationship else ""

        # Line style defaults
        line_type = 'line'  # solid
        line_width = '1.0'
        source_arrow = 'none'
        target_arrow = 'standard'

        # Dotted lines for: taglia, tagliato da, >>, <<
        if rel in ['taglia', 'tagliato da', '>>', '<<']:
            line_type = 'dashed'

        # Double-width lines without arrows for: uguale a, si lega
        elif rel in ['uguale a', 'si lega a']:
            line_type = 'line'
            line_width = '2.0'  # Thicker line to simulate double line
            source_arrow = 'none'
            target_arrow = 'none'

        # Square arrowheads for: si appoggia, gli si appoggia
        elif rel in ['si appoggia a', 'gli si appoggia']:
            target_arrow = 'white_delta'  # Square-like arrowhead

        # Line style
        line_style = SubElement(poly_line, '{http://www.yworks.com/xml/graphml}LineStyle')
        line_style.set('color', '#000000')
        line_style.set('type', line_type)
        line_style.set('width', line_width)

        # Arrows
        arrows = SubElement(poly_line, '{http://www.yworks.com/xml/graphml}Arrows')
        arrows.set('source', source_arrow)
        arrows.set('target', target_arrow)

        # Edge Label
        if label:
            edge_label = SubElement(poly_line, '{http://www.yworks.com/xml/graphml}EdgeLabel')
            edge_label.set('alignment', 'center')
            edge_label.set('configuration', 'AutoFlippingLabel')
            edge_label.set('distance', '2.0')
            edge_label.set('fontFamily', 'Dialog')
            edge_label.set('fontSize', '10')
            edge_label.set('fontStyle', 'plain')
            edge_label.set('hasBackgroundColor', 'false')
            edge_label.set('hasLineColor', 'false')
            edge_label.set('modelName', 'centered')
            edge_label.set('preferredPlacement', 'anywhere')
            edge_label.set('ratio', '0.5')
            edge_label.set('textColor', '#000000')
            edge_label.set('visible', 'true')
            edge_label.text = label

    def to_string(self, pretty_print: bool = True) -> str:
        """
        Convert GraphML tree to XML string

        Args:
            pretty_print: Format XML with indentation

        Returns:
            XML string
        """
        if pretty_print:
            # Use minidom for pretty printing
            rough_string = ElementTree.tostring(self.root, encoding='utf-8')
            reparsed = minidom.parseString(rough_string)
            return reparsed.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')
        else:
            return ElementTree.tostring(self.root, encoding='utf-8').decode('utf-8')

    def write_to_file(self, output_path: str):
        """
        Write GraphML to file

        Args:
            output_path: Output file path
        """
        # Add SVG resources before writing (for CON, Extractor, Combinar nodes)
        SVGResources.create_resources_section(self.root)

        # Register namespaces to avoid ET auto-adding them
        from xml.etree import ElementTree as ET
        ET.register_namespace('', 'http://graphml.graphdrawing.org/xmlns')
        ET.register_namespace('java', 'http://www.yworks.com/xml/yfiles-common/1.0/java')
        ET.register_namespace('sys', 'http://www.yworks.com/xml/yfiles-common/markup/primitives/2.0')
        ET.register_namespace('x', 'http://www.yworks.com/xml/yfiles-common/markup/2.0')
        ET.register_namespace('xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        ET.register_namespace('y', 'http://www.yworks.com/xml/graphml')
        ET.register_namespace('yed', 'http://www.yworks.com/xml/yed/3')

        tree = ElementTree(self.root)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)

        print(f"✅ GraphML written to: {output_path}")
