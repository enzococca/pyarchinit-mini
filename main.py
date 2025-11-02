#!/usr/bin/env python3
"""
Main entry point for PyArchInit-Mini API server
"""
import uvicorn
from pyarchinit_mini.api import create_app
from pyarchinit_mini.api.dependencies import init_database
import os

# Initialize database at module level for reload to work
database_url = os.getenv("DATABASE_URL", "sqlite:///./pyarchinit_mini.db")

print(f"🗄️  Initializing database: {database_url}")
try:
    init_database(database_url)
    print("✅ Database initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize database: {e}")

# Create FastAPI application at module level
app = create_app(database_url)

def main():
    """Main function to start the API server"""
    
    # Configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "true").lower() == "true"
    
    print(f"🚀 Starting PyArchInit-Mini API server")
    print(f"📍 Server URL: http://{host}:{port}")
    print(f"📖 API Documentation: http://{host}:{port}/docs")
    print(f"🔄 Auto-reload: {reload}")
    
    # Start server
    try:
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        return 1

if __name__ == "__main__":
    exit(main())