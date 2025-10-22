REST API Documentation
======================

PyArchInit-Mini provides a comprehensive REST API built with FastAPI that allows programmatic access to all archaeological data management features. The API follows RESTful principles and includes automatic documentation via Swagger/OpenAPI.

.. toctree::
   :maxdepth: 2
   :caption: API Contents:

   quickstart
   authentication
   endpoints/sites
   endpoints/us
   endpoints/inventory
   endpoints/harris_matrix
   endpoints/graphml
   endpoints/analytics
   endpoints/export_import
   schemas
   examples

Quick Start
-----------

Starting the API Server
~~~~~~~~~~~~~~~~~~~~~~~

To start the REST API server:

.. code-block:: bash

   pyarchinit-mini-api
   # API runs on http://localhost:8000
   # Documentation at http://localhost:8000/docs

Or programmatically:

.. code-block:: python

   from pyarchinit_mini.api import run_server
   run_server()

Base URL
~~~~~~~~

The default base URL for all API endpoints is:

.. code-block::

   http://localhost:8000/api

Authentication
~~~~~~~~~~~~~~

Most endpoints require authentication. First obtain a JWT token:

.. code-block:: bash

   curl -X POST http://localhost:8000/api/auth/login \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=admin"

Then include the token in subsequent requests:

.. code-block:: bash

   curl -H "Authorization: Bearer <your-token>" \
     http://localhost:8000/api/sites

Response Format
~~~~~~~~~~~~~~~

All API responses follow a consistent JSON format:

Success Response:

.. code-block:: json

   {
     "status": "success",
     "data": {
       // Response data
     }
   }

Error Response:

.. code-block:: json

   {
     "status": "error",
     "message": "Error description",
     "detail": {
       // Additional error details
     }
   }

Common HTTP Status Codes
~~~~~~~~~~~~~~~~~~~~~~~~

- **200 OK**: Successful GET, PUT
- **201 Created**: Successful POST
- **204 No Content**: Successful DELETE
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Missing or invalid authentication
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource not found
- **422 Unprocessable Entity**: Validation error
- **500 Internal Server Error**: Server error

Available Endpoints
-------------------

Sites
~~~~~

- ``GET /api/sites`` - List all sites with pagination
- ``GET /api/sites/{id}`` - Get site by ID
- ``POST /api/sites`` - Create new site
- ``PUT /api/sites/{id}`` - Update site
- ``DELETE /api/sites/{id}`` - Delete site

Stratigraphic Units (US)
~~~~~~~~~~~~~~~~~~~~~~~~

- ``GET /api/us`` - List all US with filters
- ``GET /api/us/{id}`` - Get US by ID
- ``GET /api/us/site/{site_name}`` - Get US by site
- ``POST /api/us`` - Create new US
- ``PUT /api/us/{id}`` - Update US
- ``DELETE /api/us/{id}`` - Delete US

Inventory
~~~~~~~~~

- ``GET /api/inventario`` - List inventory items
- ``GET /api/inventario/{id}`` - Get inventory item
- ``POST /api/inventario`` - Create inventory item
- ``PUT /api/inventario/{id}`` - Update inventory item
- ``DELETE /api/inventario/{id}`` - Delete inventory item

Harris Matrix
~~~~~~~~~~~~~

- ``GET /api/harris-matrix/{site_name}`` - Generate matrix
- ``POST /api/harris-matrix/validate`` - Validate relationships
- ``GET /api/harris-matrix/pdf/{site_name}`` - Export as PDF

GraphML Export
~~~~~~~~~~~~~~

- ``POST /api/graphml/convert`` - Convert DOT to GraphML
- ``POST /api/graphml/convert-content`` - Convert DOT content
- ``GET /api/graphml/template`` - Get yEd template
- ``GET /api/graphml/health`` - Health check

Analytics
~~~~~~~~~

- ``GET /api/analytics/overview`` - Get overview statistics
- ``GET /api/analytics/sites/by-region`` - Sites by region
- ``GET /api/analytics/us/by-period`` - US by period
- ``GET /api/analytics/inventory/by-type`` - Inventory by type

Rate Limiting
-------------

The API implements rate limiting to prevent abuse:

- **Default limit**: 100 requests per minute per IP
- **Authentication endpoints**: 5 requests per minute
- **Export endpoints**: 10 requests per hour

Headers returned:

.. code-block::

   X-RateLimit-Limit: 100
   X-RateLimit-Remaining: 99
   X-RateLimit-Reset: 1234567890

Pagination
----------

List endpoints support pagination via query parameters:

.. code-block::

   GET /api/sites?skip=0&limit=20&sort_by=site_name&sort_order=asc

Parameters:

- ``skip``: Number of records to skip (default: 0)
- ``limit``: Maximum records to return (default: 20, max: 100)
- ``sort_by``: Field to sort by
- ``sort_order``: Sort order (asc/desc)

Response includes pagination metadata:

.. code-block:: json

   {
     "data": [...],
     "pagination": {
       "total": 150,
       "skip": 0,
       "limit": 20,
       "pages": 8,
       "current_page": 1
     }
   }

Filtering
---------

Most list endpoints support filtering:

.. code-block::

   GET /api/us?site_name=Pompei&area=A&period=Romano

Common filter parameters:

- String fields: Partial match (case-insensitive)
- Numeric fields: Exact match or range
- Date fields: Before/after/between
- Boolean fields: true/false

Error Handling
--------------

The API provides detailed error messages:

.. code-block:: json

   {
     "status": "error",
     "message": "Validation error",
     "detail": {
       "errors": [
         {
           "field": "site_name",
           "message": "Site name is required",
           "type": "missing"
         }
       ]
     }
   }

CORS Configuration
------------------

CORS is enabled for common origins:

- ``http://localhost:3000`` (React development)
- ``http://localhost:5001`` (Flask web interface)
- ``http://localhost:8080`` (Vue development)

To add custom origins, set environment variable:

.. code-block:: bash

   export CORS_ORIGINS="http://myapp.com,https://myapp.com"

API Versioning
--------------

The API uses URL versioning. Current version: v1

Future versions will be available at:

.. code-block::

   http://localhost:8000/api/v2/sites

The v1 API will be maintained for backward compatibility.

OpenAPI Documentation
---------------------

Interactive API documentation is available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

The documentation includes:

- All endpoints with parameters
- Request/response schemas
- Authentication requirements
- Example requests and responses
- Try-it-out functionality