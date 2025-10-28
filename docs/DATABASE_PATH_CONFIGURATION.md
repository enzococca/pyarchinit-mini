# Database Path Configuration Guide

**Version**: 1.6.1
**Date**: 2025-10-28

## Problem Overview

PyArchInit-Mini can use **two different database locations**:

1. **Development Database** (PyCharm): `/Users/enzo/Documents/pyarchinit-mini-desk/pyarchinit_mini.db`
2. **User Database** (Installed package): `/Users/enzo/.pyarchinit_mini/data/pyarchinit_mini.db`

When you import Excel data, it goes to whichever database the application is configured to use. This causes confusion when working in PyCharm because data imported via GUI might go to the user database, while you're viewing the development database.

---

## How Database Path is Determined

### Web Interface (app.py)

The database path is determined in this order:

1. **Environment Variable** `DATABASE_URL` (highest priority)
2. **Default**: Project package directory `pyarchinit_mini.db`

```python
# From pyarchinit_mini/web_interface/app.py line 389-391
default_db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pyarchinit_mini.db')
default_db_url = f"sqlite:///{default_db_path}"
database_url = os.getenv("DATABASE_URL", default_db_url)
```

### Excel Import Routes

Excel import uses the **same database** as the web interface:

```python
# From web_interface/excel_import_routes.py line 131
db_url = current_app.config.get('CURRENT_DATABASE_URL')
```

---

## Solution: Configure DATABASE_URL for PyCharm

### Option 1: PyCharm Environment Variables (RECOMMENDED)

1. Open **Run → Edit Configurations**
2. Select your Flask app configuration (or create new Python configuration)
3. Find **Environment Variables** section
4. Click **+** to add:
   - **Name**: `DATABASE_URL`
   - **Value**: `sqlite:////Users/enzo/Documents/pyarchinit-mini-desk/pyarchinit_mini.db`
5. Click **OK** and run the configuration

### Option 2: Terminal Export (Temporary)

```bash
# Set environment variable for current shell session
export DATABASE_URL="sqlite:////Users/enzo/Documents/pyarchinit-mini-desk/pyarchinit_mini.db"

# Start Flask app
cd web_interface
python app.py
```

**Note**: This only works for the current terminal session.

### Option 3: .env File with python-dotenv (BEST for Teams)

1. Install python-dotenv:
   ```bash
   pip install python-dotenv
   ```

2. Use the provided `.env.development` file in project root

3. Add to beginning of `web_interface/app.py` (after imports):
   ```python
   from dotenv import load_dotenv
   load_dotenv('.env.development')
   ```

4. The DATABASE_URL will be automatically loaded

---

## Verification

### Check Current Database Path

When you start Flask, look for these log messages:

```
[FLASK] Current working directory: /Users/enzo/Documents/pyarchinit-mini-desk/web_interface
[FLASK] Using database: sqlite:////Users/enzo/Documents/pyarchinit-mini-desk/pyarchinit_mini.db
[FLASK] SQLite absolute path: /Users/enzo/Documents/pyarchinit-mini-desk/pyarchinit_mini.db
[FLASK] Database exists: True
```

### Verify Excel Import Uses Same Database

After importing Excel:

```bash
# Count records in development database
sqlite3 /Users/enzo/Documents/pyarchinit-mini-desk/pyarchinit_mini.db \
  "SELECT sito, COUNT(*) FROM us_table GROUP BY sito;"

# Should show your imported data (e.g., MetroC_AmbaAradam|65)
```

---

## SQLAlchemy text() Error

### Problem

You see this error when loading database in Gestione Database:

```
File non valido: Textual SQL expression 'SELECT name FROM sqlite_m...'
should be explicitly declared as text('SELECT name FROM sqlite_m...')
```

### Root Cause

SQLAlchemy 2.0 requires raw SQL queries to be wrapped in `text()` function.

### Fix Applied (v1.6.1)

All problematic queries have been fixed:

```python
# BEFORE (wrong)
session.execute('SELECT name FROM sqlite_master WHERE type="table"')

# AFTER (correct)
from sqlalchemy import text
session.execute(text('SELECT name FROM sqlite_master WHERE type="table"'))
```

**Fixed locations**:
- `pyarchinit_mini/web_interface/app.py:2108` - Database upload validation
- `pyarchinit_mini/web_interface/app.py:2168` - Connection test
- `pyarchinit_mini/web_interface/app.py:2197` - Get table list (SQLite)
- `pyarchinit_mini/web_interface/app.py:2200` - Get table list (PostgreSQL)
- `pyarchinit_mini/web_interface/app.py:2208` - Count rows

**Desktop GUI**: Already correct, no changes needed.

---

## Understanding the Two Databases

### Development Database (PyCharm)

**Location**: `/Users/enzo/Documents/pyarchinit-mini-desk/pyarchinit_mini.db`

**When Used**:
- Running Flask from PyCharm
- Running tests in PyCharm
- CLI commands run from project directory

**Pros**:
- Easy to delete/recreate
- Version controlled (if desired)
- Separate from user data

**Cons**:
- Not shared with installed package
- Must configure environment variable

### User Database (Installed Package)

**Location**: `/Users/enzo/.pyarchinit_mini/data/pyarchinit_mini.db`

**When Used**:
- Running installed package: `pyarchinit-mini-web`
- Desktop GUI app
- CLI commands from installed package

**Pros**:
- Persistent user data
- Shared across all interfaces
- Standard location

**Cons**:
- Hidden in home directory
- Can be harder to locate

---

## Best Practice for Development

1. **Always set DATABASE_URL** when working in PyCharm
2. **Check Flask startup logs** to verify correct database
3. **Use separate databases** for development vs. production
4. **Backup before schema changes** (especially id_us fixes)

### Example PyCharm Configuration

Create a PyCharm run configuration named "Flask Dev":

```
Script path: /Users/enzo/Documents/pyarchinit-mini-desk/web_interface/app.py
Working directory: /Users/enzo/Documents/pyarchinit-mini-desk/web_interface
Environment variables:
  DATABASE_URL=sqlite:////Users/enzo/Documents/pyarchinit-mini-desk/pyarchinit_mini.db
Python interpreter: (your venv)
```

---

## Database Management UI

### Load External Database in Web Interface

1. Go to **Admin → Database Management**
2. Click **Load Database**
3. Select database file
4. Enter description
5. Database is **copied** to `web_interface/databases/` folder
6. Does NOT change `CURRENT_DATABASE_URL`

### Connect to External Database

1. Go to **Admin → Database Management**
2. Click **Connect Database**
3. Enter connection details:
   - **SQLite**: Full path to .db file
   - **PostgreSQL**: Host, port, database, credentials
4. Connection is saved but does NOT change active database

**Important**: Loaded/connected databases are stored in `app.config['DATABASE_CONNECTIONS']` but the **active database** remains `CURRENT_DATABASE_URL`.

---

## Troubleshooting

### Problem: Excel import data not visible

**Symptom**: Import succeeds but data doesn't appear in US list.

**Cause**: Import went to different database than you're viewing.

**Solution**:
1. Check Flask startup logs for database path
2. Set DATABASE_URL environment variable
3. Restart Flask
4. Re-import Excel

### Problem: "File non valido" error when loading database

**Symptom**: SQLAlchemy text() error message.

**Cause**: Old version without text() fixes.

**Solution**: Update to v1.6.1 or later.

### Problem: Two different databases with same data

**Symptom**: Development and user databases diverged.

**Cause**: Working with both environments without DATABASE_URL set.

**Solution**:
```bash
# Copy development database to user location
cp /Users/enzo/Documents/pyarchinit-mini-desk/pyarchinit_mini.db \
   /Users/enzo/.pyarchinit_mini/data/pyarchinit_mini.db

# OR copy user database to development
cp /Users/enzo/.pyarchinit_mini/data/pyarchinit_mini.db \
   /Users/enzo/Documents/pyarchinit-mini-desk/pyarchinit_mini.db
```

---

## Database Switch GUI (New in v1.6.2)

### Overview

The web interface now includes a **Database Switch** feature that allows you to:
- View all available database connections
- See which database is currently active
- Switch between databases with one click
- No server restart required

### Using the Database Switcher

1. Go to **Admin → Database Management**
2. Scroll to **Connessioni Salvate** section
3. You'll see two default connections:
   - **Database Root (Progetto)**: `/path/to/pyarchinit-mini-desk/pyarchinit_mini.db`
   - **Database Package**: `/path/to/pyarchinit-mini-desk/pyarchinit_mini/pyarchinit_mini.db`
4. Active database is highlighted in green with "Attivo" badge
5. Click **Cambia** button to switch to another database

### Features

- **Visual Indicator**: Active database row is highlighted in green
- **Safety Check**: Connection is tested before switching
- **Confirmation Dialog**: Asks for confirmation before switching
- **Automatic Reinitialization**: All services are reinitialized with new database
- **Persistent Connections**: Database connections are saved in session

### Adding Custom Connections

You can add custom database connections:

1. **Upload SQLite Database**: Use "Carica Database SQLite" button
2. **Connect to PostgreSQL**: Use "Connetti Database" button
3. All connections appear in the table and can be switched to

### Technical Details

**Route**: `POST /admin/database/switch/<connection_name>`

**Process**:
1. Validates connection exists
2. Tests connection with `SELECT 1` query
3. Updates `app.config['CURRENT_DATABASE_URL']`
4. Reinitializes `DatabaseConnection` and `DatabaseManager`
5. Reinitializes all services (SiteService, USService, etc.)
6. Redirects back to database admin page

**Default Connections**: Automatically created at app startup with paths:
- Root database: `project_root/pyarchinit_mini.db`
- Package database: `project_root/pyarchinit_mini/pyarchinit_mini.db`

---

## Summary

✅ **Always configure DATABASE_URL in PyCharm** for consistent behavior
✅ **Check Flask logs** to verify database path on startup
✅ **Use .env.development** file for team development
✅ **Separate databases** for development vs. production
✅ **v1.6.1 fixes** all SQLAlchemy text() errors
✅ **v1.6.2 adds** Database Switch GUI for easy database switching

**For PyCharm development**, set this environment variable:
```
DATABASE_URL=sqlite:////Users/enzo/Documents/pyarchinit-mini-desk/pyarchinit_mini.db
```

**Or use the GUI**: Go to Admin → Database Management and click "Cambia" on the desired database.
