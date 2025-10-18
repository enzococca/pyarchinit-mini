# pyarchinit_mini/harris_matrix/matrix_visualizer.py

## Overview

This file contains 21 documented elements.

## Classes

### MatrixVisualizer

Visualizes Harris Matrix using different rendering methods

#### Methods

##### __init__(self)

Initializes the visualizer with a set of default styling parameters for rendering Harris Matrices. This includes node dimensions, spacing, font size, and color schemes for various matrix elements, ensuring consistent visualization across different rendering methods.

##### render_matplotlib(self, graph, levels, output_path, style)

Render Harris Matrix using matplotlib

Args:
    graph: NetworkX graph
    levels: Matrix levels from generator
    output_path: Optional file path to save
    style: Optional style overrides
    
Returns:
    Base64 encoded image string

##### render_graphviz(self, graph, output_path)

Render Harris Matrix using Graphviz for better layouts

##### create_interactive_html(self, graph, levels)

Create interactive HTML visualization using D3.js or similar

##### export_to_formats(self, graph, levels, base_filename)

Export Harris Matrix to multiple formats

Returns:
    Dictionary mapping format to file path

### MatrixVisualizer

Visualizes Harris Matrix using different rendering methods

#### Methods

##### __init__(self)

Initializes a new instance of the visualizer with default style settings for rendering Harris Matrix diagrams. This method defines standard dimensions, spacing, font size, and color schemes to ensure consistent visualization appearance across different rendering methods. These default styles can later be customized or overridden as needed during rendering.

##### render_matplotlib(self, graph, levels, output_path, style)

Render Harris Matrix using matplotlib

Args:
    graph: NetworkX graph
    levels: Matrix levels from generator
    output_path: Optional file path to save
    style: Optional style overrides
    
Returns:
    Base64 encoded image string

##### render_graphviz(self, graph, output_path)

Render Harris Matrix using Graphviz for better layouts

##### create_interactive_html(self, graph, levels)

Create interactive HTML visualization using D3.js or similar

##### export_to_formats(self, graph, levels, base_filename)

Export Harris Matrix to multiple formats

Returns:
    Dictionary mapping format to file path

### MatrixVisualizer

Visualizes Harris Matrix using different rendering methods

#### Methods

##### __init__(self)

Initializes a new instance of the Harris Matrix visualizer with a set of default visualization styles and parameters. This includes default node dimensions, spacing, font size, and color schemes for various elements of the Harris Matrix diagram. These defaults are used unless overridden by custom style definitions during rendering.

##### render_matplotlib(self, graph, levels, output_path, style)

Render Harris Matrix using matplotlib

Args:
    graph: NetworkX graph
    levels: Matrix levels from generator
    output_path: Optional file path to save
    style: Optional style overrides
    
Returns:
    Base64 encoded image string

##### render_graphviz(self, graph, output_path)

Render Harris Matrix using Graphviz for better layouts

##### create_interactive_html(self, graph, levels)

Create interactive HTML visualization using D3.js or similar

##### export_to_formats(self, graph, levels, base_filename)

Export Harris Matrix to multiple formats

Returns:
    Dictionary mapping format to file path

