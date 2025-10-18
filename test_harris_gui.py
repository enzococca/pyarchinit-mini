#!/usr/bin/env python3
"""
Test script for Harris Matrix GUI functionality
"""

import sys
import os
sys.path.insert(0, '.')

import tkinter as tk
from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator
from pyarchinit_mini.harris_matrix.pyarchinit_visualizer import PyArchInitMatrixVisualizer
from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.services.us_service import USService
from pyarchinit_mini.services.site_service import SiteService
from desktop_gui.harris_matrix_editor import HarrisMatrixEditor

def test_harris_gui():
    """Test Harris Matrix GUI with sample data"""
    
    print("🎨 Testing Harris Matrix GUI")
    print("=" * 40)
    
    # Initialize database components
    db_path = 'pyarchinit_mini.db'
    connection = DatabaseConnection(f'sqlite:///{db_path}')
    db_manager = DatabaseManager(connection)
    us_service = USService(db_manager)
    site_service = SiteService(db_manager)
    
    # Initialize matrix components
    generator = HarrisMatrixGenerator(db_manager, us_service)
    visualizer = PyArchInitMatrixVisualizer()
    
    # Create root window
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    print("🏛️ Opening Harris Matrix Editor...")
    
    try:
        # Create Harris Matrix Editor
        editor = HarrisMatrixEditor(
            parent=root,
            matrix_generator=generator,
            matrix_visualizer=visualizer,
            site_service=site_service,
            us_service=us_service
        )
        
        print("✅ Harris Matrix Editor opened successfully!")
        print("📊 Features available:")
        print("   • PyArchInit-style Graphviz visualization")
        print("   • Period/Area/Phase grouping")
        print("   • All stratigraphic relationships (copre, taglia, riempie, etc.)")
        print("   • Hierarchical orthogonal layout")
        print("   • Matrix validation and statistics")
        print("   • Relationship management")
        print("")
        print("🚀 GUI is ready - close the Harris Matrix Editor window to exit")
        
        # Start GUI event loop
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error opening GUI: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_harris_gui()