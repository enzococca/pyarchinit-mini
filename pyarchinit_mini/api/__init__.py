"""
FastAPI REST API for PyArchInit-Mini
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .site import router as site_router
from .us import router as us_router
from .inventario import router as inventario_router

def create_app(database_url: str = None) -> FastAPI:
    """
    Create and configure FastAPI application
    
    Args:
        database_url: Database connection URL
        
    Returns:
        Configured FastAPI app
    """
    app = FastAPI(
        title="PyArchInit-Mini API",
        description="REST API for archaeological data management",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(site_router, prefix="/api/v1/sites", tags=["sites"])
    app.include_router(us_router, prefix="/api/v1/us", tags=["stratigraphic-units"])
    app.include_router(inventario_router, prefix="/api/v1/inventario", tags=["inventory"])
    
    # Store database URL in app state
    if database_url:
        app.state.database_url = database_url
    
    @app.get("/")
    async def root():
        return {
            "message": "PyArchInit-Mini API",
            "version": "0.1.0",
            "docs": "/docs"
        }
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    
    return app

__all__ = ["create_app"]