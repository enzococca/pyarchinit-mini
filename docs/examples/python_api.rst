================================
Python Module Usage Examples
================================

This guide shows how to use PyArchInit-Mini modules directly in your Python projects, without needing the web interface or API.

.. contents:: Table of Contents
   :local:
   :depth: 2

Basic Setup
===========

Database Connection
-------------------

First, establish a database connection:

.. code-block:: python

    from pyarchinit_mini.database.connection import DatabaseConnection
    from pyarchinit_mini.database.manager import DatabaseManager

    # SQLite (local file)
    db_conn = DatabaseConnection.from_url("sqlite:///./my_archaeology.db")

    # PostgreSQL (server)
    db_conn = DatabaseConnection.from_url(
        "postgresql://user:password@localhost:5432/archaeology_db"
    )

    # Create tables if needed
    db_conn.create_tables()

    # Initialize manager
    db_manager = DatabaseManager(db_conn)

    # Run migrations
    migrations_applied = db_manager.run_migrations()
    print(f"Applied {migrations_applied} migrations")


Site Management
===============

Creating and Managing Sites
----------------------------

.. code-block:: python

    from pyarchinit_mini.services.site_service import SiteService

    # Initialize service
    site_service = SiteService(db_manager)

    # Create a new archaeological site
    site_data = {
        'sito': 'Pompei',
        'nazione': 'Italia',
        'regione': 'Campania',
        'comune': 'Pompei',
        'provincia': 'Napoli',
        'definizione_sito': 'Città romana',
        'descrizione': 'Antica città romana sepolta dall\'eruzione del Vesuvio nel 79 d.C.'
    }

    new_site = site_service.create_site(site_data)
    print(f"Created site: {new_site.sito} (ID: {new_site.id_sito})")

    # Get all sites
    sites = site_service.get_all_sites(page=1, size=10)
    for site in sites:
        print(f"- {site.sito} ({site.nazione})")

    # Search sites by name
    pompei_sites = site_service.search_sites_by_name("Pompei")

    # Get single site
    site = site_service.get_site_dto_by_id(new_site.id_sito)
    print(f"Site name: {site.sito}")
    print(f"Region: {site.regione}")

    # Update site
    site_service.update_site(new_site.id_sito, {
        'descrizione': 'Updated description with more details'
    })

    # Delete site
    site_service.delete_site(new_site.id_sito)


Stratigraphic Units (US)
=========================

Managing US Records
-------------------

.. code-block:: python

    from pyarchinit_mini.services.us_service import USService

    us_service = USService(db_manager)

    # Create a stratigraphic unit
    us_data = {
        'sito': 'Pompei',
        'area': '1',
        'us': 1001,
        'unita_tipo': 'US',
        'd_stratigrafica': 'Strato di crollo con frammenti di intonaco',
        'interpretazione': 'Crollo della copertura',
        'periodo_iniziale': '79 d.C.',
        'periodo_finale': '79 d.C.',
        'anno_scavo': 2024,
        'metodo_di_scavo': 'Manuale',
        'schedatore': 'Dr. Rossi',
        'colore': 'Marrone rossastro',
        'consistenza': 'Compatta',
        'inclusi': 'Ceramica, malta, intonaco',
        # Stratigraphic relations
        'rapporti': 'COVERS:1002,FILLS:1003'
    }

    new_us = us_service.create_us(us_data)
    print(f"Created US {new_us.us} for site {new_us.sito}")

    # Get US by site
    pompei_us = us_service.get_us_by_site('Pompei', page=1, size=50)
    for us in pompei_us:
        print(f"US {us.us}: {us.d_stratigrafica}")

    # Get single US
    us = us_service.get_us_dto_by_id(new_us.id_us)

    # Get US by number and site
    us_1001 = us_service.get_us_by_us_and_site(1001, 'Pompei')

    # Update US
    us_service.update_us(new_us.id_us, {
        'd_stratigrafica': 'Updated stratigraphic description',
        'colore': 'Rosso mattone'
    })

    # Delete US
    us_service.delete_us(new_us.id_us)


Advanced US Queries
-------------------

.. code-block:: python

    # Filter by type
    walls = us_service.get_us_by_type('USM')  # Masonry units

    # Get US by area
    area_1_units = us_service.get_us_by_area('Pompei', '1')

    # Get US by excavation year
    us_2024 = us_service.get_us_by_year('Pompei', 2024)


Material Inventory
==================

Managing Archaeological Finds
------------------------------

.. code-block:: python

    from pyarchinit_mini.services.inventario_service import InventarioService

    inventario_service = InventarioService(db_manager)

    # Create inventory record
    inventory_data = {
        'sito': 'Pompei',
        'numero_inventario': 'POM-2024-001',
        'tipo_reperto': 'Ceramica',
        'criterio_schedatura': 'TMA',  # Tipologico
        'definizione': 'Anfora vinaria',
        'descrizione': 'Anfora completa tipo Dressel 2-4',
        'area': '1',
        'us': 1001,
        'stato_conservazione': 'Integro',
        'datazione_reperto': 'I secolo d.C.',
        'materiale': 'Terracotta',
        'tecniche_lavorazione': 'Tornio',
        'dimensioni_lung': 65.5,  # cm
        'dimensioni_larg': 32.0,
        'dimensioni_alt': 85.0,
        'peso': 12.5,  # kg
        'quantita': 1
    }

    new_item = inventario_service.create_inventario(inventory_data)
    print(f"Created inventory item: {new_item.numero_inventario}")

    # Get all inventory for site
    items = inventario_service.get_inventario_by_site('Pompei', page=1, size=20)

    # Filter by type
    ceramics = inventario_service.get_inventario_by_type('Pompei', 'Ceramica')

    # Filter by US
    us_finds = inventario_service.get_inventario_by_us('Pompei', 1001)

    # Get by inventory number
    item = inventario_service.get_by_inventory_number('POM-2024-001')


Harris Matrix Generation
=========================

Generating Stratigraphic Diagrams
----------------------------------

.. code-block:: python

    from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator
    from pyarchinit_mini.harris_matrix.pyarchinit_visualizer import PyArchInitMatrixVisualizer
    import tempfile

    # Initialize generator
    matrix_gen = HarrisMatrixGenerator(us_service)

    # Generate matrix for site
    graph = matrix_gen.generate_matrix('Pompei')

    print(f"Nodes: {len(graph['nodes'])}")
    print(f"Edges: {len(graph['edges'])}")
    print(f"Levels: {graph['levels']}")

    # Detect paradoxes
    paradoxes = matrix_gen.detect_paradoxes('Pompei')
    if paradoxes:
        print("⚠️ Stratigraphic paradoxes detected:")
        for paradox in paradoxes:
            print(f"  - Cycle: {' -> '.join(map(str, paradox))}")

    # Visualize with PyArchInit style
    visualizer = PyArchInitMatrixVisualizer()

    # Export as PNG
    output_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    visualizer.visualize(
        graph=graph,
        output_path=output_file.name,
        title='Harris Matrix - Pompei',
        format='png',
        layout='dot'  # or 'neato', 'circo', 'twopi'
    )
    print(f"Matrix exported to: {output_file.name}")

    # Export as DOT (Graphviz)
    dot_file = tempfile.NamedTemporaryFile(suffix='.dot', delete=False, mode='w')
    visualizer.export_dot(graph, dot_file.name)
    print(f"DOT file: {dot_file.name}")


GraphML Export
--------------

.. code-block:: python

    from pyarchinit_mini.graphml_converter import convert_dot_content_to_graphml

    # Generate DOT content
    dot_content = visualizer.generate_dot(graph)

    # Convert to GraphML (yEd compatible)
    graphml_output = convert_dot_content_to_graphml(
        dot_content=dot_content,
        output_file='pompei_matrix.graphml',
        palette='extended_matrix'  # or 'default'
    )
    print(f"GraphML exported to: {graphml_output}")


PDF Export
==========

Generating Site/US Reports
---------------------------

.. code-block:: python

    from pyarchinit_mini.pdf_export.pdf_generator import PDFGenerator
    from datetime import datetime

    pdf_gen = PDFGenerator()

    # Generate site report
    site = site_service.get_site_dto_by_id(site_id)

    pdf_path = pdf_gen.generate_site_pdf(
        site=site,
        output_path='pompei_report.pdf',
        title='Site Report - Pompei',
        author='Archaeological Team',
        logo_path='logo/logo_pyarchinit-mini.png'  # Optional
    )
    print(f"Site report: {pdf_path}")

    # Generate US report
    us = us_service.get_us_dto_by_id(us_id)

    pdf_path = pdf_gen.generate_us_pdf(
        us=us,
        output_path=f'us_{us.us}_report.pdf',
        title=f'US {us.us} Report',
        include_photos=True,
        include_drawings=True
    )
    print(f"US report: {pdf_path}")

    # Generate inventory report
    items = inventario_service.get_inventario_by_site('Pompei')

    pdf_path = pdf_gen.generate_inventory_pdf(
        items=items,
        output_path='pompei_inventory.pdf',
        title='Material Inventory - Pompei',
        group_by='tipo_reperto'  # or 'us', 'area'
    )


Media Management
================

Handling Photos and Documents
------------------------------

.. code-block:: python

    from pyarchinit_mini.media_manager.media_handler import MediaHandler
    from pyarchinit_mini.services.media_service import MediaService
    import os

    media_handler = MediaHandler(base_upload_dir='uploads')
    media_service = MediaService(db_manager)

    # Store file
    photo_path = '/path/to/photo.jpg'

    stored_metadata = media_handler.store_file(
        file_path=photo_path,
        entity_type='us',  # or 'site', 'inventario'
        entity_id=us_id,
        description='Foto dello strato di crollo',
        tags='crollo,intonaco,us1001',
        author='Dr. Rossi'
    )

    print(f"File stored at: {stored_metadata['stored_path']}")
    print(f"File type: {stored_metadata['media_type']}")
    print(f"Size: {stored_metadata['file_size']} bytes")

    # Get media for entity
    us_media = media_handler.get_media_for_entity('us', us_id)
    for media in us_media:
        print(f"- {media['filename']} ({media['media_type']})")

    # Create media archive (ZIP)
    archive_path = media_handler.create_media_archive(
        entity_type='us',
        entity_id=us_id,
        output_file='us_1001_media.zip'
    )
    print(f"Archive created: {archive_path}")


Thesaurus and Controlled Vocabularies
======================================

Using ICCD Thesaurus
--------------------

.. code-block:: python

    from pyarchinit_mini.services.thesaurus_service import ThesaurusService

    thesaurus_service = ThesaurusService(db_manager)

    # Get material types
    materials = thesaurus_service.get_materiale_types()
    print("Materials:", materials)

    # Get conservation states
    states = thesaurus_service.get_stato_conservazione_types()
    print("Conservation states:", states)

    # Get technique types
    techniques = thesaurus_service.get_tecnica_types()

    # Add custom vocabulary
    thesaurus_service.add_custom_term(
        category='materiale',
        term='Pasta vitrea',
        description='Vetro romano opaco'
    )


Database Export/Import
======================

Backup and Migration
--------------------

.. code-block:: python

    from pyarchinit_mini.database.manager import DatabaseManager
    import json

    # Export entire database
    export_data = {
        'sites': [s.__dict__ for s in site_service.get_all_sites(size=1000)],
        'us': [u.__dict__ for u in us_service.get_all_us(size=10000)],
        'inventory': [i.__dict__ for i in inventario_service.get_all_inventario(size=10000)]
    }

    with open('pompei_backup.json', 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, default=str)

    # Import from backup
    with open('pompei_backup.json', 'r', encoding='utf-8') as f:
        import_data = json.load(f)

    for site_data in import_data['sites']:
        site_service.create_site(site_data)

    for us_data in import_data['us']:
        us_service.create_us(us_data)


3D Visualization (s3Dgraphy)
=============================

Managing 3D Models
------------------

.. code-block:: python

    from pyarchinit_mini.s3d_integration.model_manager import Model3DManager
    from pyarchinit_mini.s3d_integration.s3d_exporter import S3DExporter

    # Initialize manager
    model_manager = Model3DManager(base_path='uploads/3d_models')

    # Upload 3D model
    model_path = '/path/to/us_1001.obj'

    stored_path = model_manager.store_model(
        model_path=model_path,
        site_name='Pompei',
        us_id='1001',
        model_type='OBJ'  # or 'GLTF', 'GLB'
    )
    print(f"3D model stored: {stored_path}")

    # Get models for site
    site_models = model_manager.get_models_for_site('Pompei')
    for model in site_models:
        print(f"- US {model['us_id']}: {model['filename']}")

    # Generate Extended Matrix colored model
    from pyarchinit_mini.s3d_integration.test_model_generator import generate_test_3d_model

    generate_test_3d_model(
        output_dir='models',
        site_name='Pompei',
        us_number=1001,
        us_type='Deposito',  # Extended Matrix category
        format='both'  # OBJ and GLTF
    )


Complete Integration Example
============================

Archaeological Campaign Workflow
---------------------------------

.. code-block:: python

    from pyarchinit_mini.database.connection import DatabaseConnection
    from pyarchinit_mini.database.manager import DatabaseManager
    from pyarchinit_mini.services.site_service import SiteService
    from pyarchinit_mini.services.us_service import USService
    from pyarchinit_mini.services.inventario_service import InventarioService
    from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator
    from pyarchinit_mini.harris_matrix.pyarchinit_visualizer import PyArchInitMatrixVisualizer

    # 1. Setup
    db_conn = DatabaseConnection.from_url("sqlite:///./campagna_2024.db")
    db_conn.create_tables()
    db_manager = DatabaseManager(db_conn)

    site_service = SiteService(db_manager)
    us_service = USService(db_manager)
    inventario_service = InventarioService(db_manager)

    # 2. Create site
    site = site_service.create_site({
        'sito': 'Scavo Via Roma',
        'comune': 'Milano',
        'anno_scavo': 2024
    })

    # 3. Add stratigraphic units
    us_data = [
        {'sito': 'Scavo Via Roma', 'us': 1, 'area': '1',
         'd_stratigrafica': 'Humus superficiale', 'rapporti': ''},
        {'sito': 'Scavo Via Roma', 'us': 2, 'area': '1',
         'd_stratigrafica': 'Strato medievale', 'rapporti': 'COVERED_BY:1'},
        {'sito': 'Scavo Via Roma', 'us': 3, 'area': '1',
         'd_stratigrafica': 'Muro romano', 'rapporti': 'COVERED_BY:2'},
    ]

    for us in us_data:
        us_service.create_us(us)

    # 4. Add finds
    inventario_service.create_inventario({
        'sito': 'Scavo Via Roma',
        'numero_inventario': 'SVR-001',
        'us': 2,
        'tipo_reperto': 'Ceramica',
        'definizione': 'Frammento di pentola'
    })

    # 5. Generate Harris Matrix
    matrix_gen = HarrisMatrixGenerator(us_service)
    graph = matrix_gen.generate_matrix('Scavo Via Roma')

    visualizer = PyArchInitMatrixVisualizer()
    visualizer.visualize(graph, 'matrix_via_roma.png', title='Harris Matrix - Via Roma')

    print("Campaign documentation complete!")


Using with External Projects
=============================

Integration in Django
---------------------

.. code-block:: python

    # django_app/archaeology/models.py
    from django.db import models
    from pyarchinit_mini.database.connection import DatabaseConnection
    from pyarchinit_mini.services.us_service import USService

    class ArchaeologicalSite(models.Model):
        name = models.CharField(max_length=200)
        pyarchinit_db_url = models.CharField(max_length=500)

        def get_stratigraphic_units(self):
            """Get US from PyArchInit database"""
            db_conn = DatabaseConnection.from_url(self.pyarchinit_db_url)
            db_manager = DatabaseManager(db_conn)
            us_service = USService(db_manager)
            return us_service.get_us_by_site(self.name)


Integration in Flask
--------------------

.. code-block:: python

    # flask_app/routes.py
    from flask import Flask, jsonify
    from pyarchinit_mini.services.site_service import SiteService

    app = Flask(__name__)

    @app.route('/api/sites/<site_name>/us')
    def get_site_us(site_name):
        us_list = us_service.get_us_by_site(site_name)
        return jsonify([{
            'us': u.us,
            'description': u.d_stratigrafica,
            'area': u.area
        } for u in us_list])


Async Operations (asyncio)
---------------------------

.. code-block:: python

    import asyncio
    from concurrent.futures import ThreadPoolExecutor

    async def process_multiple_sites(site_names):
        """Process multiple sites in parallel"""

        def process_site(site_name):
            graph = matrix_gen.generate_matrix(site_name)
            visualizer.visualize(graph, f'{site_name}_matrix.png')
            return site_name

        with ThreadPoolExecutor(max_workers=4) as executor:
            loop = asyncio.get_event_loop()
            tasks = [
                loop.run_in_executor(executor, process_site, site)
                for site in site_names
            ]
            completed = await asyncio.gather(*tasks)
            return completed

    # Run async
    sites = ['Pompei', 'Ercolano', 'Ostia']
    asyncio.run(process_multiple_sites(sites))


Next Steps
==========

* :doc:`/api/index` - Complete API Reference
* :doc:`/features/harris_matrix` - Harris Matrix Features
* :doc:`/features/s3dgraphy` - 3D Visualization
* :doc:`rest_api` - REST API Documentation
* :doc:`integration` - Advanced Integration Patterns
