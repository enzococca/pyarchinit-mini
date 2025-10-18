# PyArchInit-Mini Interfaces Guide

This document provides a comprehensive guide to all available interfaces in PyArchInit-Mini.

## 🎯 Overview

PyArchInit-Mini provides **four complete interfaces** for archaeological data management:

1. **🚀 FastAPI REST Server** - Scalable API with automatic documentation
2. **🌐 Flask Web Interface** - Modern responsive web application  
3. **🖥️ Tkinter Desktop GUI** - Full-featured desktop application
4. **💻 Rich CLI Interface** - Interactive command-line interface

## 🚀 FastAPI REST Server

### Features
- RESTful API with OpenAPI/Swagger documentation
- Automatic request/response validation with Pydantic
- Async support for high performance
- CORS enabled for web applications
- Comprehensive error handling

### Quick Start
```bash
cd pyarchinit-mini
python main.py
```

### Access Points
- **API Base**: `http://localhost:8000/api/v1/`
- **Documentation**: `http://localhost:8000/docs`
- **Alternative Docs**: `http://localhost:8000/redoc`

### Key Endpoints
```http
GET    /api/v1/sites/           # List sites
POST   /api/v1/sites/           # Create site
GET    /api/v1/sites/{id}       # Get site by ID
PUT    /api/v1/sites/{id}       # Update site
DELETE /api/v1/sites/{id}       # Delete site

GET    /api/v1/us/              # List stratigraphic units
POST   /api/v1/us/              # Create US
GET    /api/v1/us/{id}          # Get US by ID

GET    /api/v1/inventario/      # List inventory items
POST   /api/v1/inventario/      # Create inventory item
```

### Use Cases
- Third-party integrations
- Mobile app backends
- Microservices architecture
- API-first development
- Automated data import/export

## 🌐 Flask Web Interface

### Features
- Bootstrap-based responsive design
- Interactive forms with validation
- Dashboard with statistics
- Harris Matrix visualization
- PDF export functionality
- Media upload and management
- Real-time search and filtering

### Quick Start
```bash
cd pyarchinit-mini
python web_interface/app.py
```

### Access
- **Web Interface**: `http://localhost:5000`

### Main Sections
- **Dashboard**: Overview with statistics and quick actions
- **Sites**: Complete site management with search
- **US**: Stratigraphic units with advanced filtering
- **Inventory**: Material catalog with type filtering
- **Tools**: Harris Matrix, PDF export, media management

### Use Cases
- Team collaboration
- Remote data entry
- Client presentations
- Field data collection via tablets
- Training and education

## 🖥️ Tkinter Desktop GUI

### Features
- Native desktop application
- Tabbed interface design
- Advanced dialog forms
- Real-time data refresh
- Comprehensive CRUD operations
- Integrated Harris Matrix tools
- PDF report generation
- Media file management
- Statistics and analytics

### Quick Start
```bash
cd pyarchinit-mini
python desktop_gui/gui_app.py
```

### Interface Components

#### Main Window
- **Dashboard Tab**: Statistics cards and recent activity
- **Sites Tab**: Site list with search and management
- **US Tab**: Stratigraphic units with filtering
- **Inventory Tab**: Material inventory management

#### Dialog Windows
- **Site Dialog**: Create/edit archaeological sites
- **US Dialog**: Manage stratigraphic units with extensive form
- **Inventory Dialog**: Handle material inventory items
- **Harris Matrix Dialog**: Generate and export matrix visualizations
- **PDF Export Dialog**: Create comprehensive reports
- **Media Manager**: Upload and organize multimedia files
- **Statistics Dialog**: View detailed analytics

### Use Cases
- Power users and archaeologists
- Offline data entry and analysis
- Complex data relationships
- Professional report generation
- Detailed data validation

## 💻 Rich CLI Interface

### Features
- Interactive menus with colors and formatting
- Data tables and statistics display
- Guided data entry forms
- Harris Matrix generation
- PDF export capabilities
- Real-time search and filtering
- Database configuration support

### Quick Start
```bash
cd pyarchinit-mini
python cli_interface/cli_app.py
```

### Navigation
- Use numbers to select menu options
- Press `0` to go back to previous menu
- Press `Ctrl+C` to exit at any time
- Follow prompts for data entry

### Main Menus
1. **Site Management**: Create, view, edit, delete sites
2. **US Management**: Handle stratigraphic units
3. **Inventory Management**: Manage material catalog
4. **Harris Matrix**: Generate and export matrices
5. **Statistics**: View reports and analytics
6. **PDF Export**: Create archaeological reports
7. **Database Config**: Configure connections
8. **Help**: User guidance and support

### Use Cases
- Server administration
- Batch operations
- Automation and scripting
- Quick data queries
- System maintenance

## 🗄️ Database Configuration

All interfaces support both SQLite and PostgreSQL databases through environment variables:

### SQLite (Default)
```bash
export DATABASE_URL="sqlite:///./pyarchinit_mini.db"
```

### PostgreSQL
```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/pyarchinit"
```

## 🔧 Dependencies

### Core Requirements (All Interfaces)
```bash
pip install sqlalchemy psycopg2-binary pydantic
```

### Web Interface
```bash
pip install flask flask-wtf wtforms jinja2
```

### Desktop GUI  
```bash
pip install tkinter pillow
```

### CLI Interface
```bash
pip install click rich inquirer
```

### Advanced Features
```bash
pip install networkx matplotlib reportlab
```

### Complete Installation
```bash
pip install -r requirements.txt
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_interfaces.py
```

This verifies all interfaces can be imported and initialized correctly.

## 📊 Interface Comparison

| Feature | API Server | Web Interface | Desktop GUI | CLI Interface |
|---------|------------|---------------|-------------|---------------|
| **Accessibility** | Remote | Browser | Local | Terminal |
| **User Experience** | Programmatic | Modern Web | Native Desktop | Text-based |
| **Data Entry** | JSON/API | Forms | Dialogs | Prompts |
| **Visualization** | None | Basic | Advanced | Tables |
| **Harris Matrix** | JSON | Web View | Interactive | Text Export |
| **PDF Export** | Binary | Download | Save Dialog | File Output |
| **Media Handling** | Upload API | Web Upload | File Browser | File Paths |
| **Multi-user** | Yes | Yes | No | No |
| **Offline Use** | No | No | Yes | Yes |
| **Automation** | Yes | Limited | No | Yes |

## 🎯 Choosing the Right Interface

### Use FastAPI Server when:
- Building integrations with other systems
- Developing mobile applications
- Need API-first architecture
- Want to separate frontend/backend
- Require high performance and scalability

### Use Web Interface when:
- Working with multiple users
- Need remote access capability
- Want modern, responsive design
- Sharing data with stakeholders
- Training new users

### Use Desktop GUI when:
- Working offline frequently
- Need advanced data entry forms
- Want native OS integration
- Require complex data relationships
- Professional report generation

### Use CLI Interface when:
- Administering systems
- Running batch operations
- Automating workflows
- Quick data queries
- Minimal resource usage

## 📚 Additional Resources

- **API Documentation**: Available at `/docs` endpoint when running API server
- **Example Scripts**: See `examples/` directory
- **Test Suite**: Run `python test_interfaces.py`
- **Source Code**: Each interface in its respective directory
- **Issue Tracker**: GitHub Issues for bug reports and feature requests

---

*PyArchInit-Mini provides the flexibility to choose the right interface for your archaeological data management needs.*