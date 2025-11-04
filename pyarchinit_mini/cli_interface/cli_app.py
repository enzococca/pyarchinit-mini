#!/usr/bin/env python3
"""
Interactive CLI for PyArchInit-Mini
"""

import click
import os
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.progress import track
from datetime import datetime

# Add parent directory to path for imports
sys.path.append('..')

from pyarchinit_mini import __version__
from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.services.site_service import SiteService
from pyarchinit_mini.services.us_service import USService
from pyarchinit_mini.services.inventario_service import InventarioService
from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator
from pyarchinit_mini.harris_matrix.matrix_visualizer import MatrixVisualizer
from pyarchinit_mini.pdf_export.pdf_generator import PDFGenerator

console = Console()

class PyArchInitCLI:
    """Interactive CLI for PyArchInit-Mini"""
    
    def __init__(self, database_url: str = None):
        self.console = console
        
        # Setup database
        if not database_url:
            database_url = os.getenv("DATABASE_URL", "sqlite:///./pyarchinit_mini.db")
        
        self.db_conn = DatabaseConnection.from_url(database_url)
        self.db_conn.create_tables()
        self.db_manager = DatabaseManager(self.db_conn)
        
        # Initialize services
        self.site_service = SiteService(self.db_manager)
        self.us_service = USService(self.db_manager)
        self.inventario_service = InventarioService(self.db_manager)
        self.matrix_generator = HarrisMatrixGenerator(self.db_manager)
        self.matrix_visualizer = MatrixVisualizer()
        self.pdf_generator = PDFGenerator()
    
    def show_welcome(self):
        """Show welcome screen"""
        welcome_text = """
🏛️  [bold blue]PyArchInit-Mini CLI[/bold blue]
Archaeological Data Management System

Gestione dati archeologici via interfaccia a riga di comando
        """
        
        self.console.print(Panel(welcome_text, title="Benvenuto", border_style="blue"))
    
    def show_main_menu(self):
        """Show main menu and handle selection"""
        while True:
            self.console.print("\n" + "="*50)
            self.console.print("[bold]MENU PRINCIPALE[/bold]")
            self.console.print("="*50)
            
            options = [
                "1. 🏛️  Gestione Siti Archeologici",
                "2. 📋 Gestione Unità Stratigrafiche (US)",
                "3. 📦 Gestione Inventario Materiali",
                "4. 🔗 Harris Matrix",
                "5. 📊 Statistiche e Report",
                "6. 📄 Export PDF",
                "7. ⚙️  Configurazione Database",
                "8. ❓ Aiuto",
                "0. 🚪 Esci"
            ]
            
            for option in options:
                self.console.print(option)
            
            choice = Prompt.ask("\nSeleziona un'opzione", choices=["0","1","2","3","4","5","6","7","8"])
            
            if choice == "0":
                self.console.print("[green]Arrivederci! 👋[/green]")
                break
            elif choice == "1":
                self.sites_menu()
            elif choice == "2":
                self.us_menu()
            elif choice == "3":
                self.inventario_menu()
            elif choice == "4":
                self.harris_matrix_menu()
            elif choice == "5":
                self.statistics_menu()
            elif choice == "6":
                self.export_menu()
            elif choice == "7":
                self.database_menu()
            elif choice == "8":
                self.show_help()
    
    def sites_menu(self):
        """Sites management menu"""
        while True:
            self.console.print("\n[bold blue]🏛️  GESTIONE SITI[/bold blue]")
            
            options = [
                "1. Lista Siti",
                "2. Crea Nuovo Sito", 
                "3. Visualizza Sito",
                "4. Modifica Sito",
                "5. Elimina Sito",
                "6. Cerca Siti",
                "0. Torna al Menu Principale"
            ]
            
            for option in options:
                self.console.print(option)
            
            choice = Prompt.ask("Seleziona", choices=["0","1","2","3","4","5","6"])
            
            if choice == "0":
                break
            elif choice == "1":
                self.list_sites()
            elif choice == "2":
                self.create_site()
            elif choice == "3":
                self.view_site()
            elif choice == "4":
                self.edit_site()
            elif choice == "5":
                self.delete_site()
            elif choice == "6":
                self.search_sites()
    
    def list_sites(self):
        """List all sites"""
        try:
            sites = self.site_service.get_all_sites(size=50)
            
            if not sites:
                self.console.print("[yellow]Nessun sito trovato[/yellow]")
                return
            
            table = Table(title="Siti Archeologici")
            table.add_column("ID", style="cyan")
            table.add_column("Nome Sito", style="green")
            table.add_column("Comune", style="blue")
            table.add_column("Provincia", style="magenta")
            table.add_column("Nazione", style="red")
            
            for site in sites:
                table.add_row(
                    str(site.id_sito),
                    site.sito,
                    site.comune or "-",
                    site.provincia or "-",
                    site.nazione or "-"
                )
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"[red]Errore: {e}[/red]")
    
    def create_site(self):
        """Create new site"""
        self.console.print("\n[bold]CREA NUOVO SITO[/bold]")
        
        try:
            site_data = {}
            
            site_data['sito'] = Prompt.ask("Nome Sito")
            site_data['nazione'] = Prompt.ask("Nazione", default="Italia")
            site_data['regione'] = Prompt.ask("Regione", default="")
            site_data['comune'] = Prompt.ask("Comune", default="")
            site_data['provincia'] = Prompt.ask("Provincia", default="")
            site_data['definizione_sito'] = Prompt.ask("Definizione Sito", default="")
            site_data['descrizione'] = Prompt.ask("Descrizione", default="")
            
            # Remove empty strings
            site_data = {k: v for k, v in site_data.items() if v}
            
            site = self.site_service.create_site(site_data)
            self.console.print(f"[green]✅ Sito '{site_data['sito']}' creato con successo![/green]")
            
        except Exception as e:
            self.console.print(f"[red]Errore nella creazione: {e}[/red]")
    
    def view_site(self):
        """View site details"""
        try:
            sites = self.site_service.get_all_sites(size=20)
            if not sites:
                self.console.print("[yellow]Nessun sito disponibile[/yellow]")
                return
            
            # Show sites list
            self.console.print("\n[bold]SELEZIONA SITO[/bold]")
            for i, site in enumerate(sites, 1):
                self.console.print(f"{i}. {site.sito} ({site.comune})")
            
            choice = Prompt.ask("Numero sito (0 per annullare)", default="0")
            
            try:
                site_idx = int(choice) - 1
                if 0 <= site_idx < len(sites):
                    site = sites[site_idx]
                    
                    # Show site details
                    info_text = f"""
[bold]Nome:[/bold] {site.sito}
[bold]Comune:[/bold] {site.comune or 'N/A'}
[bold]Provincia:[/bold] {site.provincia or 'N/A'}
[bold]Regione:[/bold] {site.regione or 'N/A'}
[bold]Nazione:[/bold] {site.nazione or 'N/A'}
[bold]Definizione:[/bold] {site.definizione_sito or 'N/A'}
[bold]Descrizione:[/bold] {site.descrizione or 'N/A'}
                    """
                    
                    self.console.print(Panel(info_text, title=f"Dettagli Sito: {site.sito}"))
                    
                    # Show related data counts
                    site_name = site.sito
                    us_count = self.us_service.count_us({'sito': site_name})
                    inv_count = self.inventario_service.count_inventario({'sito': site_name})
                    
                    self.console.print(f"\n[blue]US associate: {us_count}[/blue]")
                    self.console.print(f"[blue]Reperti catalogati: {inv_count}[/blue]")
                
            except (ValueError, IndexError):
                self.console.print("[red]Selezione non valida[/red]")
                
        except Exception as e:
            self.console.print(f"[red]Errore: {e}[/red]")
    
    def us_menu(self):
        """US management menu"""
        while True:
            self.console.print("\n[bold blue]📋 GESTIONE US[/bold blue]")
            
            options = [
                "1. Lista US",
                "2. Crea Nuova US",
                "3. Visualizza US",
                "4. Lista US per Sito",
                "0. Torna al Menu Principale"
            ]
            
            for option in options:
                self.console.print(option)
            
            choice = Prompt.ask("Seleziona", choices=["0","1","2","3","4"])
            
            if choice == "0":
                break
            elif choice == "1":
                self.list_us()
            elif choice == "2":
                self.create_us()
            elif choice == "3":
                self.view_us()
            elif choice == "4":
                self.list_us_by_site()
    
    def list_us(self):
        """List all US"""
        try:
            us_list = self.us_service.get_all_us(size=50)
            
            if not us_list:
                self.console.print("[yellow]Nessuna US trovata[/yellow]")
                return
            
            table = Table(title="Unità Stratigrafiche")
            table.add_column("Sito", style="cyan")
            table.add_column("Area", style="green")
            table.add_column("US", style="blue", justify="right")
            table.add_column("Descrizione", style="white")
            table.add_column("Anno", style="magenta", justify="right")
            
            for us in us_list:
                table.add_row(
                    us.sito or "-",
                    us.area or "-",
                    str(us.us),
                    (us.d_stratigrafica or "")[:40] + "..." if len(us.d_stratigrafica or "") > 40 else (us.d_stratigrafica or "-"),
                    str(us.anno_scavo) if us.anno_scavo else "-"
                )
            
            self.console.print(table)
            
        except Exception as e:
            self.console.print(f"[red]Errore: {e}[/red]")
    
    def harris_matrix_menu(self):
        """Harris Matrix menu"""
        while True:
            self.console.print("\n[bold blue]🔗 HARRIS MATRIX[/bold blue]")
            
            options = [
                "1. Genera Matrix per Sito",
                "2. Visualizza Matrix",
                "3. Esporta Matrix",
                "4. Statistiche Matrix",
                "0. Torna al Menu Principale"
            ]
            
            for option in options:
                self.console.print(option)
            
            choice = Prompt.ask("Seleziona", choices=["0","1","2","3","4"])
            
            if choice == "0":
                break
            elif choice == "1":
                self.generate_harris_matrix()
            elif choice == "2":
                self.view_harris_matrix()
            elif choice == "3":
                self.export_harris_matrix()
            elif choice == "4":
                self.harris_matrix_stats()
    
    def generate_harris_matrix(self):
        """Generate Harris Matrix for a site"""
        try:
            # Get sites
            sites = self.site_service.get_all_sites(size=20)
            if not sites:
                self.console.print("[yellow]Nessun sito disponibile[/yellow]")
                return
            
            # Select site
            self.console.print("\n[bold]SELEZIONA SITO[/bold]")
            for i, site in enumerate(sites, 1):
                self.console.print(f"{i}. {site.sito}")
            
            choice = Prompt.ask("Numero sito", default="0")
            
            try:
                site_idx = int(choice) - 1
                if 0 <= site_idx < len(sites):
                    site_name = sites[site_idx].sito
                    
                    with self.console.status(f"[bold green]Generando Harris Matrix per {site_name}..."):
                        # Generate matrix
                        graph = self.matrix_generator.generate_matrix(site_name)
                        levels = self.matrix_generator.get_matrix_levels(graph)
                        stats = self.matrix_generator.get_matrix_statistics(graph)
                    
                    # Show statistics
                    stats_text = f"""
[bold]Sito:[/bold] {site_name}
[bold]Totale US:[/bold] {stats['total_us']}
[bold]Relazioni:[/bold] {stats['total_relationships']}
[bold]Livelli:[/bold] {stats['levels']}
[bold]Matrix Valida:[/bold] {'Sì' if stats['is_valid'] else 'No'}
[bold]US Isolate:[/bold] {stats['isolated_us']}
                    """
                    
                    self.console.print(Panel(stats_text, title="Statistiche Harris Matrix"))
                    
                    # Show levels
                    if levels:
                        self.console.print("\n[bold]LIVELLI STRATIGRAFICI:[/bold]")
                        for level, us_list in levels.items():
                            self.console.print(f"Livello {level}: US {', '.join(map(str, us_list))}")
                    
                    # Ask for export
                    if Confirm.ask("Vuoi esportare la matrix?"):
                        # Ask for format
                        self.console.print("\n[bold]FORMATO EXPORT:[/bold]")
                        self.console.print("1. PNG/SVG/HTML (visualizzazione)")
                        self.console.print("2. GraphML (yEd - Extended Matrix)")
                        self.console.print("3. Entrambi")

                        export_choice = Prompt.ask("Seleziona formato", choices=["1","2","3"], default="3")

                        filename = f"harris_matrix_{site_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        exports = {}

                        # Export PNG/SVG/HTML
                        if export_choice in ["1", "3"]:
                            with self.console.status("[bold green]Esportando matrix (PNG/SVG/HTML)..."):
                                viz_exports = self.matrix_visualizer.export_to_formats(graph, levels, filename)
                                exports.update(viz_exports)

                        # Export GraphML
                        if export_choice in ["2", "3"]:
                            with self.console.status("[bold green]Esportando matrix (GraphML)..."):
                                graphml_path = f"{filename}.graphml"
                                result = self.matrix_generator.export_to_graphml(
                                    graph=graph,
                                    output_path=graphml_path,
                                    site_name=site_name,
                                    title=site_name,
                                    use_extended_labels=True,
                                    include_periods=True,
                                    reverse_epochs=False
                                )
                                if result:
                                    exports['graphml'] = result

                        if exports:
                            self.console.print(f"[green]✅ Matrix esportata in: {', '.join(exports.keys())}[/green]")
                            for format_type, path in exports.items():
                                self.console.print(f"  {format_type}: {path}")
                        else:
                            self.console.print("[red]❌ Errore durante l'export[/red]")
                
            except (ValueError, IndexError):
                self.console.print("[red]Selezione non valida[/red]")
                
        except Exception as e:
            self.console.print(f"[red]Errore: {e}[/red]")
    
    def statistics_menu(self):
        """Statistics and reports menu"""
        self.console.print("\n[bold blue]📊 STATISTICHE[/bold blue]")
        
        try:
            # Get basic statistics
            total_sites = self.site_service.count_sites()
            total_us = self.us_service.count_us()
            total_inventory = self.inventario_service.count_inventario()
            
            stats_text = f"""
[bold]STATISTICHE GENERALI[/bold]

🏛️  [bold]Siti Archeologici:[/bold] {total_sites}
📋 [bold]Unità Stratigrafiche:[/bold] {total_us}
📦 [bold]Reperti Catalogati:[/bold] {total_inventory}

[bold]DATABASE:[/bold] {self.db_conn.connection_string.split('://')[0].upper()}
[bold]DATA AGGIORNAMENTO:[/bold] {datetime.now().strftime('%d/%m/%Y %H:%M')}
            """
            
            self.console.print(Panel(stats_text, title="Dashboard Statistiche"))
            
            # Site statistics
            if total_sites > 0:
                sites = self.site_service.get_all_sites(size=10)
                
                table = Table(title="Statistiche per Sito")
                table.add_column("Sito", style="cyan")
                table.add_column("US", style="blue", justify="right")
                table.add_column("Reperti", style="green", justify="right")
                
                for site in sites:
                    site_name = site.sito
                    us_count = self.us_service.count_us({'sito': site_name})
                    inv_count = self.inventario_service.count_inventario({'sito': site_name})
                    
                    table.add_row(site_name, str(us_count), str(inv_count))
                
                self.console.print(table)
            
        except Exception as e:
            self.console.print(f"[red]Errore: {e}[/red]")
    
    def show_help(self):
        """Show help information"""
        help_text = """
[bold blue]AIUTO PYARCHINIT-MINI CLI[/bold blue]

[bold]COMANDI PRINCIPALI:[/bold]
• Gestione Siti: Crea, visualizza, modifica siti archeologici
• Gestione US: Gestisci unità stratigrafiche
• Inventario: Cataloga e gestisci reperti
• Harris Matrix: Genera matrici stratigrafiche
• Statistiche: Visualizza report e statistiche
• Export: Esporta dati in PDF

[bold]NAVIGAZIONE:[/bold]
• Usa i numeri per selezionare le opzioni
• Premi 0 per tornare al menu precedente
• Premi Ctrl+C per uscire in qualsiasi momento

[bold]DATABASE:[/bold]
La CLI si connette automaticamente al database configurato.
Usa la variabile d'ambiente DATABASE_URL per configurare la connessione.

[bold]ESEMPI:[/bold]
export DATABASE_URL="postgresql://user:pass@localhost/pyarchinit"
export DATABASE_URL="sqlite:///./mio_database.db"

[bold]SUPPORTO:[/bold]
GitHub: https://github.com/enzococca/pyarchinit-mini
Email: enzo.ccc@gmail.com
        """
        
        self.console.print(Panel(help_text, title="Aiuto"))
    
    def run(self):
        """Run the CLI application"""
        try:
            self.show_welcome()
            self.show_main_menu()
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Operazione interrotta dall'utente[/yellow]")
        except Exception as e:
            self.console.print(f"\n[red]Errore imprevisto: {e}[/red]")
        finally:
            self.db_conn.close()

@click.command()
@click.option('--database-url', '-d', help='Database URL connection string')
@click.option('--version', is_flag=True, help='Show version information')
@click.option('--list-commands', is_flag=True, help='List all available commands')
def main(database_url, version, list_commands):
    """PyArchInit-Mini Interactive CLI

    This is the main interactive CLI for PyArchInit-Mini.

    For other specialized commands, use:

    \b
    INTERFACES:
      pyarchinit-mini              Interactive CLI (this command)
      pyarchinit-mini-api          REST API server
      pyarchinit-mini-web          Web interface
      pyarchinit-mini-gui          Desktop GUI application

    \b
    SETUP & CONFIGURATION:
      pyarchinit-mini-setup        Setup user environment
      pyarchinit-mini-init         Initialize database and create admin user
      pyarchinit-mini-configure-claude  Configure Claude Desktop MCP
      pyarchinit-mini-migrate      Run database migrations

    \b
    MCP SERVERS:
      pyarchinit-mini-mcp          MCP server (stdio)
      pyarchinit-mini-mcp-http     MCP server (HTTP)
      pyarchinit-mcp-server        MCP server (alias)
      pyarchinit-mcp-http          MCP HTTP server (alias)

    \b
    DATA IMPORT/EXPORT:
      pyarchinit-export-import     Export/import data to Excel/CSV
      pyarchinit-graphml           Export Harris Matrix to GraphML
      pyarchinit-mini-import       Import from PyArchInit v18+
      pyarchinit-harris-import     Import Harris Matrix from Excel
      pyarchinit-harris-template   Generate Harris Matrix Excel template

    \b
    EXAMPLES:
      # Start interactive CLI with default database
      pyarchinit-mini

      # Connect to PostgreSQL database
      pyarchinit-mini -d "postgresql://user:pass@localhost/pyarchinit"

      # Start web interface
      pyarchinit-mini-web

      # Generate Harris Matrix template
      pyarchinit-harris-template --site "My Site" --output template.xlsx

      # Import from PyArchInit
      pyarchinit-mini-import --input pyarchinit.db --output pyarchinit_mini.db

    For detailed help on each command, use: <command> --help
    """

    if version:
        console.print(f"[bold blue]PyArchInit-Mini v{__version__}[/bold blue]")
        console.print("Archaeological Data Management System\n")
        console.print(f"[dim]Python Package: pyarchinit-mini[/dim]")
        console.print(f"[dim]GitHub: https://github.com/enzococca/pyarchinit-mini[/dim]")
        return

    if list_commands:
        console.print(f"\n[bold blue]PyArchInit-Mini v{__version__} - Complete Command Reference[/bold blue]\n")

        # INTERFACES Section
        console.print("[bold cyan]═══ INTERFACES ═══[/bold cyan]\n")

        console.print("[green]pyarchinit-mini[/green]")
        console.print("  Interactive CLI with menu-driven interface")
        console.print("  [dim]Options:[/dim]")
        console.print("    -d, --database-url TEXT    Database connection string")
        console.print("    --version                  Show version")
        console.print("    --list-commands            Show this help")
        console.print("  [dim]Example:[/dim] pyarchinit-mini -d \"postgresql://user:pass@localhost/db\"\n")

        console.print("[green]pyarchinit-mini-api[/green]")
        console.print("  REST API server on port 8000")
        console.print("  [dim]Options:[/dim]")
        console.print("    --host TEXT                Host to bind (default: 0.0.0.0)")
        console.print("    --port INTEGER             Port number (default: 8000)")
        console.print("  [dim]Example:[/dim] pyarchinit-mini-api --host localhost --port 5000\n")

        console.print("[green]pyarchinit-mini-web[/green]")
        console.print("  Web interface on port 5001")
        console.print("  [dim]Options:[/dim]")
        console.print("    --host TEXT                Host to bind (default: 0.0.0.0)")
        console.print("    --port INTEGER             Port number (default: 5001)")
        console.print("    --debug                    Enable debug mode")
        console.print("  [dim]Example:[/dim] pyarchinit-mini-web --port 8080 --debug\n")

        console.print("[green]pyarchinit-mini-gui[/green]")
        console.print("  Desktop GUI application (requires PyQt5)")
        console.print("  [dim]Example:[/dim] pyarchinit-mini-gui\n")

        # SETUP & CONFIGURATION Section
        console.print("[bold cyan]═══ SETUP & CONFIGURATION ═══[/bold cyan]\n")

        console.print("[green]pyarchinit-mini-setup[/green]")
        console.print("  Setup user environment in ~/.pyarchinit_mini")
        console.print("  [dim]Creates directories:[/dim] data, media, export, backup, config, logs")
        console.print("  [dim]Copies sample database and creates default configuration[/dim]")
        console.print("  [dim]Example:[/dim] pyarchinit-mini-setup\n")

        console.print("[green]pyarchinit-mini-init[/green]")
        console.print("  Initialize database and create admin user")
        console.print("  [dim]Creates all required tables and default admin account[/dim]")
        console.print("  [dim]Example:[/dim] pyarchinit-mini-init\n")

        console.print("[green]pyarchinit-mini-configure-claude[/green]")
        console.print("  Configure Claude Desktop MCP integration")
        console.print("  [dim]Automatically detects and configures Claude Desktop[/dim]")
        console.print("  [dim]Requires uvx to be installed (pip install uv)[/dim]")
        console.print("  [dim]Example:[/dim] pyarchinit-mini-configure-claude\n")

        console.print("[green]pyarchinit-mini-migrate[/green]")
        console.print("  Run database migrations")
        console.print("  [dim]Options:[/dim]")
        console.print("    --database-url TEXT        Database connection string")
        console.print("  [dim]Example:[/dim] pyarchinit-mini-migrate --database-url \"sqlite:///my_db.db\"\n")

        # MCP SERVERS Section
        console.print("[bold cyan]═══ MCP SERVERS ═══[/bold cyan]\n")

        console.print("[green]pyarchinit-mini-mcp[/green] / [green]pyarchinit-mcp-server[/green]")
        console.print("  MCP server using stdio transport (for Claude Desktop)")
        console.print("  [dim]Configured automatically via pyarchinit-mini-configure-claude[/dim]")
        console.print("  [dim]Example:[/dim] pyarchinit-mini-mcp\n")

        console.print("[green]pyarchinit-mini-mcp-http[/green] / [green]pyarchinit-mcp-http[/green]")
        console.print("  MCP server using HTTP transport")
        console.print("  [dim]Options:[/dim]")
        console.print("    --host TEXT                Host to bind (default: localhost)")
        console.print("    --port INTEGER             Port number (default: 8080)")
        console.print("  [dim]Example:[/dim] pyarchinit-mini-mcp-http --port 9000\n")

        # DATA IMPORT/EXPORT Section
        console.print("[bold cyan]═══ DATA IMPORT/EXPORT ═══[/bold cyan]\n")

        console.print("[green]pyarchinit-export-import[/green]")
        console.print("  Export/import data to/from Excel and CSV")
        console.print("  [dim]Subcommands:[/dim]")
        console.print("    export-sites               Export all sites")
        console.print("    export-us                  Export stratigraphic units")
        console.print("    export-inventario          Export inventory")
        console.print("  [dim]Options (common):[/dim]")
        console.print("    -f, --format [excel|csv]   Output format (default: csv)")
        console.print("    -o, --output PATH          Output file path (required)")
        console.print("    -s, --site TEXT            Filter by site name")
        console.print("    -d, --database-url TEXT    Database connection")
        console.print("  [dim]Examples:[/dim]")
        console.print("    pyarchinit-export-import export-sites -f excel -o sites.xlsx")
        console.print("    pyarchinit-export-import export-us -f csv -o us.csv -s \"Pompei\"\n")

        console.print("[green]pyarchinit-graphml[/green]")
        console.print("  Convert Graphviz DOT files to yEd GraphML format")
        console.print("  [dim]Subcommands:[/dim]")
        console.print("    convert INPUT OUTPUT       Convert DOT to GraphML")
        console.print("    template OUTPUT            Download yEd template")
        console.print("  [dim]Options (convert):[/dim]")
        console.print("    -t, --title TEXT           Diagram title")
        console.print("    --reverse-epochs           Reverse epoch ordering")
        console.print("    -v, --verbose              Verbose output")
        console.print("  [dim]Examples:[/dim]")
        console.print("    pyarchinit-graphml convert harris.dot output.graphml -t \"Pompei\"")
        console.print("    pyarchinit-graphml template my_palette.graphml\n")

        console.print("[green]pyarchinit-mini-import[/green]")
        console.print("  Import from PyArchInit (full version) database")
        console.print("  [dim]Subcommands:[/dim]")
        console.print("    import-from-pyarchinit     Import data from PyArchInit v18+")
        console.print("  [dim]Options:[/dim]")
        console.print("    -s, --source-db TEXT       Source database URL (required)")
        console.print("    -t, --target-db TEXT       Target database URL")
        console.print("    -T, --tables [sites|us|inventario|periodizzazione|thesaurus|all]")
        console.print("                               Tables to import (multiple allowed)")
        console.print("    --sites TEXT               Filter by site names (multiple allowed)")
        console.print("    --import-relationships     Import US relationships (default: yes)")
        console.print("    --dry-run                  Preview without changes")
        console.print("  [dim]Examples:[/dim]")
        console.print("    pyarchinit-mini-import import-from-pyarchinit \\")
        console.print("      -s sqlite:////path/to/pyarchinit.db")
        console.print("    pyarchinit-mini-import import-from-pyarchinit \\")
        console.print("      -s postgresql://user:pass@host/db \\")
        console.print("      -T sites -T us --sites \"Pompei\" --dry-run\n")

        console.print("[green]pyarchinit-harris-import[/green]")
        console.print("  Import Harris Matrix from Excel/CSV files")
        console.print("  [dim]Arguments:[/dim]")
        console.print("    INPUT_FILE                 Excel or CSV file with Harris Matrix data")
        console.print("  [dim]Options:[/dim]")
        console.print("    --site TEXT                Site name (required)")
        console.print("    --export-graphml           Export to GraphML after import")
        console.print("    --output PATH              GraphML output path")
        console.print("    -d, --database-url TEXT    Database connection")
        console.print("  [dim]File structure:[/dim]")
        console.print("    Sheet 1 (NODES): us_number, unit_type, description, area, period")
        console.print("    Sheet 2 (RELATIONSHIPS): from_us, to_us, relationship, notes")
        console.print("  [dim]Examples:[/dim]")
        console.print("    pyarchinit-harris-import matrix.xlsx --site \"Pompei\"")
        console.print("    pyarchinit-harris-import matrix.csv --site \"Rome\" --export-graphml\n")

        console.print("[green]pyarchinit-harris-template[/green]")
        console.print("  Generate Harris Matrix Excel template")
        console.print("  [dim]Options:[/dim]")
        console.print("    --site TEXT                Site name for template")
        console.print("    --output PATH              Output file path (default: harris_template.xlsx)")
        console.print("    --format [excel|csv]       Template format")
        console.print("  [dim]Example:[/dim] pyarchinit-harris-template --site \"My Site\" -o template.xlsx\n")

        console.print("[bold]═══════════════════════════════════════════════════════════[/bold]")
        console.print("[dim]For detailed help on any command, use: <command> --help[/dim]")
        console.print("[dim]Documentation: https://github.com/enzococca/pyarchinit-mini[/dim]")
        return

    cli = PyArchInitCLI(database_url)
    cli.run()

if __name__ == '__main__':
    main()