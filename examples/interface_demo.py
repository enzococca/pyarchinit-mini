#!/usr/bin/env python3
"""
PyArchInit-Mini Interface Demo
Demonstrates all available interfaces and their capabilities
"""

import os
import sys
import subprocess
import time
import threading

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def print_banner(title):
    """Print a formatted banner"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def create_sample_data():
    """Create sample archaeological data for demonstration"""
    print_banner("CREATING SAMPLE DATA")
    
    try:
        from pyarchinit_mini.database.connection import DatabaseConnection
        from pyarchinit_mini.database.manager import DatabaseManager
        from pyarchinit_mini.services.site_service import SiteService
        from pyarchinit_mini.services.us_service import USService
        from pyarchinit_mini.services.inventario_service import InventarioService
        
        # Initialize database
        database_url = os.getenv("DATABASE_URL", "sqlite:///./demo_pyarchinit.db")
        db_conn = DatabaseConnection.from_url(database_url)
        db_conn.create_tables()
        db_manager = DatabaseManager(db_conn)
        
        # Initialize services
        site_service = SiteService(db_manager)
        us_service = USService(db_manager)
        inventario_service = InventarioService(db_manager)
        
        print("📊 Initializing services...")
        
        # Create sample sites
        sites_data = [
            {
                "sito": "Pompei",
                "nazione": "Italia",
                "regione": "Campania",
                "comune": "Pompei",
                "provincia": "NA",
                "definizione_sito": "Città Romana",
                "descrizione": "Antica città romana sepolta dall'eruzione del Vesuvio nel 79 d.C."
            },
            {
                "sito": "Forum Romanum",
                "nazione": "Italia", 
                "regione": "Lazio",
                "comune": "Roma",
                "provincia": "RM",
                "definizione_sito": "Foro Romano",
                "descrizione": "Centro politico, commerciale e religioso dell'antica Roma"
            },
            {
                "sito": "Villa di Adriano",
                "nazione": "Italia",
                "regione": "Lazio",
                "comune": "Tivoli",
                "provincia": "RM",
                "definizione_sito": "Villa Imperiale",
                "descrizione": "Complesso di edifici residenziali dell'imperatore Adriano"
            }
        ]
        
        print("🏛️  Creating sample sites...")
        for site_data in sites_data:
            try:
                site = site_service.create_site(site_data)
                print(f"   ✅ Created site: {site_data['sito']}")
            except Exception as e:
                print(f"   ⚠️  Site {site_data['sito']} may already exist")
        
        # Create sample US (Stratigraphic Units)
        us_data = [
            {
                "sito": "Pompei",
                "area": "Regio VII",
                "us": 1001,
                "d_stratigrafica": "Strato di lapilli vulcanici",
                "d_interpretativa": "Deposito dell'eruzione del 79 d.C.",
                "anno_scavo": 2023,
                "schedatore": "Dr. A. Archeologo",
                "formazione": "Natural"
            },
            {
                "sito": "Pompei", 
                "area": "Regio VII",
                "us": 1002,
                "d_stratigrafica": "Pavimento in opus tessellatum",
                "d_interpretativa": "Piano di calpestio di ambiente residenziale",
                "anno_scavo": 2023,
                "schedatore": "Dr. A. Archeologo",
                "formazione": "Artificial"
            },
            {
                "sito": "Forum Romanum",
                "area": "Basilica Iulia",
                "us": 2001,
                "d_stratigrafica": "Fondazioni in travertino",
                "d_interpretativa": "Strutture portanti della basilica",
                "anno_scavo": 2024,
                "schedatore": "Prof. R. Romano",
                "formazione": "Artificial"
            }
        ]
        
        print("📋 Creating sample stratigraphic units...")
        for us in us_data:
            try:
                created_us = us_service.create_us(us)
                print(f"   ✅ Created US {us['us']} for {us['sito']}")
            except Exception as e:
                print(f"   ⚠️  US {us['us']} may already exist")
        
        # Create sample inventory
        inventory_data = [
            {
                "sito": "Pompei",
                "numero_inventario": 1001,
                "tipo_reperto": "Ceramica",
                "definizione": "Anfora Dressel 1A",
                "descrizione": "Anfora vinaria di produzione tirrenica",
                "area": "Regio VII",
                "us": 1001,
                "peso": 2450.5
            },
            {
                "sito": "Pompei",
                "numero_inventario": 1002,
                "tipo_reperto": "Metallo",
                "definizione": "Fibula bronzea",
                "descrizione": "Spilla in bronzo con decorazione incisa",
                "area": "Regio VII", 
                "us": 1002,
                "peso": 15.2
            },
            {
                "sito": "Forum Romanum",
                "numero_inventario": 2001,
                "tipo_reperto": "Pietra",
                "definizione": "Frammento iscrizione",
                "descrizione": "Frammento di iscrizione onoraria in marmo",
                "area": "Basilica Iulia",
                "us": 2001,
                "peso": 850.0
            }
        ]
        
        print("📦 Creating sample inventory items...")
        for item in inventory_data:
            try:
                created_item = inventario_service.create_inventario(item)
                print(f"   ✅ Created item {item['numero_inventario']} for {item['sito']}")
            except Exception as e:
                print(f"   ⚠️  Item {item['numero_inventario']} may already exist")
        
        print("\n✅ Sample data created successfully!")
        print(f"📊 Database: {database_url}")
        
        # Show statistics
        total_sites = site_service.count_sites()
        total_us = us_service.count_us()
        total_inventory = inventario_service.count_inventario()
        
        print(f"\n📈 DATA SUMMARY:")
        print(f"   🏛️  Sites: {total_sites}")
        print(f"   📋 Stratigraphic Units: {total_us}")
        print(f"   📦 Inventory Items: {total_inventory}")
        
        db_conn.close()
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")

def demo_api_server():
    """Demonstrate the FastAPI server"""
    print_banner("FastAPI REST SERVER DEMO")
    
    print("🚀 Starting FastAPI server...")
    print("📖 API Documentation will be available at: http://localhost:8000/docs")
    print("🔗 API Base URL: http://localhost:8000/api/v1/")
    print("\n📝 Example API endpoints:")
    print("   GET  /api/v1/sites/ - List all sites")
    print("   POST /api/v1/sites/ - Create new site")
    print("   GET  /api/v1/us/ - List stratigraphic units")
    print("   GET  /api/v1/inventario/ - List inventory items")
    print("\n💡 To test the API:")
    print("   1. Keep this terminal open")
    print("   2. Open browser: http://localhost:8000/docs")
    print("   3. Use the interactive API documentation")
    print("   4. Press Ctrl+C to stop the server")
    
    try:
        # Set database URL for demo
        os.environ["DATABASE_URL"] = "sqlite:///./demo_pyarchinit.db"
        
        # Run the server
        subprocess.run([sys.executable, "main.py"], cwd=os.path.dirname(os.path.dirname(__file__)))
        
    except KeyboardInterrupt:
        print("\n🛑 API server stopped by user")
    except Exception as e:
        print(f"❌ Error running API server: {e}")

def demo_web_interface():
    """Demonstrate the Flask web interface"""
    print_banner("FLASK WEB INTERFACE DEMO")
    
    print("🌐 Starting Flask web interface...")
    print("📱 Web Interface will be available at: http://localhost:5000")
    print("\n✨ Features available:")
    print("   🏛️  Site management with forms")
    print("   📋 Stratigraphic units with filtering")
    print("   📦 Inventory management")
    print("   📊 Dashboard with statistics")
    print("   🔗 Harris Matrix visualization")
    print("   📄 PDF export functionality")
    print("   🖼️  Media upload and management")
    
    print("\n💡 To test the web interface:")
    print("   1. Keep this terminal open")
    print("   2. Open browser: http://localhost:5000")
    print("   3. Navigate through the interface")
    print("   4. Press Ctrl+C to stop the server")
    
    try:
        # Set database URL for demo
        os.environ["DATABASE_URL"] = "sqlite:///./demo_pyarchinit.db"
        
        # Run the web interface
        subprocess.run([sys.executable, "web_interface/app.py"], cwd=os.path.dirname(os.path.dirname(__file__)))
        
    except KeyboardInterrupt:
        print("\n🛑 Web interface stopped by user")
    except Exception as e:
        print(f"❌ Error running web interface: {e}")

def demo_desktop_gui():
    """Demonstrate the Tkinter desktop GUI"""
    print_banner("TKINTER DESKTOP GUI DEMO")
    
    print("🖥️  Starting desktop GUI application...")
    print("\n✨ Features available:")
    print("   📊 Dashboard with statistics cards")
    print("   🏛️  Complete site management")
    print("   📋 Stratigraphic units with advanced forms")
    print("   📦 Inventory management with filters")
    print("   🔗 Harris Matrix generation and export")
    print("   📄 PDF report generation")
    print("   🖼️  Media file management")
    print("   📈 Statistics and analytics")
    
    print("\n💡 GUI Features:")
    print("   🔄 Real-time data refresh")
    print("   🔍 Advanced search and filtering")
    print("   💾 Multi-database support (SQLite/PostgreSQL)")
    print("   📱 Responsive interface design")
    print("   ⌨️  Keyboard shortcuts and tooltips")
    
    try:
        # Set database URL for demo
        os.environ["DATABASE_URL"] = "sqlite:///./demo_pyarchinit.db"
        
        # Run the desktop GUI
        subprocess.run([sys.executable, "desktop_gui/gui_app.py"], cwd=os.path.dirname(os.path.dirname(__file__)))
        
    except KeyboardInterrupt:
        print("\n🛑 Desktop GUI stopped by user")
    except Exception as e:
        print(f"❌ Error running desktop GUI: {e}")

def demo_cli_interface():
    """Demonstrate the Rich CLI interface"""
    print_banner("RICH CLI INTERFACE DEMO")
    
    print("💻 Starting interactive CLI...")
    print("\n✨ Features available:")
    print("   🏛️  Site management with guided forms")
    print("   📋 US management with detailed input")
    print("   📦 Inventory management")
    print("   🔗 Harris Matrix generation")
    print("   📊 Statistics and reports")
    print("   📄 PDF export functionality")
    
    print("\n💡 CLI Features:")
    print("   🎨 Rich colors and formatting")
    print("   📋 Interactive menus and prompts")
    print("   📊 Data tables and statistics")
    print("   🔍 Search and filtering options")
    print("   💾 Database configuration support")
    
    print("\n🎯 Navigation:")
    print("   📝 Use numbers to select options")
    print("   🔙 Press 0 to go back")
    print("   ⌨️  Press Ctrl+C to exit")
    
    try:
        # Set database URL for demo
        os.environ["DATABASE_URL"] = "sqlite:///./demo_pyarchinit.db"
        
        # Run the CLI interface
        subprocess.run([sys.executable, "cli_interface/cli_app.py"], cwd=os.path.dirname(os.path.dirname(__file__)))
        
    except KeyboardInterrupt:
        print("\n🛑 CLI interface stopped by user")
    except Exception as e:
        print(f"❌ Error running CLI interface: {e}")

def demo_python_library():
    """Demonstrate using PyArchInit-Mini as a Python library"""
    print_banner("PYTHON LIBRARY DEMO")
    
    try:
        from pyarchinit_mini.database.connection import DatabaseConnection
        from pyarchinit_mini.database.manager import DatabaseManager
        from pyarchinit_mini.services.site_service import SiteService
        from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator
        from pyarchinit_mini.pdf_export.pdf_generator import PDFGenerator
        
        print("📚 Demonstrating PyArchInit-Mini as a Python library...")
        
        # Initialize
        database_url = "sqlite:///./demo_pyarchinit.db"
        db_conn = DatabaseConnection.from_url(database_url)
        db_manager = DatabaseManager(db_conn)
        site_service = SiteService(db_manager)
        
        print(f"🗄️  Connected to database: {database_url}")
        
        # Query data
        sites = site_service.get_all_sites(size=10)
        print(f"🏛️  Found {len(sites)} sites:")
        
        for site in sites:
            print(f"   📍 {site.sito} ({site.comune}, {site.nazione})")
        
        if sites:
            # Demonstrate Harris Matrix
            site_name = sites[0].sito
            print(f"\n🔗 Generating Harris Matrix for {site_name}...")
            
            matrix_generator = HarrisMatrixGenerator(db_manager)
            graph = matrix_generator.generate_matrix(site_name)
            stats = matrix_generator.get_matrix_statistics(graph)
            
            print(f"   📊 Matrix Statistics:")
            print(f"      - Total US: {stats['total_us']}")
            print(f"      - Relationships: {stats['total_relationships']}")
            print(f"      - Valid: {stats['is_valid']}")
            
            # Demonstrate PDF generation
            print(f"\n📄 Generating PDF report for {site_name}...")
            pdf_generator = PDFGenerator()
            site_data = sites[0].to_dict()
            
            try:
                pdf_bytes = pdf_generator.generate_site_report(site_data, [], [])
                print(f"   ✅ PDF generated successfully ({len(pdf_bytes)} bytes)")
            except Exception as e:
                print(f"   ⚠️  PDF generation error: {e}")
        
        # Show library capabilities
        print(f"\n📖 Library Capabilities:")
        print(f"   🔧 Database Management: SQLAlchemy ORM")
        print(f"   🏛️  Site Service: CRUD operations")
        print(f"   📋 US Service: Stratigraphic unit management")
        print(f"   📦 Inventory Service: Material catalog")
        print(f"   🔗 Harris Matrix: Graph generation and analysis")
        print(f"   📄 PDF Export: Archaeological reports")
        print(f"   🖼️  Media Handler: File management")
        print(f"   🔍 Search & Filter: Advanced queries")
        print(f"   💾 Multi-DB: SQLite and PostgreSQL support")
        
        db_conn.close()
        
    except Exception as e:
        print(f"❌ Error in library demo: {e}")

def main():
    """Main demo function"""
    print_banner("PYARCHINIT-MINI INTERFACE DEMONSTRATION")
    
    print("🏛️  Archaeological Data Management System")
    print("   Multiple interfaces for comprehensive data management")
    print("   Developed by the PyArchInit Team")
    
    # Create sample data first
    create_sample_data()
    
    while True:
        print_banner("INTERFACE SELECTION")
        print("Choose an interface to demonstrate:")
        print()
        print("1. 🚀 FastAPI REST Server")
        print("2. 🌐 Flask Web Interface")
        print("3. 🖥️  Tkinter Desktop GUI")
        print("4. 💻 Rich CLI Interface")
        print("5. 📚 Python Library Demo")
        print("6. 📊 Show Current Data")
        print("0. 🚪 Exit Demo")
        print()
        
        try:
            choice = input("Select option (0-6): ").strip()
            
            if choice == "0":
                print("\n👋 Thank you for trying PyArchInit-Mini!")
                print("📧 Support: enzo.ccc@gmail.com")
                print("🐛 Issues: https://github.com/enzococca/pyarchinit-mini/issues")
                break
            elif choice == "1":
                demo_api_server()
            elif choice == "2":
                demo_web_interface()
            elif choice == "3":
                demo_desktop_gui()
            elif choice == "4":
                demo_cli_interface()
            elif choice == "5":
                demo_python_library()
            elif choice == "6":
                create_sample_data()  # Show current data
            else:
                print("❌ Invalid choice. Please select 0-6.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Demo interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("\n" + "-"*60)
        input("Press Enter to return to main menu...")

if __name__ == "__main__":
    main()