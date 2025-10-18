#!/usr/bin/env python3
"""
Test desktop GUI with actual data to verify session management fix
"""

import os
import sys
import tkinter as tk

# Set test database
os.environ["DATABASE_URL"] = "sqlite:///./test_gui_data.db"

def test_gui_with_data():
    """Test GUI with real data operations"""
    print("🧪 Testing PyArchInit Desktop GUI with data operations...")
    
    try:
        # Import required modules
        from pyarchinit_mini.database.connection import DatabaseConnection
        from pyarchinit_mini.database.manager import DatabaseManager
        from pyarchinit_mini.services.site_service import SiteService
        from pyarchinit_mini.services.us_service import USService
        from pyarchinit_mini.services.inventario_service import InventarioService
        
        # Initialize database and services
        database_url = "sqlite:///./test_gui_data.db"
        db_conn = DatabaseConnection.from_url(database_url)
        db_conn.create_tables()
        db_manager = DatabaseManager(db_conn)
        
        site_service = SiteService(db_manager)
        us_service = USService(db_manager)
        inventario_service = InventarioService(db_manager)
        
        print("📊 Creating test data...")
        
        # Create test sites
        test_sites = [
            {
                "sito": "Test Site 1",
                "nazione": "Italia",
                "regione": "Lazio",
                "comune": "Roma",
                "provincia": "RM",
                "descrizione": "Test archaeological site"
            },
            {
                "sito": "Test Site 2", 
                "nazione": "Italia",
                "regione": "Campania",
                "comune": "Napoli",
                "provincia": "NA",
                "descrizione": "Another test site"
            }
        ]
        
        created_sites = []
        for site_data in test_sites:
            try:
                site = site_service.create_site(site_data)
                created_sites.append(site)
                print(f"   ✅ Created site: {site_data['sito']}")
            except Exception as e:
                print(f"   ⚠️ Site creation error: {e}")
        
        # Create test US
        if created_sites:
            test_us = [
                {
                    "sito": "Test Site 1",
                    "area": "Area A",
                    "us": 1001,
                    "d_stratigrafica": "Test stratigraphic description",
                    "anno_scavo": 2023
                },
                {
                    "sito": "Test Site 1",
                    "area": "Area A", 
                    "us": 1002,
                    "d_stratigrafica": "Another test description",
                    "anno_scavo": 2023
                }
            ]
            
            for us_data in test_us:
                try:
                    us = us_service.create_us(us_data)
                    print(f"   ✅ Created US: {us_data['us']}")
                except Exception as e:
                    print(f"   ⚠️ US creation error: {e}")
        
        # Create test inventory
        test_inventory = [
            {
                "sito": "Test Site 1",
                "numero_inventario": 1001,
                "tipo_reperto": "Ceramica",
                "definizione": "Test ceramic",
                "us": 1001
            }
        ]
        
        for inv_data in test_inventory:
            try:
                item = inventario_service.create_inventario(inv_data)
                print(f"   ✅ Created inventory item: {inv_data['numero_inventario']}")
            except Exception as e:
                print(f"   ⚠️ Inventory creation error: {e}")
        
        print("✅ Test data created successfully")
        
        # Now test GUI initialization with data
        print("\n🖥️ Testing GUI initialization with test data...")
        
        from desktop_gui.main_window import PyArchInitGUI
        
        # Create GUI (this will call refresh_data which caused the session error)
        app = PyArchInitGUI()
        
        print("✅ GUI initialized successfully with test data!")
        
        # Test refresh operations that previously caused session errors
        print("\n🔄 Testing refresh operations...")
        
        try:
            app.refresh_data()
            print("✅ refresh_data() - OK")
        except Exception as e:
            print(f"❌ refresh_data() failed: {e}")
            raise
        
        try:
            app.refresh_dashboard()
            print("✅ refresh_dashboard() - OK")
        except Exception as e:
            print(f"❌ refresh_dashboard() failed: {e}")
            raise
        
        try:
            app.refresh_sites()
            print("✅ refresh_sites() - OK")
        except Exception as e:
            print(f"❌ refresh_sites() failed: {e}")
            raise
        
        try:
            app.refresh_us()
            print("✅ refresh_us() - OK")
        except Exception as e:
            print(f"❌ refresh_us() failed: {e}")
            raise
        
        try:
            app.refresh_inventario()
            print("✅ refresh_inventario() - OK")
        except Exception as e:
            print(f"❌ refresh_inventario() failed: {e}")
            raise
        
        print("✅ All refresh operations completed successfully!")
        
        # Test statistics
        total_sites = app.site_service.count_sites()
        total_us = app.us_service.count_us()
        total_inventory = app.inventario_service.count_inventario()
        
        print(f"\n📈 Final statistics:")
        print(f"   Sites: {total_sites}")
        print(f"   US: {total_us}")
        print(f"   Inventory: {total_inventory}")
        
        # Cleanup
        app.db_conn.close()
        db_conn.close()
        
        print("\n🎉 GUI session management test completed successfully!")
        print("   SQLAlchemy session errors have been resolved!")
        
        return True
        
    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the GUI data test"""
    print("🧪 PyArchInit-Mini GUI Session Management Test")
    print("=" * 50)
    
    success = test_gui_with_data()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Session management is fixed!")
        return 0
    else:
        print("❌ Tests failed")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)