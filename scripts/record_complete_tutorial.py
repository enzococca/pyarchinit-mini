#!/usr/bin/env python3
"""
Complete PyArchInit-Mini Tutorial Video Recording Script
Records full workflow with real archaeological data
"""
from playwright.sync_api import sync_playwright
from pathlib import Path
import time
import shutil

# Configuration
BASE_URL = "http://localhost:5001"
OUTPUT_DIR = Path("docs/tutorial_video")
SCREENSHOTS_DIR = Path("docs/images/webapp_complete")
VIDEO_PATH = OUTPUT_DIR / "pyarchinit_complete_tutorial.webm"

# Archaeological data for realistic demo
SITE_DATA = {
    "name": "Ancient Harbor of Portus",
    "location": "Fiumicino",
    "municipality": "Fiumicino",
    "province": "RM",
    "region": "Lazio",
    "nation": "Italy",
    "definition_en": "Ancient Roman harbor complex",
    "description_en": "Major harbor serving Imperial Rome, constructed under Emperor Claudius (42-64 AD) and expanded by Trajan (100-112 AD). Features include hexagonal basin, warehouses, and maritime facilities."
}

US_DATA = [
    {
        "us_number": "1001",
        "unit_type": "Layer",
        "definition": "Surface topsoil",
        "description": "Modern topsoil layer with vegetation and recent materials",
        "interpretation": "Agricultural disturbance from 20th century farming",
        "color": "Dark brown",
        "consistency": "Loose",
        "grain": "Fine-medium",
        "position": "Area A, Sector 1",
        "date": "Modern (20th century)"
    },
    {
        "us_number": "1002",
        "unit_type": "Layer",
        "definition": "Medieval occupation layer",
        "description": "Compact brown layer with ceramic fragments and charcoal inclusions",
        "interpretation": "Living surface from medieval reoccupation phase",
        "color": "Brown",
        "consistency": "Compact",
        "grain": "Medium",
        "position": "Area A, Sector 1",
        "date": "Medieval (12th-13th century)",
        "relations": {"covered_by": ["1001"]}
    },
    {
        "us_number": "1003",
        "unit_type": "Cut",
        "definition": "Foundation trench",
        "description": "Linear cut with vertical sides and flat bottom",
        "interpretation": "Foundation trench for medieval wall construction",
        "length": "5.5",
        "width": "0.8",
        "depth": "1.2",
        "position": "Area A, Sector 1",
        "relations": {"cuts": ["1002"]}
    },
    {
        "us_number": "1004",
        "unit_type": "Masonry",
        "definition": "Stone wall foundation",
        "description": "Foundation of stone wall with lime mortar bonding",
        "interpretation": "Medieval wall foundation, part of defensive structure",
        "length": "5.5",
        "width": "0.7",
        "height": "1.0",
        "position": "Area A, Sector 1",
        "date": "Medieval (12th century)",
        "relations": {"fills": ["1003"], "covered_by": ["1002"]}
    }
]

INVENTORY_DATA = [
    {
        "inventory_num": "INV-2024-001",
        "artifact_type": "Ceramic",
        "definition": "Amphora rim",
        "description": "Rim fragment of African Red Slip ware amphora with everted rim",
        "us": "1002",
        "conservation": "Good",
        "diagnostic": "Yes",
        "ceramic_body": "Fine orange fabric",
        "dating": "Late Roman (4th-5th century AD)"
    },
    {
        "inventory_num": "INV-2024-002",
        "artifact_type": "Metal",
        "definition": "Bronze coin",
        "description": "Small bronze coin, heavily corroded, possibly Byzantine",
        "us": "1002",
        "conservation": "Poor",
        "diagnostic": "Yes",
        "dating": "Byzantine (6th-7th century AD)"
    },
    {
        "inventory_num": "INV-2024-003",
        "artifact_type": "Ceramic",
        "definition": "Bowl fragment",
        "description": "Medieval glazed bowl fragment with green glaze",
        "us": "1002",
        "conservation": "Fair",
        "diagnostic": "Yes",
        "ceramic_body": "Medieval coarse ware",
        "dating": "Medieval (12th-13th century)"
    }
]

THESAURUS_TERMS = [
    {"category": "artifact_type", "term": "Amphora", "definition_en": "Large ceramic vessel for transport"},
    {"category": "conservation", "term": "Excellent", "definition_en": "Complete or nearly complete"},
    {"category": "ceramic_body", "term": "African Red Slip", "definition_en": "Fine red ware from North Africa"}
]

DATING_PERIODS = [
    {"name": "Early Imperial", "start": -27, "end": 96, "description": "From Augustus to Domitian"},
    {"name": "High Imperial", "start": 96, "end": 192, "description": "From Nerva to Commodus"},
    {"name": "Late Roman", "start": 284, "end": 476, "description": "From Diocletian to fall of Western Empire"},
    {"name": "Medieval", "start": 476, "end": 1492, "description": "Middle Ages"}
]


class CompleteTutorialRecorder:
    def __init__(self):
        self.OUTPUT_DIR = OUTPUT_DIR
        self.SCREENSHOTS_DIR = SCREENSHOTS_DIR
        self.step_counter = 1

    def setup_directories(self):
        """Create output directories"""
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        print(f"✓ Directories created:")
        print(f"  Video: {self.OUTPUT_DIR}")
        print(f"  Screenshots: {self.SCREENSHOTS_DIR}")

    def screenshot(self, page, name, description=""):
        """Take screenshot with step counter"""
        filename = f"{str(self.step_counter).zfill(3)}_{name}.png"
        path = self.SCREENSHOTS_DIR / filename
        page.screenshot(path=str(path), full_page=False)
        print(f"  📸 {self.step_counter:03d}. {description or name}")
        self.step_counter += 1
        time.sleep(0.5)

    def wait_and_check(self, page, timeout=1000):
        """Wait for network and animations"""
        try:
            page.wait_for_load_state("networkidle", timeout=timeout)
        except:
            pass
        time.sleep(0.3)

    def fill_field(self, page, selector, value, wait=True):
        """Fill form field with value"""
        try:
            page.fill(selector, str(value))
            if wait:
                time.sleep(0.2)
        except Exception as e:
            print(f"    ⚠️  Could not fill {selector}: {e}")

    def select_dropdown(self, page, selector, value):
        """Select dropdown value"""
        try:
            page.select_option(selector, value)
            time.sleep(0.2)
        except Exception as e:
            print(f"    ⚠️  Could not select {selector}: {e}")

    def run(self):
        print("="*80)
        print("PyArchInit-Mini Complete Tutorial Video Recording")
        print("="*80)

        self.setup_directories()

        with sync_playwright() as p:
            # Launch browser with video recording
            browser = p.chromium.launch(headless=False, slow_mo=500)
            context = browser.new_context(
                locale='en-US',
                viewport={'width': 1920, 'height': 1080},
                record_video_dir=str(self.OUTPUT_DIR),
                record_video_size={'width': 1920, 'height': 1080}
            )

            page = context.new_page()
            print("\n🎬 Video recording started...")

            try:
                # =====================================================
                # 1. LOGIN
                # =====================================================
                print("\n🔐 === 1. LOGIN ===")
                page.goto(f"{BASE_URL}/?lang=en")
                self.wait_and_check(page)
                self.screenshot(page, "login_page", "Login Page")

                # Login
                page.fill("input[name='username']", "admin")
                page.fill("input[name='password']", "admin")
                self.screenshot(page, "login_filled", "Credentials Entered")
                page.click("button[type='submit']")
                self.wait_and_check(page, 3000)
                self.screenshot(page, "dashboard", "Main Dashboard")

                # =====================================================
                # 2. CREATE SITE WITH FULL DATA
                # =====================================================
                print("\n🏛️ === 2. CREATE ARCHAEOLOGICAL SITE ===")
                page.goto(f"{BASE_URL}/sites?lang=en")
                self.wait_and_check(page)
                self.screenshot(page, "sites_list", "Sites List")

                page.goto(f"{BASE_URL}/sites/new?lang=en")
                self.wait_and_check(page)
                self.screenshot(page, "site_form_empty", "Empty Site Form")

                # Fill all site fields
                self.fill_field(page, "input[name='site_name']", SITE_DATA["name"])
                self.fill_field(page, "input[name='location']", SITE_DATA["location"])
                self.fill_field(page, "input[name='municipality']", SITE_DATA["municipality"])
                self.fill_field(page, "input[name='province']", SITE_DATA["province"])
                self.fill_field(page, "input[name='region']", SITE_DATA["region"])
                self.fill_field(page, "input[name='nation']", SITE_DATA["nation"])
                self.fill_field(page, "input[name='definition_site_en']", SITE_DATA["definition_en"])
                self.fill_field(page, "textarea[name='description_en']", SITE_DATA["description_en"])

                self.screenshot(page, "site_form_filled", "Site Form Completed")
                page.click("button[type='submit']")
                self.wait_and_check(page, 2000)
                self.screenshot(page, "site_created", "Site Created Successfully")

                # =====================================================
                # 3. CREATE STRATIGRAPHIC UNITS
                # =====================================================
                print("\n📦 === 3. CREATE STRATIGRAPHIC UNITS ===")
                page.goto(f"{BASE_URL}/us?lang=en")
                self.wait_and_check(page)
                self.screenshot(page, "us_list_empty", "Empty US List")

                for i, us in enumerate(US_DATA):
                    print(f"  Creating US {us['us_number']}...")
                    page.goto(f"{BASE_URL}/us/new?lang=en")
                    self.wait_and_check(page)

                    if i == 0:
                        self.screenshot(page, "us_form_empty", "Empty US Form")

                    # Tab 1: Basic Information
                    self.select_dropdown(page, "select[name='site_id']", "1")
                    self.fill_field(page, "input[name='us_number']", us["us_number"])
                    self.select_dropdown(page, "select[name='unit_type']", us["unit_type"])
                    self.fill_field(page, "input[name='definition']", us["definition"])

                    if i == 0:
                        self.screenshot(page, "us_tab1_filled", "US Tab 1 - Basic Info Filled")

                    # Tab 2: Descriptions
                    page.click("button#description-tab")
                    self.wait_and_check(page)
                    self.fill_field(page, "textarea[name='description']", us["description"])
                    self.fill_field(page, "textarea[name='interpretation']", us["interpretation"])

                    if i == 0:
                        self.screenshot(page, "us_tab2_filled", "US Tab 2 - Descriptions Filled")

                    # Tab 3: Physical Characteristics
                    page.click("button#physical-tab")
                    self.wait_and_check(page)
                    if "color" in us:
                        self.fill_field(page, "input[name='color']", us["color"])
                    if "consistency" in us:
                        self.fill_field(page, "input[name='consistency']", us["consistency"])
                    if "grain" in us:
                        self.fill_field(page, "input[name='grain']", us["grain"])
                    if "length" in us:
                        self.fill_field(page, "input[name='length']", us["length"])
                    if "width" in us:
                        self.fill_field(page, "input[name='width']", us["width"])
                    if "depth" in us:
                        self.fill_field(page, "input[name='depth']", us["depth"])

                    if i == 0:
                        self.screenshot(page, "us_tab3_filled", "US Tab 3 - Physical Filled")

                    # Tab 4: Chronology
                    page.click("button#chronology-tab")
                    self.wait_and_check(page)
                    if "date" in us:
                        self.fill_field(page, "input[name='dating']", us["date"])

                    if i == 0:
                        self.screenshot(page, "us_tab4_filled", "US Tab 4 - Chronology Filled")

                    # Tab 5: Relationships (will add after all US created)
                    page.click("button#relationships-tab")
                    self.wait_and_check(page)

                    if i == 0:
                        self.screenshot(page, "us_tab5_empty", "US Tab 5 - Relationships")

                    # Tab 6: Documentation
                    page.click("button#documentation-tab")
                    self.wait_and_check(page)
                    self.fill_field(page, "input[name='excavator']", "Dr. Maria Rossi")
                    self.fill_field(page, "input[name='excavation_date']", "2024-01-15")

                    if i == 0:
                        self.screenshot(page, "us_tab6_filled", "US Tab 6 - Documentation Filled")

                    # Save US
                    page.click("button[type='submit']")
                    self.wait_and_check(page, 2000)

                    if i == 0:
                        self.screenshot(page, "us_created_first", "First US Created")

                # Go back to US list to see all created
                page.goto(f"{BASE_URL}/us?lang=en")
                self.wait_and_check(page)
                self.screenshot(page, "us_list_filled", "US List with All Units")

                # =====================================================
                # 4. ADD STRATIGRAPHIC RELATIONSHIPS
                # =====================================================
                print("\n🔗 === 4. ADD STRATIGRAPHIC RELATIONSHIPS ===")
                # Edit US 1002 to add relationship
                page.goto(f"{BASE_URL}/us/2/edit?lang=en")
                self.wait_and_check(page)
                page.click("button#relationships-tab")
                self.wait_and_check(page)
                self.fill_field(page, "input[name='covered_by']", "1001")
                self.screenshot(page, "us_relationship_added", "Stratigraphic Relationship Added")
                page.click("button[type='submit']")
                self.wait_and_check(page)

                # =====================================================
                # 5. CREATE INVENTORY ITEMS
                # =====================================================
                print("\n📋 === 5. CREATE MATERIAL INVENTORY ===")
                page.goto(f"{BASE_URL}/inventario?lang=en")
                self.wait_and_check(page)
                self.screenshot(page, "inventory_list_empty", "Empty Inventory List")

                for i, inv in enumerate(INVENTORY_DATA):
                    print(f"  Creating Inventory {inv['inventory_num']}...")
                    page.goto(f"{BASE_URL}/inventario/new?lang=en")
                    self.wait_and_check(page)

                    if i == 0:
                        self.screenshot(page, "inventory_form_empty", "Empty Inventory Form")

                    # Tab 1: Identification
                    self.select_dropdown(page, "select[name='site_id']", "1")
                    self.fill_field(page, "input[name='inventory_number']", inv["inventory_num"])
                    self.fill_field(page, "input[name='recorder']", "Dr. Giovanni Bianchi")
                    self.fill_field(page, "input[name='record_date']", "2024-01-20")

                    if i == 0:
                        self.screenshot(page, "inv_tab1_filled", "Inventory Tab 1 Filled")

                    # Tab 2: Classification
                    page.click("button#classification-tab")
                    self.wait_and_check(page)
                    self.fill_field(page, "input[name='artifact_type']", inv["artifact_type"])
                    self.fill_field(page, "input[name='definition']", inv["definition"])
                    self.fill_field(page, "textarea[name='description']", inv["description"])

                    if i == 0:
                        self.screenshot(page, "inv_tab2_filled", "Inventory Tab 2 Filled")

                    # Tab 3: Context
                    page.click("button#context-tab")
                    self.wait_and_check(page)
                    self.fill_field(page, "input[name='area']", "A")
                    self.fill_field(page, "input[name='us']", inv["us"])

                    if i == 0:
                        self.screenshot(page, "inv_tab3_filled", "Inventory Tab 3 Filled")

                    # Tab 4: Physical
                    page.click("button#physical-tab")
                    self.wait_and_check(page)
                    self.fill_field(page, "input[name='conservation_state']", inv["conservation"])

                    if i == 0:
                        self.screenshot(page, "inv_tab4_filled", "Inventory Tab 4 Filled")

                    # Tab 5: Conservation
                    page.click("button#conservation-tab")
                    self.wait_and_check(page)
                    self.select_dropdown(page, "select[name='diagnostic']", "Yes" if inv["diagnostic"] == "Yes" else "No")

                    if i == 0:
                        self.screenshot(page, "inv_tab5_filled", "Inventory Tab 5 Filled")

                    # Tab 8: Documentation
                    page.click("button#documentation-tab")
                    self.wait_and_check(page)
                    self.fill_field(page, "input[name='dating']", inv["dating"])

                    if i == 0:
                        self.screenshot(page, "inv_tab8_filled", "Inventory Tab 8 Filled")

                    # Save
                    page.click("button[type='submit']")
                    self.wait_and_check(page, 2000)

                page.goto(f"{BASE_URL}/inventario?lang=en")
                self.wait_and_check(page)
                self.screenshot(page, "inventory_list_filled", "Inventory List with Items")

                # =====================================================
                # 6. UPLOAD MEDIA
                # =====================================================
                print("\n📤 === 6. UPLOAD MEDIA FILES ===")
                page.goto(f"{BASE_URL}/upload_media?lang=en")
                self.wait_and_check(page)
                self.screenshot(page, "media_upload_interface", "Media Upload Interface")

                # =====================================================
                # 7. HARRIS MATRIX CREATOR
                # =====================================================
                print("\n✏️ === 7. HARRIS MATRIX CREATOR ===")
                page.goto(f"{BASE_URL}/harris_creator?lang=en")
                self.wait_and_check(page, 2000)
                self.screenshot(page, "harris_creator_main", "Harris Matrix Creator Main")

                # =====================================================
                # 8. DATING PERIODS
                # =====================================================
                print("\n📅 === 8. DATING PERIODS ===")
                page.goto(f"{BASE_URL}/dating-periods?lang=en")
                self.wait_and_check(page)
                self.screenshot(page, "dating_periods_list", "Dating Periods List")

                # Create one period
                page.goto(f"{BASE_URL}/dating-periods/new?lang=en")
                self.wait_and_check(page)
                self.screenshot(page, "dating_period_form", "Dating Period Form")
                self.fill_field(page, "input[name='period_name']", DATING_PERIODS[0]["name"])
                self.fill_field(page, "input[name='start_date']", str(DATING_PERIODS[0]["start"]))
                self.fill_field(page, "input[name='end_date']", str(DATING_PERIODS[0]["end"]))
                self.fill_field(page, "textarea[name='description']", DATING_PERIODS[0]["description"])
                self.screenshot(page, "dating_period_filled", "Dating Period Filled")
                page.click("button[type='submit']")
                self.wait_and_check(page)

                # =====================================================
                # 9. THESAURUS
                # =====================================================
                print("\n📚 === 9. ICCD THESAURUS ===")
                page.goto(f"{BASE_URL}/thesaurus?lang=en")
                self.wait_and_check(page)
                self.screenshot(page, "thesaurus_list", "Thesaurus List")

                # =====================================================
                # 10. ANALYTICS
                # =====================================================
                print("\n📈 === 10. ANALYTICS DASHBOARD ===")
                page.goto(f"{BASE_URL}/analytics?lang=en")
                self.wait_and_check(page, 2000)
                self.screenshot(page, "analytics_dashboard", "Analytics Dashboard")

                # =====================================================
                # 11. ADMIN - DATABASE
                # =====================================================
                print("\n🔧 === 11. DATABASE MANAGEMENT ===")
                page.goto(f"{BASE_URL}/admin/database?lang=en")
                self.wait_and_check(page)
                self.screenshot(page, "admin_database", "Database Management")

                # =====================================================
                # 12. FINAL DASHBOARD
                # =====================================================
                print("\n🏠 === 12. RETURN TO DASHBOARD ===")
                page.goto(f"{BASE_URL}/?lang=en")
                self.wait_and_check(page)
                self.screenshot(page, "dashboard_final", "Final Dashboard with Data")

                print(f"\n✅ Complete tutorial recorded!")
                print(f"📸 Total screenshots: {self.step_counter - 1}")

            except Exception as e:
                print(f"\n❌ Error during recording: {e}")
                import traceback
                traceback.print_exc()

            finally:
                # Close and save video
                print("\n🎬 Saving video...")
                context.close()
                browser.close()

                # Move video to final location
                video_files = list(self.OUTPUT_DIR.glob("*.webm"))
                if video_files:
                    video_file = video_files[0]
                    final_video = self.OUTPUT_DIR / "pyarchinit_complete_tutorial.webm"
                    shutil.move(str(video_file), str(final_video))
                    print(f"✓ Video saved: {final_video}")

        print("\n" + "="*80)
        print("Recording completed!")
        print(f"📁 Screenshots: {self.SCREENSHOTS_DIR}")
        print(f"🎬 Video: {VIDEO_PATH}")
        print("="*80)


if __name__ == "__main__":
    recorder = CompleteTutorialRecorder()
    recorder.run()
