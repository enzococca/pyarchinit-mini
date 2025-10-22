Web Interface Documentation
===========================

PyArchInit-Mini provides a modern web interface built with Flask, offering a responsive, user-friendly experience for managing archaeological data through any web browser.

.. toctree::
   :maxdepth: 2
   :caption: Web Interface Contents:

   quickstart
   authentication
   sites_management
   us_management
   inventory_management
   harris_matrix
   analytics
   export_import
   media_management
   real_time_collaboration
   administration

Quick Start
-----------

Starting the Web Server
~~~~~~~~~~~~~~~~~~~~~~~

To start the web interface:

.. code-block:: bash

   pyarchinit-mini-web
   
   * Running on http://localhost:5001
   * Debug mode: on

Access the interface at: http://localhost:5001

First Login
~~~~~~~~~~~

1. Navigate to http://localhost:5001
2. You'll be redirected to the login page
3. Default credentials:
   
   - Username: ``admin``
   - Password: ``admin``

4. **Important**: Change the default password immediately

Interface Overview
------------------

Navigation Structure
~~~~~~~~~~~~~~~~~~~~

The web interface features a responsive navigation system:

**Top Navigation Bar:**

- Logo and site name
- Hamburger menu (all sections)
- Dashboard link
- Analytics
- Database management
- User management (admin only)
- Language switcher (IT/EN)
- User menu with logout

**Sidebar (Desktop):**

- Quick access to main sections
- Sites, US, Inventory
- Tools and utilities
- Administration links

**Mobile Navigation:**

- Collapsible hamburger menu
- Touch-optimized buttons
- Bottom navigation for common actions

Dashboard
~~~~~~~~~

The main dashboard provides:

1. **Overview Statistics**
   
   - Total sites count
   - Total stratigraphic units
   - Total inventory items
   - Active users online

2. **Recent Activity**
   
   - Latest sites added
   - Recent US entries
   - New inventory items
   - User activity feed

3. **Quick Actions**
   
   - Create new site
   - Add stratigraphic unit
   - Register inventory item
   - Generate reports

Sites Management
----------------

Listing Sites
~~~~~~~~~~~~~

The sites list page (``/sites``) displays all archaeological sites in a responsive table/card view:

**Features:**

- Pagination (20 items per page)
- Search by name or location
- Sort by any column
- Quick actions (view, edit, delete)
- Mobile-optimized card view

**Table Columns:**

- ID
- Site Name
- Location (Nation)
- Region
- Comune
- Province
- Definition
- Actions

Creating a Site
~~~~~~~~~~~~~~~

Click "New Site" to open the site creation form:

**Required Fields:**

- Site name (unique)

**Optional Fields:**

- Location/Nation
- Region  
- Comune (municipality)
- Province
- Definition (Italian)
- Definition (English)

**Form Features:**

- Real-time validation
- Auto-save draft
- Multi-language support
- Help tooltips

Editing Sites
~~~~~~~~~~~~~

Click the edit button to modify site information:

1. Form pre-populated with current data
2. Change tracking (shows modified fields)
3. Validation before save
4. Confirmation for critical changes

Site Details
~~~~~~~~~~~~

The site detail page shows:

- Complete site information
- Related stratigraphic units count
- Inventory items count
- Quick links to related data
- Export options

Stratigraphic Units (US) Management
------------------------------------

US List Page
~~~~~~~~~~~~

Access via ``/us`` or sidebar:

**Features:**

- Filter by site
- Filter by area
- Search in descriptions
- Advanced filters (period, type)
- Bulk operations

US Form (49 Fields)
~~~~~~~~~~~~~~~~~~~

The US form is organized into 6 tabs:

**1. Dati Generali (General Data)**

- Sito* (Site - required)
- Area
- US* (Unit number - required)  
- Definizione stratigrafica
- Definizione interpretativa
- Anno di scavo

**2. Dati Stratigrafici (Stratigraphic Data)**

- Periodo iniziale
- Fase iniziale
- Periodo finale  
- Fase finale
- Attività
- Unità tipo (US, USM, USD, USV, VSF)

**3. Caratteristiche (Characteristics)**

- Formazione
- Colore
- Consistenza
- Modo di formazione
- Inclusi
- Componenti organici
- Componenti inorganici

**4. Rapporti Stratigrafici (Relationships)**

- Si lega a
- Uguale a
- Copre
- Coperto da
- Riempie
- Riempito da
- Taglia
- Tagliato da
- Si appoggia a
- Gli si appoggia

**5. Documentazione (Documentation)**

- Documentazione (text)
- Osservazioni
- Interpretazione
- Elementi datanti
- Campioni
- Piante
- Sezione/Prospetto
- Foto

**6. Misurazioni (Measurements)**

- Lunghezza max
- Altezza max
- Profondità max
- Volume
- Superficie

Form Behavior
~~~~~~~~~~~~~

- Tab validation (red indicator if errors)
- Auto-save to localStorage
- Relationship validation
- ICCD thesaurus integration
- Real-time collaboration updates

Inventory Management
--------------------

Inventory List
~~~~~~~~~~~~~~

The inventory page (``/inventario``) provides:

- Advanced filtering options
- Image thumbnails
- Conservation state indicators
- Export selected items
- Print labels

Inventory Form (37 Fields)
~~~~~~~~~~~~~~~~~~~~~~~~~~

Organized in 8 tabs:

**1. Dati Principali**

- N. Inventario* (required)
- Tipo reperto
- Classe materiale
- Definizione
- Stato conservazione

**2. Dati di Scavo**

- Sito
- Area
- US
- Quadrato
- Ambiente

**3. Misurazioni**

- Lunghezza
- Larghezza  
- Altezza
- Diametro
- Peso
- EVE (Estimated Vessel Equivalent)

**4. Tecnologia**

- Tipo oggetto
- Funzione
- Descrizione
- Corpo ceramico
- Rivestimento
- Decorazione

**5. Elementi di Datazione**

- Datazione reperto
- Criterio datazione
- Bibliografia

**6. Quantificazione**

- Frammenti
- Totale frammenti
- Tipo quantità

**7. Morfologia**

- Forma
- Tipologia
- Confronti

**8. Conservazione**

- Luogo conservazione
- Lavato
- Restaurato
- Catalogato

Harris Matrix Visualization
---------------------------

Interactive Features
~~~~~~~~~~~~~~~~~~~~

Access via Tools → Harris Matrix:

1. **Site Selection**
   
   - Dropdown of available sites
   - Unit count preview

2. **Visualization Options**
   
   - Grouping: period+area, period, area, none
   - Export format: PNG, PDF, SVG
   - Resolution settings

3. **Interactive Graph**
   
   - Pan and zoom
   - Node clicking for details
   - Relationship highlighting
   - Period color coding

GraphML Export
~~~~~~~~~~~~~~

Export to yEd format:

1. Select site
2. Choose "Export GraphML (yEd)"
3. Configure options:
   
   - Include descriptions
   - EM_palette styling
   - Custom metadata

4. Download .graphml file

Analytics Dashboard
-------------------

Real-time analytics with 8 chart types:

Overview Cards
~~~~~~~~~~~~~~

- Total sites
- Total US count
- Total finds
- Geographic spread

Interactive Charts
~~~~~~~~~~~~~~~~~~

1. **Sites by Region** (Pie chart)
2. **Sites by Province** (Bar chart)
3. **US by Period** (Horizontal bar)
4. **US by Type** (Doughnut chart)
5. **Finds by Type** (Bar chart)
6. **Conservation State** (Pie chart)
7. **US per Site** (Top 10 bar)
8. **Finds per Site** (Top 10 bar)

**Chart Features:**

- Hover tooltips
- Click to filter
- Export as image
- Print view

Export/Import Interface
-----------------------

Web-based import/export:

Export Options
~~~~~~~~~~~~~~

1. Select data type (Sites/US/Inventory)
2. Choose format (Excel/CSV)
3. Apply filters (optional)
4. Click Export
5. Download starts automatically

Import Process
~~~~~~~~~~~~~~

1. Select data type
2. Upload CSV/Excel file
3. Preview data mapping
4. Configure options:
   
   - Skip duplicates
   - Update existing
   - Validation rules

5. Review import summary

Real-time Collaboration
-----------------------

WebSocket Features
~~~~~~~~~~~~~~~~~~

The web interface includes real-time updates:

**Online Users Badge**

- Shows count of connected users
- Updates automatically
- Click to see user list

**Live Notifications**

Toast notifications for:

- User connections/disconnections
- Data creation
- Data modifications
- Data deletions

**Activity Types:**

- "User X created site Y"
- "User X modified US Z"  
- "User X deleted inventory item"

**Notification Settings:**

- Position: top-right
- Duration: 5 seconds
- Sound: optional
- Persistence: important alerts

Media Management
----------------

Upload Interface
~~~~~~~~~~~~~~~~

Access via Tools → Upload Media:

1. **Drag & Drop Zone**
   
   - Multiple file support
   - Progress indicators
   - Auto-thumbnail generation

2. **File Types**
   
   - Images: JPG, PNG, GIF
   - Documents: PDF, DOC, DOCX
   - Videos: MP4, AVI, MOV
   - Max size: 100MB

3. **Metadata**
   
   - Title
   - Description
   - Tags
   - Related entity (Site/US/Inventory)

Media Gallery
~~~~~~~~~~~~~

Browse uploaded media:

- Grid/list view toggle
- Filter by type
- Search by filename
- Bulk operations

Internationalization
--------------------

Language Support
~~~~~~~~~~~~~~~~

Full support for Italian and English:

**Switching Languages:**

1. Click flag icon in navbar
2. Select IT or EN
3. Page reloads in selected language
4. Preference saved in session

**Translated Elements:**

- All interface text
- Form labels and help
- Error messages
- Chart labels
- Export headers

Administration
--------------

Database Management
~~~~~~~~~~~~~~~~~~~

Admin-only features:

**Upload Database:**

1. Navigate to Database → Upload
2. Select .db file
3. Validation checks
4. Replace or merge options

**Connect PostgreSQL:**

1. Database → Connect
2. Enter connection details
3. Test connection
4. Save configuration

**Database Info:**

- Current connection
- Table statistics
- Health check

User Management
~~~~~~~~~~~~~~~

Manage users (admin only):

**User List:**

- Username
- Email
- Role
- Last login
- Actions

**Create User:**

1. Click "New User"
2. Fill required fields:
   
   - Username
   - Email
   - Password
   - Role (Admin/Operator/Viewer)

**Edit User:**

- Change role
- Reset password
- Enable/disable account

Responsive Design
-----------------

Mobile Optimization
~~~~~~~~~~~~~~~~~~~

The interface adapts to different screen sizes:

**Phone (< 768px):**

- Single column layout
- Card view for lists
- Bottom action buttons
- Touch-optimized controls
- Minimum 44px touch targets

**Tablet (768-991px):**

- Two column layout
- Collapsible sidebar
- Optimized forms
- Readable font sizes

**Desktop (≥ 992px):**

- Full sidebar
- Multi-column tables
- Hover interactions
- Keyboard shortcuts

Performance Features
--------------------

Optimization Techniques
~~~~~~~~~~~~~~~~~~~~~~~

1. **Lazy Loading**
   
   - Images load on scroll
   - Pagination for large datasets
   - Deferred JavaScript

2. **Caching**
   
   - Static assets cached
   - API responses cached
   - LocalStorage for drafts

3. **Compression**
   
   - Gzip enabled
   - Minified CSS/JS
   - Optimized images

Security Features
-----------------

Built-in Security
~~~~~~~~~~~~~~~~~

1. **Authentication Required**
   
   - All pages protected
   - Session timeout
   - Remember me option

2. **CSRF Protection**
   
   - Tokens on all forms
   - Automatic validation

3. **Input Validation**
   
   - Client-side validation
   - Server-side validation
   - SQL injection prevention

4. **File Upload Security**
   
   - Type validation
   - Size limits
   - Virus scanning (optional)

Browser Support
---------------

Supported Browsers
~~~~~~~~~~~~~~~~~~

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile Chrome/Safari

**Not Supported:**

- Internet Explorer
- Older browser versions

Keyboard Shortcuts
------------------

Available shortcuts:

- ``Ctrl+N``: New item (context-aware)
- ``Ctrl+S``: Save current form
- ``Ctrl+F``: Focus search
- ``Ctrl+E``: Export data
- ``ESC``: Close modals
- ``?``: Show shortcuts help

Configuration
-------------

Web-specific settings in config.yaml:

.. code-block:: yaml

   web:
     host: "0.0.0.0"
     port: 5001
     debug: true
     secret_key: "change-this-in-production"
     session_lifetime: 1800  # 30 minutes
     max_upload_size: 104857600  # 100MB
     allowed_extensions: ["jpg", "png", "pdf", "doc"]
     enable_socketio: true
     cors_origins: ["http://localhost:3000"]