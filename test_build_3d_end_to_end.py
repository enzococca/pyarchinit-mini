#!/usr/bin/env python3
"""Test end-to-end 3D build: GraphML → Proxies → Blender"""

import os
import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set database URL
os.environ['DATABASE_URL'] = 'sqlite:///data/pyarchinit_tutorial.db'

from pyarchinit_mini.database.connection import get_session
from pyarchinit_mini.mcp_server.tools.build_3d_tool import Build3DTool
from pyarchinit_mini.config.settings import Config


def test_build_3d():
    """Test complete 3D build flow"""

    print("\n" + "=" * 80)
    print("TEST: Complete 3D Build Flow")
    print("=" * 80)

    # Get database session
    db_session = get_session()

    # Create config
    config = Config()

    # Create Build3D tool
    tool = Build3DTool(config, db_session)

    # Test arguments
    arguments = {
        'mode': 'all',
        'site_id': 1,
        'options': {
            'positioning': 'graphml',
            'auto_color': True,
            'auto_material': True,
            'use_blender': True
        }
    }

    print("\n📋 Test Arguments:")
    print(f"  - mode: {arguments['mode']}")
    print(f"  - site_id: {arguments['site_id']}")
    print(f"  - use_blender: {arguments['options']['use_blender']}")

    # Execute build
    print("\n🚀 Executing Build3D tool...\n")

    import asyncio
    result = asyncio.run(tool.execute(arguments))

    print("\n📊 Result:")
    print(f"  - success: {result.get('success', False)}")

    if result.get('success'):
        print(f"  - session_id: {result.get('data', {}).get('session_id', 'N/A')}")
        print(f"  - proxies_count: {result.get('data', {}).get('proxies_count', 0)}")
        print(f"  - blender_enabled: {result.get('data', {}).get('blender_enabled', False)}")
        print(f"  - blender_status: {result.get('data', {}).get('blender_status', 'N/A')}")

        # Show proxy details
        proxies = result.get('data', {}).get('proxies', [])
        if proxies:
            print(f"\n📦 Generated {len(proxies)} proxies:")
            for proxy in proxies:
                print(f"  - US {proxy.get('us_id')}: {proxy.get('geometry_type')} at {proxy.get('location')}")

        # Show Blender result
        blender_result = result.get('data', {}).get('blender_result')
        if blender_result:
            print(f"\n🎨 Blender Result:")
            print(f"  - objects_created: {blender_result.get('objects_created', 0)}")
            print(f"  - scene: {blender_result.get('scene', 'N/A')}")
    else:
        print(f"  - error: {result.get('error', 'Unknown error')}")
        print(f"  - error_type: {result.get('error_type', 'Unknown')}")

    print("\n" + "=" * 80)

    # Close session
    db_session.close()

    return result.get('success', False)


if __name__ == "__main__":
    success = test_build_3d()
    sys.exit(0 if success else 1)
