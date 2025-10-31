#!/usr/bin/env python3
"""
Capture screenshots of Media Viewer features in PyArchInit-Mini v1.8.0/1.8.1
"""
import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:5001"
SCREENSHOT_DIR = "docs/images/webapp"
SAMPLE_FILES = "/tmp/pyarchinit_media_samples"

def take_screenshot(page, name):
    """Take a screenshot with a descriptive name"""
    filepath = f"{SCREENSHOT_DIR}/{name}.png"
    page.screenshot(path=filepath)
    print(f"  📸 {name}")
    return filepath

def main():
    print("="*80)
    print("PyArchInit-Mini Media Viewers Screenshot Capture")
    print("="*80 + "\n")

    # Ensure screenshot directory exists
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    os.makedirs(SAMPLE_FILES, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={'width': 1280, 'height': 720})

        try:
            # Login
            print("\n🔐 Login...")
            page.goto(f"{BASE_URL}/login")
            page.fill('input[name="username"]', 'admin')
            page.fill('input[name="password"]', 'admin')
            page.click('button[type="submit"]')
            page.wait_for_url(f"{BASE_URL}/")
            time.sleep(1)

            # Check if we have sample files, if not use existing media
            sample_files_exist = Path(f"{SAMPLE_FILES}/sample_image.jpg").exists()

            if sample_files_exist:
                print("\n📤 Uploading sample media files...")

                # Go to sites to get first site
                page.goto(f"{BASE_URL}/sites")
                time.sleep(0.5)

                # Try to get first site name
                site_selector = 'table tbody tr:first-child td:first-child a'
                if page.query_selector(site_selector):
                    site_name = page.text_content(site_selector)
                    print(f"   Using site: {site_name}")

                    # Upload image
                    if Path(f"{SAMPLE_FILES}/sample_image.jpg").exists():
                        page.goto(f"{BASE_URL}/media/upload")
                        page.select_option('select[name="entity_type"]', 'site')
                        time.sleep(0.3)
                        page.select_option('select[name="entity_id"]', site_name)
                        page.set_input_files('input[name="file"]', f"{SAMPLE_FILES}/sample_image.jpg")
                        page.fill('textarea[name="description"]', 'Sample archaeological site photo')
                        page.click('button[type="submit"]')
                        time.sleep(1)

                    # Upload PDF
                    if Path(f"{SAMPLE_FILES}/sample_pdf.pdf").exists():
                        page.goto(f"{BASE_URL}/media/upload")
                        page.select_option('select[name="entity_type"]', 'site')
                        time.sleep(0.3)
                        page.select_option('select[name="entity_id"]', site_name)
                        page.set_input_files('input[name="file"]', f"{SAMPLE_FILES}/sample_pdf.pdf")
                        page.fill('textarea[name="description"]', 'Site excavation report')
                        page.click('button[type="submit"]')
                        time.sleep(1)

                    # Upload Excel
                    if Path(f"{SAMPLE_FILES}/sample_excel.xls").exists():
                        page.goto(f"{BASE_URL}/media/upload")
                        page.select_option('select[name="entity_type"]', 'site')
                        time.sleep(0.3)
                        page.select_option('select[name="entity_id"]', site_name)
                        page.set_input_files('input[name="file"]', f"{SAMPLE_FILES}/sample_excel.xls")
                        page.fill('textarea[name="description"]', 'Site data spreadsheet')
                        page.click('button[type="submit"]')
                        time.sleep(1)

                    # Upload DOCX
                    if Path(f"{SAMPLE_FILES}/sample_docx.docx").exists():
                        page.goto(f"{BASE_URL}/media/upload")
                        page.select_option('select[name="entity_type"]', 'site')
                        time.sleep(0.3)
                        page.select_option('select[name="entity_id"]', site_name)
                        page.set_input_files('input[name="file"]', f"{SAMPLE_FILES}/sample_docx.docx")
                        page.fill('textarea[name="description"]', 'Material analysis report')
                        page.click('button[type="submit"]')
                        time.sleep(1)

                    # Upload 3D OBJ
                    if Path(f"{SAMPLE_FILES}/sample_3d_obj.obj").exists():
                        page.goto(f"{BASE_URL}/media/upload")
                        page.select_option('select[name="entity_type"]', 'site')
                        time.sleep(0.3)
                        page.select_option('select[name="entity_id"]', site_name)
                        page.set_input_files('input[name="file"]', f"{SAMPLE_FILES}/sample_3d_obj.obj")
                        page.fill('textarea[name="description"]', '3D scan of artifact')
                        page.click('button[type="submit"]')
                        time.sleep(1)

            # Go to media list
            print("\n📸 Capturing Media Viewer Screenshots...")
            page.goto(f"{BASE_URL}/media")
            time.sleep(1)

            # Screenshot 1: Media list page
            take_screenshot(page, "072_media_list_with_files")

            # Scroll to show all media
            page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
            time.sleep(0.5)
            take_screenshot(page, "073_media_list_scrolled")

            # Try to find and click on image to open GLightbox
            print("\n   Opening Image Viewer (GLightbox)...")
            img_link = page.query_selector('a.glightbox')
            if img_link:
                img_link.click()
                time.sleep(1)
                take_screenshot(page, "074_media_image_viewer_glightbox")
                page.keyboard.press('Escape')
                time.sleep(0.5)

            # Try to find PDF and click to view
            print("   Opening PDF Viewer...")
            pdf_icons = page.query_selector_all('i.fa-file-pdf')
            if pdf_icons:
                # Click parent link of first PDF icon
                pdf_link = pdf_icons[0].evaluate('el => el.closest("a")')
                if pdf_link:
                    page.click('i.fa-file-pdf')
                    time.sleep(1)
                    take_screenshot(page, "075_media_pdf_viewer")
                    page.keyboard.press('Escape')
                    time.sleep(0.5)

            # Try to find Excel and click to view
            print("   Opening Excel Viewer...")
            excel_icons = page.query_selector_all('i.fa-file-excel')
            if excel_icons:
                excel_icons[0].evaluate('el => el.closest("a")').click() if excel_icons[0].evaluate('el => el.closest("a")') else None
                page.click('i.fa-file-excel')
                time.sleep(1)
                take_screenshot(page, "076_media_excel_viewer")
                page.keyboard.press('Escape')
                time.sleep(0.5)

            # Try to find DOCX and click to view
            print("   Opening DOCX Viewer...")
            docx_icons = page.query_selector_all('i.fa-file-word')
            if docx_icons:
                page.click('i.fa-file-word')
                time.sleep(1)
                take_screenshot(page, "077_media_docx_viewer")
                page.keyboard.press('Escape')
                time.sleep(0.5)

            # Try to find 3D model and click to view
            print("   Opening 3D Model Viewer...")
            model_icons = page.query_selector_all('i.fa-cube')
            if model_icons:
                page.click('i.fa-cube')
                time.sleep(2)  # 3D viewer needs more time to load
                take_screenshot(page, "078_media_3d_viewer")
                page.keyboard.press('Escape')
                time.sleep(0.5)

            # Scroll back to top
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(0.5)

            print("\n" + "="*80)
            print("✅ Screenshot capture completed!")
            print(f"Screenshots saved to: {SCREENSHOT_DIR}")
            print("="*80)

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

        finally:
            browser.close()

if __name__ == "__main__":
    main()
