#!/usr/bin/env python3
"""
Test script per verificare navigazione tab Bootstrap
"""
import sys
import time
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("✗ Playwright non installato")
    sys.exit(1)

BASE_URL = "http://localhost:5001"
OUTPUT_DIR = Path("docs/images/webapp/test")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def test_tabs():
    print("🧪 Testing Bootstrap tab navigation...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=1000)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})

        # Login
        page.goto(f"{BASE_URL}/auth/login")
        page.fill('input[name="username"]', 'admin')
        page.fill('input[name="password"]', 'admin')
        page.click('button[type="submit"]')
        page.wait_for_url(f"{BASE_URL}/")
        page.goto(f"{BASE_URL}/?lang=en")
        time.sleep(1)

        # Go to US new
        page.goto(f"{BASE_URL}/us/create")
        time.sleep(2)
        page.screenshot(path=str(OUTPUT_DIR / "01_us_tab1_basic.png"))
        print("✓ Tab 1 (Basic) - default active")

        # Try clicking tab 2 (Descriptions)
        page.click('button#description-tab')
        time.sleep(2)
        page.screenshot(path=str(OUTPUT_DIR / "02_us_tab2_descriptions.png"))
        print("✓ Tab 2 (Descriptions) clicked")

        # Try clicking tab 3 (Physical)
        page.click('button#physical-tab')
        time.sleep(2)
        page.screenshot(path=str(OUTPUT_DIR / "03_us_tab3_physical.png"))
        print("✓ Tab 3 (Physical) clicked")

        # Try clicking tab 4 (Chronology)
        page.click('button#chronology-tab')
        time.sleep(2)
        page.screenshot(path=str(OUTPUT_DIR / "04_us_tab4_chronology.png"))
        print("✓ Tab 4 (Chronology) clicked")

        # Try clicking tab 5 (Relationships)
        page.click('button#relationships-tab')
        time.sleep(2)
        page.screenshot(path=str(OUTPUT_DIR / "05_us_tab5_relationships.png"))
        print("✓ Tab 5 (Relationships) clicked")

        # Try clicking tab 6 (Documentation)
        page.click('button#documentation-tab')
        time.sleep(2)
        page.screenshot(path=str(OUTPUT_DIR / "06_us_tab6_documentation.png"))
        print("✓ Tab 6 (Documentation) clicked")

        browser.close()
        print("\n✅ Test completato! Controlla le immagini in:", OUTPUT_DIR.absolute())

if __name__ == "__main__":
    test_tabs()
