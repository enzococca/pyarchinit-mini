#!/usr/bin/env python3
"""
Test per verificare che il Media Manager funzioni correttamente
"""

import sys
import os
sys.path.insert(0, '.')

import tkinter as tk
from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.media_manager.media_handler import MediaHandler
from desktop_gui.dialogs import MediaManagerDialog

def test_media_manager():
    """Test Media Manager Dialog"""
    
    print("🎬 Testing Media Manager Dialog Fix")
    print("=" * 40)
    
    try:
        # Initialize database components
        db_path = 'pyarchinit_mini.db'
        connection = DatabaseConnection(f'sqlite:///{db_path}')
        db_manager = DatabaseManager(connection)
        media_handler = MediaHandler()
        
        # Create root window
        root = tk.Tk()
        root.withdraw()  # Hide main window
        
        print("📁 Opening Media Manager Dialog...")
        
        # Test dialog creation with correct parameters
        dialog = MediaManagerDialog(root, media_handler)
        
        print("✅ Media Manager Dialog opened successfully!")
        print("   No more 'callback' parameter error")
        print("")
        print("🚀 Media Manager is ready - close the dialog to exit test")
        
        # Start GUI event loop
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_media_manager()