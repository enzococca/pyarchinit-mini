#!/usr/bin/env python3
"""
Test Chat-based 3D Builder

Tests the complete chat functionality:
1. Command parsing
2. MCP tool execution
3. 3D proxy generation
"""

import sys
import asyncio
from pyarchinit_mini.services.command_parser import CommandParser
from pyarchinit_mini.services.mcp_executor import get_executor


def test_command_parser():
    """Test command parser with various Italian/English commands"""
    print("=" * 60)
    print("TEST 1: Command Parser")
    print("=" * 60)

    parser = CommandParser()

    test_commands = [
        "Crea US 1,2,3",
        "Mostra solo periodo Romano",
        "Nascondi US 5,6",
        "Costruisci tutto",
        "Esporta come .glb",
        "Colora US 3 rosso",
        "Build US 10,11,12",
        "Hide US 99",
    ]

    for cmd in test_commands:
        print(f"\nCommand: '{cmd}'")
        tool_calls = parser.parse(cmd)

        if tool_calls:
            for tool_name, arguments in tool_calls:
                print(f"  → Tool: {tool_name}")
                print(f"  → Arguments: {arguments}")
        else:
            print("  → No pattern matched")

    print("\n✓ Command Parser Test Complete\n")


async def test_mcp_executor():
    """Test MCP executor with build_3d tool"""
    print("=" * 60)
    print("TEST 2: MCP Executor - Build 3D")
    print("=" * 60)

    # Get executor instance
    database_url = "sqlite:///data/pyarchinit_tutorial.db"
    executor = get_executor(database_url)

    # Test build_3d tool
    print("\nExecuting build_3d tool with US [1,2,3]...")

    try:
        result = await executor.execute_tool(
            "build_3d",
            {
                "us_ids": [1, 2, 3],
                "mode": "selected",
                "site_id": 1,  # Optional
                "options": {
                    "positioning": "graphml",
                    "auto_color": True,
                    "auto_material": True
                }
            }
        )

        print("\nResult:")
        print(f"  Success: {result.get('success', False)}")
        print(f"  Message: {result.get('message', 'N/A')}")

        if result.get('success') and 'data' in result:
            data = result['data']
            print(f"  Session ID: {data.get('session_id', 'N/A')}")
            print(f"  Proxies Count: {data.get('proxies_count', 0)}")

            if 'proxies' in data and data['proxies']:
                print(f"\n  First Proxy Sample:")
                first_proxy = data['proxies'][0]
                print(f"    US ID: {first_proxy.get('us_id')}")
                print(f"    Proxy ID: {first_proxy.get('proxy_id')}")
                print(f"    Position: {first_proxy.get('position')}")

        print("\n✓ MCP Executor Test Complete\n")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


async def test_full_chat_flow():
    """Test complete chat flow from command to 3D generation"""
    print("=" * 60)
    print("TEST 3: Full Chat Flow")
    print("=" * 60)

    parser = CommandParser()
    database_url = "sqlite:///data/pyarchinit_tutorial.db"
    executor = get_executor(database_url)

    # Test command
    test_command = "Crea US 1,2,3"

    print(f"\nUser Command: '{test_command}'")

    # Step 1: Parse command
    print("\nStep 1: Parsing command...")
    tool_calls = parser.parse(test_command)

    if not tool_calls:
        print("  ✗ No tool calls parsed")
        return

    print(f"  ✓ Parsed {len(tool_calls)} tool call(s)")

    # Step 2: Execute tools
    print("\nStep 2: Executing tools...")
    for tool_name, arguments in tool_calls:
        print(f"  Tool: {tool_name}")
        print(f"  Arguments: {arguments}")

        try:
            result = await executor.execute_tool(tool_name, arguments)

            if result.get('success'):
                print(f"  ✓ Success: {result.get('message')}")

                if 'data' in result and 'proxies_count' in result['data']:
                    count = result['data']['proxies_count']
                    print(f"  ✓ Generated {count} 3D proxies")

            else:
                print(f"  ✗ Failed: {result.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"  ✗ Exception: {e}")

    print("\n✓ Full Chat Flow Test Complete\n")


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("PyArchInit-Mini: Chat-Based 3D Builder Tests")
    print("=" * 60 + "\n")

    # Test 1: Command Parser
    test_command_parser()

    # Test 2: MCP Executor
    await test_mcp_executor()

    # Test 3: Full Flow
    await test_full_chat_flow()

    print("=" * 60)
    print("ALL TESTS COMPLETE")
    print("=" * 60)
    print("\nTo test the web interface:")
    print("1. Start server: DATABASE_URL='sqlite:///data/pyarchinit_tutorial.db' python3 -m pyarchinit_mini.web_interface.app")
    print("2. Open browser: http://localhost:5001/3d-builder/")
    print("3. Use the chat interface in the right sidebar")
    print("4. Try commands like: 'Crea US 1,2,3'\n")


if __name__ == "__main__":
    asyncio.run(main())
