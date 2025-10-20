"""
Swimlane module for GraphML files.

This module provides functionality to organize GraphML nodes into swimlanes
(horizontal rows) based on grouping criteria like archaeological periods or areas,
similar to yEd's swimlane tool.

Swimlanes are implemented by organizing nodes by Y-coordinate position, with each
period occupying a horizontal "lane" or row in the visualization.
"""

import xml.dom.minidom as minidom
from typing import Dict, List, Optional, Set, Tuple
import re


class SwimlaneOrganizer:
    """
    Organizes GraphML nodes into swimlanes by setting Y-coordinates based on periods.

    yEd's swimlane system works by:
    1. Creating a TableNode group with rows for each period
    2. Positioning nodes at different Y-coordinates based on their period
    3. Nodes at y=0 go in first row, y=1000 in second row, etc.
    4. Nodes remain in the main graph (not moved to nested graph)
    """

    def __init__(self, graphml_content: str, period_mapping: Optional[Dict[int, str]] = None):
        """
        Initialize swimlane organizer with GraphML content.

        Args:
            graphml_content: XML string containing GraphML data
            period_mapping: Optional dict mapping US numbers to period names
                           Example: {1001: 'Romano Imperiale', 1002: 'Medievale'}
        """
        self.graphml_content = graphml_content
        self.dom = minidom.parseString(graphml_content)
        self.periods: List[str] = []  # Ordered list of periods
        self.node_to_period: Dict[str, str] = {}
        self.us_to_period: Optional[Dict[int, str]] = period_mapping

        # Extract periods from mapping if provided
        if period_mapping:
            unique_periods = sorted(set(period_mapping.values()), reverse=True)
            self.periods = unique_periods

    def extract_periods_from_labels(self) -> Dict[str, str]:
        """
        Extract period information from node labels.

        Returns:
            Dictionary mapping node IDs to their periods
        """
        node_to_period = {}

        # Use provided period mapping if available
        if self.us_to_period:
            # Map GraphML node IDs to periods using US numbers from labels
            for shape_node in self.dom.getElementsByTagName('y:ShapeNode'):
                labels = shape_node.getElementsByTagName('y:NodeLabel')
                if not labels or not labels[0].firstChild:
                    continue

                label_text = labels[0].firstChild.nodeValue.strip()

                # Extract US number from label (format: US{number} or USM{number})
                us_match = re.match(r'USM?\s*(\d+)', label_text, re.MULTILINE)
                if us_match:
                    us_number = int(us_match.group(1))

                    # Find parent node element to get node ID
                    data_element = shape_node.parentNode
                    node_element = data_element.parentNode
                    node_id = node_element.getAttribute('id')

                    # Look up period from mapping
                    if us_number in self.us_to_period:
                        period = self.us_to_period[us_number]
                        node_to_period[node_id] = period

        self.node_to_period = node_to_period
        return node_to_period

    def create_table_node_group(
        self,
        title: str = "Archaeological Context",
        row_colors: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Create yEd TableNode group element for swimlane organization.

        This creates a visual grouping/container but DOES NOT move nodes into it.
        Nodes stay in main graph and are positioned by Y-coordinate.

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

        # Default colors for rows
        if row_colors is None:
            colors = ['#5AE9EA', '#992694', '#5EE692', '#FFD700', '#FF6347', '#4169E1']
            row_colors = {
                period: colors[i % len(colors)]
                for i, period in enumerate(self.periods)
            }

        # Get graph element
        graph_elements = self.dom.getElementsByTagName('graph')
        if not graph_elements:
            raise ValueError("No graph element found in GraphML")

        main_graph = graph_elements[0]

        # Create TableNode group element
        table_node_id = "swimlane_table"
        table_node = self.dom.createElement('node')
        table_node.setAttribute('id', table_node_id)
        table_node.setAttribute('yfiles.foldertype', 'group')

        # Add description
        desc_data = self.dom.createElement('data')
        desc_data.setAttribute('key', 'd5')
        desc_data.setAttribute('xml:space', 'preserve')
        desc_text = self.dom.createCDATASection('Stratigrafia')
        desc_data.appendChild(desc_text)
        table_node.appendChild(desc_data)

        # Create TableNode graphics
        graphics_data = self.dom.createElement('data')
        graphics_data.setAttribute('key', 'd6')

        y_table_node = self.dom.createElement('y:TableNode')
        y_table_node.setAttribute('configuration', 'YED_TABLE_NODE')

        # Geometry (height = num_periods * 1000 + some padding)
        total_height = len(self.periods) * 1000 + 200
        geometry = self.dom.createElement('y:Geometry')
        geometry.setAttribute('height', str(total_height))
        geometry.setAttribute('width', '1500.0')
        geometry.setAttribute('x', '100.0')
        geometry.setAttribute('y', '0.0')
        y_table_node.appendChild(geometry)

        # Fill
        fill = self.dom.createElement('y:Fill')
        fill.setAttribute('color', '#ECF5FF')
        fill.setAttribute('color2', '#0042F440')
        fill.setAttribute('transparent', 'false')
        y_table_node.appendChild(fill)

        # Border
        border = self.dom.createElement('y:BorderStyle')
        border.setAttribute('color', '#000000')
        border.setAttribute('type', 'line')
        border.setAttribute('width', '1.0')
        y_table_node.appendChild(border)

        # Header label (title)
        header_label = self.dom.createElement('y:NodeLabel')
        header_label.setAttribute('alignment', 'center')
        header_label.setAttribute('autoSizePolicy', 'content')
        header_label.setAttribute('fontFamily', 'DialogInputInput')
        header_label.setAttribute('fontSize', '24')
        header_label.setAttribute('fontStyle', 'bold')
        header_label.setAttribute('hasBackgroundColor', 'false')
        header_label.setAttribute('hasLineColor', 'false')
        header_label.setAttribute('height', '32.265625')
        header_label.setAttribute('horizontalTextPosition', 'center')
        header_label.setAttribute('iconTextGap', '4')
        header_label.setAttribute('modelName', 'internal')
        header_label.setAttribute('modelPosition', 't')
        header_label.setAttribute('textColor', '#000000')
        header_label.setAttribute('verticalTextPosition', 'bottom')
        header_label.setAttribute('visible', 'true')
        header_label.setAttribute('xml:space', 'preserve')
        header_text = self.dom.createTextNode(title)
        header_label.appendChild(header_text)
        y_table_node.appendChild(header_label)

        # Create row labels for each period (swimlane labels)
        for i, period in enumerate(self.periods):
            row_label = self.dom.createElement('y:NodeLabel')
            row_label.setAttribute('alignment', 'center')
            row_label.setAttribute('autoSizePolicy', 'content')
            row_label.setAttribute('backgroundColor', row_colors.get(period, '#CCCCCC'))
            row_label.setAttribute('fontFamily', 'DialogInput')
            row_label.setAttribute('fontSize', '24')
            row_label.setAttribute('fontStyle', 'bold')
            row_label.setAttribute('hasLineColor', 'false')
            row_label.setAttribute('height', '32.265625')
            row_label.setAttribute('horizontalTextPosition', 'center')
            row_label.setAttribute('iconTextGap', '4')
            row_label.setAttribute('modelName', 'custom')
            row_label.setAttribute('rotationAngle', '270.0')  # Vertical text
            row_label.setAttribute('textColor', '#000000')
            row_label.setAttribute('verticalTextPosition', 'bottom')
            row_label.setAttribute('visible', 'true')
            row_label.setAttribute('xml:space', 'preserve')

            # Label text
            period_text = self.dom.createTextNode(period)
            row_label.appendChild(period_text)

            # Label model for row positioning
            label_model = self.dom.createElement('y:LabelModel')
            row_model = self.dom.createElement('y:RowNodeLabelModel')
            row_model.setAttribute('offset', '3.0')
            label_model.appendChild(row_model)
            row_label.appendChild(label_model)

            # Model parameter
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

        # Alternate row style
        prop1 = self.dom.createElement('y:Property')
        prop1.setAttribute('name', 'y.view.tabular.TableNodePainter.ALTERNATE_ROW_STYLE')
        simple_style1 = self.dom.createElement('y:SimpleStyle')
        simple_style1.setAttribute('fillColor', '#474A4340')
        simple_style1.setAttribute('lineColor', '#000000')
        simple_style1.setAttribute('lineType', 'line')
        simple_style1.setAttribute('lineWidth', '1.0')
        prop1.appendChild(simple_style1)
        style_props.appendChild(prop1)

        # Color properties
        color_props = [
            ('yed.table.section.color', 'java.awt.Color', '#7192b2'),
            ('yed.table.lane.color.main', 'java.awt.Color', '#c4d7ed'),
            ('yed.table.header.color.alternating', 'java.awt.Color', '#abc8e2'),
        ]

        for prop_name, prop_class, color in color_props:
            prop = self.dom.createElement('y:Property')
            prop.setAttribute('class', prop_class)
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
        insets.setAttribute('bottomF', '0.0')
        insets.setAttribute('left', '0')
        insets.setAttribute('leftF', '0.0')
        insets.setAttribute('right', '0')
        insets.setAttribute('rightF', '0.0')
        insets.setAttribute('top', '0')
        insets.setAttribute('topF', '0.0')
        y_table_node.appendChild(insets)

        # Border insets
        border_insets = self.dom.createElement('y:BorderInsets')
        border_insets.setAttribute('bottom', '62')
        border_insets.setAttribute('bottomF', '61.8')
        border_insets.setAttribute('left', '40')
        border_insets.setAttribute('leftF', '40.0')
        border_insets.setAttribute('right', '40')
        border_insets.setAttribute('rightF', '40.0')
        border_insets.setAttribute('top', '71')
        border_insets.setAttribute('topF', '71.0')
        y_table_node.appendChild(border_insets)

        # Table structure
        table = self.dom.createElement('y:Table')
        table.setAttribute('autoResizeTable', 'true')
        table.setAttribute('defaultColumnWidth', '120.0')
        table.setAttribute('defaultMinimumColumnWidth', '80.0')
        table.setAttribute('defaultMinimumRowHeight', '50.0')
        table.setAttribute('defaultRowHeight', '80.0')

        # Default column insets
        default_col_insets = self.dom.createElement('y:DefaultColumnInsets')
        default_col_insets.setAttribute('bottom', '0.0')
        default_col_insets.setAttribute('left', '0.0')
        default_col_insets.setAttribute('right', '0.0')
        default_col_insets.setAttribute('top', '0.0')
        table.appendChild(default_col_insets)

        # Default row insets (left margin for period labels)
        default_row_insets = self.dom.createElement('y:DefaultRowInsets')
        default_row_insets.setAttribute('bottom', '0.0')
        default_row_insets.setAttribute('left', '54.0')  # Space for period label
        default_row_insets.setAttribute('right', '0.0')
        default_row_insets.setAttribute('top', '0.0')
        table.appendChild(default_row_insets)

        # Table insets
        table_insets = self.dom.createElement('y:Insets')
        table_insets.setAttribute('bottom', '0.0')
        table_insets.setAttribute('left', '0.0')
        table_insets.setAttribute('right', '0.0')
        table_insets.setAttribute('top', '30.0')
        table.appendChild(table_insets)

        # Columns
        columns = self.dom.createElement('y:Columns')
        column = self.dom.createElement('y:Column')
        column.setAttribute('id', 'column_0')
        column.setAttribute('minimumWidth', '80.0')
        column.setAttribute('width', '1020.0')
        col_insets = self.dom.createElement('y:Insets')
        col_insets.setAttribute('bottom', '0.0')
        col_insets.setAttribute('left', '0.0')
        col_insets.setAttribute('right', '0.0')
        col_insets.setAttribute('top', '0.0')
        column.appendChild(col_insets)
        columns.appendChild(column)
        table.appendChild(columns)

        # Rows - one for each period
        rows = self.dom.createElement('y:Rows')
        for i, period in enumerate(self.periods):
            row = self.dom.createElement('y:Row')
            row.setAttribute('height', '940.0')  # Height of each swimlane
            row.setAttribute('id', f'row_{i}')
            row.setAttribute('minimumHeight', '50.0')

            # Row insets (left margin for period label)
            row_insets = self.dom.createElement('y:Insets')
            row_insets.setAttribute('bottom', '0.0')
            row_insets.setAttribute('left', '54.0')
            row_insets.setAttribute('right', '0.0')
            row_insets.setAttribute('top', '0.0')
            row.appendChild(row_insets)

            rows.appendChild(row)
        table.appendChild(rows)

        y_table_node.appendChild(table)
        graphics_data.appendChild(y_table_node)
        table_node.appendChild(graphics_data)

        # Add empty nested graph (required by yEd format, but nodes stay in main graph)
        nested_graph = self.dom.createElement('graph')
        nested_graph.setAttribute('edgedefault', 'directed')
        nested_graph.setAttribute('id', f'{table_node_id}:')
        table_node.appendChild(nested_graph)

        # Insert table node as first child of main graph
        main_graph.insertBefore(table_node, main_graph.firstChild)

        return table_node_id

    def position_nodes_by_period(self):
        """
        Set Y-coordinates of nodes based on their period assignment.

        Nodes are positioned at:
        - Period 0: y = 0.0
        - Period 1: y = 1000.0
        - Period 2: y = 2000.0
        - etc.

        This creates the swimlane effect without moving nodes in the DOM.
        """
        if not self.node_to_period:
            self.extract_periods_from_labels()

        # Find all ShapeNode elements (US nodes) and update their Y-coordinates
        for shape_node in self.dom.getElementsByTagName('y:ShapeNode'):
            # Find parent node element to get node ID
            data_element = shape_node.parentNode
            node_element = data_element.parentNode
            node_id = node_element.getAttribute('id')

            # Skip if this node doesn't have a period assigned
            if node_id not in self.node_to_period:
                continue

            # Get period and calculate Y-coordinate
            period = self.node_to_period[node_id]
            try:
                period_index = self.periods.index(period)
            except ValueError:
                continue

            # Y-coordinate for this period's swimlane
            y_coord = period_index * 1000.0

            # Update geometry Y-coordinate
            geometries = shape_node.getElementsByTagName('y:Geometry')
            if geometries:
                geometries[0].setAttribute('y', str(y_coord))

    def apply_swimlanes(
        self,
        title: str = "Archaeological Context",
        row_colors: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Apply swimlane organization to GraphML.

        This is the main entry point that:
        1. Extracts periods from node labels
        2. Creates TableNode group for visual swimlanes
        3. Positions nodes by Y-coordinate based on period

        Args:
            title: Header title for the swimlane table
            row_colors: Optional dict mapping period names to background colors

        Returns:
            Modified GraphML content as XML string
        """
        # Extract periods
        self.extract_periods_from_labels()

        # Create table structure (visual grouping)
        self.create_table_node_group(title, row_colors)

        # Position nodes by Y-coordinate
        self.position_nodes_by_period()

        # Return modified GraphML
        return self.dom.toxml()


def apply_swimlanes_to_graphml(
    graphml_content: str,
    title: str = "Archaeological Context",
    row_colors: Optional[Dict[str, str]] = None,
    period_mapping: Optional[Dict[int, str]] = None
) -> str:
    """
    Convenience function to apply swimlanes to GraphML content.

    Args:
        graphml_content: XML string containing GraphML data
        title: Header title for the swimlane table
        row_colors: Optional dict mapping period names to background colors
        period_mapping: Optional dict mapping US numbers to period names
                       Example: {1001: 'Romano Imperiale', 1002: 'Medievale'}

    Returns:
        Modified GraphML content with swimlane structure

    Example:
        >>> graphml = open('harris_matrix.graphml').read()
        >>> period_mapping = {1001: 'Medievale', 1002: 'Romano Imperiale'}
        >>> swimlane_graphml = apply_swimlanes_to_graphml(
        ...     graphml,
        ...     title="Pompei Excavation",
        ...     period_mapping=period_mapping
        ... )
        >>> with open('harris_matrix_swimlanes.graphml', 'w') as f:
        ...     f.write(swimlane_graphml)
    """
    organizer = SwimlaneOrganizer(graphml_content, period_mapping=period_mapping)
    return organizer.apply_swimlanes(title, row_colors)
