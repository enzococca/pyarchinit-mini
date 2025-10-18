# pyarchinit_mini/harris_matrix/pyarchinit_visualizer.py

## Overview

This file contains 5 documented elements.

## Classes

### PyArchInitMatrixVisualizer

Harris Matrix visualizer that replicates PyArchInit plugin behavior
Uses Graphviz with hierarchical orthogonal layout and period/area grouping

#### Methods

##### __init__(self)

Initializes a new instance of the Harris Matrix visualizer with a predefined set of default visualization settings. These settings control the appearance and layout of the matrix, including resolution, node and edge styles, grouping options, and legend visibility, to replicate the behavior of the PyArchInit plugin using Graphviz.

##### create_matrix(self, graph, grouping, settings, output_path)

Create Harris Matrix using PyArchInit approach

Args:
    graph: NetworkX directed graph with US nodes and relationships
    grouping: 'period_area', 'period', 'area', 'none'
    settings: Optional style settings override
    output_path: Optional output file path
    
Returns:
    Path to generated file

##### export_multiple_formats(self, graph, base_filename, grouping)

Export matrix in multiple formats

