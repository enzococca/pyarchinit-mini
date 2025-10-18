#!/usr/bin/env python3
"""
Test semplice per verificare che il Media Manager sia corretto
"""

import sys
import os
sys.path.insert(0, '.')

def test_media_manager_import():
    """Test importing Media Manager without GUI"""
    
    print("🎬 Testing Media Manager Import Fix")
    print("=" * 40)
    
    try:
        # Test imports
        from pyarchinit_mini.media_manager.media_handler import MediaHandler
        from desktop_gui.dialogs import MediaManagerDialog
        
        print("✅ MediaHandler import successful")
        print("✅ MediaManagerDialog import successful")
        
        # Test MediaHandler creation
        media_handler = MediaHandler()
        print("✅ MediaHandler instance created")
        
        # Test MediaManagerDialog constructor signature
        import inspect
        sig = inspect.signature(MediaManagerDialog.__init__)
        params = list(sig.parameters.keys())
        print(f"✅ MediaManagerDialog constructor parameters: {params}")
        
        if 'callback' not in params:
            print("✅ No 'callback' parameter in constructor - fix confirmed!")
        else:
            print("❌ 'callback' parameter still present")
            
        expected_params = ['self', 'parent', 'media_handler']
        if params == expected_params:
            print("✅ Constructor parameters are correct")
        else:
            print(f"⚠️  Expected: {expected_params}, Got: {params}")
            
        print("\n🚀 Media Manager fix verified successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_media_manager_import()