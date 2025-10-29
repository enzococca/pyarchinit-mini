#!/usr/bin/env python3
"""
PyArchInit-Mini Web GUI - Complete Documentation Screenshot Capture
Explores all pages, tabs, and functions with button/menu highlighting
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

# CSS for highlighting elements (injected into page)
HIGHLIGHT_CSS = """
.pyarchinit-highlight {
    outline: 3px solid #FF6B6B !important;
    outline-offset: 2px !important;
    box-shadow: 0 0 10px rgba(255, 107, 107, 0.5) !important;
    position: relative !important;
    z-index: 9999 !important;
}
.pyarchinit-highlight::before {
    content: '👆 Cliccato' !important;
    position: absolute !important;
    top: -25px !important;
    left: 0 !important;
    background: #FF6B6B !important;
    color: white !important;
    padding: 2px 8px !important;
    border-radius: 3px !important;
    font-size: 12px !important;
    font-weight: bold !important;
    white-space: nowrap !important;
    z-index: 10000 !important;
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
            headless=False,  # Mostra browser per debug
            slow_mo=500  # Rallenta per vedere cosa succede
        )
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='it-IT'
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
        print(f"      → {filepath}")
        self.screenshot_counter += 1
        time.sleep(0.5)

    def highlight_and_click(self, selector, description=""):
        """Evidenzia elemento e poi clicca"""
        try:
            # Add highlight class
            self.page.evaluate(f"""
                const el = document.querySelector('{selector}');
                if (el) {{
                    el.classList.add('pyarchinit-highlight');
                    el.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                }}
            """)
            time.sleep(0.5)

            # Screenshot with highlight
            if description:
                self.save_screenshot(f"click_{description}", f"Click: {description}")

            # Click
            self.page.click(selector)
            time.sleep(1)

            # Remove highlight
            self.page.evaluate(f"""
                const el = document.querySelector('{selector}');
                if (el) el.classList.remove('pyarchinit-highlight');
            """)

        except Exception as e:
            print(f"    ⚠️  Errore highlight/click {selector}: {e}")

    def highlight_element(self, selector, description=""):
        """Evidenzia elemento senza cliccare"""
        try:
            self.page.evaluate(f"""
                const el = document.querySelector('{selector}');
                if (el) {{
                    el.classList.add('pyarchinit-highlight');
                    el.scrollIntoView({{behavior: 'smooth', block: 'center'}});
                }}
            """)
            time.sleep(0.5)

            if description:
                self.save_screenshot(f"highlight_{description}", f"Elemento: {description}")

            # Remove highlight
            self.page.evaluate(f"""
                const el = document.querySelector('{selector}');
                if (el) el.classList.remove('pyarchinit-highlight');
            """)

        except Exception as e:
            print(f"    ⚠️  Errore highlight {selector}: {e}")

    def login(self):
        """Esegue login"""
        print("\n🔐 === LOGIN ===")
        self.page.goto(f"{BASE_URL}/auth/login")
        time.sleep(1)

        # Screenshot pagina login
        self.save_screenshot("login_page", "Pagina di Login")

        # Evidenzia e compila username
        self.highlight_element('input[name="username"]', "Campo Username")
        self.page.fill('input[name="username"]', USERNAME)

        # Evidenzia e compila password
        self.highlight_element('input[name="password"]', "Campo Password")
        self.page.fill('input[name="password"]', PASSWORD)

        # Evidenzia e clicca login button
        self.highlight_and_click('button[type="submit"]', "Bottone Login")

        # Wait for dashboard
        self.page.wait_for_url(f"{BASE_URL}/")
        time.sleep(1)

        print("  ✓ Login effettuato")

    def explore_dashboard(self):
        """Esplora dashboard"""
        print("\n📊 === DASHBOARD ===")
        self.save_screenshot("dashboard_main", "Dashboard Principale")

        # Evidenzia sezioni dashboard
        self.highlight_element('.card:has-text("Statistiche Sito")', "Statistiche Sito")
        self.highlight_element('.card:has-text("Attività Recente")', "Attività Recente")
        self.highlight_element('.card:has-text("Sistema")', "Informazioni Sistema")

    def explore_sites(self):
        """Esplora gestione siti"""
        print("\n🏛️ === GESTIONE SITI ===")

        # Click menu Sites
        self.highlight_and_click('a[href="/sites"]', "Menu Siti")
        self.save_screenshot("sites_list", "Lista Siti")

        # Try to click on first site if exists
        try:
            self.highlight_and_click('.table tbody tr:first-child a', "Dettaglio Primo Sito")
            self.save_screenshot("sites_detail", "Dettaglio Sito")
            self.page.go_back()
            time.sleep(1)
        except:
            print("    ℹ️  Nessun sito da visualizzare")

        # Click New Site button
        self.highlight_and_click('a[href="/sites/new"]', "Bottone Nuovo Sito")
        self.save_screenshot("sites_form", "Form Nuovo Sito")

        # Back to list
        self.page.go_back()

    def explore_us(self):
        """Esplora gestione US"""
        print("\n📦 === GESTIONE US ===")

        # Click menu US
        self.highlight_and_click('a[href="/us"]', "Menu US")
        self.save_screenshot("us_list", "Lista Unità Stratigrafiche")

        # Click New US button
        try:
            self.highlight_and_click('a[href="/us/new"]', "Bottone Nuova US")
            self.save_screenshot("us_form_tab1", "Form US - Tab 1")

            # Navigate tabs if exists
            for i in range(2, 7):
                try:
                    self.highlight_and_click(f'#tab{i}', f"Tab {i}")
                    self.save_screenshot(f"us_form_tab{i}", f"Form US - Tab {i}")
                except:
                    break

            self.page.go_back()
        except:
            print("    ℹ️  Form US non disponibile")

    def explore_inventario(self):
        """Esplora inventario materiali"""
        print("\n📋 === INVENTARIO MATERIALI ===")

        # Click menu Inventario
        self.highlight_and_click('a[href="/inventario"]', "Menu Inventario")
        self.save_screenshot("inventario_list", "Lista Inventario")

        # Click New Inventario
        try:
            self.highlight_and_click('a[href="/inventario/new"]', "Bottone Nuovo Reperto")
            self.save_screenshot("inventario_form_tab1", "Form Inventario - Tab 1")

            # Navigate tabs
            for i in range(2, 9):
                try:
                    self.highlight_and_click(f'#tab{i}', f"Tab {i}")
                    self.save_screenshot(f"inventario_form_tab{i}", f"Form Inventario - Tab {i}")
                except:
                    break

            self.page.go_back()
        except:
            print("    ℹ️  Form Inventario non disponibile")

    def explore_harris_matrix(self):
        """Esplora Harris Matrix"""
        print("\n🔗 === HARRIS MATRIX ===")

        # Click menu Harris Matrix
        try:
            self.highlight_and_click('a[href="/harris-matrix"]', "Menu Harris Matrix")
            time.sleep(2)
            self.save_screenshot("harris_matrix_view", "Visualizzazione Harris Matrix")

            # Try GraphML export
            try:
                self.highlight_and_click('a[href="/harris-matrix/graphml"]', "Esporta GraphML")
                self.save_screenshot("harris_matrix_graphml", "Export GraphML")
                self.page.go_back()
            except:
                print("    ℹ️  Export GraphML non disponibile")

        except:
            print("    ℹ️  Harris Matrix non disponibile")

    def explore_harris_creator(self):
        """Esplora Harris Creator"""
        print("\n✏️ === HARRIS MATRIX CREATOR ===")

        try:
            self.highlight_and_click('a[href="/harris-creator"]', "Menu Harris Creator")
            time.sleep(2)
            self.save_screenshot("harris_creator", "Editor Interattivo Harris Matrix")
        except:
            print("    ℹ️  Harris Creator non disponibile")

    def explore_excel_import(self):
        """Esplora Excel Import"""
        print("\n📥 === EXCEL IMPORT ===")

        try:
            self.highlight_and_click('a[href="/excel-import"]', "Menu Excel Import")
            self.save_screenshot("excel_import", "Interfaccia Import Excel")
        except:
            print("    ℹ️  Excel Import non disponibile")

    def explore_pyarchinit_import(self):
        """Esplora PyArchInit Import/Export"""
        print("\n🔄 === PYARCHINIT IMPORT/EXPORT ===")

        try:
            self.highlight_and_click('a[href="/pyarchinit-import-export"]', "Menu PyArchInit I/E")
            self.save_screenshot("pyarchinit_import_export", "PyArchInit Import/Export")
        except:
            print("    ℹ️  PyArchInit I/E non disponibile")

    def explore_em_node_config(self):
        """Esplora EM Node Config"""
        print("\n⚙️ === EXTENDED MATRIX NODE CONFIG ===")

        try:
            self.highlight_and_click('a[href="/em-node-config"]', "Menu EM Node Config")
            self.save_screenshot("em_node_config", "Configurazione Nodi Extended Matrix")
        except:
            print("    ℹ️  EM Node Config non disponibile")

    def explore_analytics(self):
        """Esplora Analytics"""
        print("\n📈 === ANALYTICS ===")

        try:
            self.highlight_and_click('a[href="/analytics"]', "Menu Analytics")
            time.sleep(2)
            self.save_screenshot("analytics_dashboard", "Dashboard Analytics")
        except:
            print("    ℹ️  Analytics non disponibile")

    def explore_validation(self):
        """Esplora Validation"""
        print("\n✅ === VALIDAZIONE STRATIGRAFICA ===")

        try:
            self.highlight_and_click('a[href="/validation"]', "Menu Validazione")
            self.save_screenshot("validation_report", "Report Validazione")
        except:
            print("    ℹ️  Validazione non disponibile")

    def explore_admin(self):
        """Esplora Admin"""
        print("\n🔧 === AMMINISTRAZIONE ===")

        # Database management
        try:
            self.highlight_and_click('a[href="/admin/database"]', "Menu Database")
            self.save_screenshot("admin_database", "Gestione Database")
        except:
            print("    ℹ️  Admin Database non disponibile")

        # User management
        try:
            self.highlight_and_click('a[href="/auth/users"]', "Menu Utenti")
            self.save_screenshot("admin_users", "Gestione Utenti")
        except:
            print("    ℹ️  Gestione Utenti non disponibile")

    def run(self):
        """Esegue cattura completa"""
        print("=" * 70)
        print("PyArchInit-Mini Web GUI - Screenshot Documentation Capture")
        print("=" * 70)

        try:
            self.init_browser()

            # Login
            self.login()

            # Explore all sections
            self.explore_dashboard()
            self.explore_sites()
            self.explore_us()
            self.explore_inventario()
            self.explore_harris_matrix()
            self.explore_harris_creator()
            self.explore_excel_import()
            self.explore_pyarchinit_import()
            self.explore_em_node_config()
            self.explore_analytics()
            self.explore_validation()
            self.explore_admin()

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
