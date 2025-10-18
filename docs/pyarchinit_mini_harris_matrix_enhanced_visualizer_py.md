# pyarchinit_mini/harris_matrix/enhanced_visualizer.py

## Overview

This file contains 8 documented elements.

## Classes

### EnhancedHarrisMatrixVisualizer

Enhanced Harris Matrix visualizer using Graphviz for hierarchical orthogonal layout
Supports area/period/phase grouping and all stratigraphic relationships

#### Methods

##### __init__(self)

**__init__**

Initializes the visualizer by configuring default styles and properties for stratigraphic relationships, area color assignments, and period shapes used in Harris Matrix diagrams. Sets up dictionaries that define the visual representation (such as color, line style, and arrowhead type) for different relationship types, as well as color codes for excavation areas and shapes for archaeological periods. These configurations are used throughout the visualizer to ensure consistent and meaningful graphical output.

##### create_graphviz_matrix(self, graph, grouping, output_format, output_path)

Create Harris Matrix using Graphviz with hierarchical orthogonal layout

Args:
    graph: NetworkX directed graph
    grouping: 'none', 'area', 'period', 'phase', or 'area_period'
    output_format: 'png', 'svg', 'pdf', 'dot'
    output_path: Optional output file path
    
Returns:
    Path to generated file or DOT source

##### create_temporal_matrix(self, graph, output_path)

Create Harris Matrix with temporal/chronological ordering
Groups by periods and phases with hierarchical display

##### export_multiple_formats(self, graph, base_filename, grouping)

Export Harris Matrix in multiple formats

##### create_relationship_legend(self, output_path)

Create a legend showing all relationship types and their visual styles

##### analyze_matrix_statistics(self, graph)

Analyze Harris Matrix and provide statistics

