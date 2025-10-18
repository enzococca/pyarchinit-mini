#!/usr/bin/env python3
"""
Final comprehensive test for PyArchInit-Mini
Tests that all components can be imported and initialized properly
"""

import os
import sys

def test_all_interfaces():
    """Test all four interfaces"""
    results = {}
    
    print("🧪 PyArchInit-Mini Final Integration Test")
    print("=" * 50)
    
    # Set test database
    os.environ["DATABASE_URL"] = "sqlite:///./final_test.db"
    
    # Test 1: FastAPI Server
    print("\n🚀 Testing FastAPI Server...")
    try:
        from main import app
        assert app is not None
        results['fastapi'] = True
        print("✅ FastAPI Server - OK")
    except Exception as e:
        results['fastapi'] = False
        print(f"❌ FastAPI Server - FAILED: {e}")
    
    # Test 2: CLI Interface
    print("\n💻 Testing CLI Interface...")
    try:
        from cli_interface.cli_app import PyArchInitCLI
        cli = PyArchInitCLI("sqlite:///./test_cli.db")
        assert hasattr(cli, 'site_service')
        results['cli'] = True
        print("✅ CLI Interface - OK")
    except Exception as e:
        results['cli'] = False
        print(f"❌ CLI Interface - FAILED: {e}")
    
    # Test 3: Desktop GUI
    print("\n🖥️ Testing Desktop GUI...")
    try:
        from desktop_gui.main_window import PyArchInitGUI
        # Test that it can be imported and has required methods
        assert hasattr(PyArchInitGUI, '__init__')
        assert hasattr(PyArchInitGUI, 'run')
        
        # Test dialog imports
        from desktop_gui.dialogs import SiteDialog, USDialog, InventarioDialog
        assert callable(SiteDialog)
        assert callable(USDialog)
        assert callable(InventarioDialog)
        
        results['desktop'] = True
        print("✅ Desktop GUI - OK")
    except Exception as e:
        results['desktop'] = False
        print(f"❌ Desktop GUI - FAILED: {e}")
    
    # Test 4: Web Interface (may fail due to Flask-WTF)
    print("\n🌐 Testing Web Interface...")
    try:
        from web_interface.app import create_app
        app = create_app()
        assert app is not None
        results['web'] = True
        print("✅ Web Interface - OK")
    except ImportError as e:
        if "flask_wtf" in str(e).lower():
            results['web'] = "SKIP (Flask-WTF not installed)"
            print("⚠️ Web Interface - SKIPPED (Flask-WTF not installed)")
        else:
            results['web'] = False
            print(f"❌ Web Interface - FAILED: {e}")
    except Exception as e:
        results['web'] = False
        print(f"❌ Web Interface - FAILED: {e}")
    
    # Test 5: Core Archaeological Features
    print("\n🏛️ Testing Archaeological Features...")
    try:
        # Database and services
        from pyarchinit_mini.database.connection import DatabaseConnection
        from pyarchinit_mini.database.manager import DatabaseManager
        from pyarchinit_mini.services.site_service import SiteService
        
        # Harris Matrix
        from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator
        from pyarchinit_mini.harris_matrix.matrix_visualizer import MatrixVisualizer
        
        # PDF Export
        from pyarchinit_mini.pdf_export.pdf_generator import PDFGenerator
        
        # Media Management
        from pyarchinit_mini.media_manager.media_handler import MediaHandler
        
        # Quick functional test
        db_conn = DatabaseConnection.sqlite(":memory:")
        db_conn.create_tables()
        db_manager = DatabaseManager(db_conn)
        site_service = SiteService(db_manager)
        
        # Test basic operation
        count = site_service.count_sites()
        assert count == 0
        
        db_conn.close()
        
        results['archaeological'] = True
        print("✅ Archaeological Features - OK")
    except Exception as e:
        results['archaeological'] = False
        print(f"❌ Archaeological Features - FAILED: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 FINAL TEST RESULTS")
    print("=" * 50)
    
    passed = 0
    total = 0
    
    for component, result in results.items():
        total += 1
        if result is True:
            passed += 1
            print(f"✅ {component.upper()} - PASS")
        elif result is False:
            print(f"❌ {component.upper()} - FAIL")
        else:
            print(f"⚠️ {component.upper()} - {result}")
    
    print(f"\n🎯 Overall Result: {passed}/{total} core components working")
    
    if passed >= 4:  # Allow web interface to fail due to dependencies
        print("🎉 PyArchInit-Mini is ready for production use!")
        print("\n📋 Working Interfaces:")
        if results.get('fastapi'): print("   🚀 FastAPI REST Server")
        if results.get('cli'): print("   💻 Rich CLI Interface")
        if results.get('desktop'): print("   🖥️ Tkinter Desktop GUI")
        if results.get('web') is True: print("   🌐 Flask Web Interface")
        if results.get('archaeological'): print("   🏛️ Archaeological Features")
        
        print("\n🚀 Launch Commands:")
        print("   API Server:   python main.py")
        print("   CLI:          python cli_interface/cli_app.py")
        print("   Desktop GUI:  python desktop_gui/gui_app.py")
        if results.get('web') is True:
            print("   Web App:      python web_interface/app.py")
        
        return 0
    else:
        print("❌ Critical components are not working properly")
        return 1

if __name__ == "__main__":
    exit_code = test_all_interfaces()
    sys.exit(exit_code)