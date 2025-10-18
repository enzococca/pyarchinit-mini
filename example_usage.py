#!/usr/bin/env python3
"""
Example usage of PyArchInit-Mini as a Python library
"""

from pyarchinit_mini import DatabaseManager, SiteService, USService, InventarioService
from pyarchinit_mini.database import DatabaseConnection
from pyarchinit_mini.utils.exceptions import ValidationError, DuplicateRecordError

def main():
    """Demonstrate PyArchInit-Mini usage"""
    
    print("🏛️  PyArchInit-Mini Example Usage")
    print("=" * 50)
    
    # 1. Initialize database connection
    print("\n1. 🗄️  Connecting to database...")
    db_conn = DatabaseConnection.sqlite("example_archaeological_data.db")
    db_manager = DatabaseManager(db_conn)
    
    # Create all tables
    db_conn.create_tables()
    print("✅ Database connected and tables created")
    
    # 2. Initialize services
    print("\n2. ⚙️  Initializing services...")
    site_service = SiteService(db_manager)
    us_service = USService(db_manager)
    inventario_service = InventarioService(db_manager)
    print("✅ Services initialized")
    
    # 3. Create a site
    print("\n3. 🏛️  Creating archaeological site...")
    site_name = "Pompei Excavation 2024"
    
    try:
        site_data = {
            "sito": site_name,
            "nazione": "Italia",
            "regione": "Campania",
            "comune": "Pompei", 
            "provincia": "NA",
            "definizione_sito": "Ancient Roman City",
            "descrizione": "Major archaeological excavation of Pompeii ruins",
            "find_check": True
        }
        
        site = site_service.create_site(site_data)
        print(f"✅ Created site: {site_name} (ID: {site.id_sito})")
        
    except DuplicateRecordError as e:
        print(f"⚠️  Site already exists: {e}")
        print(f"📍 Using existing site: {site_name}")
    
    # 4. Create stratigraphic units
    print("\n4. 📋 Creating stratigraphic units...")
    
    us_data_list = [
        {
            "sito": site_name,
            "area": "A",
            "us": 1001,
            "d_stratigrafica": "Topsoil layer",
            "d_interpretativa": "Modern surface deposit",
            "descrizione": "Dark brown soil with modern materials",
            "formazione": "Natural",
            "anno_scavo": 2024,
            "schedatore": "Dr. Archaeologist"
        },
        {
            "sito": site_name,
            "area": "A", 
            "us": 1002,
            "d_stratigrafica": "Wall foundation",
            "d_interpretativa": "Roman period construction",
            "descrizione": "Stone foundation blocks in mortar",
            "formazione": "Artificial",
            "anno_scavo": 2024,
            "schedatore": "Dr. Archaeologist"
        }
    ]
    
    created_us = []
    for i, us_data in enumerate(us_data_list):
        try:
            us = us_service.create_us(us_data)
            created_us.append(us)
            print(f"✅ Created US: {us_data['sito']}.{us_data['area']}.{us_data['us']}")
        except ValidationError as e:
            print(f"❌ Error creating US {i+1}: {e}")
    
    # 5. Create inventory items
    print("\n5. 📦 Creating inventory items...")
    
    inventory_data_list = [
        {
            "sito": site_name,
            "numero_inventario": 2024001,
            "tipo_reperto": "Ceramica",
            "definizione": "Anfora",
            "descrizione": "Fragment of Roman amphora handle",
            "area": "A",
            "us": 1001,
            "stato_conservazione": "Frammentario",
            "totale_frammenti": 3,
            "peso": 145.5,
            "diagnostico": "SI",
            "repertato": "SI"
        },
        {
            "sito": site_name,
            "numero_inventario": 2024002,
            "tipo_reperto": "Metallo",
            "definizione": "Moneta",
            "descrizione": "Bronze coin, possibly Augustan period",
            "area": "A", 
            "us": 1002,
            "stato_conservazione": "Integro",
            "peso": 8.2,
            "diagnostico": "SI",
            "repertato": "SI"
        }
    ]
    
    created_inventory = []
    for i, inv_data in enumerate(inventory_data_list):
        try:
            inv_item = inventario_service.create_inventario(inv_data)
            created_inventory.append(inv_item)
            print(f"✅ Created inventory item: {inv_data['sito']} #{inv_data['numero_inventario']}")
        except ValidationError as e:
            print(f"❌ Error creating inventory item {i+1}: {e}")
    
    # 6. Query and display data
    print("\n6. 🔍 Querying data...")
    
    # Get all sites
    sites = site_service.get_all_sites(size=10)
    print(f"📊 Total sites: {len(sites)}")
    
    # Get US for our site
    us_list = us_service.get_us_by_site(site_name)
    print(f"📊 US for {site_name}: {len(us_list)}")
    
    # Get inventory for our site
    inventory_list = inventario_service.get_inventario_by_site(site_name)
    print(f"📊 Inventory items for {site_name}: {len(inventory_list)}")
    
    # 7. Display statistics
    print("\n7. 📈 Site statistics...")
    try:
        # For this example, we'll use basic counts
        print(f"📊 Site: {site_name}")
        print(f"📊 US count: {len(us_list)}")
        print(f"📊 Inventory count: {len(inventory_list)}")
        print("📊 Demo statistics completed")
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")
    
    # 8. Search functionality
    print("\n8. 🔍 Search functionality...")
    
    # Search sites
    search_results = site_service.search_sites("Pompei")
    print(f"🔍 Search results for 'Pompei': {len(search_results)} sites")
    
    # Search inventory by type
    ceramic_items = inventario_service.get_inventario_by_type("Ceramica")
    print(f"🔍 Ceramic items: {len(ceramic_items)}")
    
    print("\n✅ Example completed successfully!")
    print("🌐 Try running 'python main.py' to start the REST API server")
    
    # Close database connection
    db_conn.close()

if __name__ == "__main__":
    main()