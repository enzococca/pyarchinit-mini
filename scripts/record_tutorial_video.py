#!/usr/bin/env python3
"""
Record complete tutorial video with automatic data entry for PyArchInit-Mini
Urban Excavation scenario with 5 US, relationships, and 3 materials with images
"""
from playwright.sync_api import sync_playwright
import time
import os

BASE_URL = "http://localhost:5001"
VIDEO_DIR = "docs/tutorial_video"
IMAGE_DIR = "/tmp/tutorial_images"

# Urban excavation data
SITE_DATA = {
    "name": "Roman Forum Excavation",
    "country": "Italy",
    "description": "Urban archaeological excavation in the Roman Forum area, documenting late Imperial period structures and stratigraphy"
}

# Datazioni (Periodization) - must be created before US
DATAZIONI = [
    {
        "nome": "Late Imperial",
        "fascia": "3rd-4th century AD",
        "descrizione": "Late Roman Imperial period"
    },
    {
        "nome": "Late Imperial - Early Medieval",
        "fascia": "4th-6th century AD",
        "descrizione": "Transition period from Late Imperial to Early Medieval"
    },
    {
        "nome": "Medieval",
        "fascia": "8th-9th century AD",
        "descrizione": "Early Medieval period"
    }
]

# 5 Stratigraphic Units with realistic data
# Note: Relationships will be added as text in the rapporti field
# Note: periodo_iniziale/finale and fase_iniziale/finale are INTEGER fields
US_DATA = [
    {
        "number": "1001",
        "type": "USM",
        "definition": "Stone wall foundation",
        "description": "Well-preserved stone wall foundation, late Imperial period. Built with irregular limestone blocks and mortar.",
        "area": "Trench A",
        "periodo_iniziale": "1",
        "fase_iniziale": "1",
        "datazione_estesa": "Late Imperial (3rd-4th century AD)",
        "relationships": ""  # No relationships - this is a base layer
    },
    {
        "number": "1002",
        "type": "US",
        "definition": "Floor surface",
        "description": "Compact mortar floor surface, associated with wall US1001. Shows evidence of wear and repair.",
        "area": "Trench A",
        "periodo_iniziale": "1",
        "fase_iniziale": "1",
        "datazione_estesa": "Late Imperial (3rd-4th century AD)",
        "relationships": "Abuts 1001"  # Floor abuts wall
    },
    {
        "number": "1003",
        "type": "US",
        "definition": "Destruction layer",
        "description": "Rubble and burnt material overlying floor US1002. Contains collapsed architectural elements and ash.",
        "area": "Trench A",
        "periodo_iniziale": "1",
        "fase_iniziale": "2",
        "periodo_finale": "2",
        "fase_finale": "1",
        "datazione_estesa": "Late Imperial - Early Medieval transition",
        "relationships": "Covers 1002"  # Destruction covers floor
    },
    {
        "number": "1004",
        "type": "USD",
        "definition": "Pit cut",
        "description": "Circular pit cutting through destruction layer US1003. Likely a spoliation pit from medieval period.",
        "area": "Trench A",
        "periodo_iniziale": "2",
        "fase_iniziale": "1",
        "datazione_estesa": "Medieval (8th-9th century AD)",
        "relationships": "Cuts 1003"  # Pit cuts destruction
    },
    {
        "number": "1005",
        "type": "US",
        "definition": "Pit fill",
        "description": "Loose fill within pit US1004. Contains mixed material including redeposited Roman pottery and medieval ceramics.",
        "area": "Trench A",
        "periodo_iniziale": "2",
        "fase_iniziale": "1",
        "datazione_estesa": "Medieval (8th-9th century AD)",
        "relationships": "Fills 1004"  # Fill fills pit
    }
]

# 3 Archaeological materials
MATERIALS = [
    {
        "inventory_number": "RF-001",
        "type": "Pottery",
        "description": "African Red Slip ware bowl fragment (Hayes Form 50). Fine orange fabric with red slip.",
        "dating": "Late 3rd-early 4th century AD",
        "area": "Trench A",
        "us": "1002"
    },
    {
        "inventory_number": "RF-002",
        "type": "Metal",
        "description": "Bronze coin, partially corroded. Appears to be a follis of Constantine I period.",
        "dating": "Early 4th century AD",
        "area": "Trench A",
        "us": "1003"
    },
    {
        "inventory_number": "RF-003",
        "type": "Glass",
        "description": "Window glass fragments, greenish transparent glass with weathering. Likely from building fenestration.",
        "dating": "3rd-4th century AD",
        "area": "Trench A",
        "us": "1003"
    }
]

def slow_type(page, selector, text, delay=15):
    """Type text to simulate human typing (3x faster than before)"""
    page.fill(selector, "")  # Clear first
    for char in text:
        page.type(selector, char, delay=delay)

def log_step(step_num, description):
    """Print formatted step log"""
    print(f"\n{'='*80}")
    print(f"STEP {step_num}: {description}")
    print(f"{'='*80}\n")

def main():
    # Create video output directory
    os.makedirs(VIDEO_DIR, exist_ok=True)

    with sync_playwright() as p:
        # Launch browser with video recording
        browser = p.chromium.launch(
            headless=False,  # Show browser for video
            slow_mo=500      # Slow down actions for visibility
        )

        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=VIDEO_DIR,
            record_video_size={"width": 1920, "height": 1080}
        )

        page = context.new_page()

        try:
            # ==================== STEP 1: LOGIN ====================
            log_step(1, "Login to PyArchInit-Mini")
            page.goto(f"{BASE_URL}/auth/login")
            time.sleep(2)

            slow_type(page, 'input[name="username"]', 'admin')
            time.sleep(0.3)
            slow_type(page, 'input[name="password"]', 'admin')
            time.sleep(0.5)
            page.click('button[type="submit"]')
            time.sleep(2)

            # ==================== STEP 2: CREATE DATAZIONI (PERIODIZATION) ====================
            for i, dat in enumerate(DATAZIONI, 1):
                log_step(f"2.{i}", f"Create Datazione: {dat['nome']}")

                page.goto(f"{BASE_URL}/periodizzazione/create")
                time.sleep(1)

                slow_type(page, 'input[name="nome_datazione"]', dat["nome"])
                time.sleep(0.3)

                slow_type(page, 'input[name="fascia_cronologica"]', dat["fascia"])
                time.sleep(0.3)

                slow_type(page, 'textarea[name="descrizione"]', dat["descrizione"])
                time.sleep(0.5)

                page.click('button[type="submit"]')
                time.sleep(2)

            # ==================== STEP 3: CREATE ARCHAEOLOGICAL SITE ====================
            log_step(3, "Create Archaeological Site")
            page.goto(f"{BASE_URL}/sites/create")
            time.sleep(1)

            # Use correct field names from sites/form.html - 3x faster
            slow_type(page, 'input[name="sito"]', SITE_DATA["name"])
            time.sleep(0.3)
            slow_type(page, 'input[name="nazione"]', SITE_DATA["country"])
            time.sleep(0.3)
            slow_type(page, 'textarea[name="descrizione"]', SITE_DATA["description"])
            time.sleep(0.5)

            page.click('button[type="submit"]')
            time.sleep(2)

            # ==================== STEP 4: CREATE 5 STRATIGRAPHIC UNITS ====================
            for i, us in enumerate(US_DATA, 1):
                log_step(f"4.{i}", f"Create US {us['number']} - {us['definition']}")

                page.goto(f"{BASE_URL}/us/create")
                time.sleep(2)

                # TAB 1: Basic Information (default active tab)
                page.select_option('select[name="sito"]', SITE_DATA["name"])
                time.sleep(0.5)

                slow_type(page, 'input[name="us"]', us["number"], delay=100)
                time.sleep(0.5)

                page.select_option('select[name="unita_tipo"]', us["type"])
                time.sleep(0.5)

                slow_type(page, 'input[name="area"]', us["area"], delay=80)
                time.sleep(1)

                # TAB 2: Descriptions - click tab to reveal fields
                print("   Switching to Descriptions tab")
                page.click('#description-tab')
                time.sleep(1)

                slow_type(page, 'textarea[name="d_stratigrafica"]', us["definition"])
                time.sleep(0.3)

                slow_type(page, 'textarea[name="descrizione"]', us["description"])
                time.sleep(0.5)

                # TAB 4: Chronology - click tab to reveal period fields
                print("   Switching to Chronology tab")
                page.click('#chronology-tab')
                time.sleep(1)

                # Periodo and Fase are INTEGER fields
                slow_type(page, 'input[name="periodo_iniziale"]', us["periodo_iniziale"])
                time.sleep(0.3)

                slow_type(page, 'input[name="fase_iniziale"]', us["fase_iniziale"])
                time.sleep(0.3)

                # Add periodo_finale and fase_finale if present
                if "periodo_finale" in us and us["periodo_finale"]:
                    slow_type(page, 'input[name="periodo_finale"]', us["periodo_finale"])
                    time.sleep(0.3)

                if "fase_finale" in us and us["fase_finale"]:
                    slow_type(page, 'input[name="fase_finale"]', us["fase_finale"])
                    time.sleep(0.3)

                # TAB 5: Stratigraphic Relationships - click tab to reveal rapporti field
                if us["relationships"]:
                    print("   Switching to Relationships tab")
                    page.click('#relationships-tab')
                    time.sleep(1)

                    print(f"   Adding relationships: {us['relationships']}")
                    slow_type(page, 'textarea[name="rapporti"]', us["relationships"])
                    time.sleep(0.5)

                # Save US
                page.click('button[type="submit"]')
                time.sleep(2)

            # ==================== STEP 5: CREATE 3 ARCHAEOLOGICAL MATERIALS ====================
            for i, material in enumerate(MATERIALS, 1):
                log_step(f"5.{i}", f"Create Material: {material['type']} - {material['inventory_number']}")

                page.goto(f"{BASE_URL}/inventario/create")
                time.sleep(2)

                # TAB 1: Identification (default active tab)
                page.select_option('select[name="sito"]', SITE_DATA["name"])
                time.sleep(0.3)

                slow_type(page, 'input[name="numero_inventario"]', material["inventory_number"])
                time.sleep(0.5)

                # TAB 2: Classification - click tab to reveal description and type fields
                print("   Switching to Classification tab")
                page.click('#classification-tab')
                time.sleep(1)

                # tipo_reperto is a select field, but we'll try typing if it accepts custom values
                try:
                    page.select_option('select[name="tipo_reperto"]', material["type"])
                except:
                    # If selection fails, the field might accept typing
                    print(f"   Could not select artifact type, field might be read-only")
                time.sleep(0.3)

                slow_type(page, 'textarea[name="descrizione"]', material["description"])
                time.sleep(0.5)

                # TAB 3: Context - click tab to reveal area and us fields
                print("   Switching to Context tab")
                page.click('#context-tab')
                time.sleep(1)

                slow_type(page, 'input[name="area"]', material["area"])
                time.sleep(0.3)

                slow_type(page, 'input[name="us"]', material["us"])
                time.sleep(0.5)

                # TAB 8: Documentation - click tab to reveal datazione_reperto field
                print("   Switching to Documentation tab")
                page.click('#documentation-tab')
                time.sleep(1)

                slow_type(page, 'input[name="datazione_reperto"]', material["dating"])
                time.sleep(0.5)

                # Save material
                page.click('button[type="submit"]')
                time.sleep(2)

            # ==================== STEP 6: GENERATE HARRIS MATRIX ====================
            log_step(6, "Generate Harris Matrix")
            # URL format: /harris_matrix/<site_name>
            page.goto(f"{BASE_URL}/harris_matrix/{SITE_DATA['name']}")
            time.sleep(5)  # Wait for matrix to render

            # Scroll to see the matrix
            page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
            time.sleep(3)
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(2)

            # ==================== STEP 7: EXPORT TO GRAPHML ====================
            log_step(7, "Export to GraphML format")
            # Correct route: /harris_matrix/graphml_export
            page.goto(f"{BASE_URL}/harris_matrix/graphml_export")
            time.sleep(1)

            # Use correct field names from GraphMLExportForm - 3x faster
            page.select_option('select[name="site"]', SITE_DATA["name"])
            time.sleep(0.5)

            slow_type(page, 'input[name="title"]', "Roman Forum Excavation - Trench A")
            time.sleep(0.5)

            # Select grouping option
            page.select_option('select[name="grouping"]', 'period_area')
            time.sleep(0.5)

            page.click('button[type="submit"]')
            time.sleep(2)

            # ==================== STEP 8: VIEW SITE SUMMARY ====================
            log_step(8, "View Site Summary")
            page.goto(f"{BASE_URL}/sites")
            time.sleep(2)

            page.click(f'text="{SITE_DATA["name"]}"')
            time.sleep(3)

            # Scroll through the page to show all data
            page.evaluate("window.scrollTo(0, 300)")
            time.sleep(2)
            page.evaluate("window.scrollTo(0, 600)")
            time.sleep(2)
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(3)

            print("\n" + "="*80)
            print("✅ VIDEO TUTORIAL RECORDING COMPLETE!")
            print("="*80)
            print(f"\nVideo saved to: {VIDEO_DIR}/")
            print("\nTutorial covered:")
            print("  ✓ 3 Datazioni (Periodization entries)")
            print("  ✓ Site creation")
            print("  ✓ 5 Stratigraphic Units with relationships")
            print("  ✓ 3 Archaeological materials")
            print("  ✓ Harris Matrix generation")
            print("  ✓ GraphML export")
            print("\n")

        except Exception as e:
            print(f"\n❌ Error during recording: {e}")
            import traceback
            traceback.print_exc()

        finally:
            # Close and save video
            context.close()
            browser.close()

            # Find the video file
            import glob
            video_files = glob.glob(f"{VIDEO_DIR}/*.webm")
            if video_files:
                print(f"📹 Video file: {video_files[0]}")

if __name__ == "__main__":
    print("\n" + "="*80)
    print("PyArchInit-Mini Tutorial Video Recording")
    print("Urban Archaeological Excavation Scenario")
    print("="*80 + "\n")
    print("This will record a complete tutorial video showing:")
    print("  • 3 Datazioni (Periodization entries)")
    print("  • Site creation (Roman Forum Excavation)")
    print("  • 5 Stratigraphic Units with relationships")
    print("  • 3 Archaeological materials")
    print("  • Harris Matrix generation")
    print("  • GraphML export\n")
    print("Make sure the web server is running on http://localhost:5001")
    print("Press Ctrl+C to cancel...")
    time.sleep(5)

    main()
