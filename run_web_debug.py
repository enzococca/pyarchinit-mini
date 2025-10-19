#!/usr/bin/env python3
"""
Run web interface in debug mode with verbose logging
"""

import os
import sys

# Get absolute path to project root
project_root = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(project_root, 'pyarchinit_mini.db')

# Set environment variables
os.environ['PYARCHINIT_WEB_DEBUG'] = 'true'
os.environ['FLASK_ENV'] = 'development'
os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'

# Add web_interface to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'web_interface'))

print("=" * 60)
print("PyArchInit-Mini Web Interface - DEBUG MODE")
print("=" * 60)
print()
print("Server Configuration:")
print(f"  Host: 0.0.0.0")
print(f"  Port: 5001")
print(f"  Debug: ON")
print(f"  Database: {db_path}")
print(f"  Database exists: {os.path.exists(db_path)}")
print()
print("Login Credentials:")
print(f"  Username: admin")
print(f"  Password: admin")
print()
print("Access the web interface at:")
print(f"  http://localhost:5001/")
print(f"  http://localhost:5001/auth/login")
print()
print("=" * 60)
print()

# Import and run
from web_interface.app import create_app

app = create_app()

# Run with debug mode and verbose logging
app.run(
    debug=True,
    host='0.0.0.0',
    port=5001,
    use_reloader=True
)
