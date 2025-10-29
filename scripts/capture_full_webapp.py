#!/usr/bin/env python3
"""
PyArchInit-Mini Web GUI - Complete Documentation Screenshot Capture
Cattura TUTTI gli screenshot della web GUI con evidenziazione gialla visibile
"""
import sys
import time
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("✗ Playwright non installato")
    print("  Installa con: pip install playwright && playwright install chromium")
    sys.exit(1)

# Configuration
BASE_URL = "http://localhost:5001"
OUTPUT_DIR = Path("docs/images/webapp")
USERNAME = "admin"
PASSWORD = "admin"

# CSS for BIG yellow circle highlighting - MOLTO PIU' VISIBILE
HIGHLIGHT_CSS = """
.pyarchinit-highlight-overlay {
    position: fixed !important;
    border: 6px solid #FFD700 !important;
    border-radius: 50% !important;
    background: rgba(255, 215, 0, 0.25) !important;
    pointer-events: none !important;
    z-index: 999999 !important;
    box-shadow: 0 0 40px 15px rgba(255, 215, 0, 0.9),
                inset 0 0 30px rgba(255, 215, 0, 0.4) !important;
    animation: pulse 1s infinite !important;
}
@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 0.8; }
    50% { transform: scale(1.08); opacity: 1; }
}
"""


class WebAppExplorer:
    """Esplora e cattura screenshot della web app completa"""

    def __init__(self):
        self.output_dir = OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.screenshot_counter = 1
        self.page = None
        self.context = None
        self.browser = None

    def init_browser(self):
        """Inizializza browser"""
        print("🚀 Avvio browser Chromium...")
        playwright = sync_playwright().start()
        self.browser = playwright.chromium.launch(
            headless=False,  # Visible for debugging
            slow_mo=800  # Slow down for visibility
        )
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='en-US'  # English for international docs
        )
        self.page = self.context.new_page()

        # Inject CSS for highlighting
        self.page.add_init_script(f"""
            const style = document.createElement('style');
            style.textContent = `{HIGHLIGHT_CSS}`;
            document.head.appendChild(style);
        """)

    def save_screenshot(self, name, description=""):
        """Salva screenshot con nome e descrizione"""
        filename = f"{self.screenshot_counter:03d}_{name}.png"
        filepath = self.output_dir / filename
        self.page.screenshot(path=str(filepath), full_page=True)
        print(f"  📸 {self.screenshot_counter:03d}. {description or name}")
        self.screenshot_counter += 1
        time.sleep(0.5)

    def highlight_and_click(self, selector, description="", screenshot=True):
        """Evidenzia elemento con GROSSO cerchio giallo e poi clicca"""
        try:
            # Scroll into view
            self.page.evaluate(f"""
                const el = document.querySelector('{selector}');
                if (el) {{
                    el.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                }}
            """)
            time.sleep(2)  # Wait for scroll

            # Add BIG yellow glow - MOLTO PIU' GRANDE
            self.page.evaluate(f"""
                const el = document.querySelector('{selector}');
                if (el) {{
                    el.setAttribute('data-original-outline', el.style.outline || '');
                    el.setAttribute('data-original-box-shadow', el.style.boxShadow || '');
                    el.setAttribute('data-original-border-radius', el.style.borderRadius || '');

                    // Apply MASSIVE yellow glow
                    el.style.outline = '10px solid #FFD700';
                    el.style.outlineOffset = '12px';
                    el.style.boxShadow = '0 0 50px 20px rgba(255, 215, 0, 0.9), inset 0 0 30px rgba(255, 215, 0, 0.4)';
                    el.style.borderRadius = '50%';
                    el.style.transition = 'all 0.3s ease';
                }}
            """)

            time.sleep(2.5)  # Wait for effect to be visible

            # Screenshot with highlight
            if screenshot and description:
                self.save_screenshot(f"click_{description.replace(' ', '_')}", f"Click: {description}")

            # Restore styles
            self.page.evaluate(f"""
                const el = document.querySelector('{selector}');
                if (el) {{
                    el.style.outline = el.getAttribute('data-original-outline') || '';
                    el.style.boxShadow = el.getAttribute('data-original-box-shadow') || '';
                    el.style.borderRadius = el.getAttribute('data-original-border-radius') || '';
                    el.style.outlineOffset = '';
                    el.removeAttribute('data-original-outline');
                    el.removeAttribute('data-original-box-shadow');
                    el.removeAttribute('data-original-border-radius');
                }}
            """)
            time.sleep(0.5)

            # Click with fallback
            try:
                self.page.click(selector, timeout=5000)
            except:
                href = self.page.evaluate(f"document.querySelector('{selector}')?.getAttribute('href')")
                if href:
                    self.page.goto(f"{BASE_URL}{href}")

            time.sleep(3)  # Wait for page load

        except Exception as e:
            print(f"    ⚠️  Errore highlight/click {selector}: {e}")

    def highlight_element(self, selector, description=""):
        """Evidenzia elemento SENZA cliccare"""
        try:
            self.page.evaluate(f"""
                const el = document.querySelector('{selector}');
                if (el) {{
                    el.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                }}
            """)
            time.sleep(2)

            self.page.evaluate(f"""
                const el = document.querySelector('{selector}');
                if (el) {{
                    el.setAttribute('data-original-outline', el.style.outline || '');
                    el.setAttribute('data-original-box-shadow', el.style.boxShadow || '');
                    el.setAttribute('data-original-border-radius', el.style.borderRadius || '');

                    el.style.outline = '10px solid #FFD700';
                    el.style.outlineOffset = '12px';
                    el.style.boxShadow = '0 0 50px 20px rgba(255, 215, 0, 0.9), inset 0 0 30px rgba(255, 215, 0, 0.4)';
                    el.style.borderRadius = '50%';
                }}
            """)

            time.sleep(2.5)

            if description:
                self.save_screenshot(f"highlight_{description.replace(' ', '_')}", f"Highlight: {description}")

            self.page.evaluate(f"""
                const el = document.querySelector('{selector}');
                if (el) {{
                    el.style.outline = el.getAttribute('data-original-outline') || '';
                    el.style.boxShadow = el.getAttribute('data-original-box-shadow') || '';
                    el.style.borderRadius = el.getAttribute('data-original-border-radius') || '';
                    el.style.outlineOffset = '';
                    el.removeAttribute('data-original-outline');
                    el.removeAttribute('data-original-box-shadow');
                    el.removeAttribute('data-original-border-radius');
                }}
            """)
            time.sleep(0.5)

        except Exception as e:
            print(f"    ⚠️  Errore highlight {selector}: {e}")

    def navigate_to(self, url, description=""):
        """Navigate directly to URL"""
        self.page.goto(f"{BASE_URL}{url}")
        time.sleep(2)
        if description:
            print(f"  → Navigated to: {description}")

    def login(self):
        """Esegue login"""
        print("\n🔐 === 1. LOGIN & DASHBOARD ===")
        self.page.goto(f"{BASE_URL}/auth/login")
        time.sleep(1)

        self.save_screenshot("login_page", "Login Page")

        self.highlight_element('input[name="username"]', "Username_Field")
        self.page.fill('input[name="username"]', USERNAME)

        self.highlight_element('button[type="submit"]', "Login_Button")
        self.page.fill('input[name="password"]', PASSWORD)

        self.highlight_and_click('button[type="submit"]', "", screenshot=False)
        self.page.wait_for_url(f"{BASE_URL}/")
        time.sleep(1)

        # Set English language
        print("  🌍 Setting language to English...")
        self.page.goto(f"{BASE_URL}/?lang=en")
        time.sleep(1)
        self.save_screenshot("dashboard_main", "Main Dashboard")
        print("  ✓ Login completed, English set")

    def explore_sites(self):
        """Explore Archaeological Sites"""
        print("\n🏛️ === 2. ARCHAEOLOGICAL SITES ===")

        self.highlight_and_click('a[href="/sites"]', "Sites_Menu")
        self.save_screenshot("sites_list", "Sites List")

        # New site button
        self.highlight_and_click('a[href="/sites/create"]', "New_Site_Button")
        self.save_screenshot("sites_form", "Site Form")

        # Back to list
        self.page.go_back()
        time.sleep(2)

        # Click first site if exists
        try:
            self.highlight_and_click('.table tbody tr:first-child a', "Site_Detail_Link")
            self.save_screenshot("sites_detail", "Site Detail Page")
            self.page.go_back()
            time.sleep(2)
        except:
            print("    ℹ️  No sites to view")

    def explore_us(self):
        """Explore Stratigraphic Units with CORRECT tab navigation"""
        print("\n📦 === 3. STRATIGRAPHIC UNITS (US) ===")

        self.highlight_and_click('a[href="/us"]', "US_Menu")
        self.save_screenshot("us_list", "US List")

        # New US button
        self.highlight_and_click('a[href="/us/create"]', "New_US_Button")
        self.save_screenshot("us_form_tab1_basic", "US Form - Tab 1: Basic Information")

        # Navigate tabs with CORRECT selectors
        tabs = [
            ("button#description-tab", "us_form_tab2_descriptions", "Tab 2: Descriptions"),
            ("button#physical-tab", "us_form_tab3_physical", "Tab 3: Physical Characteristics"),
            ("button#chronology-tab", "us_form_tab4_chronology", "Tab 4: Chronology"),
            ("button#relationships-tab", "us_form_tab5_relationships", "Tab 5: Stratigraphic Relationships"),
            ("button#documentation-tab", "us_form_tab6_documentation", "Tab 6: Documentation"),
        ]

        for selector, screenshot_name, description in tabs:
            try:
                self.highlight_and_click(selector, f"US_{screenshot_name.replace('us_form_', '')}")
                self.save_screenshot(screenshot_name, f"US Form - {description}")
            except Exception as e:
                print(f"    ⚠️  Tab {description} not found: {e}")

        self.page.go_back()
        time.sleep(2)

    def explore_inventario(self):
        """Explore Material Inventory with ALL tabs"""
        print("\n📋 === 4. MATERIAL INVENTORY ===")

        self.highlight_and_click('a[href="/inventario"]', "Inventario_Menu")
        self.save_screenshot("inventario_list", "Inventory List")

        # New artifact button
        self.highlight_and_click('a[href="/inventario/create"]', "New_Artifact_Button")
        self.save_screenshot("inventario_form_tab1_identification", "Inventory Form - Tab 1: Identification")

        # Navigate all 8 inventory tabs with CORRECT Bootstrap 5 selectors
        tabs = [
            ("button#classification-tab", "inventario_form_tab2_classification", "Tab 2: Classification"),
            ("button#context-tab", "inventario_form_tab3_context", "Tab 3: Context"),
            ("button#physical-tab", "inventario_form_tab4_physical", "Tab 4: Physical"),
            ("button#conservation-tab", "inventario_form_tab5_conservation", "Tab 5: Conservation"),
            ("button#ceramic-tab", "inventario_form_tab6_ceramic", "Tab 6: Ceramic"),
            ("button#measurements-tab", "inventario_form_tab7_measurements", "Tab 7: Measurements"),
            ("button#documentation-tab", "inventario_form_tab8_documentation", "Tab 8: Documentation"),
        ]

        for selector, filename, description in tabs:
            try:
                self.highlight_and_click(selector, f"Inventario_{description.replace(' ', '_').replace(':', '')}")
                time.sleep(2)
                self.save_screenshot(filename, f"Inventory Form - {description}")
            except Exception as e:
                print(f"    ⚠️  {description} not accessible: {e}")

        self.page.go_back()
        time.sleep(2)

    def explore_media_upload(self):
        """Explore Media Upload"""
        print("\n📤 === 5. UPLOAD MEDIA ===")

        try:
            self.highlight_and_click('a[href="/media/upload"]', "Media_Upload_Menu")
            self.save_screenshot("media_upload_page", "Media Upload Interface")
        except:
            print("    ℹ️  Media Upload not accessible")

    def explore_harris_creator(self):
        """Explore Harris Matrix Creator"""
        print("\n✏️ === 6. HARRIS MATRIX CREATOR ===")

        try:
            self.highlight_and_click('a[href="/harris-creator"]', "Harris_Creator_Menu")
            time.sleep(3)
            self.save_screenshot("harris_creator_interface", "Harris Matrix Creator Interface")

            # Try to access editor
            try:
                self.navigate_to("/harris-creator/editor", "Harris Creator Editor")
                self.save_screenshot("harris_creator_editor", "Harris Matrix Creator Editor")
            except:
                print("    ℹ️  Harris Creator Editor not accessible")
        except:
            print("    ℹ️  Harris Creator not accessible")

    def explore_harris_matrix(self):
        """Explore Harris Matrix View"""
        print("\n🔗 === 7. HARRIS MATRIX VIEW ===")

        try:
            # Need a site name - use first available
            self.navigate_to("/sites")
            time.sleep(2)

            # Get first site name from the page
            site_name = self.page.evaluate("""
                const firstSiteLink = document.querySelector('.table tbody tr:first-child a');
                firstSiteLink ? firstSiteLink.textContent.trim() : null;
            """)

            if site_name:
                self.navigate_to(f"/harris_matrix/{site_name}", "Harris Matrix View")
                self.save_screenshot("harris_matrix_view", "Harris Matrix Visualization")

                # GraphML export
                self.navigate_to("/harris_matrix/graphml_export", "GraphML Export")
                self.save_screenshot("harris_graphml_export", "Harris Matrix GraphML Export")
            else:
                print("    ℹ️  No sites available for Harris Matrix")
        except Exception as e:
            print(f"    ℹ️  Harris Matrix not accessible: {e}")

    def explore_excel_import(self):
        """Explore Excel Import"""
        print("\n📥 === 8. EXCEL IMPORT ===")

        try:
            self.highlight_and_click('a[href="/excel-import"]', "Excel_Import_Menu")
            self.save_screenshot("excel_import_interface", "Excel Import Interface")
        except:
            print("    ℹ️  Excel Import not accessible")

    def explore_pyarchinit_import_export(self):
        """Explore PyArchInit Import/Export"""
        print("\n🔄 === 9. PYARCHINIT IMPORT/EXPORT ===")

        try:
            self.highlight_and_click('a[href="/pyarchinit-import-export"]', "PyArchInit_IE_Menu")
            self.save_screenshot("pyarchinit_ie_main", "PyArchInit Import/Export Main")

            # Scroll to different sections
            self.page.evaluate("window.scrollTo(0, 400)")
            time.sleep(1)
            self.save_screenshot("pyarchinit_import_section", "PyArchInit Import Section")

            self.page.evaluate("window.scrollTo(0, 800)")
            time.sleep(1)
            self.save_screenshot("pyarchinit_export_section", "PyArchInit Export Section")

            self.page.evaluate("window.scrollTo(0, 1200)")
            time.sleep(1)
            self.save_screenshot("pyarchinit_create_db", "PyArchInit Create Database")

        except:
            print("    ℹ️  PyArchInit I/E not accessible")

    def explore_em_node_config(self):
        """Explore Extended Matrix Node Config"""
        print("\n⚙️ === 10. EXTENDED MATRIX NODE CONFIG ===")

        try:
            self.highlight_and_click('a[href="/em-node-config"]', "EM_Node_Config_Menu")
            self.save_screenshot("em_node_config_interface", "EM Node Configuration")
        except:
            print("    ℹ️  EM Node Config not accessible")

    def explore_dating_periods(self):
        """Explore Dating Periods"""
        print("\n📅 === 11. DATING PERIODS ===")

        try:
            self.highlight_and_click('a[href="/periodizzazione"]', "Dating_Periods_Menu")
            self.save_screenshot("dating_periods_list", "Dating Periods List")

            # New period button
            try:
                self.highlight_and_click('a[href="/periodizzazione/create"]', "New_Dating_Period_Button")
                self.save_screenshot("dating_periods_form", "Dating Period Form")
                self.page.go_back()
                time.sleep(2)
            except:
                print("    ℹ️  Dating period form not accessible")
        except:
            print("    ℹ️  Dating Periods not accessible")

    def explore_periodization_records(self):
        """Explore Periodization Records"""
        print("\n🗓️ === 12. PERIODIZATION RECORDS ===")

        try:
            self.highlight_and_click('a[href="/periodization-records"]', "Periodization_Records_Menu")
            self.save_screenshot("periodization_records_list", "Periodization Records List")

            # Try to view a record
            try:
                self.page.click('.table tbody tr:first-child a', timeout=3000)
                time.sleep(2)
                self.save_screenshot("periodization_record_detail", "Periodization Record Detail")
                self.page.go_back()
                time.sleep(2)
            except:
                print("    ℹ️  No periodization records to view")
        except:
            print("    ℹ️  Periodization Records not accessible")

    def explore_thesaurus(self):
        """Explore ICCD Thesaurus"""
        print("\n📚 === 13. ICCD THESAURUS ===")

        try:
            self.highlight_and_click('a[href="/thesaurus"]', "Thesaurus_Menu")
            self.save_screenshot("thesaurus_list", "ICCD Thesaurus List")

            # Show management interface
            self.page.evaluate("window.scrollTo(0, 400)")
            time.sleep(1)
            self.save_screenshot("thesaurus_management", "Thesaurus Management")
        except:
            print("    ℹ️  Thesaurus not accessible")

    def explore_analytics(self):
        """Explore Analytics"""
        print("\n📈 === 14. ANALYTICS ===")

        try:
            self.highlight_and_click('a[href="/analytics"]', "Analytics_Menu")
            time.sleep(3)
            self.save_screenshot("analytics_dashboard", "Analytics Dashboard")
        except:
            print("    ℹ️  Analytics not accessible")

    def explore_validation(self):
        """Explore Validation"""
        print("\n✅ === 15. VALIDATION ===")

        try:
            # Need a site name
            self.navigate_to("/sites")
            time.sleep(2)

            site_name = self.page.evaluate("""
                const firstSiteLink = document.querySelector('.table tbody tr:first-child a');
                firstSiteLink ? firstSiteLink.textContent.trim() : null;
            """)

            if site_name:
                self.navigate_to(f"/validate/{site_name}", "Validation Report")
                self.save_screenshot("validation_report", "Stratigraphic Validation Report")
            else:
                print("    ℹ️  No sites for validation")
        except:
            print("    ℹ️  Validation not accessible")

    def explore_admin_database(self):
        """Explore Admin Database Management"""
        print("\n🔧 === 16. ADMIN - DATABASE MANAGEMENT ===")

        try:
            self.highlight_and_click('a[href="/admin/database"]', "Admin_Database_Menu")
            self.save_screenshot("admin_database_main", "Database Management")

            # Upload database page
            try:
                self.navigate_to("/admin/database/upload", "Database Upload")
                self.save_screenshot("admin_database_upload", "Upload Database")
            except:
                print("    ℹ️  Database upload not accessible")

            # Connect database page
            try:
                self.navigate_to("/admin/database/connect", "Database Connect")
                self.save_screenshot("admin_database_connect", "Connect to Database")
            except:
                print("    ℹ️  Database connect not accessible")

        except:
            print("    ℹ️  Admin Database not accessible")

    def explore_admin_users(self):
        """Explore Admin User Management"""
        print("\n👥 === 17. ADMIN - USER MANAGEMENT ===")

        try:
            self.highlight_and_click('a[href="/auth/users"]', "Admin_Users_Menu")
            self.save_screenshot("admin_users_list", "User Management")
        except:
            print("    ℹ️  User Management not accessible")

    def run(self):
        """Esegue cattura completa"""
        print("=" * 70)
        print("PyArchInit-Mini Web GUI - COMPLETE Screenshot Capture")
        print("=" * 70)

        try:
            self.init_browser()

            # Execute all exploration functions
            self.login()
            self.explore_sites()
            self.explore_us()
            self.explore_inventario()
            self.explore_media_upload()
            self.explore_harris_creator()
            self.explore_harris_matrix()
            self.explore_excel_import()
            self.explore_pyarchinit_import_export()
            self.explore_em_node_config()
            self.explore_dating_periods()
            self.explore_periodization_records()
            self.explore_thesaurus()
            self.explore_analytics()
            self.explore_validation()
            self.explore_admin_database()
            self.explore_admin_users()

            print("\n" + "=" * 70)
            print(f"✅ Cattura completata!")
            print(f"📁 Screenshot salvati in: {self.output_dir.absolute()}")
            print(f"📸 Totale screenshot: {self.screenshot_counter - 1}")
            print("=" * 70)

        except KeyboardInterrupt:
            print("\n⚠️  Cattura interrotta dall'utente")
        except Exception as e:
            print(f"\n❌ Errore: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.browser:
                self.browser.close()
                print("🛑 Browser chiuso")


if __name__ == "__main__":
    explorer = WebAppExplorer()
    explorer.run()
