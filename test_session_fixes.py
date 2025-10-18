#!/usr/bin/env python3
"""
Test script to verify SQLAlchemy session fixes
"""

import os
import tempfile
from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.services.site_service import SiteService
from pyarchinit_mini.services.us_service import USService
from pyarchinit_mini.services.inventario_service import InventarioService

def test_session_fixes():
    """Test that all session fixes work correctly"""
    print("🧪 Testing SQLAlchemy session fixes...")
    
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
        db_path = temp_db.name
    
    try:
        # Initialize database
        db_connection = DatabaseConnection.sqlite(db_path)
        db_connection.initialize_database()
        
        db_manager = DatabaseManager(db_connection)
        
        # Initialize services
        site_service = SiteService(db_manager)
        us_service = USService(db_manager)
        inventario_service = InventarioService(db_manager)
        
        print("✅ Database and services initialized")
        
        # Test 1: Site creation and DTO retrieval
        print("\n🔍 Test 1: Site operations with DTOs")
        
        site_data = {
            "sito": "Test_Site_2024",
            "nazione": "Italia",
            "regione": "Lazio",
            "comune": "Roma",
            "descrizione": "Sito di test per verifica sessioni"
        }
        
        # Create site
        site_dto = site_service.create_site_dto(site_data)
        print(f"✅ Site created: {site_dto.sito}")
        
        # Get site as DTO (should not have session issues)
        site_dto_retrieved = site_service.get_site_dto_by_id(site_dto.id_sito)
        print(f"✅ Site retrieved as DTO: {site_dto_retrieved.sito}")
        
        # Update site using DTO method (should not have session issues)
        update_data = {"descrizione": "Descrizione aggiornata senza errori di sessione"}
        updated_site_dto = site_service.update_site_dto(site_dto.id_sito, update_data)
        print(f"✅ Site updated via DTO: {updated_site_dto.descrizione}")
        
        # Test 2: US operations with DTOs
        print("\n🔍 Test 2: US operations with DTOs")
        
        us_data = {
            "sito": site_dto.sito,
            "area": "A",
            "us": 1001,
            "d_stratigrafica": "Strato di test",
            "d_interpretativa": "Test per verifica sessioni"
        }
        
        # Create US using DTO version
        us_dto = us_service.create_us_dto(us_data)
        print(f"✅ US created: US {us_dto.us}")
        
        # Get US as DTO (test retrieval)
        us_dto_retrieved = us_service.get_us_dto_by_id(us_dto.id_us)
        print(f"✅ US retrieved as DTO: US {us_dto_retrieved.us}")
        
        # Update US using DTO method
        us_update_data = {"d_stratigrafica": "Strato aggiornato senza errori"}
        updated_us_dto = us_service.update_us_dto(us_dto.id_us, us_update_data)
        print(f"✅ US updated via DTO: {updated_us_dto.d_stratigrafica}")
        
        # Test 3: Inventario operations with DTOs
        print("\n🔍 Test 3: Inventario operations with DTOs")
        
        inv_data = {
            "sito": site_dto.sito,
            "numero_inventario": 1001,
            "area": "A",
            "us": 1001,
            "tipo_reperto": "Ceramica",
            "definizione": "Test reperto",
            "descrizione": "Reperto di test per verifica sessioni"
        }
        
        # Create inventario using DTO version
        inv_dto = inventario_service.create_inventario_dto(inv_data)
        print(f"✅ Inventario created: {inv_dto.numero_inventario}")
        
        # Get inventario as DTO (test retrieval)
        inv_dto_retrieved = inventario_service.get_inventario_dto_by_id(inv_dto.id_invmat)
        print(f"✅ Inventario retrieved as DTO: {inv_dto_retrieved.numero_inventario}")
        
        # Test 4: List operations (should return DTOs)
        print("\n🔍 Test 4: List operations with DTOs")
        
        # Get all sites (should return DTOs)
        sites_list = site_service.get_all_sites(size=10)
        print(f"✅ Sites list retrieved: {len(sites_list)} sites (DTOs)")
        
        # Get all US (should return DTOs)
        us_list = us_service.get_all_us(size=10)
        print(f"✅ US list retrieved: {len(us_list)} US (DTOs)")
        
        # Get all inventario (should return DTOs)
        inv_list = inventario_service.get_all_inventario(size=10)
        print(f"✅ Inventario list retrieved: {len(inv_list)} items (DTOs)")
        
        # Test 5: Search operations (should return DTOs)
        print("\n🔍 Test 5: Search operations with DTOs")
        
        # Search sites
        search_sites = site_service.search_sites("Test", size=10)
        print(f"✅ Site search completed: {len(search_sites)} results (DTOs)")
        
        # Search US
        search_us = us_service.search_us("test", size=10)
        print(f"✅ US search completed: {len(search_us)} results (DTOs)")
        
        # Search inventario
        search_inv = inventario_service.search_inventario("test", size=10)
        print(f"✅ Inventario search completed: {len(search_inv)} results (DTOs)")
        
        print("\n🎉 All tests passed! Session fixes are working correctly.")
        print("✅ No 'Instance is not bound to a Session' errors occurred")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up temporary database
        try:
            os.unlink(db_path)
        except:
            pass

if __name__ == "__main__":
    success = test_session_fixes()
    exit(0 if success else 1)