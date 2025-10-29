"""
Desktop GUI package for PyArchInit-Mini

This package provides a complete Tkinter-based desktop interface for
archaeological data management including:

- Site management
- Stratigraphic units (US) management  
- Inventory management
- Harris Matrix generation and visualization
- PDF export capabilities
- Media file management
- Statistics and reporting

Main Components:
- main_window.py: Main application window with tabs and navigation
- dialogs.py: Dialog classes for data entry and specialized functions
- gui_app.py: Application launcher and dependency checker

Usage:
    from desktop_gui.gui_app import main
    main()

Or run directly:
    python desktop_gui/gui_app.py
"""

from pyarchinit_mini import __version__, __author__

# Import main classes for easier access
from .main_window import PyArchInitGUI
from .dialogs import (
    SiteDialog,
    USDialog, 
    InventarioDialog,
    HarrisMatrixDialog,
    PDFExportDialog,
    MediaManagerDialog,
    StatisticsDialog
)

__all__ = [
    'PyArchInitGUI',
    'SiteDialog',
    'USDialog',
    'InventarioDialog', 
    'HarrisMatrixDialog',
    'PDFExportDialog',
    'MediaManagerDialog',
    'StatisticsDialog'
]