<p align="center">
  <img src="https://raw.githubusercontent.com/enzococca/pyarchinit-mini/main/logo/logo_pyarchinit-mini.png" alt="PyArchInit-Mini Logo" width="300">
</p>

<h1 align="center">PyArchInit-Mini</h1>

<p align="center">
  <a href="https://badge.fury.io/py/pyarchinit-mini"><img src="https://badge.fury.io/py/pyarchinit-mini.svg" alt="PyPI version"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.8--3.14-blue.svg" alt="Python 3.8-3.14"></a>
  <a href="https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html"><img src="https://img.shields.io/badge/License-GPL%20v2-blue.svg" alt="License: GPL v2"></a>
  <a href="https://pyarchinit-mini.readthedocs.io/en/latest/?badge=latest"><img src="https://readthedocs.org/projects/pyarchinit-mini/badge/?version=latest" alt="Documentation Status"></a>
  <a href="https://pypi.org/project/pyarchinit-mini/"><img src="https://img.shields.io/badge/status-stable-green.svg" alt="Status"></a>
</p>

**Lightweight Archaeological Data Management System - 100% Desktop GUI Parity**

PyArchInit-Mini is a standalone, modular version of PyArchInit focused on core archaeological data management functionality without GIS dependencies. It provides multiple interfaces (Web, Desktop GUI, CLI, REST API) with a clean, scalable architecture for managing archaeological sites, stratigraphic units, and material inventories.

---

## ✨ Features

### 🏛️ Core Data Management
- **Site Management**: Complete CRUD operations for archaeological sites with i18n support
- **Stratigraphic Units (US)**: 49 fields organized in 6 tabs, matching desktop GUI
- **Material Inventory**: 37 fields in 8 tabs with ICCD thesaurus support
- **Multi-Database**: SQLite and PostgreSQL with upload/connect capabilities
- **Internationalization**: Full support for Italian and English languages

### 🔬 Advanced Archaeological Tools
- **Harris Matrix**: Graphviz visualizer with 4 grouping modes and GraphML export
- **3D Visualization**: s3Dgraphy integration for stratigraphic unit visualization
- **Stratigraphic Validation**: Paradox detection, cycle detection, auto-fix reciprocal relationships
- **PDF Export**: Desktop-style reports (Sites, US, Inventario, Harris Matrix embedded)
- **Media Management**: Images, documents, videos with metadata
- **Thesaurus ICCD**: 4 controlled vocabularies for standardized data entry

### 🖥️ Multiple User Interfaces
- **Web Interface (Flask)**: Modern Bootstrap 5 UI, responsive design
- **Desktop GUI (Tkinter)**: Complete native application
- **CLI Interface**: Rich-based interactive command-line
- **REST API (FastAPI)**: Scalable API with automatic OpenAPI docs

### 📊 Data Export/Import
- **Excel Export**: Export Sites, US, Inventario to .xlsx format
- **CSV Export**: Export to CSV with optional site filtering
- **Batch Import**: Import data from CSV with validation and statistics
- **Multi-Interface**: Available in Web UI, Desktop GUI, and CLI
- **Duplicate Handling**: Skip duplicates option to preserve existing data

### 🔐 Multi-User Authentication
- **Role-Based Access Control**: 3 user roles (Admin, Operator, Viewer)
- **JWT Authentication**: Secure API access with JSON Web Tokens
- **Session Management**: Flask-Login for Web interface
- **Password Security**: Bcrypt hashing for secure password storage
- **User Management**: Admin interface for creating/editing/deleting users
- **Permissions**: Granular permissions (create, read, update, delete, manage_users)
- **Protected Routes**: All web routes require authentication

### 🌐 Real-Time Collaboration (NEW in v1.0.9)
- **WebSocket Support**: Flask-SocketIO for bidirectional real-time communication
- **Live Notifications**: Toast notifications for all CRUD operations (Sites, US, Inventario)
- **Online User Presence**: See who's currently connected to the system
- **Activity Tracking**: Real-time updates when users create, edit, or delete data
- **User Join/Leave Events**: Notifications when team members connect or disconnect
- **Instant Data Sync**: All team members see changes immediately without refreshing
- **Multi-Tab Support**: Works across multiple browser tabs and windows

### 📊 Analytics Dashboard (NEW in v1.1.0)
- **Interactive Charts**: 8 different chart types for comprehensive data visualization
- **Overview Statistics**: Total counts for sites, US, inventory items, regions, and provinces
- **Geographic Analysis**: Sites distribution by region and province (pie and bar charts)
- **Chronological Analysis**: US distribution by chronological period
- **Typological Analysis**: US and inventory items grouped by type (doughnut and bar charts)
- **Conservation Analysis**: Inventory items by conservation state with color-coded pie chart
- **Site-Level Aggregations**: Top 10 sites by US count and inventory count
- **Multi-Interface Support**: Available in both Web UI (Chart.js) and Desktop GUI (matplotlib)
- **Real-Time Data**: Charts update automatically with current database state

### 🔄 GraphML Converter - Harris Matrix Export (NEW in v1.1.5)
Export Harris Matrix diagrams to yEd Graph Editor with full EM_palette styling and archaeological metadata.

**Core Features**:
- **yEd Compatibility**: Export to yEd Graph Editor compatible GraphML format
- **EM_palette Styling**: Automatic node colors and shapes based on `unita_tipo` (US, USM, USD, USV, USV/s)
- **Archaeological Metadata**: Node descriptions with `d_stratigrafica` + `d_interpretativa` visible in yEd
- **Clean Edge Display**: Edges without text labels (relationship types in tooltips)
- **Period Preservation**: Automatic grouping by archaeological periods with color coding
- **Flexible Grouping**: Support for period+area, period-only, area-only, or no grouping modes
- **Transitive Reduction**: Automatic removal of redundant stratigraphic relationships
- **Multi-Interface Support**: Available via Python API, CLI, REST API, Web UI, and Desktop GUI

**EM_palette Node Styles** (based on `unita_tipo`):
- **US/USM** (Stratigraphic Unit): Red border (#9B3333), white fill, rectangle
- **USD** (Documentary US): Orange border (#D86400), white fill, rounded rectangle
- **USV** (Virtual US negative): Green border (#31792D), black fill, hexagon
- **USV/s** (Virtual US structural): Blue border (#248FE7), black fill, trapezium

**Edge Styles** (PyArchInit convention):
- **Contemporary** (uguale a, si lega a): No arrow, solid line
- **Stratigraphic** (copre, sotto): Arrow, solid line
- **Negative** (taglia): Arrow, dashed line
- **Virtual/Uncertain**: Arrow, dashed line

**Data Requirements** (for external API use):
```python
# Graph node structure
graph.nodes[us_number] = {
    'd_stratigrafica': str,        # Stratigraphic description
    'd_interpretativa': str,       # Archaeological interpretation
    'unita_tipo': str,             # Unit type: US, USM, USD, USV, USV/s
    'period_initial': str,         # Initial chronological period
    'area': str,                   # Archaeological area/sector
}

# Graph edge structure
graph.edges[(source, target)] = {
    'relationship': str,           # Type: copre, taglia, uguale a, si lega a
    'certainty': str              # certain, uncertain
}
```

**Usage Examples**:
```python
# Python API - From NetworkX graph
from pyarchinit_mini.graphml_converter import convert_dot_to_graphml
import networkx as nx

graph = nx.DiGraph()
graph.add_node(1001,
    d_stratigrafica='Strato di riempimento',
    d_interpretativa='Deposito medievale',
    unita_tipo='US',
    period_initial='Medievale')
graph.add_edge(1001, 1002, relationship='copre')

# Generate DOT and convert
# ... (see documentation for full example)

# CLI - From DOT file
pyarchinit-graphml convert harris.dot harris.graphml -t "Pompei - Regio VI"

# REST API - Upload DOT file
curl -X POST http://localhost:8000/api/graphml/convert \
     -F "file=@harris.dot" -F "title=Pompei"

# Web Interface - Export from database
# Navigate to: Harris Matrix → Export GraphML (yEd)
# Select site, configure options, download .graphml file

# Desktop GUI - Tools menu
# Tools → Export GraphML (yEd)
```

**Available Interfaces**:
- **Python Library**: `from pyarchinit_mini.graphml_converter import convert_dot_to_graphml`
- **CLI Tool**: `pyarchinit-graphml convert|template|batch`
- **REST API**: 4 endpoints at `/api/graphml/*` (convert, convert-content, template, health)
- **Web Interface**: Form-based export with site selection and real-time download
- **Desktop GUI**: Tkinter dialog in Tools menu with file save dialog

**Output**:
- GraphML file compatible with yEd Graph Editor
- Node descriptions visible in yEd "Description" field
- EM_palette colors and shapes applied automatically
- Edge relationships available as tooltips
- Period-based table structure for hierarchical visualization

### 🎨 s3Dgraphy - 3D Stratigraphic Visualization (NEW in v1.6.0)

**Interactive 3D Harris Matrix with Extended Matrix (EM) Palette Integration**

s3Dgraphy provides a complete 3D visualization system for Harris Matrix diagrams, combining stratigraphic relationships with 3D models of archaeological contexts. The system uses GraphViz DOT layout for accurate positioning and supports OBJ, GLTF, and GLB 3D formats.

#### Core Features

- **Integrated 3D+2D Viewer**: Side-by-side Harris Matrix and 3D model visualization
- **GraphViz DOT Layout**: Professional stratigraphic positioning following archaeological standards
- **Extended Matrix Palette**: Automatic node coloring based on US type (10 archaeological categories)
- **3D Model Support**: OBJ, GLTF (with vertex colors), and GLB formats
- **Interactive Navigation**: Click nodes to focus 3D model, navigate between related US
- **Real-Time Sync**: Bi-directional synchronization between matrix and 3D view
- **Model Upload**: REST API for uploading 3D models per stratigraphic unit
- **Persistent Storage**: Site-based organization of 3D models

#### Extended Matrix Color Palette

Automatic node coloring based on `unita_tipo`:

| Type | Color | RGB | Hex |
|------|-------|-----|-----|
| Taglio | Brown | (139, 69, 19) | #8B4513 |
| Deposito | Chocolate | (210, 105, 30) | #D2691E |
| Riempimento | Peru | (205, 133, 63) | #CD853F |
| Humus | Dark Olive Green | (85, 107, 47) | #556B2F |
| Muro | Gray | (128, 128, 128) | #808080 |
| Pavimento | Dark Gray | (169, 169, 169) | #A9A9A9 |
| Crollo | Maroon | (128, 0, 0) | #800000 |
| Costruzione | Light Gray | (211, 211, 211) | #D3D3D3 |
| Distruzione | Dark Red | (139, 0, 0) | #8B0000 |
| Altro | Light Steel Blue | (176, 196, 222) | #B0C4DE |

#### API Endpoints

**Model Management**:
```python
# Upload 3D model for a specific US
POST /api/s3d/upload
Content-Type: multipart/form-data
Fields:
  - site_name: str          # Archaeological site name
  - us_id: str              # Stratigraphic unit ID
  - file: File              # 3D model file (OBJ/GLTF/GLB)

Response: {"message": str, "path": str}
```

**Viewer Access**:
```python
# Get integrated 3D Harris Matrix viewer
GET /s3d/viewer/<site_name>

# Get models for a site
GET /api/s3d/models/<site_name>

Response: [
    {
        "name": str,           # Display name
        "path": str,          # Relative path
        "us_id": str,         # US number or null for site-level
        "format": str         # "obj", "gltf", or "glb"
    }
]
```

#### Data Format for External Use

**Harris Matrix Graph Structure**:
```python
# Input format for Harris Matrix visualization
{
    "nodes": [
        {
            "id": str,                    # Unique node ID
            "us_number": str,             # US number for display
            "type": str,                  # EM palette type (see table above)
            "area": str,                  # Archaeological area/sector
            "period": str,                # Chronological period
            "definition": str,            # US description
            "d_stratigrafica": str,       # Stratigraphic description
            "d_interpretativa": str       # Archaeological interpretation
        }
    ],
    "edges": [
        {
            "source": str,                # Source node ID
            "target": str,                # Target node ID
            "stratigraphic_relation": str # COVERS, CUTS, FILLS, etc.
        }
    ]
}
```

**3D Model Requirements**:
- **OBJ Format**: Wavefront OBJ with optional MTL file
- **GLTF/GLB Format**: GLTF 2.0 with vertex colors support
- **File Size**: Max 100MB per model (configurable)
- **Coordinate System**: Y-up, meters
- **Model Organization**:
  - Site-level: `uploads/3d_models/<site_name>/site/model.obj`
  - US-level: `uploads/3d_models/<site_name>/US_<us_id>/model.obj`

#### Usage Examples

**Python API - Upload and Visualize**:
```python
from pyarchinit_mini.s3d_integration import Model3DManager
import requests

# Upload 3D model via API
files = {'file': open('model.obj', 'rb')}
data = {
    'site_name': 'Pompei',
    'us_id': '1001'
}
response = requests.post(
    'http://localhost:5001/api/s3d/upload',
    files=files,
    data=data
)

# Access viewer
viewer_url = f'http://localhost:5001/s3d/viewer/Pompei'
```

**Python API - Direct Model Management**:
```python
from pyarchinit_mini.s3d_integration import Model3DManager
from pathlib import Path

manager = Model3DManager(base_dir='uploads/3d_models')

# Get models for a site
models = manager.get_models_for_site('Pompei')
for model in models:
    print(f"US {model['us_id']}: {model['name']} ({model['format']})")

# Get model path for specific US
path = manager.get_model_path('Pompei', '1001')
```

**cURL - Upload Model**:
```bash
# Upload OBJ model
curl -X POST http://localhost:5001/api/s3d/upload \
  -F "site_name=Pompei" \
  -F "us_id=1001" \
  -F "file=@US1001.obj"

# Upload GLTF model with vertex colors
curl -X POST http://localhost:5001/api/s3d/upload \
  -F "site_name=Pompei" \
  -F "us_id=1002" \
  -F "file=@US1002.gltf"

# Upload site-level model (no US)
curl -X POST http://localhost:5001/api/s3d/upload \
  -F "site_name=Pompei" \
  -F "file=@site_overview.glb"
```

**Web Interface - Upload and View**:
1. Navigate to **Harris Matrix** → **3D Viewer** → Select site
2. Click **Upload Model** button
3. Select US (optional, leave blank for site-level model)
4. Choose 3D file (OBJ/GLTF/GLB)
5. Upload and view immediately

**Viewer Features**:
- **Dual Panel**: Harris Matrix (left) + 3D Model (right)
- **Node Click**: Click any US node to focus 3D camera on that model
- **Info Panel**: Right sidebar with US properties and stratigraphic relations
- **Navigation**: Click parent/child relations to navigate through stratigraphy
- **Scrollable Matrix**: Vertical scroll for deep stratigraphic sequences
- **Model Selection**: Dropdown to switch between different 3D models
- **Camera Controls**: OrbitControls for 3D navigation (rotate, pan, zoom)

#### Generating Test Models

For testing or creating proxy geometries:
```python
from pyarchinit_mini.s3d_integration.test_model_generator import (
    generate_test_models, EM_COLORS
)

# Generate colored box for each US type
us_data = {
    'us': 1001,
    'type': 'Deposito',      # Will use chocolate color
    'area': 'A',
    'period': 'Medievale',
    'position': (0, 0, 0),   # X, Y, Z coordinates
    'size': (2, 1, 2)        # Width, Height, Depth in meters
}

generate_test_models(
    us_list=[us_data],
    output_dir='output/3d_models',
    formats=['obj', 'gltf']  # Generate both formats
)
```

#### Integration with Existing Harris Matrix

The 3D viewer automatically integrates with PyArchInit's Harris Matrix data:

1. **Automatic Graph Generation**: Reads US and relationships from database
2. **GraphViz Layout**: Uses DOT algorithm for hierarchical positioning
3. **Extended Matrix Colors**: Applies EM palette based on `unita_tipo`
4. **Model Association**: Links 3D models by US number
5. **Bidirectional Sync**: Matrix clicks update 3D view, and vice versa

#### External Integration Example

Complete workflow for external applications:

```python
import requests
import json

# 1. Define stratigraphic data
harris_data = {
    "nodes": [
        {
            "id": "site_pompei_1001",
            "us_number": "1001",
            "type": "Deposito",
            "area": "Regio VI",
            "period": "Periodo Romano Imperiale",
            "definition": "Strato di abbandono"
        },
        {
            "id": "site_pompei_1002",
            "us_number": "1002",
            "type": "Pavimento",
            "area": "Regio VI",
            "period": "Periodo Romano Imperiale",
            "definition": "Pavimento a mosaico"
        }
    ],
    "edges": [
        {
            "source": "site_pompei_1001",
            "target": "site_pompei_1002",
            "stratigraphic_relation": "COVERS"
        }
    ]
}

# 2. Create site in PyArchInit (if not exists)
site_data = {
    "site_name": "Pompei",
    "location_region": "Campania",
    "location_comune": "Pompei"
}
requests.post('http://localhost:5001/api/sites', json=site_data)

# 3. Upload 3D models
for us in ["1001", "1002"]:
    with open(f'models/US{us}.gltf', 'rb') as f:
        files = {'file': f}
        data = {'site_name': 'Pompei', 'us_id': us}
        requests.post('http://localhost:5001/api/s3d/upload',
                     files=files, data=data)

# 4. Access integrated viewer
print("Viewer: http://localhost:5001/s3d/viewer/Pompei")
```

#### Configuration

Edit `~/.pyarchinit_mini/config/config.yaml`:

```yaml
s3dgraphy:
  enabled: true
  upload_dir: "web_interface/static/uploads/3d_models"
  max_file_size: 104857600  # 100MB
  allowed_formats: ["obj", "mtl", "gltf", "glb"]
  default_camera:
    position: [5, 5, 5]
    target: [0, 0, 0]
```

### 🚀 Technical Features
- **Production Ready**: v1.1.5 with EM_palette GraphML Export + Archaeological Metadata + Clean Edges
- **Python 3.8-3.14**: Full support for latest Python versions including 3.12, 3.13, 3.14
- **Data Validation**: Comprehensive Pydantic schemas
- **Session Management**: Proper database connection pooling
- **Auto Documentation**: Interactive Swagger/OpenAPI docs
- **Cross-Platform**: Windows, Linux, macOS support
- **Tests Included**: Full test suite included in distribution

---

## 📊 Project Status

### 🚀 Version 1.2.9 - Production Ready

PyArchInit-Mini is now **fully functional** and ready for production use. All installation issues have been resolved:

✅ **All Interfaces Working**: Web, Desktop GUI, CLI, and REST API fully operational  
✅ **PyPI Package Fixed**: All console commands work correctly after `pip install`  
✅ **Internationalization**: Complete Italian/English support with automatic migrations  
✅ **3D Visualization**: s3Dgraphy integration for stratigraphic unit visualization  
✅ **GraphML Export**: Harris Matrix export to yEd with EM_palette styling  

### 🔧 Recent Fixes (v1.2.5-1.2.8)
- Fixed missing email-validator dependency
- Fixed desktop GUI language switching
- Fixed web server Flask template/static path resolution  
- Added automatic i18n database column migrations
- All module imports now use absolute paths for installed packages

### 📈 Active Development
The project is actively maintained with regular updates. Check the [CHANGELOG](CHANGELOG.md) for detailed version history.

---

## 📦 Installation

### Basic Installation (API Only)
```bash
pip install pyarchinit-mini
```

### With CLI Interface
```bash
pip install 'pyarchinit-mini[cli]'
```

### With Web Interface
```bash
pip install 'pyarchinit-mini[web]'
```

### With Desktop GUI
```bash
pip install 'pyarchinit-mini[gui]'
```

### With Harris Matrix Visualization
```bash
pip install 'pyarchinit-mini[harris]'
```

### With Advanced PDF Export
```bash
pip install 'pyarchinit-mini[pdf]'
```

### With Excel/CSV Export and Import
```bash
pip install 'pyarchinit-mini[export]'
```

### With Authentication (Multi-User)
```bash
pip install 'pyarchinit-mini[auth]'
```

### Complete Installation (Recommended)
```bash
pip install 'pyarchinit-mini[all]'
```

### Development Installation
```bash
pip install 'pyarchinit-mini[dev]'
```

> **Note for zsh users**: Quote the package name to avoid globbing issues: `'pyarchinit-mini[all]'`

---

## 🚀 Quick Start

### 1. Initial Setup
After installation, run the initialization command to set up the database and create an admin user:

```bash
pyarchinit-mini-init
```

This command will:
1. Create the configuration directory and database in `~/.pyarchinit_mini/`
2. Prompt you to create an admin user (username, email, password)
3. Set up all necessary directories for media, exports, and backups

For non-interactive setup with default credentials:
```bash
pyarchinit-mini-init --non-interactive
# Creates admin user with username: admin, password: admin
```

**Note**: If using the non-interactive mode, change the default password immediately after first login!

The setup creates the following structure in your home directory:

```
~/.pyarchinit_mini/
├── data/              # Database SQLite files
├── media/             # Images, videos, documents
│   ├── images/
│   ├── videos/
│   ├── documents/
│   └── thumbnails/
├── export/            # Generated PDF exports
├── backup/            # Automatic database backups
├── config/            # Configuration files
│   └── config.yaml
└── logs/              # Application logs
```

### 2. Usage

#### Start the Web Interface
```bash
pyarchinit-mini-web
# Open http://localhost:5001 in your browser
# Login with the admin credentials created during initialization
```

#### Start the Desktop GUI
```bash
pyarchinit-mini-gui
```

#### Start the REST API Server
```bash
pyarchinit-mini-api
# API docs available at http://localhost:8000/docs
```

#### Start the CLI Interface
```bash
pyarchinit-mini
```

### 3. Accessing the Analytics Dashboard

The Analytics Dashboard provides comprehensive data visualization with 8 different chart types.

#### Web Interface
1. Start the web interface: `pyarchinit-mini-web`
2. Login with your admin credentials
3. Navigate to **Analytics** in the top menu
4. View interactive Chart.js charts with:
   - Sites by region (pie chart)
   - Sites by province (bar chart - top 10)
   - US by chronological period (horizontal bar chart)
   - US by type (doughnut chart)
   - Inventory by type (bar chart - top 10)
   - Inventory by conservation state (pie chart)
   - US by site (bar chart - top 10)
   - Inventory by site (bar chart - top 10)

#### Desktop GUI
1. Start the desktop application: `pyarchinit-gui`
2. Go to **Tools → Analytics Dashboard**
3. View matplotlib charts with the same 8 visualizations
4. Use the zoom/pan toolbar for detailed analysis
5. Scroll through all charts in a single window

**Charts Update Automatically**: All charts reflect the current state of your database in real-time.

---

## 📚 Dependencies Structure

### Core (Always Installed)
- **FastAPI + Uvicorn**: REST API framework
- **SQLAlchemy**: ORM and database abstraction
- **psycopg2-binary**: PostgreSQL driver
- **Pydantic**: Data validation
- **NetworkX**: Harris Matrix generation
- **ReportLab**: PDF generation
- **Pillow**: Image processing

### Optional Extras

| Extra | Components | Installation |
|-------|-----------|--------------|
| `cli` | Click, Rich, Inquirer | `pip install 'pyarchinit-mini[cli]'` |
| `web` | Flask, WTForms, Jinja2, Flask-SocketIO | `pip install 'pyarchinit-mini[web]'` |
| `gui` | (Tkinter is in stdlib) | `pip install 'pyarchinit-mini[gui]'` |
| `harris` | Matplotlib, Graphviz | `pip install 'pyarchinit-mini[harris]'` |
| `pdf` | WeasyPrint | `pip install 'pyarchinit-mini[pdf]'` |
| `media` | python-magic, moviepy | `pip install 'pyarchinit-mini[media]'` |
| `export` | pandas, openpyxl | `pip install 'pyarchinit-mini[export]'` |
| `auth` | passlib, bcrypt, python-jose, flask-login | `pip install 'pyarchinit-mini[auth]'` |
| `all` | All of the above | `pip install 'pyarchinit-mini[all]'` |
| `dev` | pytest, black, mypy, flake8 | `pip install 'pyarchinit-mini[dev]'` |

---

## ⚙️ Configuration

### Database Configuration

Edit `~/.pyarchinit_mini/config/config.yaml`:

```yaml
database:
  # SQLite (default)
  url: "sqlite:///~/.pyarchinit_mini/data/pyarchinit_mini.db"

  # Or PostgreSQL
  # url: "postgresql://user:password@localhost:5432/pyarchinit"

api:
  host: "0.0.0.0"
  port: 8000
  reload: true

web:
  host: "0.0.0.0"
  port: 5001
  debug: true

media:
  base_dir: "~/.pyarchinit_mini/media"
  max_upload_size: 104857600  # 100MB

export:
  base_dir: "~/.pyarchinit_mini/export"
  pdf_dpi: 300

backup:
  enabled: true
  frequency: "daily"
  keep_count: 7
```

### Environment Variables

Alternatively, use environment variables:

```bash
export DATABASE_URL="postgresql://user:pass@localhost:5432/pyarchinit"
export PYARCHINIT_WEB_PORT=5001
export PYARCHINIT_API_PORT=8000
```

---

## 🎯 Key Features in Detail

### Web Interface
- **Complete Forms**: US (49 fields/6 tabs), Inventario (37 fields/8 tabs)
- **Thesaurus Integration**: ICCD-compliant controlled vocabularies
- **Harris Matrix Viewer**: Interactive Graphviz visualization with 4 grouping modes
- **Validation Tools**: Stratigraphic paradox/cycle detection with auto-fix
- **Database Management**: Upload SQLite files, connect to PostgreSQL
- **PDF Export**: One-click export for Sites, US, Inventario with Harris Matrix

### Desktop GUI
- **Native Tkinter Application**: Full-featured desktop interface
- **Identical to Web**: Same 49-field US and 37-field Inventario forms
- **Offline Capable**: Works without internet connection
- **Cross-Platform**: Windows, Linux, macOS

### REST API
- **FastAPI Framework**: Modern, fast, async-capable
- **Auto Documentation**: Swagger UI at `/docs`, ReDoc at `/redoc`
- **Validation**: Automatic request/response validation
- **Scalable**: Production-ready with Uvicorn

### Harris Matrix
- **Graphviz Engine**: Professional orthogonal layout
- **4 Grouping Modes**:
  - `period_area`: Group by period and area
  - `period`: Group by period only
  - `area`: Group by area only
  - `none`: No grouping
- **High Resolution**: 300 DPI export for publications
- **PDF Integration**: Embedded in site reports

### Stratigraphic Validation
- **Paradox Detection**: Find logical impossibilities in stratigraphic relationships
- **Cycle Detection**: Identify circular dependencies
- **Reciprocal Check**: Verify bidirectional relationships
- **Auto-Fix**: One-click correction for missing reciprocals

### Export/Import
- **Web Interface**: Navigate to Export/Import page for visual interface
- **Desktop GUI**: Menu → Strumenti → Export/Import Dati
- **CLI Commands**:
  ```bash
  # Export to Excel/CSV
  pyarchinit-export-import export-sites -f excel -o sites.xlsx
  pyarchinit-export-import export-us -f csv -s "SiteName" -o us.csv
  pyarchinit-export-import export-inventario -f excel -o inventario.xlsx

  # Import from CSV
  pyarchinit-export-import import-sites sites.csv
  pyarchinit-export-import import-us --skip-duplicates us.csv
  pyarchinit-export-import import-inventario --no-skip-duplicates inv.csv
  ```
- **Features**:
  - Optional site filtering for US and Inventario exports
  - Skip duplicates option (default: enabled)
  - Import statistics (imported, skipped, errors)
  - Comprehensive error reporting

### Multi-User Authentication (v1.0.8)

Complete authentication system with role-based access control for Web and API interfaces.

#### User Roles

| Role | Permissions | Description |
|------|-------------|-------------|
| **Admin** | Full access + user management | Can create/edit/delete data and manage users |
| **Operator** | Create, Read, Update, Delete data | Can modify archaeological data but not users |
| **Viewer** | Read-only access | Can view data but cannot modify |

#### Setup Authentication

1. **Install with authentication support**:
   ```bash
   pip install 'pyarchinit-mini[auth]'
   # or
   pip install 'pyarchinit-mini[all]'
   ```

2. **Create users table and default admin**:
   ```bash
   python -m pyarchinit_mini.scripts.setup_auth
   ```

   This creates:
   - Users table in database
   - Default admin user (username: `admin`, password: `admin`)

3. **Change default password** (IMPORTANT):
   ```bash
   # Login to web interface at http://localhost:5001/auth/login
   # Navigate to Users → Edit admin user → Change password
   ```

#### Web Interface Authentication

- **Login page**: `http://localhost:5001/auth/login`
- **Default credentials**: username=`admin`, password=`admin`
- **User management**: Admin users can create/edit/delete users via the Users menu
- **Protected routes**: All web pages require authentication
- **Session management**: Uses Flask-Login with secure session cookies

#### API Authentication

- **JWT tokens**: Use `POST /api/auth/login` to get access token
- **Token usage**: Include in `Authorization: Bearer <token>` header
- **Token expiration**: 30 minutes (configurable)

Example:
```bash
# Get token
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=admin&password=admin"

# Use token
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/sites
```

#### User Management

Admins can manage users via:
- **Web Interface**: Users menu (admin only)
- **API Endpoints**:
  - `POST /api/auth/register` - Create user (admin only)
  - `GET /api/auth/users` - List all users (admin only)
  - `PUT /api/auth/users/{id}` - Update user (admin only)
  - `DELETE /api/auth/users/{id}` - Delete user (admin only)

#### Permissions

| Permission | Admin | Operator | Viewer |
|------------|-------|----------|--------|
| View data | ✓ | ✓ | ✓ |
| Create data | ✓ | ✓ | ✗ |
| Edit data | ✓ | ✓ | ✗ |
| Delete data | ✓ | ✓ | ✗ |
| Manage users | ✓ | ✗ | ✗ |
| Export data | ✓ | ✓ | ✓ |
| Import data | ✓ | ✓ | ✗ |

---

## 💾 Database Management

### Why `~/.pyarchinit_mini`?
- **Persistence**: Data survives virtualenv removal
- **Easy Backup**: Single directory to backup
- **Multi-Project**: Same database accessible from different virtualenvs
- **Standard Convention**: Follows Unix/Linux conventions

### Database Options

#### SQLite (Default)
```bash
# Automatic setup
pyarchinit-mini-setup
```

Database created at: `~/.pyarchinit_mini/data/pyarchinit_mini.db`

#### PostgreSQL
```yaml
# config.yaml
database:
  url: "postgresql://user:password@localhost:5432/pyarchinit"
```

#### Upload Existing Database
Use the web interface:
1. Navigate to **Database** → **Upload Database**
2. Select your `.db` file from PyArchInit Desktop
3. Database is validated and copied to `~/.pyarchinit_mini/databases/`

---

## 🧪 Development

### Run from Source
```bash
git clone https://github.com/pyarchinit/pyarchinit-mini.git
cd pyarchinit-mini
pip install -e '.[dev]'
```

### Run Tests
```bash
pytest
pytest --cov=pyarchinit_mini
```

### Code Quality
```bash
black pyarchinit_mini/
isort pyarchinit_mini/
flake8 pyarchinit_mini/
mypy pyarchinit_mini/
```

---

## 📖 Documentation

- **API Docs**: http://localhost:8000/docs (after starting API server)
- **User Guide**: See `docs/` directory
- **CHANGELOG**: See `CHANGELOG.md`
- **Quick Start**: See `QUICK_START.md`

---

## 🐛 Troubleshooting

### Command Not Found After Installation
```bash
# Verify installation
pip show pyarchinit-mini

# On Linux/Mac, ensure pip bin directory is in PATH
export PATH="$HOME/.local/bin:$PATH"

# On Windows, commands are in:
# C:\Users\<username>\AppData\Local\Programs\Python\PythonXX\Scripts\
```

### Database Not Found
```bash
# Re-run setup
pyarchinit-mini-setup

# Or manually specify database URL
export DATABASE_URL="sqlite:///path/to/your/database.db"
```

### Tkinter Not Available (Linux)
```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora/RHEL
sudo dnf install python3-tkinter

# Arch Linux
sudo pacman -S tk
```

### Graphviz Not Found
```bash
# macOS
brew install graphviz

# Ubuntu/Debian
sudo apt-get install graphviz

# Windows
# Download from https://graphviz.org/download/
```

### Port Already in Use
```bash
# Change web interface port
export PYARCHINIT_WEB_PORT=5002
pyarchinit-web

# Change API port
export PYARCHINIT_API_PORT=8001
pyarchinit-api
```

---

## 🗺️ Roadmap

### Recently Completed (v1.1.5)
- [x] **EM_palette Node Styling** - Automatic colors and shapes based on `unita_tipo` (US, USM, USD, USV, USV/s)
- [x] **Archaeological Metadata** - Node descriptions with `d_stratigrafica` + `d_interpretativa` visible in yEd
- [x] **Clean Edge Display** - Edges without text labels, relationship types in tooltips
- [x] **PyArchInit Edge Convention** - Contemporary (no arrow), stratigraphic (arrow), negative (dashed)
- [x] **GraphML Description Field** - Proper injection into yEd `<data key="d5">` element
- [x] **Transitive Reduction** - Automatic removal of redundant stratigraphic relationships

### Completed in v1.1.3
- [x] **GraphML Converter** - Export Harris Matrix to yEd Graph Editor compatible format
- [x] **Multi-Interface Export** - Python API, CLI, REST API, Web UI, Desktop GUI support
- [x] **Period Preservation** - Automatic archaeological periods with color coding
- [x] **Flexible Grouping** - Period+area, period, area, or no grouping modes
- [x] **yEd Template** - Custom template (EM_palette.graphml) for consistent styling
- [x] **Standalone Library** - Reusable in other projects via pip install

### Completed in v1.1.2
- [x] **Mobile & Tablet Optimization** - Complete responsive design for phones and tablets
- [x] **Touch-Friendly Interface** - 44px minimum button height (iOS/Android guidelines)
- [x] **Mobile Card View** - Tables converted to cards on mobile (< 768px)
- [x] **Responsive Breakpoints** - Mobile (<768px), Tablet (768-991px), Desktop (≥992px)
- [x] **iOS/Android Optimized** - 16px font prevents auto-zoom, optimized touch targets
- [x] **Print Styles** - Clean print layout for reports

### Completed in v1.1.1
- [x] **Full Edit Functionality** - Complete edit support for Sites, US, and Inventario in Web interface
- [x] **37 Inventario Fields Editable** - All 37 fields across 8 tabs fully editable
- [x] **49 US Fields Editable** - All 49 fields across 6 tabs fully editable
- [x] **Form Pre-population** - Forms automatically filled with existing data for editing
- [x] **Session Management Fix** - Resolved SQLAlchemy detached instance errors

### Completed in v1.1.0
- [x] **Analytics Dashboard** - Interactive charts and data visualization
- [x] **8 Chart Types** - Pie, bar, horizontal bar, and doughnut charts
- [x] **Geographic Analysis** - Sites distribution by region and province
- [x] **Chronological Analysis** - US distribution by period
- [x] **Typological Analysis** - US and inventory items by type
- [x] **Conservation Analysis** - Inventory items by conservation state
- [x] **Multi-Interface Charts** - Web UI (Chart.js) and Desktop GUI (matplotlib)

### Completed in v1.0.9
- [x] **Real-time collaboration** - WebSocket support with Flask-SocketIO
- [x] **Live notifications** - Toast notifications for all CRUD operations
- [x] **Online user presence** - See who's currently connected
- [x] **Activity tracking** - Real-time updates when users create/edit/delete data
- [x] **User join/leave events** - Team collaboration awareness

### Completed in v1.0.8
- [x] **Multi-user authentication** - Role-based access control (Admin, Operator, Viewer)
- [x] **JWT authentication** - Secure API access with JSON Web Tokens
- [x] **User management** - Admin interface for creating/editing/deleting users
- [x] **Protected routes** - All web routes require authentication
- [x] **Password security** - Bcrypt hashing for secure password storage

### Completed in v1.0.7
- [x] **Export to Excel/CSV** - Sites, US, Inventario export
- [x] **Batch import from CSV** - With validation and duplicate handling
- [x] **Multi-interface export/import** - Web UI, Desktop GUI, and CLI

### Upcoming Features
- [ ] Docker containerization
- [ ] Cloud deployment guides
- [ ] Advanced search and filtering
- [ ] Offline mode support

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
git clone https://github.com/pyarchinit/pyarchinit-mini.git
cd pyarchinit-mini
pip install -e '.[dev]'
pre-commit install  # Optional: install pre-commit hooks
```

---

## 📄 License

This project is licensed under the GNU General Public License v2.0 - see the [LICENSE](LICENSE) file for details.

---

## 💬 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/pyarchinit/pyarchinit-mini/issues)
- **Email**: enzo.ccc@gmail.com
- **PyPI**: [pypi.org/project/pyarchinit-mini](https://pypi.org/project/pyarchinit-mini/)

---

## 🙏 Acknowledgments

- **PyArchInit Team**: Original desktop application developers
- **Archaeological Community**: Feedback and feature requests
- **Open Source Contributors**: Libraries and tools that make this possible

---


**Made with ❤️ for the Archaeological Community**