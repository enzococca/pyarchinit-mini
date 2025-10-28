"""
yEd GraphML Template Generator
Generates yEd-compatible XML structures without Graphviz dependency
"""

import random
from typing import Dict, List, Tuple
from xml.etree.ElementTree import Element, SubElement


class YEdTemplate:
    """
    Template generator for yEd GraphML structures
    Handles TableNode, period rows, styling, and colors
    """

    # yEd XML namespaces
    NAMESPACES = {
        'graphml': 'http://graphml.graphdrawing.org/xmlns',
        'java': 'http://www.yworks.com/xml/yfiles-common/1.0/java',
        'sys': 'http://www.yworks.com/xml/yfiles-common/markup/primitives/2.0',
        'x': 'http://www.yworks.com/xml/yfiles-common/markup/2.0',
        'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'y': 'http://www.yworks.com/xml/graphml',
        'yed': 'http://www.yworks.com/xml/yed/3'
    }

    # Period color palette (similar to PyArchInit Extended Matrix)
    PERIOD_COLORS = [
        '#9642B7', '#7204CB', '#20ADB7', '#65C3E4', '#FA9639',
        '#85E1C9', '#6105C3', '#1DBCB1', '#9DC185', '#CB99D2',
        '#B7D2DF', '#D406E6', '#1E4B4B', '#7E0BD6', '#07D688',
        '#D37843', '#342400', '#F747A0', '#52BD36', '#E58042',
        '#097728', '#C84643', '#C9FC9E', '#085DE8', '#E4CC6F',
        '#3A8B9E', '#D4A5E8', '#8FE3B0', '#F2A65A', '#7B68EE'
    ]

    @staticmethod
    def generate_period_color() -> str:
        """Generate random color for period row"""
        return random.choice(YEdTemplate.PERIOD_COLORS)

    @staticmethod
    def create_graphml_root() -> Element:
        """Create GraphML root element with yEd namespaces"""
        # Don't add xmlns attributes manually - let ElementTree handle them
        # via register_namespace() in write_to_file()
        root = Element('graphml')

        # Schema location
        root.set(
            '{http://www.w3.org/2001/XMLSchema-instance}schemaLocation',
            'http://graphml.graphdrawing.org/xmlns '
            'http://www.yworks.com/xml/schema/graphml/1.1/ygraphml.xsd'
        )

        return root

    @staticmethod
    def create_graph_keys(root: Element) -> Dict[str, str]:
        """
        Create GraphML key definitions for yEd
        Returns mapping of attribute names to key IDs
        """
        keys = {}
        key_id = 0

        # Graph description
        key = SubElement(root, 'key')
        key.set('attr.name', 'Description')
        key.set('attr.type', 'string')
        key.set('for', 'graph')
        key.set('id', f'd{key_id}')
        keys['graph_description'] = f'd{key_id}'
        key_id += 1

        # Port graphics
        for port_type in ['portgraphics', 'portgeometry', 'portuserdata']:
            key = SubElement(root, 'key')
            key.set('for', 'port')
            key.set('id', f'd{key_id}')
            key.set('yfiles.type', port_type)
            keys[f'port_{port_type}'] = f'd{key_id}'
            key_id += 1

        # Node attributes
        for attr in ['label', 'extended_label', 'url', 'description', 'period', 'area', 'formation', 'unita_tipo', 'interpretation']:
            key = SubElement(root, 'key')
            key.set('attr.name', attr)
            key.set('attr.type', 'string')
            key.set('for', 'node')
            key.set('id', f'd{key_id}')
            keys[f'node_{attr}'] = f'd{key_id}'
            key_id += 1

        # Node graphics
        key = SubElement(root, 'key')
        key.set('for', 'node')
        key.set('id', f'd{key_id}')
        key.set('yfiles.type', 'nodegraphics')
        keys['node_graphics'] = f'd{key_id}'
        key_id += 1

        # Resources
        key = SubElement(root, 'key')
        key.set('for', 'graphml')
        key.set('id', f'd{key_id}')
        key.set('yfiles.type', 'resources')
        keys['resources'] = f'd{key_id}'
        key_id += 1

        # Edge attributes
        for attr in ['label', 'relationship', 'certainty', 'url', 'description']:
            key = SubElement(root, 'key')
            key.set('attr.name', attr)
            key.set('attr.type', 'string')
            key.set('for', 'edge')
            key.set('id', f'd{key_id}')
            keys[f'edge_{attr}'] = f'd{key_id}'
            key_id += 1

        # Edge graphics
        key = SubElement(root, 'key')
        key.set('for', 'edge')
        key.set('id', f'd{key_id}')
        key.set('yfiles.type', 'edgegraphics')
        keys['edge_graphics'] = f'd{key_id}'
        key_id += 1

        # Resources (for SVG definitions)
        key = SubElement(root, 'key')
        key.set('for', 'graphml')
        key.set('id', f'd{key_id}')
        key.set('yfiles.type', 'resources')
        keys['resources'] = f'd{key_id}'
        key_id += 1

        return keys

    @staticmethod
    def create_table_node_header(
        parent: Element,
        title: str,
        rows: List[Tuple[str, str]],  # (row_id, row_label)
        width: float = 1044.0,
        row_height: float = 940.0
    ) -> Element:
        """
        Create TableNode structure for period clustering

        Args:
            parent: Parent XML element
            title: Main title (site name)
            rows: List of (row_id, row_label) tuples for periods
            width: Table width
            row_height: Height of each row

        Returns:
            TableNode element
        """
        # Calculate total height
        total_height = row_height * len(rows) + 200  # +200 for header/footer

        # Create TableNode
        table_node = SubElement(parent, '{http://www.yworks.com/xml/graphml}TableNode')
        table_node.set('configuration', 'YED_TABLE_NODE')

        # Geometry
        geometry = SubElement(table_node, '{http://www.yworks.com/xml/graphml}Geometry')
        geometry.set('height', str(total_height))
        geometry.set('width', str(width))
        geometry.set('x', '-29.0')
        geometry.set('y', '-596.1141011840689')

        # Fill
        fill = SubElement(table_node, '{http://www.yworks.com/xml/graphml}Fill')
        fill.set('color', '#ECF5FF')
        fill.set('color2', '#0042F440')
        fill.set('transparent', 'false')

        # Border
        border = SubElement(table_node, '{http://www.yworks.com/xml/graphml}BorderStyle')
        border.set('color', '#000000')
        border.set('type', 'line')
        border.set('width', '1.0')

        # Title label
        title_label = SubElement(table_node, '{http://www.yworks.com/xml/graphml}NodeLabel')
        title_label.set('alignment', 'center')
        title_label.set('autoSizePolicy', 'content')
        title_label.set('fontFamily', 'DialogInputInput')
        title_label.set('fontSize', '24')
        title_label.set('fontStyle', 'bold')
        title_label.set('hasBackgroundColor', 'false')
        title_label.set('hasLineColor', 'false')
        title_label.set('height', '32.265625')
        title_label.set('horizontalTextPosition', 'center')
        title_label.set('iconTextGap', '4')
        title_label.set('modelName', 'internal')
        title_label.set('modelPosition', 't')
        title_label.set('textColor', '#000000')
        title_label.set('verticalTextPosition', 'bottom')
        title_label.set('visible', 'true')
        title_label.set('width', '239.88671875')
        title_label.set('x', str(width / 2 - 120))
        title_label.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        title_label.set('y', '4.0')
        title_label.text = title

        # Add row labels (period names)
        for i, (row_id, row_label) in enumerate(rows):
            row_label_elem = SubElement(table_node, '{http://www.yworks.com/xml/graphml}NodeLabel')
            row_label_elem.set('alignment', 'center')
            row_label_elem.set('autoSizePolicy', 'content')
            row_label_elem.set('fontFamily', 'DialogInput')
            row_label_elem.set('fontSize', '24')
            row_label_elem.set('fontStyle', 'bold')
            row_label_elem.set('backgroundColor', YEdTemplate.generate_period_color())
            row_label_elem.set('hasLineColor', 'false')
            row_label_elem.set('height', '32.265625')
            row_label_elem.set('horizontalTextPosition', 'center')
            row_label_elem.set('iconTextGap', '4')
            row_label_elem.set('modelName', 'custom')
            row_label_elem.set('rotationAngle', '270.0')  # Vertical text
            row_label_elem.set('textColor', '#000000')
            row_label_elem.set('verticalTextPosition', 'bottom')
            row_label_elem.set('visible', 'true')
            row_label_elem.set('width', '241.26953125')
            row_label_elem.set('x', '3.0')
            row_label_elem.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')

            # Calculate Y position for this row
            y_pos = 100 + (i * row_height) + (row_height / 2)
            row_label_elem.set('y', str(y_pos))
            row_label_elem.text = row_label

            # Add LabelModel
            label_model = SubElement(row_label_elem, '{http://www.yworks.com/xml/graphml}LabelModel')
            row_node_model = SubElement(label_model, '{http://www.yworks.com/xml/graphml}RowNodeLabelModel')
            row_node_model.set('offset', '3.0')

            # Add ModelParameter
            model_param = SubElement(row_label_elem, '{http://www.yworks.com/xml/graphml}ModelParameter')
            row_param = SubElement(model_param, '{http://www.yworks.com/xml/graphml}RowNodeLabelModelParameter')
            row_param.set('horizontalPosition', '0.0')
            row_param.set('id', row_id)
            row_param.set('inside', 'true')

        # Style properties
        style_props = SubElement(table_node, '{http://www.yworks.com/xml/graphml}StyleProperties')

        # Add standard yEd table properties
        for prop_name, prop_value in [
            ('y.view.tabular.TableNodePainter.ALTERNATE_ROW_STYLE', None),
            ('y.view.tabular.TableNodePainter.ALTERNATE_COLUMN_SELECTION_STYLE', None),
            ('y.view.tabular.TableNodePainter.ALTERNATE_ROW_SELECTION_STYLE', None),
        ]:
            prop = SubElement(style_props, '{http://www.yworks.com/xml/graphml}Property')
            prop.set('name', prop_name)
            simple_style = SubElement(prop, '{http://www.yworks.com/xml/graphml}SimpleStyle')
            simple_style.set('fillColor', '#474A4340')
            simple_style.set('lineColor', '#000000')
            simple_style.set('lineType', 'line')
            simple_style.set('lineWidth', '1.0')

        # Color properties
        for prop_name, prop_value, prop_class in [
            ('yed.table.section.color', '#7192b2', 'java.awt.Color'),
            ('yed.table.header.height', '54.0', 'java.lang.Double'),
            ('yed.table.header.font.size', '12', 'java.lang.Integer'),
            ('yed.table.lane.color.main', '#c4d7ed', 'java.awt.Color'),
            ('yed.table.header.color.alternating', '#abc8e2', 'java.awt.Color'),
            ('yed.table.lane.style', 'lane.style.rows', 'java.lang.String'),
        ]:
            prop = SubElement(style_props, '{http://www.yworks.com/xml/graphml}Property')
            prop.set('class', prop_class)
            prop.set('name', prop_name)
            prop.set('value', prop_value)

        # State
        state = SubElement(table_node, '{http://www.yworks.com/xml/graphml}State')
        state.set('autoResize', 'true')
        state.set('closed', 'false')
        state.set('closedHeight', '80.0')
        state.set('closedWidth', '100.0')

        # Insets
        insets = SubElement(table_node, '{http://www.yworks.com/xml/graphml}Insets')
        for attr in ['bottom', 'left', 'right', 'top']:
            insets.set(attr, '0')
            insets.set(f'{attr}F', '0.0')

        # Border insets
        border_insets = SubElement(table_node, '{http://www.yworks.com/xml/graphml}BorderInsets')
        border_insets.set('bottom', '62')
        border_insets.set('bottomF', '61.8')
        border_insets.set('left', '40')
        border_insets.set('leftF', '40.0')
        border_insets.set('right', '40')
        border_insets.set('rightF', '40.0')
        border_insets.set('top', '70')
        border_insets.set('topF', '71.0')

        # Table structure
        table = SubElement(table_node, '{http://www.yworks.com/xml/graphml}Table')
        table.set('autoResizeTable', 'true')
        table.set('defaultColumnWidth', '120.0')
        table.set('defaultMinimumColumnWidth', '80.0')
        table.set('defaultMinimumRowHeight', '50.0')
        table.set('defaultRowHeight', '80.0')

        # Default insets
        default_col_insets = SubElement(table, '{http://www.yworks.com/xml/graphml}DefaultColumnInsets')
        for attr in ['bottom', 'left', 'right', 'top']:
            default_col_insets.set(attr, '0.0')

        default_row_insets = SubElement(table, '{http://www.yworks.com/xml/graphml}DefaultRowInsets')
        default_row_insets.set('bottom', '0.0')
        default_row_insets.set('left', '54.0')
        default_row_insets.set('right', '0.0')
        default_row_insets.set('top', '0.0')

        table_insets = SubElement(table, '{http://www.yworks.com/xml/graphml}Insets')
        table_insets.set('bottom', '0.0')
        table_insets.set('left', '0.0')
        table_insets.set('right', '0.0')
        table_insets.set('top', '30.0')

        # Columns
        columns = SubElement(table, '{http://www.yworks.com/xml/graphml}Columns')
        column = SubElement(columns, '{http://www.yworks.com/xml/graphml}Column')
        column.set('id', 'column_0')
        column.set('minimumWidth', '80.0')
        column.set('width', str(width - 24))
        col_insets = SubElement(column, '{http://www.yworks.com/xml/graphml}Insets')
        for attr in ['bottom', 'left', 'right', 'top']:
            col_insets.set(attr, '0.0')

        # Rows
        rows_elem = SubElement(table, '{http://www.yworks.com/xml/graphml}Rows')
        for row_id, row_label in rows:
            row = SubElement(rows_elem, '{http://www.yworks.com/xml/graphml}Row')
            row.set('height', str(row_height))
            row.set('id', row_id)
            row.set('minimumHeight', '50.0')
            row_insets = SubElement(row, '{http://www.yworks.com/xml/graphml}Insets')
            row_insets.set('bottom', '0.0')
            row_insets.set('left', '54.0')
            row_insets.set('right', '0.0')
            row_insets.set('top', '0.0')

        return table_node


# Color helpers
def sanitize_period_name(period_name: str) -> str:
    """Sanitize period name for use as XML ID"""
    import re
    # Replace spaces and special chars with underscore
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', period_name)
    # Remove consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    return sanitized or 'period'
