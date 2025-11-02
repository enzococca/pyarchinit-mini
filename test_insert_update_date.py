#!/usr/bin/env python3
"""Test insert_data and update_data with Date fields"""

import os
import sys
from datetime import datetime

os.environ["DATABASE_URL"] = "sqlite:///data/pyarchinit_tutorial.db"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pyarchinit_mini.mcp_server.tools.insert_data_tool import insert_data
from pyarchinit_mini.mcp_server.tools.update_data_tool import update_data

print("="*70)
print("TEST 1: insert_data con campo Date (data_schedatura)")
print("="*70)

# Test insert_data con Date field
test_record = {
    "sito": "Test Date Field Site",
    "area": "1",
    "us": 99997,
    "unita_tipo": "US",
    "d_stratigrafica": "Strato",
    "data_schedatura": "2024-11-02",  # Date field!
    "schedatore": "Test User",
    "created_at": datetime.now(),
    "updated_at": datetime.now()
}

result = insert_data(
    table="us_table",
    data=test_record
)

print(f"Success: {result.get('success')}")
print(f"Message: {result.get('message')}")

if result.get('success'):
    inserted_id = result.get('inserted_id')
    print(f"✓ INSERT SUCCESS! ID: {inserted_id}")

    print("\n" + "="*70)
    print("TEST 2: update_data con campo Date (data_schedatura)")
    print("="*70)

    # Test update_data con Date field
    update_result = update_data(
        table="us_table",
        record_id=inserted_id,
        data={
            "data_schedatura": "2024-12-25",  # Update Date field!
            "schedatore": "Updated User"
        }
    )

    print(f"Success: {update_result.get('success')}")
    print(f"Message: {update_result.get('message')}")
    print(f"Rows updated: {update_result.get('rows_updated')}")

    if update_result.get('success'):
        print(f"✓ UPDATE SUCCESS!")
    else:
        print(f"✗ UPDATE Error: {update_result.get('error')}")
else:
    print(f"✗ INSERT Error: {result.get('error')}")

print("="*70)
