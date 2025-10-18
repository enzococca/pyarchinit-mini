#!/usr/bin/env python3
"""
Manual test for the desktop GUI to verify initialization
"""

import os
import sys

# Set test database
os.environ["DATABASE_URL"] = "sqlite:///./test_gui.db"

try:
    from desktop_gui.main_window import PyArchInitGUI
    
    print("🧪 Testing PyArchInit Desktop GUI initialization...")
    
    # Create GUI instance (this will initialize all components)
    app = PyArchInitGUI()
    
    print("✅ GUI initialized successfully!")
    print("🔍 Checking key components...")
    
    # Verify key attributes exist
    assert hasattr(app, 'root'), "Missing root window"
    assert hasattr(app, 'db_manager'), "Missing database manager"
    assert hasattr(app, 'current_site'), "Missing current_site variable"
    assert hasattr(app, 'status_text'), "Missing status_text variable"
    assert hasattr(app, 'notebook'), "Missing notebook widget"
    assert hasattr(app, 'site_service'), "Missing site service"
    
    print("✅ All key components present")
    
    # Test a basic service operation
    site_count = app.site_service.count_sites()
    print(f"📊 Current sites in database: {site_count}")
    
    # Cleanup
    app.db_conn.close()
    
    print("🎉 Desktop GUI test completed successfully!")
    
except Exception as e:
    print(f"❌ GUI test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)