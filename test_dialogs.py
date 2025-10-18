#!/usr/bin/env python3
"""
Test that dialog classes can be imported and instantiated
"""

import os
import sys
import tkinter as tk

# Set test database
os.environ["DATABASE_URL"] = "sqlite:///./test_dialogs.db"

def test_dialog_imports():
    """Test that all dialog classes can be imported"""
    print("🧪 Testing dialog class imports...")
    
    try:
        from desktop_gui.dialogs import (
            SiteDialog,
            USDialog,
            InventarioDialog,
            HarrisMatrixDialog,
            PDFExportDialog,
            MediaManagerDialog,
            StatisticsDialog
        )
        
        print("✅ All dialog classes imported successfully")
        
        # Test that they are actually classes
        assert callable(SiteDialog), "SiteDialog is not callable"
        assert callable(USDialog), "USDialog is not callable"
        assert callable(InventarioDialog), "InventarioDialog is not callable"
        
        print("✅ All dialog classes are callable")
        return True
        
    except Exception as e:
        print(f"❌ Dialog import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dialog_creation():
    """Test that dialogs can be created (without showing them)"""
    print("\n🧪 Testing dialog instantiation...")
    
    try:
        # Create a root window (required for dialogs)
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        
        # Initialize database and services
        from pyarchinit_mini.database.connection import DatabaseConnection
        from pyarchinit_mini.database.manager import DatabaseManager
        from pyarchinit_mini.services.site_service import SiteService
        from pyarchinit_mini.services.us_service import USService
        from pyarchinit_mini.services.inventario_service import InventarioService
        from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator
        from pyarchinit_mini.harris_matrix.matrix_visualizer import MatrixVisualizer
        from pyarchinit_mini.pdf_export.pdf_generator import PDFGenerator
        from pyarchinit_mini.media_manager.media_handler import MediaHandler
        
        db_conn = DatabaseConnection.sqlite(":memory:")
        db_conn.create_tables()
        db_manager = DatabaseManager(db_conn)
        
        site_service = SiteService(db_manager)
        us_service = USService(db_manager)
        inventario_service = InventarioService(db_manager)
        matrix_generator = HarrisMatrixGenerator(db_manager)
        matrix_visualizer = MatrixVisualizer()
        pdf_generator = PDFGenerator()
        media_handler = MediaHandler()
        
        # Import dialog classes
        from desktop_gui.dialogs import (
            StatisticsDialog,
            MediaManagerDialog,
            HarrisMatrixDialog
        )
        
        print("✅ Services initialized for dialog testing")
        
        # Test dialog creation (but don't show them)
        # Note: We only test dialogs that don't require additional parameters
        
        # Test StatisticsDialog
        stats_dialog = StatisticsDialog(root, site_service, us_service, inventario_service)
        print("✅ StatisticsDialog created successfully")
        stats_dialog.dialog.destroy()
        
        # Test MediaManagerDialog
        media_dialog = MediaManagerDialog(root, media_handler)
        print("✅ MediaManagerDialog created successfully")
        media_dialog.dialog.destroy()
        
        # Test HarrisMatrixDialog
        sites = []  # Empty sites list for test
        harris_dialog = HarrisMatrixDialog(root, matrix_generator, matrix_visualizer, sites)
        print("✅ HarrisMatrixDialog created successfully")
        harris_dialog.dialog.destroy()
        
        # Cleanup
        db_conn.close()
        root.destroy()
        
        print("✅ All tested dialogs created and destroyed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Dialog creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run dialog tests"""
    print("🧪 PyArchInit-Mini Dialog Tests")
    print("=" * 40)
    
    success1 = test_dialog_imports()
    success2 = test_dialog_creation()
    
    print("\n" + "=" * 40)
    if success1 and success2:
        print("🎉 All dialog tests passed!")
        return 0
    else:
        print("❌ Some dialog tests failed")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)