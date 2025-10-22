==================
REST API Usage
==================

This guide shows how to interact with PyArchInit-Mini via HTTP REST API endpoints.

.. contents:: Table of Contents
   :local:
   :depth: 2

API Base URL
============

Default: ``http://localhost:5001/api``

For production, replace with your server URL.

Authentication
==============

Login
-----

.. code-block:: bash

    curl -X POST http://localhost:5001/api/auth/login \
      -H "Content-Type: application/json" \
      -d '{
        "username": "admin",
        "password": "admin"
      }'

Response:

.. code-block:: json

    {
      "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
      "user": {
        "username": "admin",
        "role": "admin"
      }
    }

Use the token in subsequent requests:

.. code-block:: bash

    curl -H "Authorization: Bearer YOUR_TOKEN" \
         http://localhost:5001/api/sites


Sites API
=========

List All Sites
--------------

.. code-block:: bash

    curl http://localhost:5001/api/sites?page=1&size=10

Create Site
-----------

.. code-block:: bash

    curl -X POST http://localhost:5001/api/sites \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer YOUR_TOKEN" \
      -d '{
        "sito": "Pompei",
        "nazione": "Italia",
        "regione": "Campania",
        "comune": "Pompei",
        "descrizione": "Città romana"
      }'

Get Single Site
---------------

.. code-block:: bash

    curl http://localhost:5001/api/sites/1

Update Site
-----------

.. code-block:: bash

    curl -X PUT http://localhost:5001/api/sites/1 \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer YOUR_TOKEN" \
      -d '{
        "descrizione": "Updated description"
      }'

Delete Site
-----------

.. code-block:: bash

    curl -X DELETE http://localhost:5001/api/sites/1 \
      -H "Authorization: Bearer YOUR_TOKEN"


Stratigraphic Units (US) API
=============================

List US for Site
----------------

.. code-block:: bash

    curl "http://localhost:5001/api/us?site=Pompei&page=1&size=50"

Create US
---------

.. code-block:: bash

    curl -X POST http://localhost:5001/api/us \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer YOUR_TOKEN" \
      -d '{
        "sito": "Pompei",
        "area": "1",
        "us": 1001,
        "unita_tipo": "US",
        "d_stratigrafica": "Strato di crollo",
        "rapporti": "COVERS:1002,FILLS:1003"
      }'

Get Single US
-------------

.. code-block:: bash

    curl http://localhost:5001/api/us/123

Update US
---------

.. code-block:: bash

    curl -X PUT http://localhost:5001/api/us/123 \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer YOUR_TOKEN" \
      -d '{
        "colore": "Marrone rossastro",
        "consistenza": "Compatta"
      }'


Inventory API
=============

List Inventory
--------------

.. code-block:: bash

    curl "http://localhost:5001/api/inventario?site=Pompei&page=1&size=20"

Create Inventory Item
---------------------

.. code-block:: bash

    curl -X POST http://localhost:5001/api/inventario \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer YOUR_TOKEN" \
      -d '{
        "sito": "Pompei",
        "numero_inventario": "POM-2024-001",
        "tipo_reperto": "Ceramica",
        "definizione": "Anfora vinaria",
        "us": 1001
      }'


Harris Matrix API
=================

Generate Matrix
---------------

.. code-block:: bash

    curl "http://localhost:5001/api/harris-matrix/generate?site=Pompei"

Response:

.. code-block:: json

    {
      "nodes": [
        {"id": "US_1001", "us_number": 1001, "description": "..."},
        {"id": "US_1002", "us_number": 1002, "description": "..."}
      ],
      "edges": [
        {"source": "US_1001", "target": "US_1002", "relation": "COVERS"}
      ],
      "levels": 5
    }

Export as GraphML
-----------------

.. code-block:: bash

    curl "http://localhost:5001/api/graphml/export?site=Pompei" \
      -H "Authorization: Bearer YOUR_TOKEN" \
      -o pompei_matrix.graphml


s3Dgraphy API
=============

Upload 3D Model
---------------

.. code-block:: bash

    curl -X POST http://localhost:5001/api/s3d/upload \
      -H "Authorization: Bearer YOUR_TOKEN" \
      -F "file=@us_1001.obj" \
      -F "site_name=Pompei" \
      -F "us_id=1001"

List 3D Models
--------------

.. code-block:: bash

    curl "http://localhost:5001/api/s3d/models?site=Pompei"

Get Model URL
-------------

.. code-block:: bash

    curl "http://localhost:5001/api/s3d/model/Pompei/1001"


Python requests Examples
=========================

Using the ``requests`` library:

.. code-block:: python

    import requests

    BASE_URL = "http://localhost:5001/api"

    # Login
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "admin",
        "password": "admin"
    })
    token = response.json()["token"]

    headers = {"Authorization": f"Bearer {token}"}

    # Create site
    site_data = {
        "sito": "Pompei",
        "nazione": "Italia",
        "regione": "Campania"
    }
    response = requests.post(f"{BASE_URL}/sites", json=site_data, headers=headers)
    site = response.json()

    # Get all US
    response = requests.get(f"{BASE_URL}/us", params={"site": "Pompei"})
    us_list = response.json()

    # Upload 3D model
    files = {"file": open("model.obj", "rb")}
    data = {"site_name": "Pompei", "us_id": "1001"}
    response = requests.post(f"{BASE_URL}/s3d/upload",
                            files=files, data=data, headers=headers)


JavaScript/TypeScript Examples
===============================

Using fetch API:

.. code-block:: javascript

    const BASE_URL = 'http://localhost:5001/api';

    // Login
    async function login(username, password) {
        const response = await fetch(`${BASE_URL}/auth/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username, password})
        });
        const data = await response.json();
        return data.token;
    }

    // Get sites
    async function getSites(token) {
        const response = await fetch(`${BASE_URL}/sites`, {
            headers: {'Authorization': `Bearer ${token}`}
        });
        return await response.json();
    }

    // Create US
    async function createUS(token, usData) {
        const response = await fetch(`${BASE_URL}/us`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(usData)
        });
        return await response.json();
    }


Error Handling
==============

API returns standard HTTP status codes:

.. code-block:: python

    import requests

    try:
        response = requests.get(f"{BASE_URL}/sites/999")
        response.raise_for_status()
        site = response.json()
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            print("Site not found")
        elif e.response.status_code == 401:
            print("Unauthorized - check token")
        else:
            print(f"Error: {e}")
