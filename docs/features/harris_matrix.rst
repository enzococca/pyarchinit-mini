Harris Matrix Visualization
===========================

Overview
--------

PyArchInit-Mini provides advanced Harris Matrix visualization capabilities for archaeological stratigraphic sequences. The system supports both traditional Harris Matrix (US/USM units) and the Extended Matrix Framework for complex documentation scenarios.

Features
--------

* **Graphviz Rendering**: High-quality SVG/PNG matrix generation
* **Interactive Web Viewer**: Pan, zoom, and navigate large matrices
* **GraphML Export**: yEd-compatible format for advanced editing
* **Extended Matrix Support**: Beyond traditional stratigraphic units
* **Automatic Layout**: Intelligent node positioning
* **Relationship Labeling**: Correct labels based on unit type (v1.2.16+)

Relationship Labels
-------------------

.. versionchanged:: 1.2.16
   Corrected relationship labels for US and USM units

PyArchInit-Mini uses appropriate relationship labels based on unit type:

* **US and USM**: Traditional textual labels (Copre, Taglia, etc.)
* **Extended Matrix Units**: Symbolic labels (>, >>)

For complete documentation on relationship types and labeling rules, see:

.. seealso::
   :doc:`stratigraphic_relationships` - Complete relationship labeling documentation

Generating a Harris Matrix
---------------------------

Web Interface
^^^^^^^^^^^^^

1. Navigate to **Tools → Harris Matrix** or **Harris Matrix** in site details
2. Select site from dropdown
3. Click **Generate Matrix**
4. View interactive visualization
5. Download as SVG, PNG, or GraphML

Desktop GUI
^^^^^^^^^^^

1. Open **Tools → Harris Matrix**
2. Select site
3. Choose output format (Interactive, SVG, PNG, GraphML)
4. Click **Generate**
5. View or save result

Command Line
^^^^^^^^^^^^

.. code-block:: bash

   pyarchinit-mini-cli generate-harris-matrix \
     --site "Pompei" \
     --output harris_matrix.svg \
     --format svg

Python API
^^^^^^^^^^

.. code-block:: python

   from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator

   generator = HarrisMatrixGenerator(db_manager)

   # Generate DOT graph
   dot_graph = generator.generate_matrix(site_name="Pompei")

   # Render to file
   generator.render_to_file(
       site_name="Pompei",
       output_path="harris_matrix.svg",
       format="svg"
   )

Matrix Types
------------

Standard Harris Matrix
^^^^^^^^^^^^^^^^^^^^^^^

Traditional archaeological stratigraphic sequence:

.. code-block:: text

   ┌────┐
   │US 1│ Topsoil
   └────┘
      │ Copre
      ↓
   ┌────┐
   │US 2│ Medieval layer
   └────┘
      │ Copre
      ↓
   ┌────┐
   │US 3│ Roman layer
   └────┘

Features:
* Traditional stratigraphic relationships
* Textual labels (Copre, Taglia, etc.)
* Linear or branching sequences

Extended Matrix
^^^^^^^^^^^^^^^

Advanced documentation with virtual units and extraction nodes:

.. code-block:: text

   ┌─────────────┐
   │Extractor 200│ Data extraction
   └─────────────┘
         │ >>
         ↓
   ┌───────┐          ┌────────┐
   │USVA 10│───────>──│DOC 100 │ Documentation
   └───────┘          └────────┘
      │ >                │ >>
      ↓                  ↓
   ┌────┐            ┌────┐
   │US 1│───Copre───>│US 2│ Physical units
   └────┘            └────┘

Features:
* Virtual stratigraphic units (USVA, USVB, USVC)
* Documentation nodes (DOC)
* Extraction and combination nodes
* Mixed label types

Visualization Options
---------------------

Node Styling
^^^^^^^^^^^^

Nodes are styled based on unit type:

* **US**: Light blue, rectangular
* **USM**: Light green, rectangular
* **USVA/USVB/USVC**: Yellow, oval
* **DOC**: Orange, note shape
* **Extractor/Combiner**: Purple, diamond

Customization:

.. code-block:: python

   generator.set_node_style(
       unit_type='US',
       fillcolor='lightblue',
       shape='rectangle'
   )

Edge Styling
^^^^^^^^^^^^

Edges show relationship direction and type:

* **Solid lines**: Direct relationships
* **Dashed lines**: Indirect/virtual relationships
* **Bold lines**: Strong relationships (>>)

Label positioning:

.. code-block:: python

   generator.set_edge_label_position('top')  # or 'middle', 'bottom'

Interactive Features
--------------------

Web Viewer
^^^^^^^^^^

The interactive web viewer provides:

* **Pan**: Click and drag to move
* **Zoom**: Mouse wheel or pinch gestures
* **Search**: Find specific US by number
* **Filter**: Show/hide unit types
* **Export**: Download current view

Controls:

* ``+`` / ``-``: Zoom in/out
* ``Space + Drag``: Pan
* ``/``: Search
* ``F``: Toggle fullscreen
* ``R``: Reset view

GraphML Export for yEd
-----------------------

.. versionadded:: 1.5.0
   Fixed periodization display in GraphML export. All archaeological periods now properly visible in yEd (previously only 3-4 periods were displayed). Period ordering now follows chronological sequence based on periodo/fase instead of alphabetical sorting.

Export Format
^^^^^^^^^^^^^

PyArchInit-Mini exports matrices in GraphML format compatible with yEd Graph Editor:

.. code-block:: bash

   # Via CLI
   pyarchinit-mini-cli export-graphml \
     --site "Pompei" \
     --output pompei_matrix.graphml

   # Via Web
   Tools → Export GraphML (yEd)

Opening in yEd
^^^^^^^^^^^^^^

1. Export matrix as GraphML
2. Open yEd (https://www.yworks.com/products/yed)
3. File → Open → Select .graphml file
4. Layout → Hierarchical (for best results)
5. Edit, enhance, and export

yEd Features
^^^^^^^^^^^^

* Advanced layout algorithms
* Custom styling and colors
* Label editing and formatting
* Group nodes and subgraphs
* Export to various formats (PDF, SVG, PNG)

Periodization Support
^^^^^^^^^^^^^^^^^^^^^

.. versionadded:: 1.5.0

GraphML export now supports complete archaeological periodization:

* **Chronological Ordering**: Periods are arranged in chronological sequence (oldest to newest) based on periodo_iniziale and fase_iniziale fields
* **Reverse Epochs**: Optional reverse ordering shows newest to oldest periods
* **Complete Period Display**: All archaeological periods from database are now visible in GraphML export
* **Large Site Support**: Tested with Dom zu Lund site (758 US nodes, 8 periods)

Period rows in GraphML correspond to datazione_estesa values from the database, arranged in correct chronological order for proper stratigraphic visualization in yEd.

Advanced Features
-----------------

Custom Relationship Types
^^^^^^^^^^^^^^^^^^^^^^^^^

Add custom relationship types:

.. code-block:: python

   from pyarchinit_mini.models.us import USRelationship

   # Define custom relationship
   custom_rel = USRelationship(
       sito='Pompei',
       us_from='1',
       us_to='2',
       relationship_type='Contemporary with'
   )

   db_manager.session.add(custom_rel)
   db_manager.session.commit()

Swimlane Organization
^^^^^^^^^^^^^^^^^^^^^

.. versionadded:: 1.2.15

Group units by area or excavation phase:

.. code-block:: python

   generator.enable_swimlanes(
       group_by='area',  # or 'phase', 'period'
       orientation='horizontal'  # or 'vertical'
   )

Matrix Filtering
^^^^^^^^^^^^^^^^

Filter by date range, area, or unit type:

.. code-block:: python

   generator.filter_by_date(
       start_date='2023-01-01',
       end_date='2023-12-31'
   )

   generator.filter_by_area(
       areas=['Area 1', 'Area 2']
   )

   generator.filter_by_unit_type(
       unit_types=['US', 'USM']
   )

Performance
-----------

Matrix Complexity
^^^^^^^^^^^^^^^^^

Recommended limits:

* **Small**: < 50 units (renders instantly)
* **Medium**: 50-200 units (1-3 seconds)
* **Large**: 200-500 units (3-10 seconds)
* **Very Large**: > 500 units (may require pagination)

Optimization Tips
^^^^^^^^^^^^^^^^^

1. **Filter by area**: Reduce matrix size
2. **Use swimlanes**: Organize large matrices
3. **Export to GraphML**: Edit large matrices in yEd
4. **Paginate**: Split into multiple sub-matrices

Troubleshooting
---------------

Matrix Not Rendering
^^^^^^^^^^^^^^^^^^^^

**Problem**: Blank or incomplete matrix

**Solutions**:

* Verify US records exist for the site
* Check that relationships are defined
* Ensure Graphviz is installed (for SVG/PNG)
* Review error logs for details

Circular Dependencies
^^^^^^^^^^^^^^^^^^^^^

**Problem**: "Circular relationship detected"

**Solutions**:

* Review stratigraphic sequence for errors
* Remove conflicting relationships
* Use "Uguale a" for contemporaneous units
* Enable cycle breaking in generator

Label Overlap
^^^^^^^^^^^^^

**Problem**: Relationship labels overlapping

**Solutions**:

* Increase node spacing
* Rotate edge labels
* Export to yEd for manual adjustment
* Use symbolic labels for extended units

Examples
--------

Simple Sequence
^^^^^^^^^^^^^^^

.. code-block:: python

   from pyarchinit_mini.services.us_service import USService

   us_service = USService(db_manager)

   # Create stratigraphic sequence
   us_service.create_us(sito='Test Site', us='1', d_stratigrafica='Topsoil')
   us_service.create_us(sito='Test Site', us='2', d_stratigrafica='Medieval')
   us_service.create_us(sito='Test Site', us='3', d_stratigrafica='Roman')

   # Define relationships
   us_service.add_relationship('Test Site', '1', '2', 'Copre')
   us_service.add_relationship('Test Site', '2', '3', 'Copre')

   # Generate matrix
   generator = HarrisMatrixGenerator(db_manager)
   generator.render_to_file('Test Site', 'matrix.svg')

Complex Matrix with Cuts
^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Stratigraphic sequence
   us_service.add_relationship('Pompei', '1', '2', 'Copre')
   us_service.add_relationship('Pompei', '2', '3', 'Copre')

   # Pit cutting earlier layers
   us_service.add_relationship('Pompei', '4', '1', 'Taglia')
   us_service.add_relationship('Pompei', '4', '2', 'Taglia')

   # Pit fill
   us_service.add_relationship('Pompei', '5', '4', 'Riempie')

   # Generate matrix
   generator.render_to_file('Pompei', 'pompei_matrix.svg')

Result:

.. code-block:: text

   ┌────┐
   │US 5│ Pit fill
   └────┘
      │ Riempie
      ↓
   ┌────┐────────────────┐
   │US 4│ Pit            │
   └────┘                │ Taglia
      │                  │
      ├──────────┬───────┘
      │ Taglia   │
      ↓          ↓
   ┌────┐    ┌────┐
   │US 1│    │US 2│
   └────┘    └────┘
      │ Copre  │
      └────┬───┘
           ↓
        ┌────┐
        │US 3│
        └────┘

API Reference
-------------

HarrisMatrixGenerator
^^^^^^^^^^^^^^^^^^^^^

.. py:class:: HarrisMatrixGenerator(db_manager)

   Main class for Harris Matrix generation.

   .. py:method:: generate_matrix(site_name: str, use_extended_matrix: bool = False) -> Digraph

      Generate Harris Matrix as Graphviz Digraph.

      :param site_name: Name of archaeological site
      :param use_extended_matrix: Include Extended Matrix units
      :return: Graphviz Digraph object

   .. py:method:: render_to_file(site_name: str, output_path: str, format: str = 'svg')

      Render matrix to file.

      :param site_name: Site name
      :param output_path: Output file path
      :param format: Output format (svg, png, pdf)

   .. py:method:: export_graphml(site_name: str, output_path: str)

      Export matrix to GraphML format for yEd.

      :param site_name: Site name
      :param output_path: Output .graphml file path

See Also
--------

* :doc:`stratigraphic_relationships` - Relationship labeling rules
* :doc:`graphml_export` - GraphML export documentation
* :doc:`../data/stratigraphic_units` - US data model
* :doc:`/EXTENDED_MATRIX_FRAMEWORK` - Extended Matrix Framework
