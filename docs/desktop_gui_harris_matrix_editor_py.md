# desktop_gui/harris_matrix_editor.py

## Overview

This file contains 100 documented elements.

## Classes

### HarrisMatrixEditor

Advanced Harris Matrix editor with relationship management and validation

#### Methods

##### __init__(self, parent, matrix_generator, matrix_visualizer, site_service, us_service)

Initializes a new instance of the Advanced Harris Matrix editor, setting up the main window, interface components, and required services for matrix generation, visualization, and site/unit management. This constructor also initializes data structures for managing current site, area, relationships, and the underlying graph, and makes the editor window modal relative to the parent.

##### create_interface(self)

Create the main interface

##### create_control_panel(self, parent)

Create site selection and main controls

##### create_left_panel(self, parent)

Create left panel with relationships and tools

##### create_relationships_tab(self, parent)

Create relationships management tab

##### create_us_list_tab(self, parent)

Create US list tab

##### create_validation_tab(self, parent)

Create validation tab

##### create_right_panel(self, parent)

Create right panel with matrix visualization

##### load_sites(self)

Load available sites

##### on_site_changed(self, event)

Handle site selection change

##### load_areas(self)

Load areas for selected site

##### on_area_changed(self, event)

Handle area selection change

##### load_us_list(self)

Load US list for selected site/area

##### load_matrix(self)

Load existing matrix for the site

##### generate_matrix(self)

Generate new matrix from relationships

##### add_relationship(self)

Add new stratigraphic relationship

##### refresh_relationships(self)

Refresh relationships list

##### edit_relationship(self)

Edit selected relationship

##### delete_relationship(self)

Delete selected relationship

##### validate_matrix(self)

Validate current matrix

##### auto_fix_matrix(self)

Attempt automatic fixes for matrix issues

##### visualize_matrix(self)

Visualize the Harris Matrix

##### on_layout_changed(self, event)

Handle layout change

##### zoom_in(self)

Zoom in the matrix view

##### zoom_out(self)

Zoom out the matrix view

##### reset_view(self)

Reset matrix view

##### select_us_for_relation(self)

Select US from list for relationship creation

##### highlight_us_in_matrix(self)

Highlight selected US in matrix

##### save_matrix(self)

Save current matrix

##### export_matrix_image(self)

Export matrix as image

##### export_validation_report(self)

Export validation report

### HarrisMatrixEditor

Advanced Harris Matrix editor with relationship management and validation

#### Methods

##### __init__(self, parent, matrix_generator, matrix_visualizer, site_service, us_service)

Initializes a new instance of the Advanced Harris Matrix editor, setting up the main window, user interface, and essential services for matrix generation, visualization, and site/unit management. This constructor configures the application's state, loads initial site data, and ensures the editor window operates as a modal dialog relative to its parent.

##### create_interface(self)

Create the main interface

##### create_control_panel(self, parent)

Create site selection and main controls

##### create_left_panel(self, parent)

Create left panel with relationships and tools

##### create_relationships_tab(self, parent)

Create relationships management tab

##### create_us_list_tab(self, parent)

Create US list tab

##### create_validation_tab(self, parent)

Create validation tab

##### create_right_panel(self, parent)

Create right panel with matrix visualization

##### load_sites(self)

Load available sites

##### on_site_changed(self, event)

Handle site selection change

##### load_areas(self)

Load areas for selected site

##### on_area_changed(self, event)

Handle area selection change

##### load_us_list(self)

Load US list for selected site/area

##### load_matrix(self)

Load existing matrix for the site

##### generate_matrix(self)

Generate new matrix from relationships

##### add_relationship(self)

Add new stratigraphic relationship

##### refresh_relationships(self)

Refresh relationships list

##### edit_relationship(self)

Edit selected relationship

##### delete_relationship(self)

Delete selected relationship

##### validate_matrix(self)

Validate current matrix

##### auto_fix_matrix(self)

Attempt automatic fixes for matrix issues

##### visualize_matrix(self)

Visualize the Harris Matrix

##### on_layout_changed(self, event)

Handle layout change

##### zoom_in(self)

Zoom in the matrix view

##### zoom_out(self)

Zoom out the matrix view

##### reset_view(self)

Reset matrix view

##### select_us_for_relation(self)

Select US from list for relationship creation

##### highlight_us_in_matrix(self)

Highlight selected US in matrix

##### save_matrix(self)

Save current matrix

##### export_matrix_image(self)

Export matrix as image

##### export_validation_report(self)

Export validation report

### HarrisMatrixEditor

Advanced Harris Matrix editor with relationship management and validation

#### Methods

##### __init__(self, parent, matrix_generator, matrix_visualizer, site_service, us_service)

Initializes a new instance of the Advanced Harris Matrix editor, setting up required services, data structures, and the main application window. This method configures the editor’s interface, loads initial site data, and ensures the window operates modally relative to its parent. It prepares the editor for managing and visualizing Harris Matrix relationships.

##### create_interface(self)

Create the main interface

##### create_control_panel(self, parent)

Create site selection and main controls

##### create_left_panel(self, parent)

Create left panel with relationships and tools

##### create_relationships_tab(self, parent)

Create relationships management tab

##### create_us_list_tab(self, parent)

Create US list tab

##### create_validation_tab(self, parent)

Create validation tab

##### create_right_panel(self, parent)

Create right panel with matrix visualization

##### load_sites(self)

Load available sites

##### on_site_changed(self, event)

Handle site selection change

##### load_areas(self)

Load areas for selected site

##### on_area_changed(self, event)

Handle area selection change

##### load_us_list(self)

Load US list for selected site/area

##### load_matrix(self)

Load existing matrix for the site

##### generate_matrix(self)

Generate new matrix from relationships

##### add_relationship(self)

Add new stratigraphic relationship

##### refresh_relationships(self)

Refresh relationships list

##### edit_relationship(self)

Edit selected relationship

##### delete_relationship(self)

Delete selected relationship

##### validate_matrix(self)

Validate current matrix

##### auto_fix_matrix(self)

Attempt automatic fixes for matrix issues

##### visualize_matrix(self)

Visualize the Harris Matrix using PyArchInit-style Graphviz

##### on_layout_changed(self, event)

Handle layout change

##### zoom_in(self)

Zoom in the matrix view

##### zoom_out(self)

Zoom out the matrix view

##### reset_view(self)

Reset matrix view

##### select_us_for_relation(self)

Select US from list for relationship creation

##### highlight_us_in_matrix(self)

Highlight selected US in matrix

##### save_matrix(self)

Save current matrix

##### export_matrix_image(self)

Export matrix as image

##### export_validation_report(self)

Export validation report

## Functions

### save_changes()

The `save_changes` function updates a relationship between two nodes in a graph based on user input from a GUI form. It removes the old edge, adds a new edge with the specified type, refreshes the interface to reflect the changes, and displays a success or error message as appropriate.

