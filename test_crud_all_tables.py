#!/usr/bin/env python3
"""
Test CRUD tools with ALL database tables (including users, media, periodization, etc.)
This verifies the removal of hardcoded table limitations.
"""

import os
os.environ["DATABASE_URL"] = "sqlite:///data/pyarchinit_tutorial.db"

from pyarchinit_mini.mcp_server.tools.get_schema_tool import get_schema
from pyarchinit_mini.mcp_server.tools.insert_data_tool import insert_data

print("=" * 80)
print("Testing CRUD tools with ALL database tables")
print("=" * 80)

# Test 1: get_schema with ALL tables
print("\n1. Testing get_schema() with ALL tables...")
result = get_schema()
if result["success"]:
    tables = result["schema"]["tables"]
    print(f"✓ SUCCESS: Found {len(tables)} tables in database:")
    for table_name in sorted(tables.keys()):
        field_count = len(tables[table_name]["fields"])
        print(f"  - {table_name}: {field_count} fields")
else:
    print(f"✗ FAILED: {result.get('message')}")

# Test 2: get_schema with 'users' table (previously not allowed)
print("\n2. Testing get_schema(table='users')...")
result = get_schema(table="users")
if result["success"]:
    fields = result["schema"]["tables"]["users"]["fields"]
    print(f"✓ SUCCESS: users table has {len(fields)} fields:")
    for field_name, field_info in fields.items():
        print(f"  - {field_name}: {field_info['type']} (required={field_info['required']})")
else:
    print(f"✗ FAILED: {result.get('message')}")

# Test 3: Verify insert_data accepts 'users' table (validation only)
print("\n3. Testing insert_data validation with 'users' table...")
result = insert_data(
    table="users",
    data={
        "username": "test_user",
        "email": "test@example.com",
        "role": "viewer"
    },
    validate_only=True
)
if result["success"]:
    print(f"✓ SUCCESS: users table is now accepted by insert_data!")
    print(f"  Message: {result['message']}")
else:
    print(f"✗ FAILED: {result.get('message')}")
    if "validation_errors" in result:
        for err in result["validation_errors"]:
            print(f"  - {err['field']}: {err['message']}")

# Test 4: Test with invalid table name
print("\n4. Testing with non-existent table 'fake_table'...")
result = get_schema(table="fake_table")
if not result["success"] and result["error"] == "table_not_found":
    print(f"✓ SUCCESS: Correctly rejected non-existent table")
    print(f"  Message: {result['message']}")
    print(f"  Available tables: {len(result.get('available_tables', []))} tables found")
else:
    print(f"✗ FAILED: Should have rejected fake_table")

print("\n" + "=" * 80)
print("Test complete! CRUD tools now support ALL database tables.")
print("=" * 80)
