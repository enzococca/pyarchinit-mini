#!/usr/bin/env python3
"""
Test script for improved Harris Matrix dialog with high resolution and pan/zoom
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
from desktop_gui.dialogs import HarrisMatrixDialog

def test_improved_harris_dialog():
    """Test the improved Harris Matrix dialog with PyArchInit visualizer"""
    
    print("🎨 Testing Improved Harris Matrix Dialog")
    print("=" * 50)
    
    # Initialize database components
    db_path = 'pyarchinit_mini.db'
    connection = DatabaseConnection(f'sqlite:///{db_path}')
    db_manager = DatabaseManager(connection)
    us_service = USService(db_manager)
    site_service = SiteService(db_manager)
    
    # Initialize matrix components
    generator = HarrisMatrixGenerator(db_manager, us_service)
    visualizer = PyArchInitMatrixVisualizer()
    
    # Get sites
    sites = site_service.get_all_sites(size=100)
    if not sites:
        print("❌ No sites found in database")
        return
        
    print(f"📊 Found {len(sites)} sites in database")
    
    # Create root window
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    print("🏛️ Opening improved Harris Matrix Dialog...")
    print("✨ New features:")
    print("   • High resolution visualization (600 DPI)")
    print("   • Layout selector (period_area, period, area, none)")
    print("   • Zoom controls (🔍+ 🔍- ⌂)")
    print("   • Pan/zoom navigation toolbar")
    print("   • Larger window (1200x900)")
    print("   • PyArchInit-style Graphviz rendering")
    
    try:
        # Create improved Harris Matrix Dialog
        dialog = HarrisMatrixDialog(
            parent=root,
            matrix_generator=generator,
            matrix_visualizer=visualizer,
            sites=sites,
            site_service=site_service,
            us_service=us_service,
            db_manager=db_manager
        )
        
        print("✅ Improved Harris Matrix Dialog opened successfully!")
        print("")
        print("🚀 Testing instructions:")
        print("   1. Select 'Sito Archeologico di Esempio' from dropdown")
        print("   2. Click 'Genera Matrix' to create high-res visualization")
        print("   3. Try different layouts from the Layout dropdown")
        print("   4. Use zoom controls: 🔍+ (zoom in), 🔍- (zoom out), ⌂ (fit)")
        print("   5. Use the navigation toolbar for pan/zoom")
        print("   6. Test 'Esporta' for multi-format export")
        print("   7. Close dialog to exit test")
        
        # Start GUI event loop
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error opening improved dialog: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_improved_harris_dialog()