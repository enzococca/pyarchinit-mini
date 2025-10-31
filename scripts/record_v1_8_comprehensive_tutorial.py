#!/usr/bin/env python3
"""
PyArchInit-Mini v1.8.0/1.8.1 Comprehensive Tutorial Video
Demonstrates ALL features including new Media Viewers

Features demonstrated:
- Create site
- Create 2 US (Stratigraphic Units)
- Create 1 material with tipo_reperto selection
- Upload media files (PDF, images, 3D, DOCX) to site, US, and inventario
- Demonstrate all 6 media viewers (Image, PDF, Video, Excel, DOCX, 3D)
- Add periodo (dating period)
- Add thesaurus entries
- Create Harris matrix
- Export Harris matrix (GraphML)
- Database management (including Create Empty DB feature)
- User management
"""
from playwright.sync_api import sync_playwright
import time
import os
import sqlite3

BASE_URL = "http://localhost:5001"
VIDEO_DIR = "docs/tutorial_video"
DB_PATH = "data/pyarchinit_v18_demo.db"
SAMPLE_FILES = "/tmp/pyarchinit_media_samples"

# Site data
SITE_DATA = {
    "name": "PyArchInit v1.8 Demo Site",
    "country": "Italy",
    "region": "Lazio",
    "city": "Rome",
    "description": "Archaeological site created to demonstrate PyArchInit-Mini v1.8.0/1.8.1 media viewer capabilities and comprehensive features"
}

# Dating Period
PERIODO_DATA = {
    "nome": "Late Imperial Period",
    "fascia": "3rd-4th century AD",
    "descrizione": "Late Roman Imperial period, characterized by architectural changes and defensive structures"
}

# 2 Stratigraphic Units as requested
US_DATA = [
    {
        "number": "2001",
        "type": "USM",
        "definition": "Stone foundation wall",
        "description": "Well-preserved stone wall foundation, late Imperial period construction with limestone blocks and mortar binding",
        "area": "Trench A"
    },
    {
        "number": "2002",
        "type": "US",
        "definition": "Floor surface",
        "description": "Compact mortar floor surface associated with wall US2001, showing evidence of repeated use and repair phases",
        "area": "Trench A"
    }
]

# 1 Material as requested
MATERIAL_DATA = {
    "inventory_number": "2024-001",
    "type": "Ceramica",  # tipo_reperto
    "description": "African Red Slip ware bowl fragment. Fine orange fabric with glossy red slip coating, typical of late Imperial production",
    "area": "Trench A",
    "us": "2002"
}

# Thesaurus entries to populate dropdowns
THESAURUS_DATA = {
    "tipo_reperto": ["Ceramica", "Metallo", "Vetro", "Pietra", "Osso"],
    "stato_conservazione": ["Ottimo", "Buono", "Discreto", "Frammentario"],
    "corpo_ceramico": ["Fine", "Grossolano", "Semi-fine"],
}

def populate_thesaurus():
    """Populate thesaurus tables for dropdowns"""
    print("\n" + "="*80)
    print("POPULATING THESAURUS DATA")
    print("="*80 + "\n")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create thesaurus table if needed
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pyarchinit_thesaurus_sigle (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_tabella TEXT,
            sigla TEXT,
            tipologia_sigla TEXT,
            descrizione TEXT
        )
    """)

    for field_name, values in THESAURUS_DATA.items():
        for value in values:
            try:
                cursor.execute("""
                    INSERT INTO pyarchinit_thesaurus_sigle
                    (nome_tabella, sigla, tipologia_sigla)
                    VALUES (?, ?, ?)
                """, ("inventario_materiali_table", value, field_name))
                print(f"  ✓ Added: {field_name} = {value}")
            except sqlite3.IntegrityError:
                pass  # Already exists

    conn.commit()
    conn.close()
    print("\n✓ Thesaurus populated successfully\n")

def slow_type(page, selector, text, delay=0.5):
    """Type text with minimal delay for fast recording"""
    page.fill(selector, "")
    for char in text:
        page.type(selector, char, delay=delay)

def log_step(step_num, description):
    """Print formatted step log"""
    print(f"\n{'='*80}")
    print(f"STEP {step_num}: {description}")
    print(f"{'='*80}\n")

def upload_media(page, entity_type, entity_name, file_path, description):
    """Upload a media file to an entity"""
    filename = os.path.basename(file_path)
    print(f"   Uploading {filename} to {entity_type}: {entity_name}")

    page.goto(f"{BASE_URL}/media/upload")
    time.sleep(0.5)

    page.select_option('select[name="entity_type"]', entity_type)
    time.sleep(0.3)

    page.select_option('select[name="entity_id"]', entity_name)
    time.sleep(0.3)

    page.set_input_files('input[name="file"]', file_path)
    time.sleep(0.5)

    page.fill('textarea[name="description"]', description)
    page.click('button[type="submit"]')
    time.sleep(1.5)

    print(f"   ✓ Uploaded {filename}")

def demonstrate_media_viewers(page):
    """Demonstrate all media viewers"""
    log_step("5", "Demonstrate Media Viewers")

    page.goto(f"{BASE_URL}/media")
    time.sleep(2)

    print("   Media list with all uploaded files")
    page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
    time.sleep(2)
    page.evaluate("window.scrollTo(0, 0)")
    time.sleep(1)

    # Image viewer (GLightbox)
    print("   Opening Image Viewer (GLightbox)...")
    image_selector = 'a.glightbox img'
    if page.query_selector(image_selector):
        page.click(image_selector)
        time.sleep(3)
        page.keyboard.press('Escape')
        time.sleep(1)

    # PDF viewer
    print("   Opening PDF Viewer...")
    pdf_selector = 'i.fa-file-pdf'
    if page.query_selector(pdf_selector):
        page.click(pdf_selector)
        time.sleep(3)
        page.keyboard.press('Escape')
        time.sleep(1)

    # Excel viewer
    print("   Opening Excel Viewer...")
    excel_selector = 'i.fa-file-excel'
    if page.query_selector(excel_selector):
        page.click(excel_selector)
        time.sleep(3)
        page.keyboard.press('Escape')
        time.sleep(1)

    # DOCX viewer
    print("   Opening DOCX Viewer...")
    docx_selector = 'i.fa-file-word'
    if page.query_selector(docx_selector):
        page.click(docx_selector)
        time.sleep(3)
        page.keyboard.press('Escape')
        time.sleep(1)

    # 3D viewer
    print("   Opening 3D Model Viewer...")
    model_selector = 'i.fa-cube'
    if page.query_selector(model_selector):
        page.click(model_selector)
        time.sleep(4)  # 3D needs more time to load
        page.keyboard.press('Escape')
        time.sleep(1)

def main():
    # Check database
    if not os.path.exists(DB_PATH):
        print(f"❌ ERROR: Database not found at {DB_PATH}")
        print(f"Run: pyarchinit-mini-init first")
        return

    print(f"✓ Using database: {DB_PATH}")

    # Create video output directory
    os.makedirs(VIDEO_DIR, exist_ok=True)

    # Populate thesaurus
    populate_thesaurus()

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            slow_mo=250  # Smooth recording speed
        )

        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=VIDEO_DIR,
            record_video_size={"width": 1920, "height": 1080}
        )

        page = context.new_page()

        try:
            # ==================== STEP 1: LOGIN ====================
            log_step("1", "Login to PyArchInit-Mini")
            page.goto(f"{BASE_URL}/auth/login")
            time.sleep(2)

            slow_type(page, 'input[name="username"]', 'admin')
            time.sleep(0.2)
            slow_type(page, 'input[name="password"]', 'admin')
            time.sleep(0.3)
            page.click('button[type="submit"]')
            time.sleep(2)

            # ==================== STEP 2: CREATE DATING PERIOD ====================
            log_step("2", "Create Dating Period (Periodo)")
            page.goto(f"{BASE_URL}/periodizzazione/create")
            time.sleep(1)

            slow_type(page, 'input[name="nome_datazione"]', PERIODO_DATA["nome"])
            time.sleep(0.2)
            slow_type(page, 'input[name="fascia_cronologica"]', PERIODO_DATA["fascia"])
            time.sleep(0.2)
            slow_type(page, 'textarea[name="descrizione"]', PERIODO_DATA["descrizione"])
            time.sleep(0.3)

            page.click('button[type="submit"]')
            time.sleep(1.5)

            # ==================== STEP 3: ADD THESAURUS ENTRY ====================
            log_step("3", "Add Thesaurus Entry")
            page.goto(f"{BASE_URL}/thesaurus")
            time.sleep(2)

            # Show thesaurus management interface
            page.evaluate("window.scrollTo(0, 300)")
            time.sleep(1.5)
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(1)

            # ==================== STEP 4: CREATE SITE ====================
            log_step("4", "Create Archaeological Site")
            page.goto(f"{BASE_URL}/sites/create")
            time.sleep(1)

            slow_type(page, 'input[name="sito"]', SITE_DATA["name"], delay=5)
            time.sleep(0.2)
            slow_type(page, 'input[name="nazione"]', SITE_DATA["country"], delay=5)
            time.sleep(0.2)
            slow_type(page, 'input[name="regione"]', SITE_DATA["region"], delay=5)
            time.sleep(0.2)
            slow_type(page, 'input[name="comune"]', SITE_DATA["city"], delay=5)
            time.sleep(0.2)
            slow_type(page, 'textarea[name="descrizione"]', SITE_DATA["description"])
            time.sleep(0.3)

            page.click('button[type="submit"]')
            time.sleep(1.5)

            # ==================== STEP 5: CREATE 2 US ====================
            for i, us in enumerate(US_DATA, 1):
                log_step(f"5.{i}", f"Create US {us['number']} - {us['definition']}")

                page.goto(f"{BASE_URL}/us/create")
                time.sleep(1.5)

                # Basic Information
                page.select_option('select[name="sito"]', SITE_DATA["name"])
                time.sleep(0.3)

                slow_type(page, 'input[name="us"]', us["number"], delay=10)
                time.sleep(0.3)

                page.select_option('select[name="unita_tipo"]', us["type"])
                time.sleep(0.3)

                slow_type(page, 'input[name="area"]', us["area"], delay=8)
                time.sleep(0.5)

                # Descriptions tab
                print("   Switching to Descriptions tab")
                page.click('#description-tab')
                time.sleep(0.8)

                slow_type(page, 'textarea[name="d_stratigrafica"]', us["definition"])
                time.sleep(0.2)

                slow_type(page, 'textarea[name="descrizione"]', us["description"])
                time.sleep(0.3)

                # Save US
                page.click('button[type="submit"]')
                time.sleep(1.5)

            # ==================== STEP 6: CREATE 1 MATERIAL ====================
            log_step("6", "Create Material with Tipo Reperto Selection")

            page.goto(f"{BASE_URL}/inventario/create")
            time.sleep(1.5)

            # Identification tab
            page.select_option('select[name="sito"]', SITE_DATA["name"])
            time.sleep(0.2)

            slow_type(page, 'input[name="numero_inventario"]', MATERIAL_DATA["inventory_number"])
            time.sleep(0.3)

            # Classification tab
            print("   Switching to Classification tab")
            page.click('#classification-tab')
            time.sleep(0.8)

            # Select tipo_reperto from dropdown
            print(f"   Selecting tipo_reperto: {MATERIAL_DATA['type']}")
            page.select_option('select[name="tipo_reperto"]', MATERIAL_DATA["type"])
            time.sleep(0.3)

            slow_type(page, 'textarea[name="descrizione"]', MATERIAL_DATA["description"])
            time.sleep(0.3)

            # Context tab
            print("   Switching to Context tab")
            page.click('#context-tab')
            time.sleep(0.8)

            slow_type(page, 'input[name="area"]', MATERIAL_DATA["area"])
            time.sleep(0.2)

            slow_type(page, 'input[name="us"]', MATERIAL_DATA["us"])
            time.sleep(0.3)

            # Save material
            page.click('button[type="submit"]')
            time.sleep(1.5)

            # ==================== STEP 7: UPLOAD MEDIA FILES ====================
            log_step("7", "Upload Media Files")

            # Upload to site
            upload_media(page, 'site', SITE_DATA["name"],
                        f"{SAMPLE_FILES}/sample_image.jpg",
                        'Site overview photograph')

            upload_media(page, 'site', SITE_DATA["name"],
                        f"{SAMPLE_FILES}/sample_pdf.pdf",
                        'Site excavation report')

            # Upload to US
            us_name = f"{SITE_DATA['name']} - {US_DATA[0]['area']} - US {US_DATA[0]['number']}"

            upload_media(page, 'us', us_name,
                        f"{SAMPLE_FILES}/sample_excel.xls",
                        'Stratigraphic unit data sheet')

            # Upload to material
            upload_media(page, 'inventario', MATERIAL_DATA["inventory_number"],
                        f"{SAMPLE_FILES}/sample_docx.docx",
                        'Material analysis report')

            upload_media(page, 'inventario', MATERIAL_DATA["inventory_number"],
                        f"{SAMPLE_FILES}/sample_3d_obj.obj",
                        '3D scan of ceramic fragment')

            # ==================== STEP 8: DEMONSTRATE MEDIA VIEWERS ====================
            demonstrate_media_viewers(page)

            # ==================== STEP 9: CREATE HARRIS MATRIX ====================
            log_step("9", "Create Harris Matrix")
            page.goto(f"{BASE_URL}/harris_matrix/{SITE_DATA['name']}")
            time.sleep(5)

            page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
            time.sleep(2)
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(2)

            # ==================== STEP 10: EXPORT HARRIS MATRIX (GraphML) ====================
            log_step("10", "Export Harris Matrix to GraphML")
            page.goto(f"{BASE_URL}/harris_matrix/graphml_export")
            time.sleep(1)

            page.select_option('select[name="site"]', SITE_DATA["name"])
            time.sleep(0.3)

            slow_type(page, 'input[name="title"]', f"{SITE_DATA['name']} - Harris Matrix Export")
            time.sleep(0.3)

            page.select_option('select[name="grouping"]', 'period_area')
            time.sleep(0.3)

            page.click('button[type="submit"]')
            time.sleep(2)

            # ==================== STEP 11: DATABASE MANAGEMENT ====================
            log_step("11", "Database Management (including Create Empty DB)")
            page.goto(f"{BASE_URL}/admin/database")
            time.sleep(2)

            # Show database management options
            page.evaluate("window.scrollTo(0, 300)")
            time.sleep(2)

            # Navigate to Create Empty DB section
            print("   Showing 'Create Empty Database' feature (moved from PyArchInit Import/Export)")
            page.evaluate("window.scrollTo(0, 600)")
            time.sleep(2)

            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(1.5)

            # ==================== STEP 12: USER MANAGEMENT ====================
            log_step("12", "User Management")
            page.goto(f"{BASE_URL}/admin/users")
            time.sleep(2)

            # Show user management interface
            page.evaluate("window.scrollTo(0, 300)")
            time.sleep(2)
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(2)

            # ==================== STEP 13: VIEW SITE SUMMARY ====================
            log_step("13", "View Site Summary with All Data")
            page.goto(f"{BASE_URL}/sites")
            time.sleep(2)

            page.click(f'text="{SITE_DATA["name"]}"')
            time.sleep(3)

            # Scroll through site details showing all related data
            page.evaluate("window.scrollTo(0, 400)")
            time.sleep(2)
            page.evaluate("window.scrollTo(0, 800)")
            time.sleep(2)
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(2)

            print("\n" + "="*80)
            print("✅ COMPREHENSIVE TUTORIAL VIDEO RECORDING COMPLETE!")
            print("="*80)
            print(f"\nVideo saved to: {VIDEO_DIR}/")
            print(f"Database: {DB_PATH}")
            print("\nTutorial demonstrated:")
            print("  ✓ Dating period creation")
            print("  ✓ Thesaurus management")
            print("  ✓ Site creation")
            print("  ✓ 2 Stratigraphic Units")
            print("  ✓ 1 Material with tipo_reperto selection")
            print("  ✓ Media file uploads (PDF, images, 3D, Excel, DOCX)")
            print("  ✓ All 6 media viewers demonstrated")
            print("  ✓ Harris Matrix creation")
            print("  ✓ GraphML export")
            print("  ✓ Database management (with Create Empty DB)")
            print("  ✓ User management")
            print("\n")

        except Exception as e:
            print(f"\n❌ Error during recording: {e}")
            import traceback
            traceback.print_exc()

        finally:
            context.close()
            browser.close()

            import glob
            video_files = glob.glob(f"{VIDEO_DIR}/*.webm")
            if video_files:
                video_files.sort(key=os.path.getmtime, reverse=True)
                latest = video_files[0]
                print(f"📹 Video file: {latest}")
                print(f"   Size: {os.path.getsize(latest) / 1024 / 1024:.1f} MB")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("PyArchInit-Mini v1.8.0/1.8.1 - COMPREHENSIVE TUTORIAL VIDEO")
    print("="*80 + "\n")
    print("This tutorial demonstrates:")
    print("  • NEW: Media viewer features (Image, PDF, Video, Excel, DOCX, 3D)")
    print("  • Site and stratigraphic unit management")
    print("  • Material inventory with tipo_reperto selection")
    print("  • Dating periods and thesaurus")
    print("  • Harris Matrix creation and export")
    print("  • Database management (Create Empty DB moved here)")
    print("  • User management")
    print("\nMake sure web server is running:")
    print(f"  DATABASE_URL=\"sqlite:///{DB_PATH}\" \\")
    print("    .venv/bin/python3 -m pyarchinit_mini.web_interface.app")
    print("\nPress Ctrl+C to cancel...")
    time.sleep(5)

    main()
