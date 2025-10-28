PyArchInit-Mini Python API - Complete Reference
=================================================

:Date: 2025-10-28
:Version: 1.7.0+
:Status: ✅ Complete API Documentation

.. contents:: Table of Contents
   :local:
   :depth: 3

Introduction
------------

PyArchInit-Mini provides a comprehensive Python API for archaeological data management. This guide shows you how to use all APIs and modules in your Python applications, with complete input/output examples and integration patterns for external projects.

**Use Cases**:

- Custom archaeological data management systems
- Automated data processing pipelines
- Integration with existing Python applications
- Batch operations and data migration
- Custom visualization and analysis tools

Architecture Overview
---------------------

Core Components
~~~~~~~~~~~~~~~

.. code-block:: text

   PyArchInit-Mini Architecture:

   ┌─────────────────────────────────────────┐
   │         Your Application                 │
   └─────────────────┬───────────────────────┘
                     │
   ┌─────────────────┴───────────────────────┐
   │         Python API Layer                 │
   │  ┌────────────┐  ┌─────────────────┐   │
   │  │  Services  │  │ Matrix Generator │   │
   │  │  - Site    │  │ - GraphML Export │   │
   │  │  - US      │  │ - DOT Export     │   │
   │  │  - Inv.    │  └─────────────────┘   │
   │  └────────────┘                         │
   └─────────────────┬───────────────────────┘
                     │
   ┌─────────────────┴───────────────────────┐
   │      Database Manager (SQLAlchemy)       │
   │  - Connection pooling                    │
   │  - Transaction management                │
   │  - ORM models                            │
   └─────────────────┬───────────────────────┘
                     │
   ┌─────────────────┴───────────────────────┐
   │         Database (SQLite/PostgreSQL)     │
   └──────────────────────────────────────────┘

**Key Modules**:

1. **Database Layer**: ``DatabaseManager``, Models
2. **Service Layer**: ``SiteService``, ``USService``, ``InventarioService``, ``ImportExportService``
3. **Visualization Layer**: ``MatrixGenerator``, ``GraphMLExporter``
4. **Utility Layer**: Configuration, Validation, Helpers

Quick Start
-----------

Installation
~~~~~~~~~~~~

.. code-block:: bash

   # Install with all features
   pip install 'pyarchinit-mini[all]'

   # Or install specific features
   pip install 'pyarchinit-mini[harris]'  # Harris Matrix features
   pip install 'pyarchinit-mini[web]'     # Web interface
   pip install 'pyarchinit-mini[auth]'    # Authentication

Basic Usage
~~~~~~~~~~~

.. code-block:: python

   from pyarchinit_mini.database.manager import DatabaseManager
   from pyarchinit_mini.services.site_service import SiteService
   from pyarchinit_mini.services.us_service import USService

   # Initialize database
   db = DatabaseManager('sqlite:///my_project.db')

   # Initialize services
   site_service = SiteService(db)
   us_service = USService(db)

   # Create a site
   site = site_service.create({
       'sito': 'Pompeii',
       'nazione': 'Italy',
       'regione': 'Campania',
       'descrizione': 'Ancient Roman city'
   })

   # Create a stratigraphic unit
   us = us_service.create({
       'sito': 'Pompeii',
       'area': 'Area A',
       'us': 1001,
       'unita_tipo': 'US',
       'd_stratigrafica': 'Fill layer with pottery',
       'd_interpretativa': 'Medieval fill'
   })

   print(f"Created site: {site['sito']}")
   print(f"Created US: {us['us']}")

**Expected Output**:

.. code-block:: text

   Created site: Pompeii
   Created US: 1001

Database Management
-------------------

DatabaseManager Class
~~~~~~~~~~~~~~~~~~~~~

The ``DatabaseManager`` class handles all database operations.

**Import**:

.. code-block:: python

   from pyarchinit_mini.database.manager import DatabaseManager

**Initialization**:

.. code-block:: python

   # SQLite
   db = DatabaseManager('sqlite:///path/to/database.db')

   # PostgreSQL
   db = DatabaseManager('postgresql://user:pass@localhost:5432/dbname')

   # With connection options
   db = DatabaseManager(
       'sqlite:///database.db',
       echo=True,  # Log SQL queries
       pool_size=10,  # Connection pool size
       max_overflow=20  # Max connections beyond pool_size
   )

**Methods**:

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Method
     - Description
   * - ``get_session()``
     - Get a new database session
   * - ``close()``
     - Close all connections
   * - ``create_all_tables()``
     - Create all database tables
   * - ``drop_all_tables()``
     - Drop all database tables

**Complete Example**:

.. code-block:: python

   from pyarchinit_mini.database.manager import DatabaseManager
   from contextlib import contextmanager

   class ArchaeologicalDatabase:
       """
       Wrapper for database operations with context management
       """

       def __init__(self, db_url: str):
           self.db = DatabaseManager(db_url)
           self.db.create_all_tables()

       @contextmanager
       def session_scope(self):
           """
           Provide a transactional scope for database operations
           """
           session = self.db.get_session()
           try:
               yield session
               session.commit()
           except Exception as e:
               session.rollback()
               raise
           finally:
               session.close()

       def execute_query(self, model, filters=None):
           """
           Execute a database query with filters

           Args:
               model: SQLAlchemy model class
               filters: Dictionary of filter conditions

           Returns:
               list: Query results
           """
           with self.session_scope() as session:
               query = session.query(model)

               if filters:
                   for key, value in filters.items():
                       if hasattr(model, key):
                           query = query.filter(
                               getattr(model, key) == value
                           )

               return query.all()

   # Usage
   arch_db = ArchaeologicalDatabase('sqlite:///project.db')

   # Query sites
   from pyarchinit_mini.database.models import Site
   sites = arch_db.execute_query(Site, {'nazione': 'Italy'})

   for site in sites:
       print(f"Site: {site.sito}, Region: {site.regione}")

Site Service API
----------------

The ``SiteService`` class manages archaeological site data.

Create Site
~~~~~~~~~~~

.. code-block:: python

   from pyarchinit_mini.services.site_service import SiteService

   site_service = SiteService(db)

   site_data = {
       'sito': 'Pompeii',
       'nazione': 'Italy',
       'regione': 'Campania',
       'comune': 'Pompeii',
       'descrizione': 'Ancient Roman city buried by Vesuvius eruption',
       'definizione_sito': 'Urban archaeological site',
       'provincia': 'Naples',
       'latitudine': 40.7489,
       'longitudine': 14.4864
   }

   result = site_service.create(site_data)

   print(f"Created site: {result['sito']}")
   print(f"Site ID: {result['id_sito']}")

**Expected Output**:

.. code-block:: text

   Created site: Pompeii
   Site ID: 1

Read Site
~~~~~~~~~

.. code-block:: python

   # Get by ID
   site = site_service.get_by_id(1)
   print(f"Site: {site['sito']}")

   # Get by name
   site = site_service.get_by_name('Pompeii')
   print(f"Description: {site['descrizione']}")

   # Get all sites
   all_sites = site_service.get_all()
   print(f"Total sites: {len(all_sites)}")

   for site in all_sites:
       print(f"  - {site['sito']} ({site['nazione']})")

**Expected Output**:

.. code-block:: text

   Site: Pompeii
   Description: Ancient Roman city buried by Vesuvius eruption
   Total sites: 3
     - Pompeii (Italy)
     - Rome (Italy)
     - Athens (Greece)

Update Site
~~~~~~~~~~~

.. code-block:: python

   # Update site data
   updates = {
       'descrizione': 'Updated description with new findings',
       'provincia': 'Metropolitan City of Naples'
   }

   result = site_service.update(site_id=1, updates=updates)
   print(f"Updated: {result['sito']}")

**Expected Output**:

.. code-block:: text

   Updated: Pompeii

Delete Site
~~~~~~~~~~~

.. code-block:: python

   # Delete site
   result = site_service.delete(site_id=1)
   print(f"Deleted: {result['success']}")

**Expected Output**:

.. code-block:: text

   Deleted: True

US (Stratigraphic Unit) Service API
------------------------------------

The ``USService`` class manages stratigraphic unit data.

Create US
~~~~~~~~~

.. code-block:: python

   from pyarchinit_mini.services.us_service import USService

   us_service = USService(db)

   us_data = {
       'sito': 'Pompeii',
       'area': 'Area A',
       'us': 1001,
       'unita_tipo': 'US',
       'd_stratigrafica': 'Fill layer with ceramic fragments and charcoal',
       'd_interpretativa': 'Medieval fill from abandonment phase',
       'tipo_us': 'deposit',
       'formazione': 'natural',
       'stato_di_conservazione': 'good',
       'colore': 'dark brown',
       'consistenza': 'compact',
       'struttura': 'homogeneous',
       'periodo_iniziale': 'Medieval',
       'fase_iniziale': 'Early Medieval',
       'periodo_finale': 'Medieval',
       'fase_finale': 'Late Medieval'
   }

   result = us_service.create(us_data)

   print(f"Created US: {result['us']}")
   print(f"Type: {result['unita_tipo']}")
   print(f"Site: {result['sito']}, Area: {result['area']}")

**Expected Output**:

.. code-block:: text

   Created US: 1001
   Type: US
   Site: Pompeii, Area: Area A

Search US
~~~~~~~~~

.. code-block:: python

   # Search by site
   us_list = us_service.search(sito='Pompeii')
   print(f"US in Pompeii: {len(us_list)}")

   # Search by area
   us_list = us_service.search(sito='Pompeii', area='Area A')
   print(f"US in Area A: {len(us_list)}")

   # Search by type
   usm_list = us_service.search(sito='Pompeii', unita_tipo='USM')
   print(f"USM units: {len(usm_list)}")

   # Search by period
   medieval_us = us_service.search(
       sito='Pompeii',
       periodo_iniziale='Medieval'
   )
   print(f"Medieval US: {len(medieval_us)}")

**Expected Output**:

.. code-block:: text

   US in Pompeii: 125
   US in Area A: 45
   USM units: 12
   Medieval US: 23

Add Relationships
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Add stratigraphic relationship
   relationship = {
       'sito': 'Pompeii',
       'area': 'Area A',
       'us': 1001,
       'rapporti': 'Copre',  # Covers
       'nazione': '',
       'us_rapporti': 1002
   }

   result = us_service.add_relationship(relationship)
   print(f"Relationship created: US {relationship['us']} → US {relationship['us_rapporti']}")

   # Add multiple relationships
   relationships = [
       {'us': 1001, 'rapporti': 'Copre', 'us_rapporti': 1002},
       {'us': 1002, 'rapporti': 'Copre', 'us_rapporti': 1003},
       {'us': 1003, 'rapporti': 'Si appoggia', 'us_rapporti': 2001},
   ]

   for rel in relationships:
       rel.update({'sito': 'Pompeii', 'area': 'Area A', 'nazione': ''})
       us_service.add_relationship(rel)

   print(f"Created {len(relationships)} relationships")

**Expected Output**:

.. code-block:: text

   Relationship created: US 1001 → US 1002
   Created 3 relationships

Get Relationships
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Get all relationships for a site
   relationships = us_service.get_relationships(sito='Pompeii')
   print(f"Total relationships: {len(relationships)}")

   for rel in relationships[:5]:  # Show first 5
       print(f"  US {rel['us']} {rel['rapporti']} US {rel['us_rapporti']}")

   # Get relationships for specific US
   us_1001_rels = [r for r in relationships if r['us'] == 1001]
   print(f"\nUS 1001 relationships: {len(us_1001_rels)}")

**Expected Output**:

.. code-block:: text

   Total relationships: 342
     US 1001 Copre US 1002
     US 1002 Copre US 1003
     US 1003 Si appoggia US 2001
     US 2001 Si lega a US 2002
     US 1004 Taglia US 1005

   US 1001 relationships: 3

Inventario (Material Inventory) Service API
--------------------------------------------

The ``InventarioService`` class manages material finds data.

Create Inventario Entry
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pyarchinit_mini.services.inventario_service import InventarioService

   inv_service = InventarioService(db)

   inventario_data = {
       'sito': 'Pompeii',
       'area': 'Area A',
       'us': 1001,
       'numero_inventario': 'POM2024-001',
       'tipo_reperto': 'Ceramic',
       'definizione_reperto': 'Terra sigillata plate fragment',
       'descrizione': 'Red-slip ware plate fragment with stamp',
       'tecnologia': 'Wheel-thrown',
       'forma': 'Plate',
       'stato_conservazione': 'fragmentary',
       'n_reperto': 1,
       'quota': -2.35,
       'osservazioni': 'Found in fill layer, possibly intrusive'
   }

   result = inv_service.create(inventario_data)

   print(f"Created inventory: {result['numero_inventario']}")
   print(f"Type: {result['tipo_reperto']}")
   print(f"From: US {result['us']}")

**Expected Output**:

.. code-block:: text

   Created inventory: POM2024-001
   Type: Ceramic
   From: US 1001

Search Inventario
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Search by site
   finds = inv_service.search(sito='Pompeii')
   print(f"Total finds: {len(finds)}")

   # Search by US
   us_finds = inv_service.search(sito='Pompeii', us=1001)
   print(f"Finds from US 1001: {len(us_finds)}")

   # Search by material type
   ceramics = inv_service.search(sito='Pompeii', tipo_reperto='Ceramic')
   print(f"Ceramic finds: {len(ceramics)}")

   # Complex search
   results = inv_service.search(
       sito='Pompeii',
       area='Area A',
       tipo_reperto='Ceramic',
       stato_conservazione='fragmentary'
   )
   print(f"Filtered results: {len(results)}")

**Expected Output**:

.. code-block:: text

   Total finds: 1234
   Finds from US 1001: 23
   Ceramic finds: 456
   Filtered results: 12

Import/Export Service API
--------------------------

The ``ImportExportService`` class handles data synchronization between PyArchInit and PyArchInit-Mini.

Initialize Import/Export
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pyarchinit_mini.services.import_export_service import ImportExportService

   # Initialize with database connections
   service = ImportExportService(
       mini_db_connection='sqlite:///pyarchinit_mini.db',
       source_db_connection='sqlite:///pyarchinit_source.db'
   )

   # Or with PostgreSQL
   service = ImportExportService(
       mini_db_connection='sqlite:///pyarchinit_mini.db',
       source_db_connection='postgresql://user:pass@localhost/pyarchinit'
   )

Import Sites
~~~~~~~~~~~~

.. code-block:: python

   # Import all sites
   stats = service.import_sites(
       auto_migrate=True,  # Add missing i18n columns
       auto_backup=True    # Create automatic backup
   )

   print(f"Sites imported: {stats['imported']}")
   print(f"Sites updated: {stats['updated']}")
   if stats.get('backup_path'):
       print(f"Backup created: {stats['backup_path']}")

   # Import specific sites
   stats = service.import_sites(
       sito_filter=['Pompeii', 'Herculaneum'],
       auto_migrate=True,
       auto_backup=True
   )

   print(f"Filtered import: {stats['imported']} sites")

**Expected Output**:

.. code-block:: text

   Sites imported: 5
   Sites updated: 0
   Backup created: /path/to/pyarchinit_source.db.backup_20251028_143025

   Filtered import: 2 sites

Import US with Relationships
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Import US with relationships
   stats = service.import_us(
       sito_filter=['Pompeii'],
       import_relationships=True,
       auto_migrate=True,
       auto_backup=True
   )

   print(f"US imported: {stats['imported']}")
   print(f"US updated: {stats['updated']}")
   print(f"Relationships created: {stats.get('relationships_created', 0)}")

**Expected Output**:

.. code-block:: text

   US imported: 758
   US updated: 0
   Relationships created: 2459

Complete Import Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def import_complete_site(site_name: str, mini_db: str, source_db: str) -> dict:
       """
       Import complete archaeological site data

       Args:
           site_name: Name of site to import
           mini_db: Target database URL
           source_db: Source database URL

       Returns:
           dict: Import statistics
       """
       from pyarchinit_mini.services.import_export_service import ImportExportService

       service = ImportExportService(mini_db, source_db)

       results = {}

       # Import site metadata
       print(f"Importing site: {site_name}")
       site_stats = service.import_sites(
           sito_filter=[site_name],
           auto_migrate=True,
           auto_backup=True
       )
       results['sites'] = site_stats
       print(f"  ✓ Sites: {site_stats['imported']}")

       # Import stratigraphic units
       print("Importing stratigraphic units...")
       us_stats = service.import_us(
           sito_filter=[site_name],
           import_relationships=True,
           auto_migrate=True,
           auto_backup=True
       )
       results['us'] = us_stats
       print(f"  ✓ US: {us_stats['imported']}")
       print(f"  ✓ Relationships: {us_stats.get('relationships_created', 0)}")

       # Import material inventory
       print("Importing material inventory...")
       inv_stats = service.import_inventario(
           sito_filter=[site_name],
           auto_migrate=True,
           auto_backup=True
       )
       results['inventario'] = inv_stats
       print(f"  ✓ Inventario: {inv_stats['imported']}")

       # Import periodization
       print("Importing periodization...")
       per_stats = service.import_periodizzazione(
           sito_filter=[site_name]
       )
       results['periodizzazione'] = per_stats
       print(f"  ✓ Periodizzazione: {per_stats['imported']}")

       # Import thesaurus (once per database)
       print("Importing thesaurus...")
       thes_stats = service.import_thesaurus()
       results['thesaurus'] = thes_stats
       print(f"  ✓ Thesaurus: {thes_stats['imported']}")

       return results

   # Usage
   stats = import_complete_site(
       'Pompeii',
       'sqlite:///pyarchinit_mini.db',
       'sqlite:///pyarchinit_source.db'
   )

**Expected Output**:

.. code-block:: text

   Importing site: Pompeii
     ✓ Sites: 1
   Importing stratigraphic units...
     ✓ US: 758
     ✓ Relationships: 2459
   Importing material inventory...
     ✓ Inventario: 1234
   Importing periodization...
     ✓ Periodizzazione: 42
   Importing thesaurus...
     ✓ Thesaurus: 156

Harris Matrix Generation API
-----------------------------

The ``MatrixGenerator`` class creates Harris Matrix visualizations.

Generate Matrix
~~~~~~~~~~~~~~~

.. code-block:: python

   from pyarchinit_mini.harris_matrix.matrix_generator import MatrixGenerator

   # Initialize generator
   matrix_gen = MatrixGenerator('sqlite:///pyarchinit_mini.db')

   # Generate matrix
   graph = matrix_gen.generate_matrix(
       sito='Pompeii',
       area='Area A'
   )

   print(f"Matrix generated:")
   print(f"  Nodes: {graph.number_of_nodes()}")
   print(f"  Edges: {graph.number_of_edges()}")

   # Inspect graph
   for node_id, data in list(graph.nodes(data=True))[:3]:
       print(f"\nNode {node_id}:")
       print(f"  Type: {data.get('unita_tipo')}")
       print(f"  Label: {data.get('extended_label')}")

**Expected Output**:

.. code-block:: text

   Matrix generated:
     Nodes: 125
     Edges: 342

   Node 1001:
     Type: US
     Label: US1001

   Node 2001:
     Type: USM
     Label: USM2001

   Node 8001:
     Type: DOC
     Label: DOC8001

Export to GraphML
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Export to GraphML for yEd
   output_file = matrix_gen.export_to_graphml(
       graph=graph,
       output_path='pompeii_matrix.graphml',
       site_name='Pompeii',
       title='Pompeii Area A Harris Matrix',
       include_periods=True,
       reverse_epochs=False
   )

   print(f"GraphML exported: {output_file}")

**Expected Output**:

.. code-block:: text

   GraphML exported: pompeii_matrix.graphml

Export to DOT
~~~~~~~~~~~~~

.. code-block:: python

   # Export to Graphviz DOT format
   dot_file = matrix_gen.export_to_dot(
       graph=graph,
       output_path='pompeii_matrix.dot',
       site_name='Pompeii',
       include_periods=True
   )

   print(f"DOT exported: {dot_file}")

   # Generate PNG from DOT
   import subprocess
   subprocess.run([
       'dot', '-Tpng',
       'pompeii_matrix.dot',
       '-o', 'pompeii_matrix.png'
   ])

**Expected Output**:

.. code-block:: text

   DOT exported: pompeii_matrix.dot

Integration Patterns
--------------------

Pattern 1: Custom Data Pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   """
   Custom archaeological data processing pipeline
   """

   from pyarchinit_mini.database.manager import DatabaseManager
   from pyarchinit_mini.services.site_service import SiteService
   from pyarchinit_mini.services.us_service import USService
   from pyarchinit_mini.harris_matrix.matrix_generator import MatrixGenerator
   import logging

   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger(__name__)

   class ArchaeologicalDataPipeline:
       """
       Complete data processing pipeline
       """

       def __init__(self, db_url: str):
           self.db = DatabaseManager(db_url)
           self.site_service = SiteService(self.db)
           self.us_service = USService(self.db)
           self.matrix_gen = MatrixGenerator(db_url)

       def process_excavation_data(self, site_name: str, data_file: str) -> dict:
           """
           Process excavation data from file

           Args:
               site_name: Site name
               data_file: Path to data file (CSV/Excel)

           Returns:
               dict: Processing statistics
           """
           import pandas as pd

           logger.info(f"Processing data for site: {site_name}")

           # Read data
           df = pd.read_excel(data_file)
           logger.info(f"Loaded {len(df)} records")

           stats = {
               'sites': 0,
               'us': 0,
               'relationships': 0
           }

           # Create site if not exists
           existing_site = self.site_service.get_by_name(site_name)
           if not existing_site:
               self.site_service.create({'sito': site_name})
               stats['sites'] = 1
               logger.info(f"Created site: {site_name}")

           # Process US records
           for _, row in df.iterrows():
               try:
                   us_data = {
                       'sito': site_name,
                       'area': row.get('area', 'Main'),
                       'us': int(row['us']),
                       'unita_tipo': row.get('type', 'US'),
                       'd_stratigrafica': row.get('description', ''),
                       'd_interpretativa': row.get('interpretation', '')
                   }

                   self.us_service.create(us_data)
                   stats['us'] += 1

                   # Add relationships if present
                   if 'relationship_to' in row and pd.notna(row['relationship_to']):
                       rel = {
                           'sito': site_name,
                           'area': row.get('area', 'Main'),
                           'us': int(row['us']),
                           'rapporti': row.get('relationship_type', 'Copre'),
                           'nazione': '',
                           'us_rapporti': int(row['relationship_to'])
                       }
                       self.us_service.add_relationship(rel)
                       stats['relationships'] += 1

               except Exception as e:
                   logger.error(f"Error processing row {row.get('us')}: {e}")

           logger.info(f"Processing complete: {stats}")
           return stats

       def generate_outputs(self, site_name: str, output_dir: str) -> dict:
           """
           Generate all outputs for site

           Args:
               site_name: Site name
               output_dir: Output directory

           Returns:
               dict: Paths to generated files
           """
           from pathlib import Path

           output_path = Path(output_dir)
           output_path.mkdir(parents=True, exist_ok=True)

           outputs = {}

           # Generate Harris Matrix
           graph = self.matrix_gen.generate_matrix(site_name)

           # Export GraphML
           graphml_file = output_path / f'{site_name}_matrix.graphml'
           self.matrix_gen.export_to_graphml(
               graph=graph,
               output_path=str(graphml_file),
               site_name=site_name
           )
           outputs['graphml'] = str(graphml_file)
           logger.info(f"GraphML exported: {graphml_file}")

           # Export DOT
           dot_file = output_path / f'{site_name}_matrix.dot'
           self.matrix_gen.export_to_dot(
               graph=graph,
               output_path=str(dot_file),
               site_name=site_name
           )
           outputs['dot'] = str(dot_file)
           logger.info(f"DOT exported: {dot_file}")

           return outputs

   # Usage
   pipeline = ArchaeologicalDataPipeline('sqlite:///project.db')

   # Process excavation data
   stats = pipeline.process_excavation_data(
       'Pompeii',
       'excavation_data.xlsx'
   )

   # Generate outputs
   outputs = pipeline.generate_outputs('Pompeii', 'exports/')

   print(f"\nProcessing complete:")
   print(f"  Sites created: {stats['sites']}")
   print(f"  US created: {stats['us']}")
   print(f"  Relationships: {stats['relationships']}")
   print(f"\nOutputs:")
   for name, path in outputs.items():
       print(f"  {name}: {path}")

Pattern 2: Web Application Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   """
   Flask web application with PyArchInit-Mini integration
   """

   from flask import Flask, request, jsonify
   from pyarchinit_mini.database.manager import DatabaseManager
   from pyarchinit_mini.services.site_service import SiteService
   from pyarchinit_mini.services.us_service import USService

   app = Flask(__name__)

   # Initialize database and services
   db = DatabaseManager('sqlite:///webapp.db')
   site_service = SiteService(db)
   us_service = USService(db)

   @app.route('/api/sites', methods=['GET'])
   def get_sites():
       """Get all sites"""
       try:
           sites = site_service.get_all()
           return jsonify({
               'success': True,
               'data': sites,
               'count': len(sites)
           })
       except Exception as e:
           return jsonify({'success': False, 'error': str(e)}), 500

   @app.route('/api/sites', methods=['POST'])
   def create_site():
       """Create new site"""
       try:
           data = request.get_json()
           site = site_service.create(data)
           return jsonify({'success': True, 'data': site}), 201
       except Exception as e:
           return jsonify({'success': False, 'error': str(e)}), 400

   @app.route('/api/sites/<site_name>/us', methods=['GET'])
   def get_site_us(site_name):
       """Get all US for site"""
       try:
           us_list = us_service.search(sito=site_name)
           return jsonify({
               'success': True,
               'site': site_name,
               'data': us_list,
               'count': len(us_list)
           })
       except Exception as e:
           return jsonify({'success': False, 'error': str(e)}), 500

   @app.route('/api/sites/<site_name>/matrix', methods=['GET'])
   def get_harris_matrix(site_name):
       """Generate Harris Matrix for site"""
       try:
           from pyarchinit_mini.harris_matrix.matrix_generator import MatrixGenerator

           matrix_gen = MatrixGenerator('sqlite:///webapp.db')
           graph = matrix_gen.generate_matrix(site_name)

           # Export to file
           output_file = f'temp/{site_name}_matrix.graphml'
           matrix_gen.export_to_graphml(
               graph=graph,
               output_path=output_file,
               site_name=site_name
           )

           return jsonify({
               'success': True,
               'site': site_name,
               'nodes': graph.number_of_nodes(),
               'edges': graph.number_of_edges(),
               'file': output_file
           })
       except Exception as e:
           return jsonify({'success': False, 'error': str(e)}), 500

   if __name__ == '__main__':
       app.run(debug=True, port=5000)

**Usage with curl**:

.. code-block:: bash

   # Get all sites
   curl http://localhost:5000/api/sites

   # Create site
   curl -X POST http://localhost:5000/api/sites \
     -H "Content-Type: application/json" \
     -d '{"sito": "Pompeii", "nazione": "Italy"}'

   # Get US for site
   curl http://localhost:5000/api/sites/Pompeii/us

   # Generate Harris Matrix
   curl http://localhost:5000/api/sites/Pompeii/matrix

Pattern 3: Data Analysis Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   """
   Jupyter notebook / data analysis integration
   """

   import pandas as pd
   import matplotlib.pyplot as plt
   from pyarchinit_mini.database.manager import DatabaseManager
   from pyarchinit_mini.services.us_service import USService
   from pyarchinit_mini.services.inventario_service import InventarioService

   class ArchaeologicalDataAnalysis:
       """
       Archaeological data analysis toolkit
       """

       def __init__(self, db_url: str):
           self.db = DatabaseManager(db_url)
           self.us_service = USService(self.db)
           self.inv_service = InventarioService(self.db)

       def get_us_dataframe(self, site: str) -> pd.DataFrame:
           """
           Get US data as pandas DataFrame

           Args:
               site: Site name

           Returns:
               pd.DataFrame: US data
           """
           us_list = self.us_service.search(sito=site)
           return pd.DataFrame(us_list)

       def get_inventario_dataframe(self, site: str) -> pd.DataFrame:
           """
           Get inventory data as pandas DataFrame

           Args:
               site: Site name

           Returns:
               pd.DataFrame: Inventory data
           """
           inv_list = self.inv_service.search(sito=site)
           return pd.DataFrame(inv_list)

       def analyze_chronology(self, site: str) -> dict:
           """
           Analyze chronological distribution

           Args:
               site: Site name

           Returns:
               dict: Analysis results
           """
           df = self.get_us_dataframe(site)

           # Count by period
           period_counts = df['periodo_iniziale'].value_counts()

           # Count by type
           type_counts = df['unita_tipo'].value_counts()

           return {
               'total_us': len(df),
               'periods': period_counts.to_dict(),
               'types': type_counts.to_dict()
           }

       def plot_chronology(self, site: str, output_file: str = None):
           """
           Plot chronological distribution

           Args:
               site: Site name
               output_file: Optional output file path
           """
           df = self.get_us_dataframe(site)

           # Create figure
           fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

           # Plot periods
           period_counts = df['periodo_iniziale'].value_counts()
           period_counts.plot(kind='bar', ax=ax1)
           ax1.set_title(f'{site} - Distribution by Period')
           ax1.set_xlabel('Period')
           ax1.set_ylabel('Count')

           # Plot types
           type_counts = df['unita_tipo'].value_counts()
           type_counts.plot(kind='pie', ax=ax2, autopct='%1.1f%%')
           ax2.set_title(f'{site} - Distribution by Unit Type')

           plt.tight_layout()

           if output_file:
               plt.savefig(output_file, dpi=300, bbox_inches='tight')

           plt.show()

       def export_to_excel(self, site: str, output_file: str):
           """
           Export all data to Excel with multiple sheets

           Args:
               site: Site name
               output_file: Output Excel file path
           """
           with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
               # US data
               us_df = self.get_us_dataframe(site)
               us_df.to_excel(writer, sheet_name='US', index=False)

               # Inventory data
               inv_df = self.get_inventario_dataframe(site)
               inv_df.to_excel(writer, sheet_name='Inventory', index=False)

               # Relationships
               rels = self.us_service.get_relationships(sito=site)
               rel_df = pd.DataFrame(rels)
               rel_df.to_excel(writer, sheet_name='Relationships', index=False)

   # Usage in Jupyter notebook
   analysis = ArchaeologicalDataAnalysis('sqlite:///project.db')

   # Get data
   df = analysis.get_us_dataframe('Pompeii')
   print(df.head())

   # Analyze
   stats = analysis.analyze_chronology('Pompeii')
   print(stats)

   # Plot
   analysis.plot_chronology('Pompeii', 'pompeii_analysis.png')

   # Export
   analysis.export_to_excel('Pompeii', 'pompeii_export.xlsx')

Complete Example: Multi-Site Analysis
--------------------------------------

.. code-block:: python

   """
   Complete example: Multi-site archaeological data analysis system
   """

   from pyarchinit_mini.database.manager import DatabaseManager
   from pyarchinit_mini.services.site_service import SiteService
   from pyarchinit_mini.services.us_service import USService
   from pyarchinit_mini.services.inventario_service import InventarioService
   from pyarchinit_mini.harris_matrix.matrix_generator import MatrixGenerator
   import logging
   from pathlib import Path
   import json

   logging.basicConfig(
       level=logging.INFO,
       format='%(asctime)s - %(levelname)s - %(message)s'
   )
   logger = logging.getLogger(__name__)

   class MultiSiteArchaeologicalSystem:
       """
       Complete multi-site archaeological data management system
       """

       def __init__(self, db_path: str, output_dir: str):
           self.db_url = f'sqlite:///{db_path}'
           self.db = DatabaseManager(self.db_url)
           self.site_service = SiteService(self.db)
           self.us_service = USService(self.db)
           self.inv_service = InventarioService(self.db)
           self.matrix_gen = MatrixGenerator(self.db_url)
           self.output_dir = Path(output_dir)
           self.output_dir.mkdir(parents=True, exist_ok=True)

       def create_project(self, project_data: dict) -> dict:
           """
           Create complete archaeological project

           Args:
               project_data: Dictionary with project data

           Returns:
               dict: Creation statistics
           """
           logger.info("Creating archaeological project")

           stats = {
               'sites': 0,
               'us': 0,
               'relationships': 0,
               'inventario': 0
           }

           # Create sites
           for site_data in project_data.get('sites', []):
               self.site_service.create(site_data)
               stats['sites'] += 1
               logger.info(f"Created site: {site_data['sito']}")

           # Create US
           for us_data in project_data.get('us', []):
               self.us_service.create(us_data)
               stats['us'] += 1

           # Create relationships
           for rel in project_data.get('relationships', []):
               self.us_service.add_relationship(rel)
               stats['relationships'] += 1

           # Create inventory
           for inv in project_data.get('inventario', []):
               self.inv_service.create(inv)
               stats['inventario'] += 1

           logger.info(f"Project creation complete: {stats}")
           return stats

       def analyze_all_sites(self) -> dict:
           """
           Analyze all sites in database

           Returns:
               dict: Analysis results for all sites
           """
           sites = self.site_service.get_all()
           results = {}

           for site in sites:
               site_name = site['sito']
               logger.info(f"Analyzing site: {site_name}")

               # Get statistics
               us_list = self.us_service.search(sito=site_name)
               inv_list = self.inv_service.search(sito=site_name)
               rels = self.us_service.get_relationships(sito=site_name)

               results[site_name] = {
                   'us_count': len(us_list),
                   'inventario_count': len(inv_list),
                   'relationships_count': len(rels),
                   'us_by_type': {},
                   'periods': set()
               }

               # Count by type
               for us in us_list:
                   us_type = us.get('unita_tipo', 'Unknown')
                   results[site_name]['us_by_type'][us_type] = \
                       results[site_name]['us_by_type'].get(us_type, 0) + 1

                   # Collect periods
                   if us.get('periodo_iniziale'):
                       results[site_name]['periods'].add(us['periodo_iniziale'])

               # Convert set to list for JSON serialization
               results[site_name]['periods'] = list(results[site_name]['periods'])

           return results

       def export_all_matrices(self) -> dict:
           """
           Export Harris Matrices for all sites

           Returns:
               dict: Paths to exported files
           """
           sites = self.site_service.get_all()
           exported = {}

           for site in sites:
               site_name = site['sito']
               logger.info(f"Exporting matrix for: {site_name}")

               try:
                   # Generate matrix
                   graph = self.matrix_gen.generate_matrix(site_name)

                   if graph.number_of_nodes() == 0:
                       logger.warning(f"No nodes found for {site_name}")
                       continue

                   # Export GraphML
                   graphml_file = self.output_dir / f'{site_name}_matrix.graphml'
                   self.matrix_gen.export_to_graphml(
                       graph=graph,
                       output_path=str(graphml_file),
                       site_name=site_name
                   )

                   exported[site_name] = str(graphml_file)
                   logger.info(f"Exported: {graphml_file}")

               except Exception as e:
                   logger.error(f"Export failed for {site_name}: {e}")

           return exported

       def generate_report(self) -> str:
           """
           Generate comprehensive analysis report

           Returns:
               str: Path to report file
           """
           logger.info("Generating comprehensive report")

           # Analyze all sites
           analysis = self.analyze_all_sites()

           # Create report
           report = {
               'total_sites': len(analysis),
               'sites': analysis,
               'summary': {
                   'total_us': sum(s['us_count'] for s in analysis.values()),
                   'total_inventario': sum(s['inventario_count'] for s in analysis.values()),
                   'total_relationships': sum(s['relationships_count'] for s in analysis.values())
               }
           }

           # Save report
           report_file = self.output_dir / 'analysis_report.json'
           with open(report_file, 'w') as f:
               json.dump(report, f, indent=2)

           logger.info(f"Report saved: {report_file}")
           return str(report_file)

   # Example usage
   if __name__ == '__main__':
       # Initialize system
       system = MultiSiteArchaeologicalSystem(
           db_path='multi_site_project.db',
           output_dir='exports/'
       )

       # Create project with sample data
       project_data = {
           'sites': [
               {
                   'sito': 'Pompeii',
                   'nazione': 'Italy',
                   'regione': 'Campania'
               },
               {
                   'sito': 'Herculaneum',
                   'nazione': 'Italy',
                   'regione': 'Campania'
               }
           ],
           'us': [
               {
                   'sito': 'Pompeii',
                   'area': 'Area A',
                   'us': 1001,
                   'unita_tipo': 'US',
                   'd_stratigrafica': 'Fill layer',
                   'periodo_iniziale': 'Roman'
               },
               # ... more US
           ],
           'relationships': [
               {
                   'sito': 'Pompeii',
                   'area': 'Area A',
                   'us': 1001,
                   'rapporti': 'Copre',
                   'nazione': '',
                   'us_rapporti': 1002
               },
               # ... more relationships
           ],
           'inventario': [
               {
                   'sito': 'Pompeii',
                   'us': 1001,
                   'numero_inventario': 'POM-001',
                   'tipo_reperto': 'Ceramic'
               },
               # ... more inventory
           ]
       }

       # Create project
       stats = system.create_project(project_data)
       print(f"\nProject created: {stats}")

       # Analyze all sites
       analysis = system.analyze_all_sites()
       print(f"\nAnalysis results:")
       for site, data in analysis.items():
           print(f"\n{site}:")
           print(f"  US: {data['us_count']}")
           print(f"  Inventory: {data['inventario_count']}")
           print(f"  Relationships: {data['relationships_count']}")
           print(f"  Periods: {', '.join(data['periods'])}")

       # Export matrices
       exported = system.export_all_matrices()
       print(f"\nExported matrices:")
       for site, path in exported.items():
           print(f"  {site}: {path}")

       # Generate report
       report_path = system.generate_report()
       print(f"\nReport generated: {report_path}")

**Expected Output**:

.. code-block:: text

   2025-10-28 14:30:25 - INFO - Creating archaeological project
   2025-10-28 14:30:25 - INFO - Created site: Pompeii
   2025-10-28 14:30:25 - INFO - Created site: Herculaneum
   2025-10-28 14:30:26 - INFO - Project creation complete: {'sites': 2, 'us': 125, 'relationships': 342, 'inventario': 234}

   Project created: {'sites': 2, 'us': 125, 'relationships': 342, 'inventario': 234}

   2025-10-28 14:30:26 - INFO - Analyzing site: Pompeii
   2025-10-28 14:30:27 - INFO - Analyzing site: Herculaneum

   Analysis results:

   Pompeii:
     US: 75
     Inventory: 156
     Relationships: 234
     Periods: Roman, Medieval

   Herculaneum:
     US: 50
     Inventory: 78
     Relationships: 108
     Periods: Roman

   2025-10-28 14:30:27 - INFO - Exporting matrix for: Pompeii
   2025-10-28 14:30:28 - INFO - Exported: exports/Pompeii_matrix.graphml
   2025-10-28 14:30:28 - INFO - Exporting matrix for: Herculaneum
   2025-10-28 14:30:29 - INFO - Exported: exports/Herculaneum_matrix.graphml

   Exported matrices:
     Pompeii: exports/Pompeii_matrix.graphml
     Herculaneum: exports/Herculaneum_matrix.graphml

   2025-10-28 14:30:29 - INFO - Generating comprehensive report
   2025-10-28 14:30:29 - INFO - Report saved: exports/analysis_report.json

   Report generated: exports/analysis_report.json

See Also
--------

- :doc:`../features/pyarchinit-import-export` - Import/Export system guide
- :doc:`../features/extended-matrix-framework` - Extended Matrix framework
- :doc:`../features/graphml-export-technical` - GraphML export technical details
- :doc:`../examples/python_api` - Additional Python examples

**The Python API is complete, documented, and production-ready!** 🚀
