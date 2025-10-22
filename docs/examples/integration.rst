============================
Integration Patterns
============================

Advanced patterns for integrating PyArchInit-Mini with other systems and frameworks.

.. contents:: Table of Contents
   :local:
   :depth: 2

Django Integration
==================

Using PyArchInit as a Django App
---------------------------------

Add PyArchInit data to your Django project:

.. code-block:: python

    # myproject/settings.py
    PYARCHINIT_DATABASE = {
        'default': {
            'URL': 'sqlite:///./archaeology.db'
        }
    }

    # myproject/archaeology/models.py
    from django.db import models
    from pyarchinit_mini.database.connection import DatabaseConnection
    from pyarchinit_mini.database.manager import DatabaseManager
    from pyarchinit_mini.services.site_service import SiteService
    from pyarchinit_mini.services.us_service import USService
    from django.conf import settings

    class PyArchInitMixin:
        """Mixin to add PyArchInit functionality"""

        @classmethod
        def get_pyarchinit_connection(cls):
            db_url = settings.PYARCHINIT_DATABASE['default']['URL']
            db_conn = DatabaseConnection.from_url(db_url)
            return DatabaseManager(db_conn)

    class ArchaeologicalProject(models.Model, PyArchInitMixin):
        name = models.CharField(max_length=200)
        site_name = models.CharField(max_length=200)
        created_at = models.DateTimeField(auto_now_add=True)

        def get_stratigraphic_units(self):
            """Fetch US from PyArchInit"""
            db_manager = self.get_pyarchinit_connection()
            us_service = USService(db_manager)
            return us_service.get_us_by_site(self.site_name)

        def generate_harris_matrix(self):
            """Generate Harris Matrix"""
            from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator
            db_manager = self.get_pyarchinit_connection()
            us_service = USService(db_manager)
            matrix_gen = HarrisMatrixGenerator(us_service)
            return matrix_gen.generate_matrix(self.site_name)


Django Views
------------

.. code-block:: python

    # myproject/archaeology/views.py
    from django.http import JsonResponse
    from django.views import View
    from .models import ArchaeologicalProject

    class ProjectUSListView(View):
        def get(self, request, project_id):
            project = ArchaeologicalProject.objects.get(id=project_id)
            us_list = project.get_stratigraphic_units()

            return JsonResponse({
                'project': project.name,
                'us_count': len(us_list),
                'us': [{
                    'us': us.us,
                    'description': us.d_stratigrafica,
                    'area': us.area
                } for us in us_list]
            })

    class HarrisMatrixView(View):
        def get(self, request, project_id):
            project = ArchaeologicalProject.objects.get(id=project_id)
            graph = project.generate_harris_matrix()

            return JsonResponse({
                'nodes': graph['nodes'],
                'edges': graph['edges'],
                'levels': graph['levels']
            })


Django Management Command
-------------------------

.. code-block:: python

    # myproject/archaeology/management/commands/sync_pyarchinit.py
    from django.core.management.base import BaseCommand
    from archaeology.models import ArchaeologicalProject
    from pyarchinit_mini.services.site_service import SiteService

    class Command(BaseCommand):
        help = 'Sync PyArchInit sites with Django projects'

        def handle(self, *args, **options):
            db_manager = ArchaeologicalProject.get_pyarchinit_connection()
            site_service = SiteService(db_manager)

            sites = site_service.get_all_sites(size=1000)

            for site in sites:
                project, created = ArchaeologicalProject.objects.get_or_create(
                    site_name=site.sito,
                    defaults={'name': site.sito}
                )
                if created:
                    self.stdout.write(f"Created project: {site.sito}")


Flask Integration
=================

Blueprint Integration
---------------------

.. code-block:: python

    # app/archaeology.py
    from flask import Blueprint, jsonify, request
    from pyarchinit_mini.database.connection import DatabaseConnection
    from pyarchinit_mini.database.manager import DatabaseManager
    from pyarchinit_mini.services.site_service import SiteService
    from pyarchinit_mini.services.us_service import USService

    archaeology_bp = Blueprint('archaeology', __name__, url_prefix='/archaeology')

    def get_db_manager():
        """Get PyArchInit database manager"""
        db_url = current_app.config.get('PYARCHINIT_DB_URL', 'sqlite:///./archaeology.db')
        db_conn = DatabaseConnection.from_url(db_url)
        return DatabaseManager(db_conn)

    @archaeology_bp.route('/sites')
    def list_sites():
        db_manager = get_db_manager()
        site_service = SiteService(db_manager)
        sites = site_service.get_all_sites()
        return jsonify([{
            'id': s.id_sito,
            'name': s.sito,
            'country': s.nazione
        } for s in sites])

    @archaeology_bp.route('/sites/<site_name>/us')
    def site_us(site_name):
        db_manager = get_db_manager()
        us_service = USService(db_manager)
        us_list = us_service.get_us_by_site(site_name)
        return jsonify([{
            'us': u.us,
            'description': u.d_stratigrafica
        } for u in us_list])

    # In main app.py
    from app.archaeology import archaeology_bp
    app.register_blueprint(archaeology_bp)


Flask Background Tasks
----------------------

Using Celery for async processing:

.. code-block:: python

    # tasks.py
    from celery import Celery
    from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator
    from pyarchinit_mini.harris_matrix.pyarchinit_visualizer import PyArchInitMatrixVisualizer

    celery = Celery('tasks', broker='redis://localhost:6379/0')

    @celery.task
    def generate_matrix_async(site_name):
        """Generate Harris Matrix in background"""
        db_manager = get_db_manager()
        us_service = USService(db_manager)

        matrix_gen = HarrisMatrixGenerator(us_service)
        graph = matrix_gen.generate_matrix(site_name)

        visualizer = PyArchInitMatrixVisualizer()
        output_path = f'static/matrices/{site_name}_matrix.png'
        visualizer.visualize(graph, output_path)

        return output_path

    # In Flask route
    @app.route('/generate-matrix/<site_name>')
    def start_matrix_generation(site_name):
        task = generate_matrix_async.delay(site_name)
        return jsonify({'task_id': task.id})


FastAPI Integration
===================

Modern async API
----------------

.. code-block:: python

    # main.py
    from fastapi import FastAPI, HTTPException, Depends
    from pydantic import BaseModel
    from typing import List, Optional
    from pyarchinit_mini.database.connection import DatabaseConnection
    from pyarchinit_mini.database.manager import DatabaseManager
    from pyarchinit_mini.services.site_service import SiteService

    app = FastAPI(title="Archaeological Data API")

    # Database dependency
    def get_db():
        db_conn = DatabaseConnection.from_url("sqlite:///./archaeology.db")
        db_manager = DatabaseManager(db_conn)
        try:
            yield db_manager
        finally:
            pass  # Cleanup if needed

    # Pydantic models
    class SiteCreate(BaseModel):
        sito: str
        nazione: Optional[str] = None
        regione: Optional[str] = None
        comune: Optional[str] = None
        descrizione: Optional[str] = None

    class SiteResponse(BaseModel):
        id_sito: int
        sito: str
        nazione: Optional[str]
        regione: Optional[str]

        class Config:
            from_attributes = True

    # Endpoints
    @app.get("/sites", response_model=List[SiteResponse])
    async def list_sites(db: DatabaseManager = Depends(get_db)):
        site_service = SiteService(db)
        sites = site_service.get_all_sites(size=100)
        return sites

    @app.post("/sites", response_model=SiteResponse)
    async def create_site(site: SiteCreate, db: DatabaseManager = Depends(get_db)):
        site_service = SiteService(db)
        new_site = site_service.create_site(site.dict())
        return new_site

    @app.get("/sites/{site_id}", response_model=SiteResponse)
    async def get_site(site_id: int, db: DatabaseManager = Depends(get_db)):
        site_service = SiteService(db)
        site = site_service.get_site_dto_by_id(site_id)
        if not site:
            raise HTTPException(status_code=404, detail="Site not found")
        return site


React/Vue.js Integration
=========================

Frontend Data Fetching
----------------------

React hooks example:

.. code-block:: javascript

    // hooks/usePyArchInit.js
    import { useState, useEffect } from 'react';

    export function useSites() {
        const [sites, setSites] = useState([]);
        const [loading, setLoading] = useState(true);

        useEffect(() => {
            fetch('http://localhost:5001/api/sites')
                .then(res => res.json())
                .then(data => {
                    setSites(data);
                    setLoading(false);
                });
        }, []);

        return { sites, loading };
    }

    export function useHarrisMatrix(siteName) {
        const [matrix, setMatrix] = useState(null);

        useEffect(() => {
            if (!siteName) return;

            fetch(`http://localhost:5001/api/harris-matrix/generate?site=${siteName}`)
                .then(res => res.json())
                .then(data => setMatrix(data));
        }, [siteName]);

        return matrix;
    }

    // Component usage
    function SiteList() {
        const { sites, loading } = useSites();

        if (loading) return <div>Loading...</div>;

        return (
            <ul>
                {sites.map(site => (
                    <li key={site.id_sito}>{site.sito}</li>
                ))}
            </ul>
        );
    }


Vue.js Composable
-----------------

.. code-block:: javascript

    // composables/usePyArchInit.js
    import { ref, watchEffect } from 'vue';

    export function useSites() {
        const sites = ref([]);
        const loading = ref(true);

        watchEffect(async () => {
            const response = await fetch('http://localhost:5001/api/sites');
            sites.value = await response.json();
            loading.value = false;
        });

        return { sites, loading };
    }


Jupyter Notebook Integration
=============================

Data Analysis
-------------

.. code-block:: python

    # In Jupyter Notebook
    %matplotlib inline
    import pandas as pd
    import matplotlib.pyplot as plt
    from pyarchinit_mini.database.connection import DatabaseConnection
    from pyarchinit_mini.database.manager import DatabaseManager
    from pyarchinit_mini.services.us_service import USService
    from pyarchinit_mini.services.inventario_service import InventarioService

    # Connect to database
    db_conn = DatabaseConnection.from_url("sqlite:///./pompei.db")
    db_manager = DatabaseManager(db_conn)

    # Load data
    us_service = USService(db_manager)
    us_list = us_service.get_us_by_site('Pompei')

    # Create DataFrame
    df = pd.DataFrame([{
        'US': u.us,
        'Type': u.unita_tipo,
        'Area': u.area,
        'Year': u.anno_scavo
    } for u in us_list])

    # Analyze
    print(f"Total US: {len(df)}")
    print(f"\nUS by type:\n{df['Type'].value_counts()}")
    print(f"\nUS by year:\n{df['Year'].value_counts()}")

    # Visualize
    df['Type'].value_counts().plot(kind='bar', title='US Distribution by Type')
    plt.xlabel('US Type')
    plt.ylabel('Count')
    plt.show()


3D Visualization in Notebook
-----------------------------

.. code-block:: python

    from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator
    from pyarchinit_mini.harris_matrix.pyarchinit_visualizer import PyArchInitMatrixVisualizer
    from IPython.display import Image, display

    # Generate matrix
    matrix_gen = HarrisMatrixGenerator(us_service)
    graph = matrix_gen.generate_matrix('Pompei')

    # Visualize
    visualizer = PyArchInitMatrixVisualizer()
    visualizer.visualize(graph, 'harris_matrix.png', format='png')

    # Display in notebook
    display(Image('harris_matrix.png'))


GIS Integration
===============

QGIS Python Plugin
------------------

.. code-block:: python

    # qgis_plugin/pyarchinit_loader.py
    from qgis.core import QgsVectorLayer, QgsProject
    from pyarchinit_mini.services.site_service import SiteService

    def load_archaeological_sites():
        """Load PyArchInit sites as QGIS layer"""
        db_manager = get_db_manager()
        site_service = SiteService(db_manager)
        sites = site_service.get_all_sites()

        # Create GeoJSON
        features = []
        for site in sites:
            if site.x_coord and site.y_coord:
                features.append({
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Point',
                        'coordinates': [site.x_coord, site.y_coord]
                    },
                    'properties': {
                        'name': site.sito,
                        'country': site.nazione
                    }
                })

        # Add to QGIS
        layer = QgsVectorLayer('Point?crs=EPSG:4326', 'Archaeological Sites', 'memory')
        # ... add features to layer
        QgsProject.instance().addMapLayer(layer)


ArcGIS Integration
------------------

.. code-block:: python

    import arcpy
    from pyarchinit_mini.services.site_service import SiteService

    def create_site_feature_class():
        """Create ArcGIS feature class from PyArchInit sites"""
        # Create feature class
        out_path = "C:/GIS/archaeology.gdb"
        out_name = "archaeological_sites"

        arcpy.CreateFeatureclass_management(
            out_path, out_name, "POINT",
            spatial_reference=arcpy.SpatialReference(4326)
        )

        # Add fields
        arcpy.AddField_management(out_name, "site_name", "TEXT")
        arcpy.AddField_management(out_name, "country", "TEXT")

        # Insert PyArchInit data
        db_manager = get_db_manager()
        site_service = SiteService(db_manager)
        sites = site_service.get_all_sites()

        with arcpy.da.InsertCursor(out_name, ["SHAPE@XY", "site_name", "country"]) as cursor:
            for site in sites:
                if site.x_coord and site.y_coord:
                    cursor.insertRow([(site.x_coord, site.y_coord), site.sito, site.nazione])


Cloud Deployment
================

AWS Lambda
----------

Serverless function:

.. code-block:: python

    # lambda_function.py
    import json
    from pyarchinit_mini.database.connection import DatabaseConnection
    from pyarchinit_mini.services.site_service import SiteService

    def lambda_handler(event, context):
        # Connect to RDS PostgreSQL
        db_url = "postgresql://user:pass@rds-endpoint/archaeology"
        db_conn = DatabaseConnection.from_url(db_url)
        db_manager = DatabaseManager(db_conn)

        site_service = SiteService(db_manager)
        sites = site_service.get_all_sites(size=100)

        return {
            'statusCode': 200,
            'body': json.dumps([{
                'name': s.sito,
                'country': s.nazione
            } for s in sites])
        }


Google Cloud Functions
----------------------

.. code-block:: python

    # main.py
    import functions_framework
    from pyarchinit_mini.services.site_service import SiteService

    @functions_framework.http
    def get_sites(request):
        db_manager = get_db_manager()  # Cloud SQL connection
        site_service = SiteService(db_manager)
        sites = site_service.get_all_sites()

        return {
            'sites': [{'name': s.sito} for s in sites]
        }


Microservices Architecture
==========================

Service Composition
-------------------

.. code-block:: python

    # services/archaeology_service.py
    from fastapi import FastAPI
    from pyarchinit_mini.services.site_service import SiteService

    app = FastAPI()

    @app.get("/health")
    def health_check():
        return {"status": "healthy"}

    @app.get("/sites")
    def list_sites():
        # Service-specific database
        db_manager = get_db_manager()
        site_service = SiteService(db_manager)
        return site_service.get_all_sites()


Message Queue Integration
--------------------------

Using RabbitMQ:

.. code-block:: python

    import pika
    import json
    from pyarchinit_mini.services.us_service import USService

    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue='us_created')

    def on_us_created(ch, method, properties, body):
        """Handle US creation event"""
        us_data = json.loads(body)
        print(f"New US created: {us_data['us']}")

        # Process (e.g., generate matrix, send notification)
        db_manager = get_db_manager()
        us_service = USService(db_manager)
        # ... process

    channel.basic_consume(queue='us_created', on_message_callback=on_us_created, auto_ack=True)
    channel.start_consuming()


Best Practices
==============

Connection Pooling
------------------

.. code-block:: python

    from functools import lru_cache

    @lru_cache(maxsize=1)
    def get_db_connection():
        """Cached database connection"""
        return DatabaseConnection.from_url("postgresql://...")

    def get_db_manager():
        """Reuse connection"""
        return DatabaseManager(get_db_connection())


Error Handling
--------------

.. code-block:: python

    from pyarchinit_mini.exceptions import PyArchInitException

    try:
        site = site_service.create_site(data)
    except PyArchInitException as e:
        logger.error(f"PyArchInit error: {e}")
        # Handle gracefully
    except Exception as e:
        logger.exception("Unexpected error")
        raise


Logging
-------

.. code-block:: python

    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('pyarchinit_integration')

    logger.info("Fetching sites from PyArchInit")
    sites = site_service.get_all_sites()
    logger.info(f"Retrieved {len(sites)} sites")
