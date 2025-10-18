# PyArchInit-Mini Quick Start

## 🚀 Installation

### Prerequisites
- Python 3.8+
- pip

### Install Dependencies

```bash
cd pyarchinit-mini
pip install -r requirements.txt
```

## 🏃‍♂️ Quick Test

### 1. Run Example Script
Test the core functionality:

```bash
python example_usage.py
```

This will:
- Create a SQLite database
- Add sample archaeological data
- Demonstrate CRUD operations
- Show search functionality

### 2. Start API Server
Launch the REST API server:

```bash
python main.py
```

Then open your browser to:
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 📖 API Usage Examples

### Create a Site
```bash
curl -X POST "http://localhost:8000/api/v1/sites/" \
  -H "Content-Type: application/json" \
  -d '{
    "sito": "My Archaeological Site",
    "nazione": "Italia",
    "regione": "Lazio",
    "comune": "Roma"
  }'
```

### List Sites
```bash
curl "http://localhost:8000/api/v1/sites/"
```

### Create a Stratigraphic Unit (US)
```bash
curl -X POST "http://localhost:8000/api/v1/us/" \
  -H "Content-Type: application/json" \
  -d '{
    "sito": "My Archaeological Site",
    "area": "A",
    "us": 1001,
    "d_stratigrafica": "Topsoil layer",
    "descrizione": "Modern surface layer"
  }'
```

### Create Inventory Item
```bash
curl -X POST "http://localhost:8000/api/v1/inventario/" \
  -H "Content-Type: application/json" \
  -d '{
    "sito": "My Archaeological Site",
    "numero_inventario": 1,
    "tipo_reperto": "Ceramica",
    "definizione": "Vaso",
    "descrizione": "Roman ceramic vessel fragment"
  }'
```

## 🗃️ Database Configuration

### SQLite (Default)
No configuration needed - automatically creates `pyarchinit_mini.db`

### PostgreSQL
Set environment variable:
```bash
export DATABASE_URL="postgresql://username:password@localhost:5432/pyarchinit"
python main.py
```

## 📚 Python Library Usage

```python
from pyarchinit_mini import DatabaseManager, SiteService
from pyarchinit_mini.database import DatabaseConnection

# Setup
db_conn = DatabaseConnection.sqlite("my_data.db")
db_manager = DatabaseManager(db_conn)
site_service = SiteService(db_manager)

# Create site
site = site_service.create_site({
    "sito": "Pompeii",
    "nazione": "Italia",
    "comune": "Pompei"
})

# Query sites
sites = site_service.get_all_sites()
```

## 🔧 Development

### Run Tests
```bash
pytest tests/
```

### Code Formatting
```bash
pip install black isort
black pyarchinit_mini/
isort pyarchinit_mini/
```

### Type Checking
```bash
pip install mypy
mypy pyarchinit_mini/
```

## 📞 Support

- 📧 Email: enzo.ccc@gmail.com
- 🐛 Issues: GitHub Issues
- 📖 Full Documentation: README.md

## 🎯 Next Steps

1. ✅ Test with sample data (`python example_usage.py`)
2. ✅ Explore API documentation (`python main.py` → http://localhost:8000/docs)
3. ✅ Integrate into your archaeological workflow
4. ✅ Consider publishing to PyPI for easier installation