#!/usr/bin/env python3
"""Test diretto creazione proxy con sito test5"""

import os
import sys
import asyncio
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set database URL
DB_PATH = "/Users/enzo/Documents/pyarchinit-mini-desk/pyarchinit_mini/pyarchinit_mini.db"
os.environ['DATABASE_URL'] = f'sqlite:///{DB_PATH}'

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.mcp_server.tools.build_3d_tool import Build3DTool
from pyarchinit_mini.config.settings import Config
from pyarchinit_mini.models.site import Site


def test_proxy_creation_for_test5():
    """Test completo con sito test5"""

    print("\n" + "=" * 80)
    print("TEST: Creazione Proxy per sito TEST5")
    print("=" * 80)

    # Create database connection and session
    db_conn = DatabaseConnection.from_url(f'sqlite:///{DB_PATH}')
    session = db_conn.SessionLocal()

    try:
        # First, check if site "test5" exists and get its ID
        print("\n📋 Step 1: Cerco il sito 'test5' nel database")
        site = session.query(Site).filter(Site.sito == "test5").first()

        if not site:
            print("❌ Sito 'test5' non trovato nel database")
            print("\nSiti disponibili:")
            sites = session.query(Site).all()
            for s in sites:
                print(f"  - {s.sito} (id: {s.id_sito})")
            return False

        site_id = site.id_sito
        print(f"✅ Trovato sito 'test5' con ID: {site_id}")

        # Create config and tool
        config = Config()
        tool = Build3DTool(config, session)

        # Test arguments - use mode='all' to build all US for this site
        arguments = {
            'mode': 'all',
            'site_id': site_id,
            'options': {
                'positioning': 'graphml',
                'auto_color': True,
                'auto_material': True,
                'use_blender': True
            }
        }

        print(f"\n📋 Step 2: Esecuzione Build3D")
        print(f"  - mode: {arguments['mode']}")
        print(f"  - site_id: {arguments['site_id']}")
        print(f"  - positioning: {arguments['options']['positioning']}")
        print(f"  - use_blender: {arguments['options']['use_blender']}")

        # Execute build (async)
        print("\n🚀 Avvio Build3D tool...\n")
        result = asyncio.run(tool.execute(arguments))

        # Print results
        print("\n" + "=" * 80)
        print("📊 RISULTATI:")
        print("=" * 80)

        print(f"  - success: {result.get('success', False)}")

        if result.get('success'):
            data = result.get('data', {})
            print(f"  - session_id: {data.get('session_id', 'N/A')}")
            print(f"  - proxies_count: {data.get('proxies_count', 0)}")
            print(f"  - blender_enabled: {data.get('blender_enabled', False)}")
            print(f"  - blender_status: {data.get('blender_status', 'N/A')}")

            # Show proxy details
            proxies = data.get('proxies', [])
            if proxies:
                print(f"\n📦 Generati {len(proxies)} proxies:")
                for proxy in proxies[:5]:  # Show first 5
                    location = proxy.get('location', {})
                    print(f"  - US {proxy.get('us_id')}: {proxy.get('geometry_type')} "
                          f"at ({location.get('x', 0):.2f}, {location.get('y', 0):.2f}, {location.get('z', 0):.2f})")
                if len(proxies) > 5:
                    print(f"  ... e altri {len(proxies) - 5} proxies")

            # Show Blender result
            blender_result = data.get('blender_result')
            if blender_result:
                print(f"\n🎨 Blender Result:")
                print(f"  - objects_created: {blender_result.get('objects_created', 0)}")
                print(f"  - scene: {blender_result.get('scene', 'N/A')}")

            print("\n✅ TEST COMPLETATO CON SUCCESSO")
            return True
        else:
            print(f"  - error: {result.get('error', 'Unknown error')}")
            print(f"  - error_type: {result.get('error_type', 'Unknown')}")
            print("\n❌ TEST FALLITO")
            return False

    except Exception as e:
        print(f"\n❌ Errore: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        session.close()
        print("\n" + "=" * 80)


if __name__ == "__main__":
    success = test_proxy_creation_for_test5()
    sys.exit(0 if success else 1)
