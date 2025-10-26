#!/usr/bin/env python3
"""
Test script for PyArchInit Import/Export File Browser API
Tests CSRF exemption and endpoint functionality
"""

import requests
import json
import sys

BASE_URL = "http://localhost:5000"
API_ENDPOINT = f"{BASE_URL}/pyarchinit-import-export/api/pyarchinit/browse-files"

print("Testing CSRF Exemption for PyArchInit Import/Export API")
print("=" * 60)

def test_file_browser():
    """Test the file browser API endpoint"""

    print("=" * 60)
    print("Testing PyArchInit File Browser API")
    print("=" * 60)
    print("\nNOTE: These tests verify CSRF protection is exempted.")
    print("If you get 400 errors, CSRF exemption may not be working.")
    print("=" * 60)

    # Test 1: Empty path (should return home directory)
    print("\n1. Testing with empty path (home directory)...")
    print("   Testing without CSRF token (should work if exempted)...")
    try:
        response = requests.post(
            API_ENDPOINT,
            json={"path": ""},
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Success!")
            print(f"   Current Path: {data.get('current_path')}")
            print(f"   Items Found: {len(data.get('items', []))}")
        else:
            print(f"   ✗ Failed!")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Test 2: Valid path
    print("\n2. Testing with /Users path...")
    try:
        response = requests.post(
            API_ENDPOINT,
            json={"path": "/Users"},
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Success!")
            print(f"   Current Path: {data.get('current_path')}")
            print(f"   Items Found: {len(data.get('items', []))}")

            # Show first 3 items
            items = data.get('items', [])
            if items:
                print(f"   First 3 items:")
                for item in items[:3]:
                    item_type = "DIR" if item['is_dir'] else "FILE"
                    print(f"     [{item_type}] {item['name']}")
        else:
            print(f"   ✗ Failed!")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Test 3: Forbidden path (should return 403)
    print("\n3. Testing with forbidden path /etc...")
    try:
        response = requests.post(
            API_ENDPOINT,
            json={"path": "/etc"},
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status Code: {response.status_code}")

        if response.status_code == 403:
            print(f"   ✓ Correctly blocked forbidden directory!")
        else:
            data = response.json()
            print(f"   Response: {data.get('message')}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Test 4: Invalid path (should return 404)
    print("\n4. Testing with non-existent path...")
    try:
        response = requests.post(
            API_ENDPOINT,
            json={"path": "/this/path/does/not/exist"},
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status Code: {response.status_code}")

        if response.status_code == 404:
            print(f"   ✓ Correctly returned 404 for non-existent path!")
        else:
            data = response.json()
            print(f"   Response: {data.get('message')}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Test 5: Missing JSON data (should return 400)
    print("\n5. Testing with missing JSON data...")
    try:
        response = requests.post(
            API_ENDPOINT,
            data="not json",
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status Code: {response.status_code}")

        if response.status_code == 400:
            print(f"   ✓ Correctly returned 400 for invalid JSON!")
        else:
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    print("\nMake sure the Flask web server is running before running this test!")
    print("Press Enter to continue or Ctrl+C to cancel...")
    try:
        input()
    except KeyboardInterrupt:
        print("\nTest cancelled.")
        sys.exit(0)

    test_file_browser()
