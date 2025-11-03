#!/usr/bin/env python3
"""
Test Semplice MCP Tools - Verifica Registrazione e Schema

Testa che tutti i tool MCP siano correttamente registrati e abbiano schema valido.
"""

import sys
import os
import asyncio

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.mcp_server.server import PyArchInitMCPServer


async def test_mcp_server():
    """Test registrazione e schema tool MCP"""
    print("\n" + "="*80)
    print("TEST MCP SERVER - Verifica Tool Registrati")
    print("="*80)

    db_path = "data/pyarchinit_tutorial.db"

    if not os.path.exists(db_path):
        print(f"\n❌ Database non trovato: {db_path}")
        return 1

    # Set environment variable for database
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

    # Initialize server
    print(f"\n📦 Inizializzazione server con database: {db_path}")
    server = PyArchInitMCPServer()

    # Get registered tools
    tools = server.tools
    tool_names = sorted(tools.keys())

    print(f"\n✓ Server inizializzato con {len(tool_names)} tool")
    print("\n" + "-"*80)
    print("TOOL REGISTRATI:")
    print("-"*80)

    for i, name in enumerate(tool_names, 1):
        print(f"  {i:2d}. {name}")

    # Test each tool has valid schema
    print("\n" + "="*80)
    print("TEST SCHEMA TOOL")
    print("="*80)

    passed = 0
    failed = 0
    errors = []

    for tool_name in tool_names:
        try:
            tool = tools[tool_name]

            # Get tool description
            tool_desc = tool.to_tool_description()

            # Verify has required attributes
            if not hasattr(tool_desc, 'name'):
                errors.append(f"{tool_name}: missing 'name'")
                failed += 1
                print(f"  ❌ {tool_name}: missing 'name'")
                continue

            if not hasattr(tool_desc, 'description'):
                errors.append(f"{tool_name}: missing 'description'")
                failed += 1
                print(f"  ❌ {tool_name}: missing 'description'")
                continue

            if not hasattr(tool_desc, 'input_schema'):
                errors.append(f"{tool_name}: missing 'input_schema'")
                failed += 1
                print(f"  ❌ {tool_name}: missing 'input_schema'")
                continue

            # Verify input_schema structure
            schema = tool_desc.input_schema
            if not isinstance(schema, dict):
                errors.append(f"{tool_name}: input_schema not a dict")
                failed += 1
                print(f"  ❌ {tool_name}: input_schema not a dict")
                continue

            if 'type' not in schema:
                errors.append(f"{tool_name}: input_schema missing 'type'")
                failed += 1
                print(f"  ❌ {tool_name}: input_schema missing 'type'")
                continue

            passed += 1
            print(f"  ✅ {tool_name}: schema valido")

        except Exception as e:
            failed += 1
            error_msg = f"{tool_name}: {str(e)}"
            errors.append(error_msg)
            print(f"  ❌ {error_msg}")

    # Summary
    print("\n" + "="*80)
    print("RIASSUNTO TEST")
    print("="*80)
    print(f"\nTotale tool: {len(tool_names)}")
    print(f"✅ Schema validi: {passed} ({passed/len(tool_names)*100:.1f}%)")
    print(f"❌ Schema invalidi: {failed} ({failed/len(tool_names)*100:.1f}%)")

    if errors:
        print("\nErrori:")
        for error in errors:
            print(f"  - {error}")

    if failed == 0:
        print("\n🎉 TUTTI I TOOL HANNO SCHEMA VALIDO!")
    else:
        print(f"\n⚠️  {failed} tool con problemi di schema")

    print("\n" + "="*80)

    return 0 if failed == 0 else 1


async def main():
    """Main test function"""
    return await test_mcp_server()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
