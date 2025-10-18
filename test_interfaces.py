#!/usr/bin/env python3
"""
PyArchInit-Mini Interface Tests
Quick verification that all interfaces can be imported and initialized
"""

import os
import sys
import traceback

def test_component(name, test_func):
    """Test a component and report results"""
    print(f"\n🧪 Testing {name}...")
    try:
        test_func()
        print(f"✅ {name} - OK")
        return True
    except Exception as e:
        print(f"❌ {name} - FAILED")
        print(f"   Error: {str(e)}")
        if "-v" in sys.argv or "--verbose" in sys.argv:
            print("   Traceback:")
            traceback.print_exc()
        return False

def test_database_core():
    """Test core database functionality"""
    from pyarchinit_mini.database.connection import DatabaseConnection
    from pyarchinit_mini.database.manager import DatabaseManager
    
    # Test SQLite connection
    db_conn = DatabaseConnection.sqlite(":memory:")
    db_conn.create_tables()
    db_manager = DatabaseManager(db_conn)
    
    # Test basic operations
    result = db_manager.execute_raw_query("SELECT 1 as test")
    assert len(result) == 1
    assert result[0][0] == 1
    
    db_conn.close()

def test_services():
    """Test service layer"""
    from pyarchinit_mini.database.connection import DatabaseConnection
    from pyarchinit_mini.database.manager import DatabaseManager
    from pyarchinit_mini.services.site_service import SiteService
    from pyarchinit_mini.services.us_service import USService
    from pyarchinit_mini.services.inventario_service import InventarioService
    
    # Initialize in-memory database
    db_conn = DatabaseConnection.sqlite(":memory:")
    db_conn.create_tables()
    db_manager = DatabaseManager(db_conn)
    
    # Test services initialization
    site_service = SiteService(db_manager)
    us_service = USService(db_manager)
    inventario_service = InventarioService(db_manager)
    
    # Test basic operations
    count = site_service.count_sites()
    assert count == 0
    
    db_conn.close()

def test_harris_matrix():
    """Test Harris Matrix functionality"""
    from pyarchinit_mini.database.connection import DatabaseConnection
    from pyarchinit_mini.database.manager import DatabaseManager
    from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator
    from pyarchinit_mini.harris_matrix.matrix_visualizer import MatrixVisualizer
    
    # Initialize
    db_conn = DatabaseConnection.sqlite(":memory:")
    db_conn.create_tables()
    db_manager = DatabaseManager(db_conn)
    
    # Test matrix components
    matrix_generator = HarrisMatrixGenerator(db_manager)
    matrix_visualizer = MatrixVisualizer()
    
    # Test with empty data
    graph = matrix_generator.generate_matrix("test_site")
    stats = matrix_generator.get_matrix_statistics(graph)
    assert stats['total_us'] == 0
    
    db_conn.close()

def test_pdf_export():
    """Test PDF export functionality"""
    from pyarchinit_mini.pdf_export.pdf_generator import PDFGenerator
    
    pdf_generator = PDFGenerator()
    
    # Test with minimal data
    site_data = {
        'sito': 'Test Site',
        'nazione': 'Italia',
        'descrizione': 'Test description'
    }
    
    pdf_bytes = pdf_generator.generate_site_report(site_data, [], [])
    assert len(pdf_bytes) > 1000  # PDF should be substantial

def test_media_handler():
    """Test media management"""
    from pyarchinit_mini.media_manager.media_handler import MediaHandler
    import tempfile
    
    media_handler = MediaHandler(tempfile.mkdtemp())
    
    # Test initialization
    assert media_handler.base_media_path.exists()
    assert media_handler.images_path.exists()

def test_api_server():
    """Test FastAPI server initialization"""
    from main import app
    
    # Test app creation
    assert app is not None
    assert hasattr(app, 'openapi')

def test_web_interface():
    """Test Flask web interface"""
    try:
        from web_interface.app import create_app
        
        app = create_app()
        assert app is not None
        assert hasattr(app, 'config')
    except ImportError as e:
        if "flask_wtf" in str(e):
            raise ImportError("Flask-WTF not installed. Run: pip install flask-wtf")
        raise

def test_desktop_gui():
    """Test Tkinter desktop GUI"""
    # Skip GUI test in headless environments
    if os.getenv("DISPLAY") is None and sys.platform != "darwin":
        print("   ⚠️  Skipping GUI test (no display)")
        return
    
    from desktop_gui.main_window import PyArchInitGUI
    
    # Test class can be imported and has required methods
    assert hasattr(PyArchInitGUI, '__init__')
    assert hasattr(PyArchInitGUI, 'run')

def test_cli_interface():
    """Test CLI interface"""
    from cli_interface.cli_app import PyArchInitCLI
    
    # Test CLI can be initialized
    # Note: We don't actually run it to avoid blocking
    assert hasattr(PyArchInitCLI, '__init__')
    assert hasattr(PyArchInitCLI, 'run')

def main():
    """Run all interface tests"""
    print("🧪 PyArchInit-Mini Interface Tests")
    print("=" * 50)
    
    # Set test database
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    
    tests = [
        ("Database Core", test_database_core),
        ("Services Layer", test_services),
        ("Harris Matrix", test_harris_matrix),
        ("PDF Export", test_pdf_export),
        ("Media Handler", test_media_handler),
        ("FastAPI Server", test_api_server),
        ("Flask Web Interface", test_web_interface),
        ("Tkinter Desktop GUI", test_desktop_gui),
        ("Rich CLI Interface", test_cli_interface)
    ]
    
    results = []
    for name, test_func in tests:
        success = test_component(name, test_func)
        results.append((name, success))
    
    # Summary
    print("\n" + "=" * 50)
    print("🏁 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! PyArchInit-Mini is ready to use.")
        return 0
    else:
        print("⚠️  Some tests failed. Check dependencies and configuration.")
        print("\n💡 Common fixes:")
        print("   • Install missing dependencies: pip install -r requirements.txt")
        print("   • Check Python version: Python 3.8+ required")
        print("   • For GUI tests: ensure display is available")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)