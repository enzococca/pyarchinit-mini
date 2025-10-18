#!/usr/bin/env python3
"""
Launcher per PyArchInit-Mini con database di esempio
"""

import os
import sys

def main():
    """Launch PyArchInit-Mini with sample database"""
    
    print("🚀 PyArchInit-Mini - Avvio con Database di Esempio")
    print("=" * 60)
    
    # Set environment variable for sample database
    sample_db_path = os.path.join(os.path.dirname(__file__), 'data', 'pyarchinit_mini_sample.db')
    
    if not os.path.exists(sample_db_path):
        print("❌ Database di esempio non trovato!")
        print(f"   Percorso atteso: {sample_db_path}")
        print("")
        print("Per creare il database di esempio, esegui:")
        print("   python scripts/populate_simple_data.py")
        return 1
    
    # Set database URL environment variable
    database_url = f"sqlite:///{sample_db_path}"
    os.environ["DATABASE_URL"] = database_url
    
    print(f"✅ Database di esempio configurato:")
    print(f"   {sample_db_path}")
    print("")
    
    # Ask user which interface to launch
    print("Scegli l'interfaccia da avviare:")
    print("1. GUI Desktop (Tkinter)")
    print("2. API Server (FastAPI)")
    print("3. Entrambi")
    
    try:
        choice = input("\nInserisci la tua scelta (1/2/3): ").strip()
    except KeyboardInterrupt:
        print("\n\nAnnullato dall'utente.")
        return 0
    
    if choice == "1":
        # Launch desktop GUI
        print("\n🖥️  Avvio GUI Desktop...")
        try:
            from desktop_gui.main_window import PyArchInitGUI
            app = PyArchInitGUI()
            app.run()
        except Exception as e:
            print(f"❌ Errore avvio GUI: {e}")
            return 1
            
    elif choice == "2":
        # Launch API server
        print("\n🌐 Avvio API Server...")
        print("📖 Documentazione API: http://localhost:8000/docs")
        try:
            from main import main as api_main
            return api_main()
        except Exception as e:
            print(f"❌ Errore avvio API: {e}")
            return 1
            
    elif choice == "3":
        # Launch both
        print("\n🚀 Avvio GUI Desktop e API Server...")
        print("📖 API Documentation: http://localhost:8000/docs")
        
        import threading
        import time
        
        def run_api():
            try:
                from main import main as api_main
                api_main()
            except Exception as e:
                print(f"❌ Errore API Server: {e}")
        
        # Start API server in background thread
        api_thread = threading.Thread(target=run_api, daemon=True)
        api_thread.start()
        
        # Wait a moment for API to start
        time.sleep(2)
        
        # Launch GUI in main thread
        try:
            from desktop_gui.main_window import PyArchInitGUI
            app = PyArchInitGUI()
            app.run()
        except Exception as e:
            print(f"❌ Errore GUI: {e}")
            return 1
    else:
        print("❌ Scelta non valida!")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())