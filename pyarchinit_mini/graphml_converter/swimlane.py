"""
Swimlane module for GraphML files.

This module provides functionality to organize GraphML nodes into swimlanes
(horizontal rows) based on grouping criteria like archaeological periods or areas,
similar to yEd's swimlane tool.

Swimlanes are implemented using yEd's TableNode structure with rows representing
different groups (e.g., periods) and nodes positioned within their respective rows.
"""

import xml.dom.minidom as minidom
from typing import Dict, List, Optional, Set, Tuple
import re


class SwimlaneOrganizer:
    """
    Organizes GraphML nodes into swimlanes using yEd TableNode structure.

    This creates a visual layout where nodes are grouped horizontally by category
    (e.g., archaeological periods), with each group in its own row (swimlane).
    """

    def __init__(self, graphml_content: str):
        """
        Initialize swimlane organizer with GraphML content.

        Args:
            graphml_content: XML string containing GraphML data
        """
        self.graphml_content = graphml_content
        self.dom = minidom.parseString(graphml_content)
        self.periods: Set[str] = set()
        self.node_to_period: Dict[str, str] = {}

    def extract_periods_from_labels(self) -> Dict[str, str]:
        """
        Extract period information from node labels.

        Assumes node labels follow format: US{number}_{period}
        Example: US1001_Romano-Imperiale → period = "Romano-Imperiale"

        Returns:
            Dictionary mapping node IDs to their periods
        """
        node_to_period = {}

        # Find all ShapeNode elements (stratigraphic units)
        for shape_node in self.dom.getElementsByTagName('y:ShapeNode'):
            # Get node label
            labels = shape_node.getElementsByTagName('y:NodeLabel')
            if not labels or not labels[0].firstChild:
                continue

            label_text = labels[0].firstChild.nodeValue

            # Extract period from label (format: US{number}_{period})
            match = re.match(r'US\d+_(.+)', label_text)
            if match:
                period = match.group(1).replace('-', ' ')  # Romano-Imperiale → Romano Imperiale

                # Find parent node element to get node ID
                data_element = shape_node.parentNode
                node_element = data_element.parentNode
                node_id = node_element.getAttribute('id')

                node_to_period[node_id] = period
                self.periods.add(period)

        self.node_to_period = node_to_period
        return node_to_period

    def create_table_node_structure(
        self,
        title: str = "Archaeological Context",
        row_colors: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Create yEd TableNode swimlane structure.

        Args:
            title: Header title for the table
            row_colors: Optional dict mapping period names to background colors

        Returns:
            Node ID of the created TableNode group
        """
        if not self.periods:
            self.extract_periods_from_labels()

        if not self.periods:
            raise ValueError("No periods found in GraphML. Cannot create swimlanes.")

        # Default colors for rows (alternating)
        if row_colors is None:
            row_colors = {
                period: '#CCFFCC' if i % 2 == 0 else '#FFCC7F'
                for i, period in enumerate(sorted(self.periods))
            }

        # Get graph element
        graph_elements = self.dom.getElementsByTagName('graph')
        if not graph_elements:
            raise ValueError("No graph element found in GraphML")

        graph = graph_elements[0]

        # Create TableNode group element
        table_node_id = "swimlane_table"
        table_node = self.dom.createElement('node')
        table_node.setAttribute('id', table_node_id)
        table_node.setAttribute('yfiles.foldertype', 'group')

        # Add description
        desc_data = self.dom.createElement('data')
        desc_data.setAttribute('key', 'd6')
        desc_text = self.dom.createTextNode('Stratigrafia')
        desc_data.appendChild(desc_text)
        table_node.appendChild(desc_data)

        # Create TableNode graphics
        graphics_data = self.dom.createElement('data')
        graphics_data.setAttribute('key', 'd7')

        y_table_node = self.dom.createElement('y:TableNode')
        y_table_node.setAttribute('configuration', 'YED_TABLE_NODE')

        # Geometry (will be auto-resized)
        geometry = self.dom.createElement('y:Geometry')
        geometry.setAttribute('height', '2000.0')
        geometry.setAttribute('width', '1500.0')
        geometry.setAttribute('x', '100.0')
        geometry.setAttribute('y', '100.0')
        y_table_node.appendChild(geometry)

        # Fill
        fill = self.dom.createElement('y:Fill')
        fill.setAttribute('color', '#ECF5FF')
        fill.setAttribute('color2', '#0042F440')
        fill.setAttribute('transparent', 'false')
        y_table_node.appendChild(fill)

        # Border
        border = self.dom.createElement('y:BorderStyle')
        border.setAttribute('hasColor', 'false')
        border.setAttribute('type', 'line')
        border.setAttribute('width', '1.0')
        y_table_node.appendChild(border)

        # Header label
        header_label = self.dom.createElement('y:NodeLabel')
        header_label.setAttribute('alignment', 'center')
        header_label.setAttribute('autoSizePolicy', 'content')
        header_label.setAttribute('fontFamily', 'Dialog')
        header_label.setAttribute('fontSize', '15')
        header_label.setAttribute('modelName', 'internal')
        header_label.setAttribute('modelPosition', 't')
        header_label.setAttribute('visible', 'true')
        header_text = self.dom.createTextNode(title)
        header_label.appendChild(header_text)
        y_table_node.appendChild(header_label)

        # Create row labels for each period
        sorted_periods = sorted(self.periods)
        for i, period in enumerate(sorted_periods):
            row_label = self.dom.createElement('y:NodeLabel')
            row_label.setAttribute('alignment', 'center')
            row_label.setAttribute('autoSizePolicy', 'content')
            row_label.setAttribute('backgroundColor', row_colors.get(period, '#CCCCCC'))
            row_label.setAttribute('fontFamily', 'Dialog')
            row_label.setAttribute('fontSize', '12')
            row_label.setAttribute('fontStyle', 'plain')
            row_label.setAttribute('hasLineColor', 'false')
            row_label.setAttribute('modelName', 'custom')
            row_label.setAttribute('rotationAngle', '270.0')  # Vertical text
            row_label.setAttribute('textColor', '#000000')
            row_label.setAttribute('visible', 'true')

            # Label text
            period_text = self.dom.createTextNode(period)
            row_label.appendChild(period_text)

            # Model for row positioning
            label_model = self.dom.createElement('y:LabelModel')
            row_model = self.dom.createElement('y:RowNodeLabelModel')
            row_model.setAttribute('offset', '3.0')
            label_model.appendChild(row_model)
            row_label.appendChild(label_model)

            model_param = self.dom.createElement('y:ModelParameter')
            row_param = self.dom.createElement('y:RowNodeLabelModelParameter')
            row_param.setAttribute('horizontalPosition', '0.0')
            row_param.setAttribute('id', f'row_{i}')
            row_param.setAttribute('inside', 'true')
            model_param.appendChild(row_param)
            row_label.appendChild(model_param)

            y_table_node.appendChild(row_label)

        # Style properties
        style_props = self.dom.createElement('y:StyleProperties')

        # Add various table styling properties
        props = [
            ('y.view.tabular.TableNodePainter.ALTERNATE_ROW_STYLE',
             '#474A4340', '#000000', 'line', '1.0'),
            ('y.view.tabular.TableNodePainter.ALTERNATE_COLUMN_STYLE',
             '#474A4340', '#000000', 'line', '1.0'),
        ]

        for prop_name, fill_color, line_color, line_type, line_width in props:
            prop = self.dom.createElement('y:Property')
            prop.setAttribute('name', prop_name)
            simple_style = self.dom.createElement('y:SimpleStyle')
            simple_style.setAttribute('fillColor', fill_color)
            simple_style.setAttribute('lineColor', line_color)
            simple_style.setAttribute('lineType', line_type)
            simple_style.setAttribute('lineWidth', line_width)
            prop.appendChild(simple_style)
            style_props.appendChild(prop)

        # Color properties
        color_props = [
            ('yed.table.section.color', '#7192b2'),
            ('yed.table.lane.color.main', '#c4d7ed'),
            ('yed.table.lane.color.alternating', '#abc8e2'),
            ('yed.table.header.color.main', '#c4d7ed'),
            ('yed.table.header.color.alternating', '#abc8e2'),
        ]

        for prop_name, color in color_props:
            prop = self.dom.createElement('y:Property')
            prop.setAttribute('class', 'java.awt.Color')
            prop.setAttribute('name', prop_name)
            prop.setAttribute('value', color)
            style_props.appendChild(prop)

        # Lane style
        lane_style = self.dom.createElement('y:Property')
        lane_style.setAttribute('class', 'java.lang.String')
        lane_style.setAttribute('name', 'yed.table.lane.style')
        lane_style.setAttribute('value', 'lane.style.rows')
        style_props.appendChild(lane_style)

        y_table_node.appendChild(style_props)

        # State
        state = self.dom.createElement('y:State')
        state.setAttribute('autoResize', 'true')
        state.setAttribute('closed', 'false')
        y_table_node.appendChild(state)

        # Insets
        insets = self.dom.createElement('y:Insets')
        insets.setAttribute('bottom', '0')
        insets.setAttribute('left', '0')
        insets.setAttribute('right', '0')
        insets.setAttribute('top', '0')
        y_table_node.appendChild(insets)

        # Border insets
        border_insets = self.dom.createElement('y:BorderInsets')
        border_insets.setAttribute('bottom', '10')
        border_insets.setAttribute('left', '14')
        border_insets.setAttribute('right', '20')
        border_insets.setAttribute('top', '5')
        y_table_node.appendChild(border_insets)

        # Table structure
        table = self.dom.createElement('y:Table')
        table.setAttribute('autoResizeTable', 'true')
        table.setAttribute('defaultColumnWidth', '120.0')
        table.setAttribute('defaultRowHeight', '200.0')

        # Columns
        columns = self.dom.createElement('y:Columns')
        column = self.dom.createElement('y:Column')
        column.setAttribute('id', 'column_0')
        column.setAttribute('minimumWidth', '80.0')
        column.setAttribute('width', '1500.0')
        columns.appendChild(column)
        table.appendChild(columns)

        # Rows - one for each period
        rows = self.dom.createElement('y:Rows')
        for i, period in enumerate(sorted_periods):
            row = self.dom.createElement('y:Row')
            row.setAttribute('height', '300.0')  # Will auto-resize
            row.setAttribute('id', f'row_{i}')
            row.setAttribute('minimumHeight', '50.0')
            rows.appendChild(row)
        table.appendChild(rows)

        y_table_node.appendChild(table)
        graphics_data.appendChild(y_table_node)
        table_node.appendChild(graphics_data)

        # Add nested graph for child nodes
        nested_graph = self.dom.createElement('graph')
        nested_graph.setAttribute('edgedefault', 'directed')
        nested_graph.setAttribute('id', f'{table_node_id}:')
        table_node.appendChild(nested_graph)

        # Insert table node into main graph
        graph.insertBefore(table_node, graph.firstChild)

        return table_node_id

    def move_nodes_to_swimlanes(self, table_node_id: str) -> None:
        """
        Move existing nodes into the TableNode swimlane structure.

        Args:
            table_node_id: ID of the TableNode group element
        """
        if not self.node_to_period:
            self.extract_periods_from_labels()

        # Find the TableNode's nested graph
        table_node = self.dom.getElementById(table_node_id)
        if not table_node:
            raise ValueError(f"TableNode with id '{table_node_id}' not found")

        nested_graphs = table_node.getElementsByTagName('graph')
        if not nested_graphs:
            raise ValueError(f"No nested graph found in TableNode '{table_node_id}'")

        nested_graph = nested_graphs[0]

        # Find main graph
        main_graphs = [g for g in self.dom.getElementsByTagName('graph')
                      if g.getAttribute('id') == 'G']
        if not main_graphs:
            raise ValueError("Main graph with id='G' not found")

        main_graph = main_graphs[0]

        # Move nodes to nested graph
        nodes_to_move = []
        for node in main_graph.getElementsByTagName('node'):
            if node.getAttribute('id') == table_node_id:
                continue  # Skip the table node itself
            nodes_to_move.append(node)

        for node in nodes_to_move:
            main_graph.removeChild(node)
            nested_graph.appendChild(node)

    def apply_swimlanes(
        self,
        title: str = "Archaeological Context",
        row_colors: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Apply swimlane organization to GraphML.

        This is the main entry point that:
        1. Extracts periods from node labels
        2. Creates TableNode structure
        3. Moves nodes into swimlanes

        Args:
            title: Header title for the swimlane table
            row_colors: Optional dict mapping period names to background colors

        Returns:
            Modified GraphML content as XML string
        """
        # Extract periods
        self.extract_periods_from_labels()

        # Create table structure
        table_node_id = self.create_table_node_structure(title, row_colors)

        # Move nodes into table
        self.move_nodes_to_swimlanes(table_node_id)

        # Return modified GraphML
        return self.dom.toxml()


def apply_swimlanes_to_graphml(
    graphml_content: str,
    title: str = "Archaeological Context",
    row_colors: Optional[Dict[str, str]] = None
) -> str:
    """
    Convenience function to apply swimlanes to GraphML content.

    Args:
        graphml_content: XML string containing GraphML data
        title: Header title for the swimlane table
        row_colors: Optional dict mapping period names to background colors

    Returns:
        Modified GraphML content with swimlane structure

    Example:
        >>> graphml = open('harris_matrix.graphml').read()
        >>> swimlane_graphml = apply_swimlanes_to_graphml(
        ...     graphml,
        ...     title="Pompei Excavation",
        ...     row_colors={'Moderno': '#CCFFCC', 'Medievale': '#FFCC7F'}
        ... )
        >>> with open('harris_matrix_swimlanes.graphml', 'w') as f:
        ...     f.write(swimlane_graphml)
    """
    organizer = SwimlaneOrganizer(graphml_content)
    return organizer.apply_swimlanes(title, row_colors)
