#!/usr/bin/env python3
"""
Record tutorial video showcasing Media Viewer features in PyArchInit-Mini v1.8.0/1.8.1

This script demonstrates:
- Image viewer with GLightbox
- PDF viewer
- Video viewer
- Excel/CSV viewer
- DOCX viewer
- 3D model viewer
- Media deletion functionality
"""

import os
import sys
import time
import urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

# Configuration
BASE_URL = "http://localhost:5001"
VIDEO_OUTPUT = "docs/tutorial_video/media_viewer_demo.webm"
DOWNLOAD_DIR = "/tmp/pyarchinit_media_samples"

# Sample files to download
SAMPLE_FILES = {
    'image': 'https://picsum.photos/800/600',  # Random image
    'pdf': 'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf',
    'video': 'https://sample-videos.com/video321/mp4/240/big_buck_bunny_240p_1mb.mp4',
    'excel': 'https://file-examples.com/wp-content/storage/2017/02/file_example_XLS_10.xls',
    'docx': 'https://file-examples.com/wp-content/storage/2017/02/file-sample_100kB.docx',
    '3d_obj': 'https://people.sc.fsu.edu/~jburkardt/data/obj/al.obj',  # Simple 3D model
}

def setup_downloads():
    """Create download directory and download sample files"""
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    downloaded_files = {}

    print("\n" + "="*80)
    print("DOWNLOADING SAMPLE MEDIA FILES")
    print("="*80 + "\n")

    for file_type, url in SAMPLE_FILES.items():
        ext = Path(url).suffix or ('.jpg' if file_type == 'image' else '')
        filename = f"sample_{file_type}{ext}"
        filepath = os.path.join(DOWNLOAD_DIR, filename)

        try:
            print(f"Downloading {file_type}: {url}")
            urllib.request.urlretrieve(url, filepath)
            downloaded_files[file_type] = filepath
            print(f"✓ Saved to: {filepath}")
        except Exception as e:
            print(f"✗ Failed to download {file_type}: {e}")
            # Create a placeholder file
            with open(filepath, 'wb') as f:
                f.write(b'placeholder')
            downloaded_files[file_type] = filepath

    return downloaded_files

def slow_type(page, selector, text, delay=50):
    """Type text slowly with delay between keystrokes"""
    page.fill(selector, "")
    for char in text:
        page.type(selector, char, delay=delay)

def wait_and_click(page, selector, timeout=5000):
    """Wait for element and click it"""
    try:
        page.wait_for_selector(selector, timeout=timeout)
        page.click(selector)
        time.sleep(0.3)
        return True
    except PlaywrightTimeout:
        print(f"Warning: Could not find selector: {selector}")
        return False

def login(page):
    """Login to the application"""
    print("\n" + "="*80)
    print("STEP 1: Login to PyArchInit-Mini")
    print("="*80 + "\n")

    page.goto(f"{BASE_URL}/login")
    page.wait_for_selector('input[name="username"]')

    slow_type(page, 'input[name="username"]', 'admin')
    slow_type(page, 'input[name="password"]', 'admin')
    page.click('button[type="submit"]')

    page.wait_for_url(f"{BASE_URL}/")
    time.sleep(1)

def create_site(page):
    """Create a new archaeological site"""
    print("\n" + "="*80)
    print("STEP 2: Create New Site - Media Viewer Demo Site")
    print("="*80 + "\n")

    page.goto(f"{BASE_URL}/sites")
    time.sleep(0.5)

    wait_and_click(page, 'a[href="/sites/new"]')
    page.wait_for_selector('input[name="sito"]')

    # Fill site details
    slow_type(page, 'input[name="sito"]', 'Media Viewer Demo Site', delay=30)
    slow_type(page, 'input[name="nazione"]', 'Italy', delay=30)
    slow_type(page, 'input[name="regione"]', 'Lazio', delay=30)
    slow_type(page, 'input[name="comune"]', 'Rome', delay=30)
    slow_type(page, 'textarea[name="descrizione"]',
              'Archaeological site created to demonstrate media viewer capabilities', delay=20)

    # Submit form
    page.click('button[type="submit"]')
    time.sleep(2)

def create_us(page, us_number, description, tipo='Strato'):
    """Create a stratigraphic unit"""
    print(f"\n{'='*80}")
    print(f"STEP 3.{us_number}: Create US {us_number} - {description}")
    print(f"{'='*80}\n")

    page.goto(f"{BASE_URL}/us")
    time.sleep(0.5)

    wait_and_click(page, 'a[href="/us/new"]')
    page.wait_for_selector('select[name="sito"]')

    # Select site
    page.select_option('select[name="sito"]', 'Media Viewer Demo Site')
    time.sleep(0.3)

    # Fill US details
    page.fill('input[name="area"]', '1')
    page.fill('input[name="us"]', str(us_number))

    # Select unita_tipo
    if page.query_selector('select[name="unita_tipo"]'):
        page.select_option('select[name="unita_tipo"]', tipo)

    slow_type(page, 'input[name="d_stratigrafica"]', f'US {us_number} Stratigraphic Definition', delay=20)
    slow_type(page, 'textarea[name="descrizione"]', description, delay=20)

    # Submit
    page.click('button[type="submit"]')
    time.sleep(2)

def create_material(page, numero_inventario, tipo_reperto, descrizione):
    """Create material/artifact with proper tipo_reperto selection"""
    print(f"\n{'='*80}")
    print(f"STEP 4: Create Material - {numero_inventario}")
    print(f"{'='*80}\n")

    page.goto(f"{BASE_URL}/inventario")
    time.sleep(0.5)

    wait_and_click(page, 'a[href="/inventario/new"]')
    page.wait_for_selector('select[name="sito"]')

    # Select site
    page.select_option('select[name="sito"]', 'Media Viewer Demo Site')
    time.sleep(0.3)

    # Fill basic info
    page.fill('input[name="numero_inventario"]', numero_inventario)

    # Switch to Classification tab
    print("   Switching to Classification tab")
    if wait_and_click(page, 'button[data-tab="classification"]'):
        time.sleep(0.5)

        # Select tipo_reperto - try different selectors
        tipo_selectors = [
            'select[name="tipo_reperto"]',
            '#tipo_reperto',
            'select#tipo_reperto'
        ]

        for selector in tipo_selectors:
            if page.query_selector(selector):
                try:
                    # Get available options
                    options = page.eval_on_selector(selector,
                        'el => Array.from(el.options).map(o => o.value)')
                    print(f"   Available tipo_reperto options: {options[:5]}...")

                    # Try to select the tipo_reperto
                    page.select_option(selector, tipo_reperto)
                    print(f"   ✓ Selected tipo_reperto: {tipo_reperto}")
                    time.sleep(0.3)
                    break
                except Exception as e:
                    print(f"   Could not select tipo_reperto with {selector}: {e}")

        # Fill descrizione
        slow_type(page, 'textarea[name="descrizione"]', descrizione, delay=20)

    # Submit
    page.click('button[type="submit"]')
    time.sleep(2)

def upload_media(page, entity_type, entity_name, file_path, description):
    """Upload media file to an entity"""
    print(f"\n   Uploading media: {Path(file_path).name}")

    # Go to media upload page
    page.goto(f"{BASE_URL}/media/upload")
    time.sleep(0.5)

    # Select entity type
    page.select_option('select[name="entity_type"]', entity_type)
    time.sleep(0.3)

    # Select entity
    page.select_option('select[name="entity_id"]', entity_name)
    time.sleep(0.3)

    # Upload file
    page.set_input_files('input[name="file"]', file_path)
    time.sleep(0.5)

    # Add description
    page.fill('textarea[name="description"]', description)

    # Submit
    page.click('button[type="submit"]')
    time.sleep(2)

def demonstrate_viewers(page):
    """Demonstrate all media viewers"""
    print(f"\n{'='*80}")
    print("STEP 5: Demonstrate Media Viewers")
    print(f"{'='*80}\n")

    # Go to media list
    page.goto(f"{BASE_URL}/media")
    time.sleep(1)

    print("   Viewing media list with all file types")
    time.sleep(2)

    # Scroll through the list
    page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
    time.sleep(1)

    # Click on an image to open lightbox
    print("   Opening image in lightbox viewer")
    image_selector = 'a.glightbox img'
    if page.query_selector(image_selector):
        wait_and_click(page, image_selector)
        time.sleep(2)
        # Close lightbox
        page.keyboard.press('Escape')
        time.sleep(1)

    # Try to open PDF viewer
    print("   Opening PDF in viewer")
    pdf_selector = 'i.fa-file-pdf'
    if page.query_selector(pdf_selector):
        wait_and_click(page, pdf_selector)
        time.sleep(2)
        page.keyboard.press('Escape')
        time.sleep(1)

    # Scroll to bottom
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(1)

def main():
    """Main recording function"""
    print("="*80)
    print("PyArchInit-Mini Media Viewer Tutorial Video Recording")
    print("Version 1.8.0/1.8.1 Features")
    print("="*80)

    # Download sample files
    files = setup_downloads()

    # Check if server is running
    print(f"\n{'='*80}")
    print("Checking if web server is running...")
    print(f"{'='*80}\n")

    import urllib.request
    max_retries = 5
    for i in range(max_retries):
        try:
            urllib.request.urlopen(f"{BASE_URL}/login", timeout=2)
            print(f"✓ Server is running on {BASE_URL}")
            break
        except:
            if i < max_retries - 1:
                print(f"Waiting for server... ({i+1}/{max_retries})")
                time.sleep(2)
            else:
                print(f"\n❌ Server is not running on {BASE_URL}")
                print("Please start the server first:")
                print(f"  DATABASE_URL=\"sqlite:///data/media_viewer_demo.db\" python3 -m pyarchinit_mini.web_interface.app")
                return

    print(f"\n{'='*80}")
    print("Starting browser and recording...")
    print(f"{'='*80}\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            slow_mo=100  # Slow down by 100ms to make it more stable
        )
        context = browser.new_context(
            viewport={'width': 1280, 'height': 720},
            record_video_dir="docs/tutorial_video/",
            record_video_size={'width': 1280, 'height': 720}
        )
        page = context.new_page()
        page.set_default_timeout(60000)  # 60 second timeout

        try:
            # Login
            login(page)

            # Create site
            create_site(page)

            # Create 3 US
            create_us(page, 2001,
                     'Foundation layer with stone blocks and mortar',
                     'Strato')
            create_us(page, 2002,
                     'Floor surface with ceramic tiles',
                     'Strato')
            create_us(page, 2003,
                     'Destruction layer with collapsed wall material',
                     'Strato')

            # Create 2 materials with tipo_reperto
            create_material(page, 'MDV-001',
                          'Ceramica',
                          'Terra sigillata bowl fragment with decoration')
            create_material(page, 'MDV-002',
                          'Metallo',
                          'Bronze coin from Imperial period')

            # Upload media files
            print(f"\n{'='*80}")
            print("STEP 5: Upload Media Files")
            print(f"{'='*80}\n")

            # Upload to site
            upload_media(page, 'site', 'Media Viewer Demo Site',
                        files['image'], 'Site overview photograph')
            upload_media(page, 'site', 'Media Viewer Demo Site',
                        files['pdf'], 'Site excavation report')

            # Upload to US
            upload_media(page, 'us', 'Media Viewer Demo Site - Area 1 - US 2001',
                        files['video'], 'Excavation process video')
            upload_media(page, 'us', 'Media Viewer Demo Site - Area 1 - US 2002',
                        files['excel'], 'Context data sheet')

            # Upload to materials
            upload_media(page, 'inventario', 'MDV-001',
                        files['docx'], 'Material analysis report')
            upload_media(page, 'inventario', 'MDV-002',
                        files['3d_obj'], '3D scan of artifact')

            # Demonstrate viewers
            demonstrate_viewers(page)

            print(f"\n{'='*80}")
            print("✅ RECORDING COMPLETE!")
            print(f"{'='*80}\n")

        except Exception as e:
            print(f"\n❌ Error during recording: {e}")
            import traceback
            traceback.print_exc()

        finally:
            # Close and save video
            context.close()
            browser.close()

            # Find the recorded video
            video_dir = Path("docs/tutorial_video")
            video_files = list(video_dir.glob("*.webm"))
            if video_files:
                latest_video = max(video_files, key=lambda p: p.stat().st_mtime)
                print(f"\n📹 Video file: {latest_video}")
                print(f"   Size: {latest_video.stat().st_size / 1024 / 1024:.1f} MB")

if __name__ == "__main__":
    main()
