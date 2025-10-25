s3Dgraphy Integration
=====================

.. include:: ../s3dgraphy_integration.md
   :parser: myst_parser.sphinx_

PyArchInit-Mini integrates with **s3Dgraphy**, a Python library for 3D stratigraphic graphs and Extended Matrix Framework.

Key Features
------------

* Export stratigraphic data to s3Dgraphy JSON v1.5 format
* Interactive 3D stratigraph viewer
* 3D model management (GLB, GLTF, OBJ, PLY, STL, FBX)
* Extended Matrix Framework compliance
* Multi-temporal knowledge graph support

Export Formats
--------------

s3Dgraphy JSON v1.5
~~~~~~~~~~~~~~~~~~~

Standard export format for general web platforms:

* Complete metadata for each stratigraphic unit
* Archaeological period context
* Stratigraphic relationships (is_before, has_same_time)
* 3D model references
* Extended Matrix node categories (10 categories)

Heriverse/ATON JSON
~~~~~~~~~~~~~~~~~~~

Full-featured format specifically for Heriverse and ATON platforms:

* **CouchDB/scene wrapper** with auto-generated UUIDs
* **Environment configuration** (panoramas, lighting)
* **Scenegraph** for 3D scene hierarchy
* **USVn category** for virtual negative units (separate from USVs)
* **Semantic shapes** - Auto-generated 3D proxy models (GLB)
* **Representation models** - Full-detail 3D models (GLTF)
* **Panorama models** - 360° panoramic images
* **Additional edge types** (generic_connection, changed_from, contrasts_with)
* **13 node categories** (including semantic_shapes, representation_models, panorama_models)
* **13 edge types** for comprehensive relationships

Usage
-----

Web Interface
~~~~~~~~~~~~~

1. Navigate to: **Menu → Harris Matrix → Export GraphML**
2. Scroll to **"Export s3Dgraphy (Extended Matrix)"** section
3. Select your archaeological site
4. Choose export format:

   * **Export JSON** - Standard s3Dgraphy v1.5 format
   * **Export Heriverse** - Heriverse/ATON format with CouchDB wrapper
   * **Interactive Viewer** - View in browser

5. Download the generated JSON file

API
~~~

Export s3Dgraphy JSON v1.5::

    GET /3d/export/json/<site_name>

Export Heriverse JSON::

    GET /3d/export/heriverse/<site_name>

Interactive Viewer::

    GET /3d/viewer/<site_name>

Upload 3D Model::

    POST /3d/upload
    Form data:
      - model_file: 3D model file
      - site_name: Archaeological site name
      - us_id: Stratigraphic unit ID

Python API
~~~~~~~~~~

.. code-block:: python

    from pyarchinit_mini.s3d_integration import S3DConverter, Model3DManager

    # Create s3Dgraphy graph from US data
    converter = S3DConverter()
    graph = converter.create_graph_from_us(us_list, "Pompeii")

    # Export to s3Dgraphy JSON v1.5
    converter.export_to_json(graph, "pompeii_s3d.json")

    # Export to Heriverse JSON (with CouchDB wrapper)
    converter.export_to_heriverse_json(
        graph,
        "pompeii_heriverse.json",
        site_name="Pompeii",
        creator_id="user:12345",
        resource_path="https://server/uploads"
    )

    # Manage 3D models
    manager = Model3DManager("uploads")
    metadata = manager.save_model("scan.glb", us_id="001", site_name="Pompeii")

Comparison with Native GraphML Export
--------------------------------------

.. list-table::
   :header-rows: 1
   :widths: 25 25 25 25

   * - Feature
     - Native GraphML
     - s3Dgraphy JSON v1.5
     - Heriverse JSON
   * - Format
     - GraphML (yEd)
     - JSON v1.5
     - Heriverse/CouchDB
   * - Metadata
     - Minimal
     - Complete
     - Complete + Scene
   * - 3D Model Support
     - No
     - References
     - Semantic shapes + Models
   * - CouchDB Wrapper
     - No
     - No
     - Yes
   * - USVn Category
     - No
     - No
     - Yes
   * - Use Case
     - yEd visualization
     - General web platforms
     - Heriverse/ATON platforms
   * - Period Layout
     - TableNode rows
     - Epoch context
     - Epoch context + Environment

When to Use
-----------

**Use Native GraphML for:**

* Quick visualization in yEd Graph Editor
* Period-based table layout
* Traditional Harris Matrix diagrams
* Transitive reduction visualization

**Use s3Dgraphy JSON v1.5 for:**

* General web platform integration
* Programmatic analysis
* Complete metadata export
* 3D model integration
* Extended Matrix Framework compliance

**Use Heriverse JSON for:**

* Uploading to Heriverse platform
* Integration with ATON viewer
* CouchDB-based systems
* Advanced 3D visualization with semantic shapes
* Full scene environment configuration

Resources
---------

* `s3Dgraphy GitHub <https://github.com/zalmoxes-laran/s3dgraphy>`_
* `Extended Matrix Framework <https://www.extendedmatrix.org>`_
* `s3Dgraphy Documentation <https://docs.extendedmatrix.org/projects/s3dgraphy/>`_
* `Import/Export Specification <https://docs.extendedmatrix.org/projects/s3dgraphy/en/latest/s3dgraphy_import_export.html>`_

See Also
--------

* :doc:`harris_matrix` - Native Harris Matrix generation
* :doc:`stratigraphic_relationships` - Relationship types
* :doc:`../EXTENDED_MATRIX_EXPORT` - Native GraphML export
