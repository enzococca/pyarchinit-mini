Authentication & Authorization
==============================

PyArchInit-Mini uses JWT (JSON Web Tokens) for API authentication with role-based access control (RBAC).

User Roles
----------

The system has three user roles with different permission levels:

Admin
~~~~~
- Full access to all resources
- Can create, read, update, delete all data
- Can manage users (create, edit, delete)
- Can access system configuration

Operator
~~~~~~~~
- Can create, read, update, delete archaeological data
- Cannot manage users
- Cannot modify system configuration

Viewer
~~~~~~
- Read-only access to all data
- Can export data
- Cannot create, modify, or delete records

Obtaining Authentication Token
------------------------------

Login Endpoint
~~~~~~~~~~~~~~

.. code-block:: http

   POST /api/auth/login
   Content-Type: application/x-www-form-urlencoded

   username=admin&password=admin

Response:

.. code-block:: json

   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "token_type": "bearer",
     "expires_in": 1800,
     "user": {
       "id": 1,
       "username": "admin",
       "email": "admin@example.com",
       "role": "admin",
       "permissions": ["create", "read", "update", "delete", "manage_users"]
     }
   }

Using cURL:

.. code-block:: bash

   curl -X POST http://localhost:8000/api/auth/login \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=admin&password=admin"

Using Python requests:

.. code-block:: python

   import requests

   response = requests.post(
       "http://localhost:8000/api/auth/login",
       data={"username": "admin", "password": "admin"}
   )
   token = response.json()["access_token"]

Using the Token
----------------

Include the token in the Authorization header:

.. code-block:: http

   GET /api/sites
   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

cURL example:

.. code-block:: bash

   curl -H "Authorization: Bearer <your-token>" \
     http://localhost:8000/api/sites

Python example:

.. code-block:: python

   headers = {"Authorization": f"Bearer {token}"}
   response = requests.get("http://localhost:8000/api/sites", headers=headers)

JavaScript/Axios example:

.. code-block:: javascript

   const axios = require('axios');

   const api = axios.create({
     baseURL: 'http://localhost:8000/api',
     headers: {
       'Authorization': `Bearer ${token}`
     }
   });

   const sites = await api.get('/sites');

Token Expiration
----------------

- Default expiration: 30 minutes
- Check the ``expires_in`` field in login response
- Token expiration time is included in the JWT payload

Refreshing Tokens
~~~~~~~~~~~~~~~~~

Currently, token refresh is not implemented. When a token expires:

1. Catch the 401 Unauthorized response
2. Re-authenticate with username/password
3. Get a new token

Example with automatic retry:

.. code-block:: python

   import requests
   from datetime import datetime, timedelta

   class APIClient:
       def __init__(self, base_url, username, password):
           self.base_url = base_url
           self.username = username
           self.password = password
           self.token = None
           self.token_expires = None

       def login(self):
           response = requests.post(
               f"{self.base_url}/auth/login",
               data={"username": self.username, "password": self.password}
           )
           data = response.json()
           self.token = data["access_token"]
           self.token_expires = datetime.now() + timedelta(seconds=data["expires_in"])

       def get_headers(self):
           if not self.token or datetime.now() >= self.token_expires:
               self.login()
           return {"Authorization": f"Bearer {self.token}"}

       def get(self, endpoint):
           response = requests.get(
               f"{self.base_url}/{endpoint}",
               headers=self.get_headers()
           )
           if response.status_code == 401:
               self.login()
               response = requests.get(
                   f"{self.base_url}/{endpoint}",
                   headers=self.get_headers()
               )
           return response

User Management Endpoints
-------------------------

These endpoints require admin role:

List Users
~~~~~~~~~~

.. code-block:: http

   GET /api/auth/users
   Authorization: Bearer <admin-token>

Response:

.. code-block:: json

   [
     {
       "id": 1,
       "username": "admin",
       "email": "admin@example.com",
       "role": "admin",
       "is_active": true,
       "created_at": "2025-01-01T00:00:00Z",
       "last_login": "2025-01-20T10:30:00Z"
     }
   ]

Create User
~~~~~~~~~~~

.. code-block:: http

   POST /api/auth/register
   Authorization: Bearer <admin-token>
   Content-Type: application/json

   {
     "username": "newuser",
     "email": "newuser@example.com",
     "password": "securepassword123",
     "role": "operator"
   }

Update User
~~~~~~~~~~~

.. code-block:: http

   PUT /api/auth/users/{user_id}
   Authorization: Bearer <admin-token>
   Content-Type: application/json

   {
     "email": "updated@example.com",
     "role": "viewer",
     "is_active": true
   }

Delete User
~~~~~~~~~~~

.. code-block:: http

   DELETE /api/auth/users/{user_id}
   Authorization: Bearer <admin-token>

Change Password
~~~~~~~~~~~~~~~

Users can change their own password:

.. code-block:: http

   POST /api/auth/change-password
   Authorization: Bearer <user-token>
   Content-Type: application/json

   {
     "current_password": "oldpassword",
     "new_password": "newpassword123"
   }

Permission Checking
-------------------

The API uses decorators to check permissions:

.. code-block:: python

   from pyarchinit_mini.api.dependencies import require_permission

   @app.post("/api/sites")
   @require_permission("create")
   async def create_site(site_data: SiteCreate):
       # Only users with 'create' permission can access
       pass

Permission Matrix
~~~~~~~~~~~~~~~~~

+----------------+-------+----------+--------+
| Action         | Admin | Operator | Viewer |
+================+=======+==========+========+
| View data      | ✓     | ✓        | ✓      |
+----------------+-------+----------+--------+
| Create records | ✓     | ✓        | ✗      |
+----------------+-------+----------+--------+
| Update records | ✓     | ✓        | ✗      |
+----------------+-------+----------+--------+
| Delete records | ✓     | ✓        | ✗      |
+----------------+-------+----------+--------+
| Export data    | ✓     | ✓        | ✓      |
+----------------+-------+----------+--------+
| Import data    | ✓     | ✓        | ✗      |
+----------------+-------+----------+--------+
| Manage users   | ✓     | ✗        | ✗      |
+----------------+-------+----------+--------+

Security Best Practices
-----------------------

1. **HTTPS in Production**
   
   Always use HTTPS in production to prevent token interception:

   .. code-block:: python

      # Configure SSL in production
      uvicorn.run(app, host="0.0.0.0", port=8000, ssl_keyfile="key.pem", ssl_certfile="cert.pem")

2. **Secure Token Storage**
   
   - Never store tokens in localStorage (XSS vulnerable)
   - Use httpOnly cookies or secure session storage
   - For mobile apps, use secure device storage

3. **Token Rotation**
   
   - Implement short-lived access tokens (15-30 minutes)
   - Use refresh tokens for long-term access
   - Rotate refresh tokens on use

4. **Rate Limiting**
   
   Authentication endpoints have stricter rate limits:
   - 5 login attempts per minute per IP
   - 10 password change attempts per hour

5. **Password Requirements**
   
   - Minimum 8 characters
   - At least one uppercase letter
   - At least one number
   - No common passwords (checked against list)

Error Responses
---------------

Authentication errors return appropriate HTTP status codes:

401 Unauthorized
~~~~~~~~~~~~~~~~

.. code-block:: json

   {
     "status": "error",
     "message": "Invalid authentication credentials",
     "detail": {
       "type": "invalid_token",
       "description": "Token has expired or is invalid"
     }
   }

403 Forbidden
~~~~~~~~~~~~~

.. code-block:: json

   {
     "status": "error",
     "message": "Insufficient permissions",
     "detail": {
       "required_permission": "manage_users",
       "user_permissions": ["create", "read", "update", "delete"]
     }
   }

Integration Examples
--------------------

React/TypeScript
~~~~~~~~~~~~~~~~

.. code-block:: typescript

   import axios, { AxiosInstance } from 'axios';

   class PyArchInitAPI {
     private api: AxiosInstance;
     private token: string | null = null;

     constructor(baseURL: string = 'http://localhost:8000/api') {
       this.api = axios.create({ baseURL });

       // Add auth interceptor
       this.api.interceptors.request.use(
         (config) => {
           if (this.token) {
             config.headers.Authorization = `Bearer ${this.token}`;
           }
           return config;
         },
         (error) => Promise.reject(error)
       );

       // Add response interceptor for auto-retry
       this.api.interceptors.response.use(
         (response) => response,
         async (error) => {
           if (error.response?.status === 401 && error.config && !error.config._retry) {
             error.config._retry = true;
             await this.refreshAuth();
             return this.api(error.config);
           }
           return Promise.reject(error);
         }
       );
     }

     async login(username: string, password: string): Promise<void> {
       const response = await this.api.post('/auth/login', 
         new URLSearchParams({ username, password })
       );
       this.token = response.data.access_token;
     }

     async getSites() {
       const response = await this.api.get('/sites');
       return response.data;
     }
   }

Python Async Client
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import asyncio
   import aiohttp
   from typing import Optional, Dict, Any

   class PyArchInitAsyncClient:
       def __init__(self, base_url: str = "http://localhost:8000/api"):
           self.base_url = base_url
           self.token: Optional[str] = None
           self.session: Optional[aiohttp.ClientSession] = None

       async def __aenter__(self):
           self.session = aiohttp.ClientSession()
           return self

       async def __aexit__(self, exc_type, exc_val, exc_tb):
           if self.session:
               await self.session.close()

       async def login(self, username: str, password: str):
           async with self.session.post(
               f"{self.base_url}/auth/login",
               data={"username": username, "password": password}
           ) as response:
               data = await response.json()
               self.token = data["access_token"]

       async def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
           headers = kwargs.pop("headers", {})
           if self.token:
               headers["Authorization"] = f"Bearer {self.token}"

           async with self.session.request(
               method,
               f"{self.base_url}/{endpoint}",
               headers=headers,
               **kwargs
           ) as response:
               if response.status == 401:
                   # Token expired, need to re-login
                   raise Exception("Authentication required")
               response.raise_for_status()
               return await response.json()

       async def get_sites(self):
           return await self._request("GET", "sites")

       async def create_site(self, site_data: dict):
           return await self._request("POST", "sites", json=site_data)

   # Usage
   async def main():
       async with PyArchInitAsyncClient() as client:
           await client.login("admin", "admin")
           sites = await client.get_sites()
           print(sites)