#!/usr/bin/env python3
"""
Script per caricare il database di esempio come database principale
"""

import os
import shutil
import sys

def load_sample_database():
    """Copy sample database as main database"""
    
    print("📥 Caricamento Database di Esempio")
    print("=" * 50)
    
    # Paths
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sample_db_path = os.path.join(root_dir, 'data', 'pyarchinit_mini_sample.db')
    main_db_path = os.path.join(root_dir, 'pyarchinit_mini.db')
    backup_db_path = os.path.join(root_dir, 'pyarchinit_mini_backup.db')
    
    # Check if sample database exists
    if not os.path.exists(sample_db_path):
        print("❌ Database di esempio non trovato!")
        print(f"   Percorso: {sample_db_path}")
        print("")
        print("Per creare il database di esempio, esegui:")
        print("   python scripts/populate_simple_data.py")
        return 1
    
    print(f"✅ Database di esempio trovato: {sample_db_path}")
    
    # Backup existing main database if it exists
    if os.path.exists(main_db_path):
        print(f"📦 Backup del database esistente...")
        try:
            if os.path.exists(backup_db_path):
                os.remove(backup_db_path)
            shutil.copy2(main_db_path, backup_db_path)
            print(f"   Backup salvato: {backup_db_path}")
        except Exception as e:
            print(f"❌ Errore durante il backup: {e}")
            return 1
    
    # Copy sample database as main database
    try:
        print(f"📂 Copia del database di esempio...")
        if os.path.exists(main_db_path):
            os.remove(main_db_path)
        shutil.copy2(sample_db_path, main_db_path)
        print(f"   Copiato in: {main_db_path}")
    except Exception as e:
        print(f"❌ Errore durante la copia: {e}")
        return 1
    
    print("")
    print("✅ Database di esempio caricato con successo!")
    print("")
    print("📊 Contenuto del database:")
    print("   • 1 Sito archeologico")
    print("   • 100 Unità Stratigrafiche")
    print("   • 50 Materiali")
    print("   • 70+ Relazioni stratigrafiche")
    print("")
    print("🚀 Ora puoi avviare PyArchInit-Mini normalmente:")
    print("   python main.py                 # API Server")
    print("   python desktop_gui/main.py     # GUI Desktop")
    print("   python launch_with_sample_data.py  # Launcher interattivo")
    
    return 0

if __name__ == "__main__":
    sys.exit(load_sample_database())