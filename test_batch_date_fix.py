#!/usr/bin/env python3
"""Test batch_insert with Date fields"""

import os
import sys

os.environ["DATABASE_URL"] = "sqlite:///data/pyarchinit_tutorial.db"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pyarchinit_mini.mcp_server.tools.batch_insert_tool import batch_insert

# Test with a single US that has data_schedatura (Date field)
test_record = {
    "sito": "Test Date Field",
    "area": "1",
    "us": 9999,
    "unita_tipo": "US",
    "definizione_stratigrafica": "Strato",
    "data_schedatura": "2024-06-15",  # Date field as string
    "schedatore": "Test User"
}

print("Testing batch_insert with Date field...")
print("=" * 60)

result = batch_insert(
    table="us_table",
    records=[test_record],
    validate_only=False,
    stop_on_error=False
)

print(f"\nSuccess: {result.get('success')}")
print(f"Message: {result.get('message')}")

if result.get('success'):
    print(f"✓ Date field conversion works!")
    print(f"Inserted ID: {result.get('inserted_ids')}")
else:
    print(f"✗ Error: {result.get('error')}")

print("=" * 60)
