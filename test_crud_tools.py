#!/usr/bin/env python3
"""
Test script for CRUD + Validation tools (v1.9.11)

Tests all data management operations:
- get_schema
- insert
- update
- delete
- upsert (resolve_conflicts)
- validate_stratigraphy
"""

import os
import sys
from datetime import datetime

# Set database URL for testing
os.environ["DATABASE_URL"] = "sqlite:///data/pyarchinit_tutorial.db"

from pyarchinit_mini.mcp_server.tools.get_schema_tool import get_schema
from pyarchinit_mini.mcp_server.tools.insert_data_tool import insert_data
from pyarchinit_mini.mcp_server.tools.update_data_tool import update_data
from pyarchinit_mini.mcp_server.tools.delete_data_tool import delete_data
from pyarchinit_mini.mcp_server.tools.resolve_conflicts_tool import resolve_conflicts
from pyarchinit_mini.mcp_server.tools.validate_stratigraphy_tool import validate_stratigraphy


def print_section(title):
    """Print test section header"""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print(f"{'=' * 80}\n")


def print_result(test_name, result):
    """Print test result"""
    status = "✓ PASS" if result.get("success") else "✗ FAIL"
    print(f"{status} - {test_name}")
    if not result.get("success"):
        print(f"  Error: {result.get('error', 'Unknown error')}")
        print(f"  Message: {result.get('message', 'No message')}")
    else:
        print(f"  Message: {result.get('message', 'Success')}")
    print()


def test_get_schema():
    """Test 1: Get database schema"""
    print_section("TEST 1: Get Database Schema")

    # Test 1a: Get schema for us_table
    print("1a. Get schema for us_table with constraints and samples...")
    result = get_schema(
        table="us_table",
        include_constraints=True,
        include_sample_values=True
    )
    print_result("Get us_table schema", result)

    if result.get("success"):
        schema = result["schema"]
        print(f"  Database type: {schema['database_type']}")
        print(f"  Tables found: {list(schema['tables'].keys())}")
        if "us_table" in schema["tables"]:
            us_fields = schema["tables"]["us_table"]["fields"]
            print(f"  US table fields: {len(us_fields)}")
            print(f"  Sample field (unita_tipo): {us_fields.get('unita_tipo', {})}")

    # Test 1b: Get schema for all tables
    print("\n1b. Get schema for all tables (without samples)...")
    result = get_schema(include_constraints=False, include_sample_values=False)
    print_result("Get all tables schema", result)

    if result.get("success"):
        schema = result["schema"]
        print(f"  Total tables: {len(schema['tables'])}")
        print(f"  Tables: {', '.join(schema['tables'].keys())}")


def test_insert():
    """Test 2: Insert new data"""
    print_section("TEST 2: Insert New Data")

    # Test 2a: Validate only (dry-run)
    print("2a. Validate insert data (dry-run)...")
    now = datetime.now()
    test_data = {
        "sito": "Scavo archeologico",  # Use existing site
        "area": "999",
        "us": "9999",
        "unita_tipo": "US",
        "d_stratigrafica": "Test stratigraphic description",
        "d_interpretativa": "Test interpretation",
        "created_at": now,
        "updated_at": now
    }
    result = insert_data(
        table="us_table",
        data=test_data,
        validate_only=True
    )
    print_result("Validate insert (dry-run)", result)

    # Test 2b: Actually insert
    print("\n2b. Actually insert test data...")
    result = insert_data(
        table="us_table",
        data=test_data,
        validate_only=False
    )
    print_result("Insert test US", result)

    if result.get("success"):
        print(f"  Inserted ID: {result.get('inserted_id')}")
        return result.get("inserted_id")

    return None


def test_update(record_id):
    """Test 3: Update existing data"""
    print_section("TEST 3: Update Existing Data")

    if not record_id:
        print("Skipping update test - no record ID from insert")
        return

    # Test 3a: Update by ID
    print(f"3a. Update record ID {record_id}...")
    result = update_data(
        table="us_table",
        record_id=record_id,
        data={
            "d_stratigrafica": "Updated description via CRUD test",
            "d_interpretativa": "Updated interpretation"
        }
    )
    print_result(f"Update US ID {record_id}", result)

    if result.get("success"):
        print(f"  Rows updated: {result.get('rows_updated')}")


def test_upsert():
    """Test 4: Upsert (insert or update)"""
    print_section("TEST 4: Upsert (Insert or Update)")

    # Test 4a: Detect conflict (should find existing record)
    print("4a. Detect conflict for existing US 9999...")
    now = datetime.now()
    result = resolve_conflicts(
        table="us_table",
        data={
            "sito": "Scavo archeologico",  # Use existing site
            "area": "999",
            "us": "9999",
            "d_stratigrafica": "This should conflict",
            "created_at": now,
            "updated_at": now
        },
        conflict_keys=["sito", "area", "us"],
        resolution="detect"
    )
    print_result("Detect conflict", result)

    if result.get("success"):
        print(f"  Conflict detected: {result.get('conflict_detected')}")

    # Test 4b: Upsert (should update existing)
    print("\n4b. Upsert US 9999 (should update)...")
    now = datetime.now()
    result = resolve_conflicts(
        table="us_table",
        data={
            "sito": "Scavo archeologico",  # Use existing site
            "area": "999",
            "us": "9999",
            "d_stratigrafica": "Upserted description",
            "unita_tipo": "US",
            "created_at": now,
            "updated_at": now
        },
        conflict_keys=["sito", "area", "us"],
        resolution="upsert",
        merge_strategy="prefer_new"
    )
    print_result("Upsert existing US", result)

    if result.get("success"):
        print(f"  Action taken: {result.get('action_taken')}")
        print(f"  Conflict detected: {result.get('conflict_detected')}")


def test_validate_stratigraphy():
    """Test 5: Validate stratigraphic relationships"""
    print_section("TEST 5: Validate Stratigraphic Relationships")

    # Test 5a: Validate all without auto-fix
    print("5a. Validate all stratigraphic relationships (no auto-fix)...")
    result = validate_stratigraphy(
        check_chronology=False,
        auto_fix=False
    )
    print_result("Validate stratigraphy", result)

    if result.get("success"):
        print(f"  Valid: {result.get('valid')}")
        print(f"  Units checked: {result.get('units_checked')}")
        print(f"  Relationships found: {result.get('relationships_found')}")
        print(f"  Errors found: {result.get('error_count')}")

        if result.get('error_count', 0) > 0:
            categories = result.get('error_categories', {})
            print(f"\n  Error breakdown:")
            print(f"    Paradoxes: {len(categories.get('paradoxes', []))}")
            print(f"    Cycles: {len(categories.get('cycles', []))}")
            print(f"    Other: {len(categories.get('other_errors', []))}")


def test_delete(record_id):
    """Test 6: Delete data"""
    print_section("TEST 6: Delete Data")

    if not record_id:
        print("Skipping delete test - no record ID from insert")
        return

    # Test 6a: Dry-run delete
    print(f"6a. Dry-run delete of US ID {record_id}...")
    result = delete_data(
        table="us_table",
        record_id=record_id,
        confirm_delete=False,
        cascade_aware=True
    )
    print_result(f"Dry-run delete US ID {record_id}", result)

    if result.get("success") and result.get("dry_run"):
        dry_run_info = result.get("dry_run_info", {})
        print(f"  Records to delete: {dry_run_info.get('records_to_delete')}")
        cascade_warnings = result.get("cascade_warnings", [])
        if cascade_warnings:
            print(f"  Cascade warnings: {len(cascade_warnings)}")

    # Test 6b: Actually delete
    print(f"\n6b. Actually delete US ID {record_id}...")
    result = delete_data(
        table="us_table",
        record_id=record_id,
        confirm_delete=True,
        cascade_aware=True
    )
    print_result(f"Delete US ID {record_id}", result)

    if result.get("success"):
        print(f"  Rows deleted: {result.get('rows_deleted')}")


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("  PyArchInit-Mini CRUD + Validation Tools Test Suite (v1.9.11)")
    print("=" * 80)

    try:
        # Test 1: Get schema
        test_get_schema()

        # Test 2: Insert
        inserted_id = test_insert()

        # Test 3: Update
        test_update(inserted_id)

        # Test 4: Upsert
        test_upsert()

        # Test 5: Validate stratigraphy
        test_validate_stratigraphy()

        # Test 6: Delete (cleanup)
        test_delete(inserted_id)

        print("\n" + "=" * 80)
        print("  All tests completed!")
        print("=" * 80 + "\n")

    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
