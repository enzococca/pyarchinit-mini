#!/usr/bin/env python3
"""Test batch_insert with correct fields including Date"""

import os
import sys
from datetime import datetime

os.environ["DATABASE_URL"] = "sqlite:///data/pyarchinit_tutorial.db"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pyarchinit_mini.mcp_server.tools.batch_insert_tool import batch_insert
from pyarchinit_mini.mcp_server.tools.insert_data_tool import insert_data

# First create test site
site_result = insert_data(
    table="site_table",
    data={
        "sito": "Test Date Field Site",
        "nazione": "Italia",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
)
print(f"Site created: {site_result.get('message')}\n")

# Now test batch insert with Date field
test_record = {
    "sito": "Test Date Field Site",
    "area": "1",
    "us": 99998,
    "unita_tipo": "US",
    "d_stratigrafica": "Strato",
    "data_schedatura": "2024-06-15",  # Date field as string - this should work now!
    "schedatore": "Test User",
    "created_at": "2024-06-15 10:00:00",
    "updated_at": "2024-06-15 10:00:00"
}

print("Testing batch_insert with Date field conversion...")
print("=" * 60)

result = batch_insert(
    table="us_table",
    records=[test_record],
    validate_only=False,
    stop_on_error=False
)

print(f"Success: {result.get('success')}")
print(f"Message: {result.get('message')}")

if result.get('success'):
    print(f"\n✓ SUCCESS! Date field conversion works perfectly!")
    print(f"  Inserted ID: {result.get('inserted_ids')}")
else:
    print(f"\n✗ Error: {result.get('error')}")
    if 'validation_errors' in result:
        for err in result['validation_errors']:
            print(f"  - {err.get('field')}: {err.get('message')}")

print("=" * 60)
