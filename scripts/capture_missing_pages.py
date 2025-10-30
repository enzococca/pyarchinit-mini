#!/usr/bin/env python3
"""
Script to capture missing pages that failed in the main capture
"""
from playwright.sync_api import sync_playwright
import time
import os

BASE_URL = "http://localhost:5001"
SCREENSHOT_DIR = "docs/images/webapp"

def capture_page(page, url, filename, description, wait_time=5):
    """Navigate to URL and capture screenshot with extended wait time"""
    print(f"\n  📸 Capturing: {description}")
    print(f"     URL: {url}")

    # Navigate with extended timeout
    page.goto(url, wait_until="networkidle", timeout=30000)
    time.sleep(wait_time)  # Extra wait for dynamic content

    # Verify we're on the right page
    current_url = page.url
    print(f"     Current URL: {current_url}")

    # Take screenshot
    screenshot_path = os.path.join(SCREENSHOT_DIR, f"{filename}.png")
    page.screenshot(path=screenshot_path, full_page=True)
    print(f"     ✓ Saved: {screenshot_path}")

    return screenshot_path

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        # Login first
        print("🔐 Logging in...")
        page.goto(f"{BASE_URL}/auth/login")
        page.fill('input[name="username"]', 'admin')
        page.fill('input[name="password"]', 'admin')
        page.click('button[type="submit"]')
        time.sleep(3)
        print("  ✓ Logged in\n")

        # Set language to English
        page.goto(f"{BASE_URL}/auth/set-language/en")
        time.sleep(2)

        # Capture the 3 missing pages
        pages_to_capture = [
            ("/excel-import/", "051_excel_import_interface", "Excel Import Interface", 6),
            ("/pyarchinit-import-export/", "053_pyarchinit_ie_main", "PyArchInit Import/Export Main", 6),
            ("/em-node-config/", "058_em_node_config_interface", "EM Node Configuration", 5),
        ]

        for url, filename, description, wait_time in pages_to_capture:
            try:
                full_url = f"{BASE_URL}{url}"
                capture_page(page, full_url, filename, description, wait_time)
            except Exception as e:
                print(f"     ✗ Error: {e}")

        # Also capture the subsections of PyArchInit I/E by scrolling
        print("\n  📸 Capturing PyArchInit I/E subsections...")
        try:
            page.goto(f"{BASE_URL}/pyarchinit-import-export/", wait_until="networkidle")
            time.sleep(3)

            # Import section
            page.evaluate("window.scrollTo(0, 500)")
            time.sleep(2)
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, "054_pyarchinit_import_section.png"), full_page=False)
            print("     ✓ 054_pyarchinit_import_section.png")

            # Export section
            page.evaluate("window.scrollTo(0, 1000)")
            time.sleep(2)
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, "055_pyarchinit_export_section.png"), full_page=False)
            print("     ✓ 055_pyarchinit_export_section.png")

            # Create DB section
            page.evaluate("window.scrollTo(0, 1500)")
            time.sleep(2)
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, "056_pyarchinit_create_db.png"), full_page=False)
            print("     ✓ 056_pyarchinit_create_db.png")

        except Exception as e:
            print(f"     ✗ Error capturing subsections: {e}")

        browser.close()
        print("\n✅ Capture complete!")

if __name__ == "__main__":
    main()
