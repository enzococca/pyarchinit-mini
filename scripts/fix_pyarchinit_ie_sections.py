#!/usr/bin/env python3
"""
Fix PyArchInit Import/Export section screenshots with correct scrolling
"""
from playwright.sync_api import sync_playwright
import time
import os

BASE_URL = "http://localhost:5001"
SCREENSHOT_DIR = "docs/images/webapp"

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

        # Navigate to PyArchInit I/E page
        print("📸 Navigating to PyArchInit Import/Export page...")
        page.goto(f"{BASE_URL}/pyarchinit-import-export/", wait_until="networkidle")
        time.sleep(4)

        # Click on the Export tab to ensure it's visible
        print("  📸 Capturing Export section (055)...")
        try:
            # Click the Export to PyArchInit tab
            page.click('text="Export to PyArchInit"')
            time.sleep(2)

            # Scroll to show the export section
            page.evaluate("window.scrollTo(0, 800)")
            time.sleep(2)

            screenshot_path = os.path.join(SCREENSHOT_DIR, "055_pyarchinit_export_section.png")
            page.screenshot(path=screenshot_path, full_page=False)
            print(f"     ✓ Saved: {screenshot_path}")
        except Exception as e:
            print(f"     ✗ Error: {e}")

        # Click on the Create Database tab
        print("  📸 Capturing Create Database section (056)...")
        try:
            # Click the Create Empty Database tab
            page.click('text="Create Empty Database"')
            time.sleep(2)

            # Scroll to show the create DB section
            page.evaluate("window.scrollTo(0, 800)")
            time.sleep(2)

            screenshot_path = os.path.join(SCREENSHOT_DIR, "056_pyarchinit_create_db.png")
            page.screenshot(path=screenshot_path, full_page=False)
            print(f"     ✓ Saved: {screenshot_path}")
        except Exception as e:
            print(f"     ✗ Error: {e}")

        browser.close()
        print("\n✅ Recapture complete!")

if __name__ == "__main__":
    main()
