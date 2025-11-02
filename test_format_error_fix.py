#!/usr/bin/env python3
"""Test _format_error fix"""

import os
import sys

os.environ["DATABASE_URL"] = "sqlite:///data/pyarchinit_tutorial.db"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pyarchinit_mini.mcp_server.tools.base_tool import BaseTool

# Create a simple concrete implementation for testing
class TestTool(BaseTool):
    def to_tool_description(self):
        pass

    async def execute(self, arguments):
        pass

# Test the tool
tool = TestTool(None, None)

# Test with single argument (old way that was failing)
error1 = tool._format_error("Site name is required")
print("Test 1 - Single argument (message only):")
print(f"  Result: {error1}")
print(f"  ✓ Success: {error1['success'] == False and error1['error']['message'] == 'Site name is required'}")

# Test with two arguments (correct way)
error2 = tool._format_error("validation_error", "Invalid input provided")
print("\nTest 2 - Two arguments (type + message):")
print(f"  Result: {error2}")
print(f"  ✓ Success: {error2['success'] == False and error2['error']['type'] == 'validation_error'}")

print("\n✓ Both methods work correctly!")
