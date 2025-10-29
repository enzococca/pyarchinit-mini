Extended Matrix GraphML Export - Technical Guide
================================================

:Date: 2025-10-29
:Version: 1.7.1+
:Status: ✅ Production Ready

.. contents:: Table of Contents
   :local:
   :depth: 3

Overview
--------

PyArchInit-Mini provides **two independent methods** for GraphML export:

1. **Pure NetworkX Export** (**Default**, **Recommended**)

   - Zero external dependencies beyond Python packages
   - Direct NetworkX → GraphML conversion
   - Full Extended Matrix (EM) support with 14 node types
   - yEd Graph Editor compatible output
   - Automatic period clustering and chronological ordering

2. **Graphviz-based Export** (Optional, Legacy)

   - Requires Graphviz software installation
   - NetworkX → Graphviz DOT → GraphML pipeline
   - Supports transitive reduction via ``tred`` command
   - Useful for DOT file generation and custom visualization

.. important::

   **Default Behavior**: All GraphML exports use **Pure NetworkX** unless you explicitly set ``use_graphviz=True``.

   **No Graphviz Required**: You do NOT need to install Graphviz software for normal GraphML export.

System Architecture
-------------------

Pure NetworkX Export (Default)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Direct Pipeline** (No external software required):

.. code-block:: text

   Database → NetworkX DiGraph → GraphML (yEd)
       ↓              ↓                ↓
     SQLite   Intermediate        XML with EM
              data structure       node styles

**Software Requirements**:

- Python 3.8+
- ``networkx>=3.0.0`` (auto-installed with pyarchinit-mini)

**No additional software needed!**

Graphviz Export (Optional)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Extended Pipeline** (Requires Graphviz installation):

.. code-block:: text

   Database → NetworkX DiGraph → Graphviz DOT → Reduced DOT → GraphML (yEd)
       ↓           ↓                   ↓             ↓            ↓
     SQLite   Intermediate       Python graphviz   tred cmd     XML
              data structure        module          (optional)

**Additional Requirements**:

- ``graphviz>=0.20.0`` (Python module, auto-installed)
- Graphviz software (manual installation, see below)

Software Requirements
---------------------

Core Requirements (Always Needed)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Install PyArchInit-Mini with NetworkX
   pip install pyarchinit-mini

This automatically installs:

- ``networkx>=3.0.0`` - Graph data structures and algorithms
- All other required Python dependencies

**That's it!** You can now export GraphML files.

Optional: Graphviz Software (Only if using ``use_graphviz=True``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Only install if you need**:

- DOT file generation for custom workflows
- Transitive reduction via ``tred`` command
- Legacy Graphviz-based export pipeline

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

**Windows (Chocolatey)**:

.. code-block:: powershell

   choco install graphviz

**Verify Installation**:

.. code-block:: bash

   dot -V
   # Output: dot - graphviz version X.X.X

Pure NetworkX Export API
-------------------------

Basic Usage (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pyarchinit_mini.database.manager import DatabaseManager
   from pyarchinit_mini.harris_matrix.matrix_generator import MatrixGenerator

   # Initialize
   db_url = 'sqlite:///pyarchinit_mini.db'
   matrix_gen = MatrixGenerator(db_url)

   # Generate NetworkX graph from database
   graph = matrix_gen.generate_matrix(
       sito='Pompeii',
       area='Area A'
   )

   # Export to GraphML using Pure NetworkX (DEFAULT)
   result = matrix_gen.export_to_graphml(
       graph=graph,
       output_path='pompeii_area_a.graphml',
       site_name='Pompeii',
       title='Pompeii - Area A Harris Matrix',
       use_extended_labels=True,      # Use EM labels (US1, DOC4001, etc.)
       include_periods=True,           # Group by archaeological periods
       reverse_epochs=False,           # False = oldest at top
       # use_graphviz=False            # This is the DEFAULT
   )

   print(f"✓ GraphML exported: {result}")

.. note::

   The ``use_graphviz`` parameter defaults to ``False``, so you get Pure NetworkX export by default.

Complete Export Example with Error Handling
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pyarchinit_mini.database.manager import DatabaseManager
   from pyarchinit_mini.harris_matrix.matrix_generator import MatrixGenerator
   from pathlib import Path

   def export_harris_matrix_pure(
       site: str,
       area: str,
       db_path: str,
       output_dir: str
   ) -> dict:
       """
       Export Harris Matrix using Pure NetworkX (no Graphviz required)

       Args:
           site: Site name
           area: Area name
           db_path: Path to SQLite database
           output_dir: Output directory for GraphML file

       Returns:
           dict: Export statistics and file paths
       """
       try:
           # Initialize generator
           db_url = f'sqlite:///{db_path}'
           matrix_gen = MatrixGenerator(db_url)

           # Generate graph
           print(f"📊 Generating graph for {site} - {area}...")
           graph = matrix_gen.generate_matrix(site, area)

           nodes = graph.number_of_nodes()
           edges = graph.number_of_edges()
           print(f"   {nodes} nodes, {edges} edges")

           # Prepare output path
           output_path = Path(output_dir) / f'{site}_{area}_matrix.graphml'
           output_path.parent.mkdir(parents=True, exist_ok=True)

           # Export using Pure NetworkX
           print(f"💾 Exporting to GraphML (Pure NetworkX)...")
           result = matrix_gen.export_to_graphml(
               graph=graph,
               output_path=str(output_path),
               site_name=site,
               title=f'{site} - {area} Harris Matrix',
               use_extended_labels=True,
               include_periods=True,
               reverse_epochs=False
               # use_graphviz=False is the default
           )

           # Check file size
           file_size = output_path.stat().st_size
           size_kb = file_size / 1024

           print(f"✅ Export complete!")
           print(f"   File: {output_path}")
           print(f"   Size: {size_kb:.1f} KB")

           return {
               'success': True,
               'output_path': str(output_path),
               'nodes': nodes,
               'edges': edges,
               'file_size': file_size,
               'method': 'Pure NetworkX (default)'
           }

       except Exception as e:
           print(f"❌ Export failed: {e}")
           import traceback
           traceback.print_exc()
           return {
               'success': False,
               'error': str(e)
           }

   # Usage
   stats = export_harris_matrix_pure(
       site='Pompeii',
       area='Area A',
       db_path='pyarchinit_mini.db',
       output_dir='exports'
   )

   if stats['success']:
       print(f"\n📊 Statistics:")
       print(f"   Nodes: {stats['nodes']}")
       print(f"   Edges: {stats['edges']}")
       print(f"   Method: {stats['method']}")
   else:
       print(f"\n❌ Error: {stats['error']}")

**Expected Output**:

.. code-block:: text

   📊 Generating graph for Pompeii - Area A...
      125 nodes, 342 edges
   💾 Exporting to GraphML (Pure NetworkX)...
   ✅ Export complete!
      File: exports/Pompeii_Area A_matrix.graphml
      Size: 245.3 KB

   📊 Statistics:
      Nodes: 125
      Edges: 342
      Method: Pure NetworkX (default)

Export Parameters Reference
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
     - ``""``
     - Diagram title (optional)
   * - ``use_extended_labels``
     - ``bool``
     - ``True``
     - Use EM labels (US1, DOC4001, etc.)
   * - ``include_periods``
     - ``bool``
     - ``True``
     - Group nodes by archaeological periods
   * - ``reverse_epochs``
     - ``bool``
     - ``False``
     - Reverse chronological order
   * - ``use_graphviz``
     - ``bool``
     - ``False``
     - Use Graphviz pipeline (requires installation)

Graphviz Export API (Optional)
-------------------------------

When to Use Graphviz Export
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use ``use_graphviz=True`` only if you need:

- **DOT file generation** for custom workflows
- **Transitive reduction** via ``tred`` command
- **Legacy compatibility** with existing Graphviz-based tools

.. warning::

   Graphviz export requires Graphviz software to be installed on your system.
   See installation instructions above.

Basic Graphviz Export
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pyarchinit_mini.harris_matrix.matrix_generator import MatrixGenerator

   # Initialize
   matrix_gen = MatrixGenerator('sqlite:///pyarchinit_mini.db')

   # Generate graph
   graph = matrix_gen.generate_matrix('Pompeii', 'Area A')

   # Export using Graphviz pipeline
   try:
       result = matrix_gen.export_to_graphml(
           graph=graph,
           output_path='pompeii_graphviz.graphml',
           site_name='Pompeii',
           use_graphviz=True  # Enable Graphviz export
       )
       print(f"✓ Graphviz export successful: {result}")

   except ImportError as e:
       print(f"❌ Graphviz not installed")
       print(f"   Install with: pip install graphviz")
       print(f"   And system Graphviz: brew install graphviz")
       print(f"\n   Or use default Pure NetworkX export:")
       print(f"   matrix_gen.export_to_graphml(graph, path, use_graphviz=False)")

   except FileNotFoundError as e:
       print(f"❌ Graphviz software not found")
       print(f"   Install system Graphviz:")
       print(f"   - macOS: brew install graphviz")
       print(f"   - Linux: sudo apt install graphviz")
       print(f"   - Windows: choco install graphviz")

Graphviz Export with DOT Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import subprocess
   from pathlib import Path

   def export_with_graphviz_pipeline(
       site: str,
       graph: nx.DiGraph,
       output_dir: str,
       apply_tred: bool = True
   ) -> dict:
       """
       Export using Graphviz pipeline with DOT files

       Generates:
       - .dot file (original Graphviz format)
       - .dot_tred file (transitively reduced, if apply_tred=True)
       - .graphml file (yEd format)

       Args:
           site: Site name
           graph: NetworkX graph
           output_dir: Output directory
           apply_tred: Apply transitive reduction using tred command

       Returns:
           dict: File paths and statistics
       """
       from pyarchinit_mini.harris_matrix.matrix_generator import MatrixGenerator

       matrix_gen = MatrixGenerator('sqlite:///pyarchinit_mini.db')
       output_path = Path(output_dir) / f'{site}_matrix.graphml'

       # Export with Graphviz
       print(f"📊 Exporting with Graphviz pipeline...")
       result = matrix_gen.export_to_graphml(
           graph=graph,
           output_path=str(output_path),
           site_name=site,
           use_graphviz=True
       )

       # Check generated files
       dot_file = output_path.with_suffix('.dot')
       dot_tred_file = output_path.parent / f'{output_path.stem}_tred.dot'

       files = {
           'graphml': str(output_path),
           'dot': str(dot_file) if dot_file.exists() else None,
           'dot_reduced': str(dot_tred_file) if dot_tred_file.exists() else None
       }

       # Generate PNG preview from DOT (optional)
       if dot_file.exists():
           png_file = output_path.with_suffix('.png')
           try:
               subprocess.run([
                   'dot', '-Tpng',
                   str(dot_file),
                   '-o', str(png_file)
               ], timeout=60, check=True)
               files['png'] = str(png_file)
               print(f"✓ PNG preview generated: {png_file}")
           except Exception as e:
               print(f"⚠️  PNG generation skipped: {e}")

       print(f"✅ Graphviz export complete!")
       for name, path in files.items():
           if path:
               print(f"   {name}: {path}")

       return files

   # Usage
   matrix_gen = MatrixGenerator('sqlite:///pyarchinit_mini.db')
   graph = matrix_gen.generate_matrix('Pompeii')

   files = export_with_graphviz_pipeline(
       site='Pompeii',
       graph=graph,
       output_dir='exports',
       apply_tred=True
   )

Comparison: Pure NetworkX vs Graphviz
--------------------------------------

.. list-table::
   :widths: 30 35 35
   :header-rows: 1

   * - Feature
     - Pure NetworkX
     - Graphviz
   * - **External Dependencies**
     - None
     - Graphviz software required
   * - **Installation**
     - ``pip install pyarchinit-mini``
     - ``pip install pyarchinit-mini`` + system Graphviz
   * - **Export Speed**
     - ⚡ Fast
     - Slower (external process)
   * - **EM Node Support**
     - ✅ Full (14 types)
     - ✅ Full (14 types)
   * - **Period Clustering**
     - ✅ Automatic
     - ✅ Via subgraphs
   * - **yEd Compatibility**
     - ✅ Optimized
     - ✅ Compatible
   * - **DOT File Output**
     - ❌ No
     - ✅ Yes (.dot + .dot_tred)
   * - **Transitive Reduction**
     - ✅ Built-in (NetworkX algorithm)
     - ✅ Via ``tred`` command
   * - **Recommended For**
     - Normal use, production
     - Custom workflows, DOT generation

**Recommendation**: Use Pure NetworkX (default) unless you specifically need DOT files.

Extended Matrix (EM) Features
------------------------------

Both export methods support the complete Extended Matrix specification:

**14 Specialized Node Types**:

- ``US`` - Standard stratigraphic unit
- ``USM`` - Masonry unit
- ``DOC`` - Document attachment (BPMN Artifact icon)
- ``Extractor`` - Extraction event
- ``Combiner`` - Combination event
- ``USVA``, ``USVB``, ``USVC`` - Virtual stratigraphic units (A/B/C)
- ``USD`` - Destructive unit
- ``TU`` - Topographical unit
- ``SF`` - Stratigraphic feature
- ``VSF`` - Virtual stratigraphic feature
- ``property`` - Property/attribute node

**Relationship Types**:

- Standard: ``copre``, ``taglia``, ``riempie``, ``si appoggia``, ``uguale a``, ``si lega a``
- Symbolic: ``>``, ``>>``, ``<``, ``<<`` (explicit direction)

**Automatic Features**:

- Period-based clustering and chronological ordering
- Differentiated edge styles (dotted, solid, bold)
- Special arrowheads (dot, box, none, standard)
- Node-specific symbols (document icon for DOC, etc.)

CLI Usage Examples
------------------

Using Default Pure NetworkX Export
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Interactive CLI
   pyarchinit-cli

   # Navigate to: 4. Harris Matrix → 1. Generate Harris Matrix
   # Enter site name: Pompeii
   # GraphML file generated automatically using Pure NetworkX

Using Python API from Command Line
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python -c "
   from pyarchinit_mini.harris_matrix.matrix_generator import MatrixGenerator

   gen = MatrixGenerator('sqlite:///pyarchinit_mini.db')
   graph = gen.generate_matrix('Pompeii')
   gen.export_to_graphml(graph, 'pompeii.graphml', 'Pompeii')

   print('✓ GraphML exported with Pure NetworkX')
   "

Using Graphviz Export from CLI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   python -c "
   from pyarchinit_mini.harris_matrix.matrix_generator import MatrixGenerator

   gen = MatrixGenerator('sqlite:///pyarchinit_mini.db')
   graph = gen.generate_matrix('Pompeii')
   gen.export_to_graphml(
       graph,
       'pompeii_graphviz.graphml',
       'Pompeii',
       use_graphviz=True
   )

   print('✓ GraphML exported with Graphviz pipeline')
   "

Troubleshooting
---------------

Problem: "Graphviz not installed" Error
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Error Message**:

.. code-block:: text

   ❌ ERROR: Python graphviz module not installed
   Install with: pip install pyarchinit-mini
   or: pip install graphviz

**Solution**:

This error only appears if you use ``use_graphviz=True``.

**Option 1** (Recommended): Use default Pure NetworkX export:

.. code-block:: python

   # Remove use_graphviz=True or set it to False
   gen.export_to_graphml(graph, 'output.graphml', site_name, use_graphviz=False)

**Option 2**: Install Graphviz if you need it:

.. code-block:: bash

   # Install Python module
   pip install graphviz

   # Install system Graphviz
   # macOS:
   brew install graphviz

   # Linux:
   sudo apt install graphviz

   # Windows:
   choco install graphviz

Problem: Missing Periods in GraphML
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Cause**: No data in ``periodizzazione_table``

**Solution**: Add period datations to your database:

.. code-block:: python

   from pyarchinit_mini.database.manager import DatabaseManager
   from pyarchinit_mini.models.datazione import Datazione

   db = DatabaseManager('sqlite:///pyarchinit_mini.db')

   # Add period datation
   period = Datazione(
       sito='Pompeii',
       periodo_iniziale=1,
       fase_iniziale=1,
       datazione_estesa='Roman Imperial Period (27 BC - 476 AD)',
       cron_iniziale=-27,
       cron_finale=476
   )
   db.session.add(period)
   db.session.commit()

See Also
--------

- :doc:`../examples/python_api` - Complete Python API examples
- :doc:`../examples/cli_usage` - CLI usage examples
- :doc:`extended-matrix-framework` - Extended Matrix specification
- :doc:`harris_matrix` - Harris Matrix user guide

**Summary**: PyArchInit-Mini provides flexible GraphML export with **Pure NetworkX as the default**, and optional Graphviz support for advanced workflows. No external dependencies required for normal use! 🚀
