#!/usr/bin/env python3
"""
Quick launcher for PyArchInit-Mini Desktop GUI
"""

import os
import sys

def main():
    """Launch the desktop GUI"""
    print("🏛️ PyArchInit-Mini Desktop GUI")
    print("Starting archaeological data management interface...")
    
    try:
        # Set default database if not configured
        if not os.getenv("DATABASE_URL"):
            os.environ["DATABASE_URL"] = "sqlite:///./pyarchinit_mini.db"
            print(f"📀 Using default database: {os.environ['DATABASE_URL']}")
        
        # Launch GUI
        from desktop_gui.gui_app import main as gui_main
        gui_main()
        
    except KeyboardInterrupt:
        print("\n👋 Application closed by user")
    except Exception as e:
        print(f"❌ Error starting GUI: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()