#!/usr/bin/env python3
"""
Screenshot automation for PyArchInit-Mini Web GUI Documentation
Captures all main pages and features for documentation
"""

import os
import time
from pathlib import Path

# Try to import playwright
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False
    print("Playwright not installed. Install with: pip install playwright")
    print("Then run: playwright install chromium")

# Configuration
BASE_URL = "http://localhost:5001"
OUTPUT_DIR = Path("docs/screenshots/web_gui")
USERNAME = "admin"
PASSWORD = "admin"

# Pages to screenshot (in logical order for documentation)
PAGES = [
    # Authentication
    ("01_login", "/auth/login", "Login Page"),

    # Dashboard
    ("02_dashboard", "/", "Main Dashboard"),

    # Sites Management
    ("03_sites_list", "/sites", "Sites List"),
    ("04_sites_form", "/sites/new", "Site Form (Create)"),

    # US (Stratigraphic Units) Management
    ("05_us_list", "/us", "US List"),
    ("06_us_form", "/us/new", "US Form (Create)"),

    # Inventario (Inventory) Management
    ("07_inventario_list", "/inventario", "Inventory List"),
    ("08_inventario_form", "/inventario/new", "Inventory Form (Create)"),

    # Harris Matrix
    ("09_harris_matrix", "/harris-matrix", "Harris Matrix Visualization"),
    ("10_harris_graphml", "/harris-matrix/graphml", "GraphML Export"),

    # Harris Matrix Creator
    ("11_harris_creator", "/harris-creator", "Harris Matrix Interactive Creator"),

    # Excel Import
    ("12_excel_import", "/excel-import", "Excel Import Interface"),

    # PyArchInit Import/Export
    ("13_pyarchinit_import", "/pyarchinit-import-export", "PyArchInit Import/Export"),

    # Extended Matrix Node Config
    ("14_em_node_config", "/em-node-config", "Extended Matrix Node Configuration"),

    # Analytics Dashboard
    ("15_analytics", "/analytics", "Analytics Dashboard"),

    # Validation
    ("16_validation", "/validation", "Stratigraphic Validation"),

    # Export/Import
    ("17_export_import", "/export-import", "Export/Import"),

    # Thesaurus
    ("18_thesaurus", "/thesaurus", "Thesaurus Management"),

    # Periodization
    ("19_periodizzazione", "/periodizzazione", "Periodization Management"),

    # Chronology
    ("20_datazioni", "/datazioni", "Chronology Management"),

    # Media Upload
    ("21_media_upload", "/media/upload", "Media Upload"),

    # User Management
    ("22_users", "/auth/users", "User Management"),

    # Database Management
    ("23_database_info", "/admin/database", "Database Information"),
    ("24_database_upload", "/admin/database/upload", "Database Upload"),
    ("25_database_connect", "/admin/database/connect", "Database Connect"),
]


def take_screenshots():
    """Take screenshots of all pages"""
    if not HAS_PLAYWRIGHT:
        return False

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Starting screenshot capture...")
    print(f"Output directory: {OUTPUT_DIR.absolute()}")
    print(f"Base URL: {BASE_URL}")
    print(f"Total pages: {len(PAGES)}")
    print()

    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='it-IT'
        )
        page = context.new_page()

        # First, login
        print("Logging in...")
        try:
            page.goto(f"{BASE_URL}/auth/login", wait_until='networkidle')
            page.fill('input[name="username"]', USERNAME)
            page.fill('input[name="password"]', PASSWORD)
            page.click('button[type="submit"]')
            page.wait_for_url(f"{BASE_URL}/", timeout=10000)
            print("✓ Login successful\n")
        except Exception as e:
            print(f"✗ Login failed: {e}")
            browser.close()
            return False

        # Take screenshot of each page
        successful = 0
        failed = 0

        for filename, url, description in PAGES:
            print(f"Capturing: {description}")
            print(f"  URL: {url}")

            try:
                # Navigate to page
                full_url = f"{BASE_URL}{url}"
                page.goto(full_url, wait_until='networkidle', timeout=30000)

                # Wait a bit for any dynamic content
                time.sleep(1)

                # Take screenshot
                output_path = OUTPUT_DIR / f"{filename}.png"
                page.screenshot(path=str(output_path), full_page=True)

                print(f"  ✓ Saved: {output_path.name}")
                successful += 1

            except PlaywrightTimeout:
                print(f"  ✗ Timeout loading page")
                failed += 1
            except Exception as e:
                print(f"  ✗ Error: {e}")
                failed += 1

            print()

        # Close browser
        browser.close()

        # Summary
        print("=" * 60)
        print(f"Screenshot capture complete!")
        print(f"Successful: {successful}/{len(PAGES)}")
        print(f"Failed: {failed}/{len(PAGES)}")
        print(f"Output directory: {OUTPUT_DIR.absolute()}")
        print("=" * 60)

        return failed == 0


if __name__ == "__main__":
    if not HAS_PLAYWRIGHT:
        print("\nTo install Playwright:")
        print("  pip install playwright")
        print("  playwright install chromium")
        exit(1)

    success = take_screenshots()
    exit(0 if success else 1)
