#!/usr/bin/env python3
"""
Test script to verify web login functionality
"""

import requests
from bs4 import BeautifulSoup
import sys

def test_login():
    """Test login with admin credentials"""
    base_url = "http://localhost:5001"

    # Create session
    session = requests.Session()

    # Get login page to retrieve CSRF token
    print("1. Fetching login page...")
    response = session.get(f"{base_url}/auth/login")

    if response.status_code != 200:
        print(f"✗ Failed to load login page: {response.status_code}")
        return False

    # Parse HTML to get CSRF token
    soup = BeautifulSoup(response.content, 'html.parser')
    csrf_token = soup.find('input', {'name': 'csrf_token'})

    if not csrf_token:
        print("✗ CSRF token not found in login page")
        print("Page content (first 500 chars):")
        print(response.text[:500])
        return False

    csrf_value = csrf_token.get('value')
    print(f"✓ CSRF token retrieved: {csrf_value[:20]}...")

    # Attempt login
    print("\n2. Attempting login with admin/admin...")
    login_data = {
        'username': 'admin',
        'password': 'admin',
        'csrf_token': csrf_value,
        'remember': 'on'
    }

    response = session.post(f"{base_url}/auth/login", data=login_data, allow_redirects=False)

    print(f"Response status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")

    if response.status_code == 302:
        redirect_url = response.headers.get('Location', '')
        print(f"✓ Login successful! Redirecting to: {redirect_url}")

        # Follow redirect
        response = session.get(redirect_url if redirect_url.startswith('http') else f"{base_url}{redirect_url}")
        print(f"✓ Dashboard loaded: {response.status_code}")
        return True
    else:
        print(f"✗ Login failed with status {response.status_code}")
        print("Response content:")
        print(response.text[:500])
        return False

if __name__ == "__main__":
    print("=== PyArchInit-Mini Login Test ===\n")
    print("Make sure the web server is running on http://localhost:5001")
    print("Start it with: python web_interface/app.py")
    print()

    input("Press Enter when server is ready...")

    success = test_login()

    if success:
        print("\n✓ Login test PASSED")
        sys.exit(0)
    else:
        print("\n✗ Login test FAILED")
        sys.exit(1)
