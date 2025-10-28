Extended Matrix GraphML Export - Technical Architecture
========================================================

:Date: 2025-10-28
:Version: 1.7.0+
:Status: ✅ Production System - Technical Reference

.. contents:: Table of Contents
   :local:
   :depth: 4

Overview
--------

The GraphML export system implements PyArchInit's **Extended Matrix Palette**, an advanced Harris Matrix visualization system that includes:

- **Special EM nodes**: DOC, Extractor, Combiner, USV (A/B/C), USD, TU, SF, VSF, property
- **Symbolic relationships**: ``>``, ``>>``, ``<``, ``<<`` (with explicit direction)
- **Differentiated edge styles**: dotted, solid, bold, with specific arrowheads (dot, box, none)
- **Archaeological periodization**: Automatic organization by periods with extended dating
- **yEd compatibility**: Export optimized for yEd Graph Editor

Software Requirements
---------------------

Python Dependencies (Auto-Installed)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install 'pyarchinit-mini[harris]'

This installs:

- ``networkx>=3.0.0`` - In-memory graph data structure
- ``graphviz>=0.20.0`` - Python module for generating DOT files

Graphviz Software (Manual Installation Required)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**IMPORTANT**: The Python ``graphviz`` module is just a wrapper. It requires the native **Graphviz** software installed on your system.

Installation by Operating System
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Linux (Debian/Ubuntu)**:

.. code-block:: bash

   sudo apt-get update
   sudo apt-get install graphviz

**Linux (Fedora/RHEL)**:

.. code-block:: bash

   sudo dnf install graphviz

**macOS (Homebrew)**:

.. code-block:: bash

   brew install graphviz

**macOS (MacPorts)**:

.. code-block:: bash

   sudo port install graphviz

**Windows (Chocolatey)** - Auto-adds to PATH:

.. code-block:: powershell

   choco install graphviz

**Windows (Direct Download)** - Requires PATH configuration:

1. **Installation**:

   - Download from: https://graphviz.org/download/
   - Run ``.msi`` installer
   - During installation: **select "Add Graphviz to the system PATH for all users"**

2. **Manual PATH addition** (if needed):

   - Find installation path: ``C:\Program Files\Graphviz\bin``
   - Settings → System → About → Advanced system settings
   - Environment Variables → System variables → Path → Edit
   - New → Paste: ``C:\Program Files\Graphviz\bin``
   - OK → **Reopen all terminals**

3. **Verify** (new terminal):

   .. code-block:: powershell

      dot -V
      tred -V

Verify Installation
^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # dot command (for DOT generation)
   dot -V
   # Output: dot - graphviz version X.X.X

   # tred command (for transitive reduction)
   tred -V
   # Output: tred - graphviz version X.X.X

.. note::

   If Graphviz software is not installed, the system will show a clear error with installation instructions.

System Architecture
-------------------

1. Transformation Pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: text

   Database → NetworkX DiGraph → Graphviz Digraph → DOT → Reduced DOT → GraphML (yEd)
       ↓           ↓                    ↓              ↓         ↓            ↓
     SQLite    Intermediate        Python graphviz   Text    tred cmd      XML
               data structure         module          file    (Graphviz)

**Software Components**:

- **NetworkX**: In-memory data structure to build and manipulate graph (normalize relationships, remove cycles)
- **Python graphviz module**: Generates DOT file with Graphviz attributes
- **Graphviz tred**: Command for graph transitive reduction
- **Custom parser**: Converts DOT to GraphML with yEd TableNode structure

2. Complete Pipeline
~~~~~~~~~~~~~~~~~~~~~

Phase 1: Database → NetworkX Graph (Intermediate Data Structure)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**File**: ``pyarchinit_mini/harris_matrix/matrix_generator.py``

**Method**: ``generate_matrix(site_name)``

**Role**: NetworkX is used ONLY as in-memory data structure for:

- Organizing nodes and edges from database
- Normalizing inverse relationships (covered by → covers)
- Inverting directions for special EM nodes
- Validating and removing cycles

.. code-block:: python

   from pyarchinit_mini.harris_matrix.matrix_generator import MatrixGenerator
   import networkx as nx

   # Initialize generator
   db_url = 'sqlite:///pyarchinit_mini.db'
   matrix_gen = MatrixGenerator(db_url)

   # Phase 1: Database → NetworkX DiGraph
   # Query database
   us_nodes = db_manager.query(US).filter(sito=site_name).all()
   relationships = db_manager.query(USRelationship).filter(sito=site_name).all()

   # Create NetworkX graph
   graph = nx.DiGraph()

   # Add nodes with attributes
   for us in us_nodes:
       graph.add_node(
           us.id_us,
           label=f"US {us.id_us}",
           extended_label=f"{us.unita_tipo}{us.id_us}",
           description=us.d_interpretativa,
           url=us.file_path if us.unita_tipo == 'DOC' else '',
           period_initial=us.periodo_iniziale,
           phase_initial=us.fase_iniziale,
           periodo_code=f"{us.periodo_iniziale}-{us.fase_iniziale}",
           unita_tipo=us.unita_tipo
       )

   # Add edges with normalization
   for rel in relationships:
       # Normalize inverse relationships (covered by → covers)
       us_from, us_to = normalize_relationship(rel)

       # Invert direction for special EM nodes (excluding symbols)
       if is_special_node(us_from) and not is_symbolic(rel.type):
           us_from, us_to = us_to, us_from

       graph.add_edge(us_from, us_to, relationship=rel.type)

**Features**:

- Cycle removal with validation
- Inverse relationship deduplication
- Automatic inversion for EM nodes (excluding ``>``, ``>>``, ``<``, ``<<``)

**Python API Example**:

.. code-block:: python

   from pyarchinit_mini.database.manager import DatabaseManager
   from pyarchinit_mini.harris_matrix.matrix_generator import MatrixGenerator

   # Initialize
   db = DatabaseManager('sqlite:///pyarchinit_mini.db')
   matrix_gen = MatrixGenerator('sqlite:///pyarchinit_mini.db')

   # Generate NetworkX graph from database
   graph = matrix_gen.generate_matrix(
       sito='Pompeii',
       area='Area A'
   )

   # Inspect graph structure
   print(f"Nodes: {graph.number_of_nodes()}")
   print(f"Edges: {graph.number_of_edges()}")

   # Check node attributes
   for node_id, node_data in list(graph.nodes(data=True))[:3]:
       print(f"\nNode {node_id}:")
       print(f"  Type: {node_data.get('unita_tipo')}")
       print(f"  Label: {node_data.get('extended_label')}")
       print(f"  Period: {node_data.get('period_initial')}")

   # Check edge relationships
   for src, tgt, edge_data in list(graph.edges(data=True))[:3]:
       print(f"\nEdge {src} → {tgt}:")
       print(f"  Relationship: {edge_data.get('relationship')}")

**Expected Output**:

.. code-block:: text

   Nodes: 125
   Edges: 342

   Node 1001:
     Type: US
     Label: US1001
     Period: Medieval

   Node 2001:
     Type: USM
     Label: USM2001
     Period: Roman

   Node 8001:
     Type: DOC
     Label: DOC8001
     Period: Medieval

   Edge 1001 → 1002:
     Relationship: Copre

   Edge 1002 → 1003:
     Relationship: Taglia

   Edge 8001 → 1001:
     Relationship: Documenta

Phase 2: NetworkX → Graphviz Digraph → DOT File
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**File**: ``pyarchinit_mini/harris_matrix/matrix_generator.py``

**Method**: ``export_to_graphml(...)``

**Role**: The Python ``graphviz`` module generates the DOT file (NOT NetworkX):

- Transfers nodes and edges from NetworkX to Graphviz Digraph
- Applies Graphviz attributes (shape, style, arrowhead, color)
- Organizes nodes into subgraphs by period
- Generates DOT file using ``G.render()``

.. code-block:: python

   from graphviz import Digraph

   # Create Graphviz Digraph (NOT NetworkX!)
   G = Digraph(engine='dot', strict=False)
   G.attr(rankdir='TB')  # Top to Bottom

   # Organize by period (if requested)
   if include_periods:
       periodo_fase_to_datazione = query_periodizzazione_table()

       for (datazione, periodo, fase), nodes in grouped_by_period:
           with G.subgraph(name=f'cluster_datazione_{id}') as c:
               c.attr(label=datazione, style='filled', color='lightblue')

               for node_id, node_data in nodes:
                   c.node(
                       node_data['extended_label'],
                       label=node_data['extended_label'],
                       shape='box',
                       style='filled',
                       fillcolor='white',
                       tooltip=node_data['description'],
                       URL=node_data.get('url', ''),
                       period=datazione  # Period name for Y positioning
                   )

   # Add edges with Extended Matrix styles
   edges_by_type = classify_edges(graph)

   # Dotted: cuts, property, EM symbols
   for src, tgt in edges_dotted:
       G.edge(src, tgt, color='black', style='dotted', arrowhead='normal')

   # Bold double: equals, bonds with
   for src, tgt in edges_double:
       G.edge(src, tgt, color='black', style='bold', dir='both',
              arrowhead='normal', arrowtail='normal')

   # Dot arrow: leans on
   for src, tgt in edges_dot:
       G.edge(src, tgt, color='black', style='solid', arrowhead='dot')

   # Box arrow: fills
   for src, tgt in edges_box:
       G.edge(src, tgt, color='black', style='solid', arrowhead='box')

   # No arrow: continuity
   for src, tgt in edges_no_arrow:
       G.edge(src, tgt, color='black', style='solid', arrowhead='none')

   # Normal: covers (default stratigraphic)
   for src, tgt in edges_normal:
       G.edge(src, tgt, color='black', style='solid', arrowhead='normal')

   # Render to DOT file
   G.render(filename='output.dot', format='dot')

**Key DOT Attributes**:

- ``label``: Displayed label (type + number, e.g., "US12", "DOC4001")
- ``tooltip``: Description (d_interpretativa or continuity)
- ``URL``: Path to attached file (DOC units only)
- ``period``: Period name (e.g., "Modern Age") for Y calculation
- ``shape``: Node shape (box, parallelogram for USV, etc.)
- ``style``: filled, dotted, bold, solid
- ``arrowhead``: normal, dot, box, none
- ``dir``: both (for double arrows)

**Python API Example**:

.. code-block:: python

   from graphviz import Digraph
   from pyarchinit_mini.harris_matrix.matrix_generator import MatrixGenerator

   # Generate NetworkX graph
   matrix_gen = MatrixGenerator('sqlite:///pyarchinit_mini.db')
   graph = matrix_gen.generate_matrix('Pompeii', 'Area A')

   # Create Graphviz Digraph
   G = Digraph('harris_matrix', engine='dot')
   G.attr(rankdir='TB', ranksep='1.0', nodesep='0.5')

   # Transfer nodes from NetworkX to Graphviz
   for node_id, node_data in graph.nodes(data=True):
       label = node_data.get('extended_label', str(node_id))
       node_type = node_data.get('unita_tipo', 'US')

       # Apply different styles based on node type
       if node_type == 'DOC':
           shape = 'note'
           fillcolor = 'lightyellow'
       elif node_type == 'USM':
           shape = 'box'
           fillcolor = 'lightgray'
       elif node_type.startswith('USV'):
           shape = 'parallelogram'
           fillcolor = 'lightblue'
       else:
           shape = 'box'
           fillcolor = 'white'

       G.node(
           label,
           label=label,
           shape=shape,
           style='filled',
           fillcolor=fillcolor,
           tooltip=node_data.get('description', '')
       )

   # Transfer edges from NetworkX to Graphviz
   for src, tgt, edge_data in graph.edges(data=True):
       src_label = graph.nodes[src].get('extended_label', str(src))
       tgt_label = graph.nodes[tgt].get('extended_label', str(tgt))
       rel_type = edge_data.get('relationship', 'covers')

       # Apply different arrow styles based on relationship
       if 'taglia' in rel_type.lower():
           style = 'dotted'
       elif 'uguale' in rel_type.lower():
           style = 'bold'
           dir = 'both'
       else:
           style = 'solid'

       G.edge(src_label, tgt_label, style=style)

   # Save DOT file
   G.save('harris_matrix.dot')
   print(f"DOT file saved: harris_matrix.dot")

   # Render to PNG for preview
   G.render('harris_matrix', format='png', cleanup=True)
   print(f"PNG preview saved: harris_matrix.png")

Phase 3: DOT → Reduced DOT (Transitive Reduction)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**File**: ``pyarchinit_mini/harris_matrix/matrix_generator.py``

**Method**: ``export_to_graphml(...)``

**Role**: Graphviz ``tred`` command performs transitive reduction:

- Shell command ``tred`` (part of Graphviz software suite)
- NOT a NetworkX algorithm
- Processes DOT file as text and generates reduced DOT

.. code-block:: python

   import subprocess

   # Apply transitive reduction with Graphviz tred command
   # tred is a COMMAND from Graphviz software (not Python)
   with open('output_tred.dot', 'w') as f:
       subprocess.run(['tred', 'output.dot'], stdout=f, timeout=30)

   # Convert reduced DOT to GraphML
   from pyarchinit_mini.graphml_converter.converter import convert_dot_to_graphml

   success = convert_dot_to_graphml(
       dot_file='output_tred.dot',
       graphml_file='output.graphml',
       title='Harris Matrix',
       reverse_epochs=False
   )

**Transitive Reduction** (Graphviz ``tred`` command):

- Removes redundant edges while preserving relationships
- Example: if US1→US2→US3 and US1→US3, removes US1→US3
- Requires Graphviz installed on system (``sudo apt install graphviz`` or ``brew install graphviz``)
- Fallback: if tred not available, uses unreduced DOT

**Python API Example**:

.. code-block:: python

   import subprocess
   import os
   from pathlib import Path

   def apply_transitive_reduction(input_dot: str, output_dot: str) -> bool:
       """
       Apply transitive reduction using Graphviz tred command

       Args:
           input_dot: Path to input DOT file
           output_dot: Path to output reduced DOT file

       Returns:
           bool: True if successful, False otherwise
       """
       try:
           # Check if tred is available
           result = subprocess.run(
               ['tred', '--version'],
               capture_output=True,
               timeout=5
           )

           if result.returncode != 0:
               print("Warning: tred command not found")
               return False

           # Apply transitive reduction
           with open(output_dot, 'w') as f:
               result = subprocess.run(
                   ['tred', input_dot],
                   stdout=f,
                   stderr=subprocess.PIPE,
                   timeout=30
               )

           if result.returncode == 0:
               print(f"Transitive reduction applied: {output_dot}")
               return True
           else:
               print(f"tred error: {result.stderr.decode()}")
               return False

       except subprocess.TimeoutExpired:
           print("Error: tred command timed out")
           return False
       except FileNotFoundError:
           print("Error: tred command not found. Install Graphviz.")
           return False
       except Exception as e:
           print(f"Error: {str(e)}")
           return False

   # Usage
   success = apply_transitive_reduction(
       'harris_matrix.dot',
       'harris_matrix_reduced.dot'
   )

   if success:
       print("Transitive reduction completed")
       # Compare file sizes
       original_size = Path('harris_matrix.dot').stat().st_size
       reduced_size = Path('harris_matrix_reduced.dot').stat().st_size
       print(f"Original: {original_size} bytes")
       print(f"Reduced: {reduced_size} bytes")
       print(f"Reduction: {100 * (1 - reduced_size/original_size):.1f}%")
   else:
       print("Using unreduced DOT file")

**Expected Output**:

.. code-block:: text

   Transitive reduction applied: harris_matrix_reduced.dot
   Transitive reduction completed
   Original: 45823 bytes
   Reduced: 32145 bytes
   Reduction: 29.8%

Phase 4: DOT → GraphML (Parsing and Rendering)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**File**: ``pyarchinit_mini/graphml_converter/dot_parser.py``

**Class**: ``Node``

.. code-block:: python

   class Node:
       def get_y(self, epoch, nome_us, node_to_cluster=None):
           """Calculate Y coordinate for positioning"""
           # 1. Try node_to_cluster (if provided)
           if node_to_cluster and nome_us in node_to_cluster:
               return (int(node_to_cluster[nome_us]) - 1) * 1000

           # 2. Try 'period' attribute
           if 'period' in self.attribs:
               period_value = self.attribs['period']
               for i, epoch_name in enumerate(epoch):
                   if epoch_name in period_value:
                       return i * 1000  # 1000 pixels per row

           # 3. Fallback: search period in label
           for i, epoch_name in enumerate(epoch):
               if epoch_name in nome_us:
                   return i * 1000

           return 0  # Default first row

       def exportGraphml(self, doc, parent, conf, epoch_sigla, node_to_cluster=None):
           """Export node to GraphML format (yEd TableNode)"""
           # Create <node> element
           node_elem = doc.createElement('node')
           node_elem.setAttribute('id', f'n0::n{self.id}')

           # Data key d5: description (from tooltip)
           if 'tooltip' in self.attribs:
               data_desc = doc.createElement('data')
               data_desc.setAttribute('key', 'd5')
               data_desc.appendChild(doc.createTextNode(self.attribs['tooltip']))
               node_elem.appendChild(data_desc)

           # Data key d4: URL (DOC only)
           if 'URL' in self.attribs:
               data_url = doc.createElement('data')
               data_url.setAttribute('key', 'd4')
               data_url.appendChild(doc.createTextNode(self.attribs['URL']))
               node_elem.appendChild(data_url)

           # Data key d6: node graphics
           data_graphics = doc.createElement('data')
           data_graphics.setAttribute('key', 'd6')

           # y:ShapeNode (or SVGNode for CON, GenericNode for DOC)
           shape_node = doc.createElement('y:ShapeNode')

           # Geometry with calculated Y
           geom = doc.createElement('y:Geometry')
           geom.setAttribute('height', '30.0')
           geom.setAttribute('width', '90.0')
           geom.setAttribute('x', '520.0')
           geom.setAttribute('y', str(self.get_y(epoch_sigla, self.label)))

           # NodeLabel with label text
           label_elem = doc.createElement('y:NodeLabel')
           label_elem.appendChild(doc.createTextNode(self.label))

           # Assemble structure
           shape_node.appendChild(geom)
           shape_node.appendChild(label_elem)
           # ... other elements (Fill, BorderStyle, Shape)

           data_graphics.appendChild(shape_node)
           node_elem.appendChild(data_graphics)

           return node_elem

**GraphML Structure (yEd TableNode)**:

.. code-block:: xml

   <graphml>
     <!-- Key definitions -->
     <key attr.name="url" for="node" id="d4" />
     <key attr.name="description" for="node" id="d5" />
     <key yfiles.type="nodegraphics" for="node" id="d6" />

     <graph edgedefault="directed">
       <!-- TableNode container (period rows) -->
       <node id="n0" yfiles.foldertype="group">
         <data key="d6">
           <y:TableNode>
             <y:Geometry height="10000" width="1044" x="-29" y="-596"/>

             <!-- Row labels (periods) -->
             <y:NodeLabel modelName="RowNodeLabelModel"
                          id="row_Modern_Age">
               Modern Age
             </y:NodeLabel>
             <y:NodeLabel modelName="RowNodeLabelModel"
                          id="row_Medieval">
               Medieval
             </y:NodeLabel>
             <!-- ... other rows ... -->

             <y:Table>
               <y:Rows>
                 <y:Row height="940" id="row_Modern_Age"/>
                 <y:Row height="940" id="row_Medieval"/>
                 <!-- ... -->
               </y:Rows>
             </y:Table>
           </y:TableNode>
         </data>

         <!-- US nodes (positioned in rows) -->
         <graph edgedefault="directed" id="n0:">
           <node id="n0::n1">
             <data key="d5">Masonry foundation</data>
             <data key="d6">
               <y:ShapeNode>
                 <y:Geometry height="30" width="90" x="520" y="0"/>
                 <y:NodeLabel>US1</y:NodeLabel>
                 <y:Shape type="rectangle"/>
               </y:ShapeNode>
             </data>
           </node>

           <node id="n0::n19">
             <data key="d4">DoSC\test1.graphml</data>
             <data key="d6">
               <y:GenericNode configuration="com.yworks.bpmn.Artifact">
                 <y:Geometry height="55" width="35" x="520" y="0"/>
                 <y:NodeLabel>DOC4001</y:NodeLabel>
               </y:GenericNode>
             </data>
           </node>

           <!-- Edges -->
           <edge source="n0::n1" target="n0::n2">
             <data key="d10">
               <y:PolyLineEdge>
                 <y:LineStyle color="#000000" type="line" width="1.0"/>
                 <y:Arrows source="none" target="standard"/>
               </y:PolyLineEdge>
             </data>
           </edge>
         </graph>
       </node>
     </graph>
   </graphml>

**Python API for Custom GraphML Export**:

.. code-block:: python

   from pyarchinit_mini.graphml_converter.graphml_exporter import GraphMLExporter
   from pyarchinit_mini.graphml_converter.converter import convert_dot_to_graphml

   def custom_graphml_export(
       site: str,
       area: str,
       db_url: str,
       output_path: str,
       include_periods: bool = True,
       reverse_epochs: bool = False
   ) -> dict:
       """
       Custom GraphML export with full control

       Args:
           site: Site name
           area: Area name
           db_url: Database connection URL
           output_path: Output GraphML file path
           include_periods: Include periodization organization
           reverse_epochs: Reverse chronological order

       Returns:
           dict: Export statistics
       """
       from pyarchinit_mini.harris_matrix.matrix_generator import MatrixGenerator
       import os
       from pathlib import Path

       # Initialize generator
       matrix_gen = MatrixGenerator(db_url)

       # Generate NetworkX graph
       graph = matrix_gen.generate_matrix(site, area)

       # Create output directory
       output_dir = Path(output_path).parent
       output_dir.mkdir(parents=True, exist_ok=True)

       # Base filename without extension
       base_name = Path(output_path).stem

       # Export to DOT first
       dot_path = output_dir / f'{base_name}.dot'
       matrix_gen.export_to_dot(
           graph=graph,
           output_path=str(dot_path),
           site_name=site,
           include_periods=include_periods
       )

       # Apply transitive reduction
       dot_reduced_path = output_dir / f'{base_name}_reduced.dot'
       apply_transitive_reduction(str(dot_path), str(dot_reduced_path))

       # Convert to GraphML
       success = convert_dot_to_graphml(
           dot_file=str(dot_reduced_path),
           graphml_file=output_path,
           title=f'{site} - {area} Harris Matrix',
           reverse_epochs=reverse_epochs
       )

       # Gather statistics
       stats = {
           'nodes': graph.number_of_nodes(),
           'edges': graph.number_of_edges(),
           'output_graphml': output_path,
           'output_dot': str(dot_path),
           'output_dot_reduced': str(dot_reduced_path),
           'success': success
       }

       # Check file sizes
       if Path(output_path).exists():
           stats['graphml_size'] = Path(output_path).stat().st_size

       return stats

   # Usage
   stats = custom_graphml_export(
       site='Pompeii',
       area='Area A',
       db_url='sqlite:///pyarchinit_mini.db',
       output_path='exports/pompeii_area_a.graphml',
       include_periods=True,
       reverse_epochs=False
   )

   print(f"Export complete:")
   print(f"  Nodes: {stats['nodes']}")
   print(f"  Edges: {stats['edges']}")
   print(f"  GraphML: {stats['output_graphml']} ({stats['graphml_size']} bytes)")
   print(f"  DOT: {stats['output_dot']}")
   print(f"  Reduced DOT: {stats['output_dot_reduced']}")

Database Schema Requirements
-----------------------------

us_table
~~~~~~~~

.. code-block:: sql

   CREATE TABLE us_table (
       id_us INTEGER PRIMARY KEY,
       sito VARCHAR(350) NOT NULL,
       unita_tipo VARCHAR(50),  -- 'US', 'USM', 'DOC', 'Extractor', etc.
       area VARCHAR(100),
       d_stratigrafica TEXT,
       d_interpretativa TEXT,
       formazione VARCHAR(100),
       periodo_iniziale INTEGER,
       fase_iniziale INTEGER,
       periodo_finale INTEGER,
       fase_finale INTEGER,
       file_path VARCHAR(500)  -- Relative path for DOC
   );

us_relationships_table
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: sql

   CREATE TABLE us_relationships_table (
       id_relationship INTEGER PRIMARY KEY,
       sito VARCHAR(350) NOT NULL,
       us_from INTEGER NOT NULL,
       us_to INTEGER NOT NULL,
       relationship_type VARCHAR(100),  -- 'copre', 'taglia', '>>', etc.
       certainty VARCHAR(20),
       FOREIGN KEY (us_from) REFERENCES us_table(id_us),
       FOREIGN KEY (us_to) REFERENCES us_table(id_us)
   );

periodizzazione_table
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: sql

   CREATE TABLE periodizzazione_table (
       id_periodo INTEGER PRIMARY KEY,
       sito VARCHAR(350) NOT NULL,
       periodo_iniziale INTEGER NOT NULL,
       fase_iniziale INTEGER NOT NULL,
       datazione_estesa VARCHAR(200),  -- "Modern Age", "15th century", etc.
       cron_iniziale INTEGER,
       cron_finale INTEGER
   );

Supported Relationship Types
-----------------------------

Standard Stratigraphic Relationships
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``copre`` / ``coperto da`` (normalized to ``copre``)
- ``taglia`` / ``tagliato da`` (normalized to ``taglia``)
- ``riempie`` / ``riempito da`` (normalized to ``riempie``)
- ``si appoggia`` / ``si appoggia a`` / ``gli si appoggia`` (normalized to ``si appoggia``)
- ``uguale a`` / ``same as``
- ``si lega a`` / ``bonds with``
- ``sopra`` / ``above``

Extended Matrix Symbolic Relationships
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- ``>`` / ``<`` (inverse pair, normalized to ``>``)
- ``>>`` / ``<<`` (inverse pair, normalized to ``>>``)

**IMPORTANT**: Symbolic relationships (``>``, ``>>``, ``<``, ``<<``) are **NOT** automatically inverted for EM nodes, because they already encode explicit direction.

Programmatic Usage
------------------

Basic Export
~~~~~~~~~~~~

.. code-block:: python

   from pyarchinit_mini.database.connection import DatabaseConnection
   from pyarchinit_mini.database.manager import DatabaseManager
   from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator
   from pyarchinit_mini.services.us_service import USService

   # Database connection
   db_url = "sqlite:///./pyarchinit_mini.db"
   db_conn = DatabaseConnection.from_url(db_url)
   db_manager = DatabaseManager(db_conn)
   us_service = USService(db_manager)

   # Matrix generator
   matrix_generator = HarrisMatrixGenerator(db_manager, us_service)

   # Generate graph
   site_name = "Archaeological Site"
   graph = matrix_generator.generate_matrix(site_name)

   # Export to GraphML with Extended Matrix
   output_path = "/path/to/output.graphml"
   result = matrix_generator.export_to_graphml(
       graph=graph,
       output_path=output_path,
       site_name=site_name,
       title="Diagram Title",
       use_extended_labels=True,  # Use type+number (e.g., USM12)
       include_periods=True,       # Organize by periods
       reverse_epochs=False        # False = Period 1 = oldest epoch
   )

   print(f"Export complete: {result}")

Export Parameters
~~~~~~~~~~~~~~~~~

.. list-table::
   :widths: 20 10 10 60
   :header-rows: 1

   * - Parameter
     - Type
     - Default
     - Description
   * - ``graph``
     - ``nx.DiGraph``
     - **required**
     - Generated NetworkX graph
   * - ``output_path``
     - ``str``
     - **required**
     - Output .graphml file path
   * - ``site_name``
     - ``str``
     - **required**
     - Archaeological site name
   * - ``title``
     - ``str``
     - ``None``
     - Diagram title
   * - ``use_extended_labels``
     - ``bool``
     - ``True``
     - Use EM labels (type+number)
   * - ``include_periods``
     - ``bool``
     - ``True``
     - Organize by periods
   * - ``reverse_epochs``
     - ``bool``
     - ``False``
     - Reverse period order

Direct Access to DOT Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Export generates 3 files:
   # 1. output.dot - Original DOT
   # 2. output_tred.dot - DOT with transitive reduction
   # 3. output.graphml - Final GraphML

   # You can work directly with DOT files
   import subprocess

   # Generate DOT without GraphML
   dot_path = "/path/to/output.dot"
   # ... (use graphviz.Digraph as above)

   # Apply tred manually
   with open('output_tred.dot', 'w') as f:
       subprocess.run(['tred', dot_path], stdout=f)

   # Visualize with dot
   subprocess.run(['dot', '-Tpng', 'output_tred.dot', '-o', 'output.png'])

Extending with New EM Node Types
---------------------------------

Step 1: Add Type to Database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Insert new US type
   us = US(
       sito="Test Site",
       id_us=999,
       unita_tipo="NEW_TYPE",  # <-- New EM type
       d_interpretativa="Node description",
       periodo_iniziale=1,
       fase_iniziale=1
   )
   db_manager.session.add(us)
   db_manager.session.commit()

Step 2: Configure Relationship Inversion
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**File**: ``pyarchinit_mini/harris_matrix/matrix_generator.py``

**Method**: ``generate_matrix()``

**Line**: ~194

.. code-block:: python

   # Special node types that should be TARGET of relationships (not source)
   special_target_types = [
       'DOC', 'Extractor', 'Combiner',
       'USVA', 'USVB', 'USVC', 'USD', 'TU', 'SF', 'VSF',
       'NEW_TYPE'  # <-- Add here
   ]

**Explanation**:

- Nodes in ``special_target_types`` are **always TARGET** of relationships
- Example: if DB has ``NEW_TYPE → US5``, system inverts to ``US5 → NEW_TYPE``
- **Exception**: Symbolic relationships (``>``, ``>>``, ``<``, ``<<``) are not inverted

Step 3: Configure Edge Style (Optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If the new node requires specific edge style:

**File**: ``pyarchinit_mini/harris_matrix/matrix_generator.py``

**Method**: ``export_to_graphml()``

**Line**: ~750-810

.. code-block:: python

   # Classify edges by type
   for source, target, edge_data in graph.edges(data=True):
       rel_type = edge_data.get('relationship', 'sopra')
       rel_lower = rel_type.lower()

       # ... existing ...

       # Add new classification
       elif rel_lower in ['new_type_relationship']:
           edges_new_type.append((source_label, target_label))

   # Render edges with specific style
   for source_label, target_label in edges_new_type:
       G.edge(source_label, target_label,
              color='black',
              style='dashed',  # Choose style
              arrowhead='diamond')  # Choose arrowhead

**Available arrowheads**: ``normal``, ``dot``, ``box``, ``diamond``, ``odiamond``, ``none``

**Available styles**: ``solid``, ``dotted``, ``dashed``, ``bold``

Step 4: Configure Node Symbology (yEd)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For special graphic symbols (like DOC = data object):

**File**: ``pyarchinit_mini/graphml_converter/dot_parser.py``

**Method**: ``exportGraphml()``

**Line**: ~1010-1050

.. code-block:: python

   # Detect node type
   if 'NEW_TYPE' in a_type:
       # Use GenericNode (example: BPMN artifact)
       generic_node = doc.createElement('y:GenericNode')
       generic_node.setAttribute('configuration', 'com.yworks.bpmn.Artifact')

       geom = doc.createElement('y:Geometry')
       geom.setAttribute('height', '55.0')
       geom.setAttribute('width', '35.0')
       geom.setAttribute('x', '520.0')
       geom.setAttribute('y', str(self.get_y(epoch_sigla, LabelText)))

       generic_node.appendChild(geom)
       # ... label, StyleProperties, etc.

       data0.appendChild(generic_node)

**Available yEd configurations**:

- ``y:ShapeNode`` - Standard shapes (rectangle, ellipse, parallelogram, etc.)
- ``y:GenericNode`` with ``com.yworks.bpmn.Artifact`` - BPMN symbols (document, data)
- ``y:SVGNode`` - Custom SVG shapes (e.g., circle for continuity)

Step 5: Test
~~~~~~~~~~~~

.. code-block:: python

   # Test with new type
   graph = matrix_generator.generate_matrix("Test Site")

   # Verify node present
   assert 999 in graph.nodes()
   assert graph.nodes[999]['unita_tipo'] == 'NEW_TYPE'

   # Verify edge direction (if it has relationships)
   edges = list(graph.out_edges(999))  # Outgoing edges
   print(f"NEW_TYPE → {edges}")

   # Export and verify GraphML
   result = matrix_generator.export_to_graphml(
       graph=graph,
       output_path="test_new_type.graphml",
       site_name="Test Site"
   )

   # Open with yEd and verify symbol and positioning

Debugging and Troubleshooting
------------------------------

Problem: Missing Nodes in GraphML
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Cause**: DOT parser doesn't find nodes

**Solution**: Verify DOT attributes

.. code-block:: bash

   # Check generated DOT
   grep "MISSING_NODE" output.dot

   # Verify it has base attributes
   # label, shape, style, fillcolor

Problem: All Nodes on First Row
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Cause**: ``period`` attribute missing or not found in epoch list

**Solution**:

.. code-block:: python

   # Verify epoch list
   from pyarchinit_mini.graphml_converter.converter import DotToGraphMLConverter
   converter = DotToGraphMLConverter()
   print(converter.epoch_list)  # Must contain period names

   # Verify period attribute in DOT
   grep "period=" output.dot
   # Should show: period="Modern Age" (NAME, not "1-2")

Problem: Inverted Relationships
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Cause**: EM node not in ``special_target_types`` or is a symbolic relationship

**Solution**:

.. code-block:: python

   # Verify node type
   node_data = graph.nodes[node_id]
   print(node_data['unita_tipo'])

   # Verify if symbolic relationship
   rel_type = edge_data['relationship']
   if rel_type in ['>', '>>', '<', '<<']:
       print("Symbolic relationship - NOT inverted")
   else:
       print("Standard relationship - inverted if EM node")

Problem: Wrong Edge Style
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Cause**: Edge classification not correct

**Solution**: Debug edge classification

.. code-block:: python

   # Before export, print classification
   edges_dotted = []
   edges_double_no_arrow = []
   # ... (classify all edges)

   print(f"Dotted: {len(edges_dotted)}")
   print(f"Double: {len(edges_double_no_arrow)}")
   # ... verify counts

Reference Files
---------------

.. list-table::
   :widths: 40 60
   :header-rows: 1

   * - File
     - Description
   * - ``pyarchinit_mini/harris_matrix/matrix_generator.py``
     - Core: generate graph, export DOT, export GraphML
   * - ``pyarchinit_mini/graphml_converter/converter.py``
     - Convert DOT → GraphML (dispatcher)
   * - ``pyarchinit_mini/graphml_converter/dot_parser.py``
     - Parse DOT, calculate positions, render nodes
   * - ``pyarchinit_mini/graphml_converter/graphml_exporter.py``
     - Render final GraphML XML
   * - ``pyarchinit_mini/graphml_converter/templates/EM_palette.graphml``
     - Base template with key definitions

Complete Integration Example
-----------------------------

Custom Archaeological Data Pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   """
   Complete example: Archaeological data pipeline with GraphML export

   This demonstrates a full workflow from database to visualization
   """

   from pyarchinit_mini.database.manager import DatabaseManager
   from pyarchinit_mini.harris_matrix.matrix_generator import MatrixGenerator
   from pyarchinit_mini.graphml_converter.graphml_exporter import GraphMLExporter
   import logging
   from pathlib import Path

   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger(__name__)

   class ArchaeologicalVisualizationPipeline:
       """
       Complete pipeline for Harris Matrix visualization
       """

       def __init__(self, db_path: str, output_dir: str):
           self.db_url = f'sqlite:///{db_path}'
           self.db_manager = DatabaseManager(self.db_url)
           self.matrix_gen = MatrixGenerator(self.db_url)
           self.output_dir = Path(output_dir)
           self.output_dir.mkdir(parents=True, exist_ok=True)

       def generate_site_matrix(
           self,
           site: str,
           area: str = None,
           include_periods: bool = True,
           apply_reduction: bool = True
       ) -> dict:
           """
           Generate complete Harris Matrix visualization

           Args:
               site: Site name
               area: Area name (optional)
               include_periods: Include periodization
               apply_reduction: Apply transitive reduction

           Returns:
               dict: Generated file paths and statistics
           """
           logger.info(f"Generating matrix for {site}")

           # Generate NetworkX graph
           graph = self.matrix_gen.generate_matrix(site, area)

           logger.info(f"Graph generated: {graph.number_of_nodes()} nodes, "
                      f"{graph.number_of_edges()} edges")

           # Prepare output paths
           safe_name = site.replace(' ', '_').lower()
           if area:
               safe_name += f"_{area.replace(' ', '_').lower()}"

           outputs = {
               'dot': self.output_dir / f'{safe_name}.dot',
               'dot_reduced': self.output_dir / f'{safe_name}_reduced.dot',
               'graphml': self.output_dir / f'{safe_name}.graphml',
               'png': self.output_dir / f'{safe_name}.png'
           }

           # Phase 1: Export to DOT
           logger.info("Phase 1: Exporting to DOT format")
           self.matrix_gen.export_to_dot(
               graph=graph,
               output_path=str(outputs['dot']),
               site_name=site,
               include_periods=include_periods
           )

           # Phase 2: Apply transitive reduction
           if apply_reduction:
               logger.info("Phase 2: Applying transitive reduction")
               success = apply_transitive_reduction(
                   str(outputs['dot']),
                   str(outputs['dot_reduced'])
               )
               dot_file = outputs['dot_reduced'] if success else outputs['dot']
           else:
               dot_file = outputs['dot']

           # Phase 3: Convert to GraphML
           logger.info("Phase 3: Converting to GraphML")
           from pyarchinit_mini.graphml_converter.converter import convert_dot_to_graphml

           success = convert_dot_to_graphml(
               dot_file=str(dot_file),
               graphml_file=str(outputs['graphml']),
               title=f'{site} Harris Matrix',
               reverse_epochs=False
           )

           # Phase 4: Generate PNG preview
           logger.info("Phase 4: Generating PNG preview")
           import subprocess
           try:
               subprocess.run([
                   'dot', '-Tpng',
                   str(dot_file),
                   '-o', str(outputs['png'])
               ], timeout=60, check=True)
           except Exception as e:
               logger.warning(f"PNG generation failed: {e}")

           # Gather statistics
           stats = {
               'site': site,
               'area': area,
               'nodes': graph.number_of_nodes(),
               'edges': graph.number_of_edges(),
               'files': {
                   name: str(path)
                   for name, path in outputs.items()
                   if path.exists()
               }
           }

           logger.info(f"Matrix generation complete for {site}")
           return stats

       def batch_export(self, sites: list) -> list:
           """
           Generate matrices for multiple sites

           Args:
               sites: List of (site, area) tuples

           Returns:
               list: Statistics for each export
           """
           results = []

           for site_data in sites:
               if isinstance(site_data, tuple):
                   site, area = site_data
               else:
                   site, area = site_data, None

               try:
                   stats = self.generate_site_matrix(site, area)
                   results.append(stats)
               except Exception as e:
                   logger.error(f"Failed to generate matrix for {site}: {e}")
                   results.append({
                       'site': site,
                       'area': area,
                       'error': str(e)
                   })

           return results

   # Usage example
   if __name__ == '__main__':
       # Initialize pipeline
       pipeline = ArchaeologicalVisualizationPipeline(
           db_path='pyarchinit_mini.db',
           output_dir='exports/harris_matrices'
       )

       # Generate single site
       stats = pipeline.generate_site_matrix('Pompeii', 'Area A')
       print(f"\nGenerated files:")
       for name, path in stats['files'].items():
           print(f"  {name}: {path}")

       # Batch export multiple sites
       sites_to_export = [
           ('Pompeii', 'Area A'),
           ('Pompeii', 'Area B'),
           ('Rome', 'Forum'),
       ]

       results = pipeline.batch_export(sites_to_export)

       print(f"\n\nBatch export complete:")
       for result in results:
           if 'error' in result:
               print(f"  ✗ {result['site']}: {result['error']}")
           else:
               print(f"  ✓ {result['site']}: {result['nodes']} nodes, "
                    f"{result['edges']} edges")

**Expected Output**:

.. code-block:: text

   INFO:__main__:Generating matrix for Pompeii
   INFO:__main__:Graph generated: 125 nodes, 342 edges
   INFO:__main__:Phase 1: Exporting to DOT format
   INFO:__main__:Phase 2: Applying transitive reduction
   Transitive reduction applied: exports/harris_matrices/pompeii_area_a_reduced.dot
   INFO:__main__:Phase 3: Converting to GraphML
   INFO:__main__:Phase 4: Generating PNG preview
   INFO:__main__:Matrix generation complete for Pompeii

   Generated files:
     dot: exports/harris_matrices/pompeii_area_a.dot
     dot_reduced: exports/harris_matrices/pompeii_area_a_reduced.dot
     graphml: exports/harris_matrices/pompeii_area_a.graphml
     png: exports/harris_matrices/pompeii_area_a.png

   Batch export complete:
     ✓ Pompeii: 125 nodes, 342 edges
     ✓ Pompeii: 89 nodes, 234 edges
     ✓ Rome: 203 nodes, 567 edges

References
----------

- **PyArchInit Extended Matrix**: `GitHub pyarchinit/pyarchinit3 <https://github.com/pyarchinit/pyarchinit3>`_
- **Graphviz DOT Language**: `graphviz.org/doc/info/lang.html <https://graphviz.org/doc/info/lang.html>`_
- **yEd GraphML Format**: `yWorks GraphML Primer <https://yed.yworks.com/support/manual/graphml_primer.html>`_
- **Harris Matrix**: Harris, E. C. (1979). Principles of Archaeological Stratigraphy. DOI: `10.1016/B978-0-12-326580-9.50009-3 <https://doi.org/10.1016/B978-0-12-326580-9.50009-3>`_

See Also
--------

- :doc:`extended-matrix-framework` - Complete EM framework documentation
- :doc:`harris_matrix` - Harris Matrix user guide
- :doc:`../python-api/overview` - Python API overview
- :doc:`../examples/python_api` - More Python examples

**The GraphML export system is production-ready with complete technical documentation!** 🚀
