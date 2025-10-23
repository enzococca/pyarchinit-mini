"""
CLI commands for Import/Export from/to PyArchInit (full version) databases
"""

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from pathlib import Path
import os

console = Console()


@click.group()
def pyarchinit():
    """Import and export data from/to PyArchInit (full version)"""
    pass


# ============================================================================
# IMPORT COMMANDS
# ============================================================================

@pyarchinit.command('import-from-pyarchinit')
@click.option('--source-db', '-s', required=True,
              help='Source PyArchInit database connection string (e.g., sqlite:////path/to/pyarchinit_db.sqlite)')
@click.option('--target-db', '-t', envvar='DATABASE_URL',
              help='Target PyArchInit-Mini database (default: sqlite:///./pyarchinit_mini.db)')
@click.option('--tables', '-T', multiple=True,
              type=click.Choice(['sites', 'us', 'inventario', 'periodizzazione', 'thesaurus', 'all']),
              default=['all'],
              help='Tables to import (can specify multiple)')
@click.option('--sites', multiple=True,
              help='Filter by specific site names (can specify multiple)')
@click.option('--import-relationships/--no-import-relationships', default=True,
              help='Import US relationships (default: yes)')
@click.option('--dry-run/--no-dry-run', default=False,
              help='Preview import without making changes')
def import_from_pyarchinit(source_db, target_db, tables, sites, import_relationships, dry_run):
    """
    Import data from PyArchInit (full version) to PyArchInit-Mini

    Examples:

      # Import all data from a PyArchInit SQLite database
      pyarchinit-mini-import import-from-pyarchinit -s sqlite:////path/to/pyarchinit_db.sqlite

      # Import only sites and US for specific sites
      pyarchinit-mini-import import-from-pyarchinit \\
        -s sqlite:////path/to/pyarchinit_db.sqlite \\
        -T sites -T us --sites Pompei --sites Ercolano

      # Import from PostgreSQL
      pyarchinit-mini-import import-from-pyarchinit \\
        -s postgresql://user:password@localhost/pyarchinit_db
    """
    try:
        from pyarchinit_mini.services.import_export_service import ImportExportService

        # Setup target database
        target_db_url = target_db or "sqlite:///./pyarchinit_mini.db"

        # Validate source database connection
        console.print(f"[cyan]Validating source database connection...[/cyan]")
        service = ImportExportService(target_db_url)

        if not service.validate_database_connection(source_db):
            console.print("[red]✗ Failed to connect to source database[/red]")
            raise click.Abort()

        service.set_source_database(source_db)
        console.print("[green]✓ Source database connection valid[/green]")

        # Get available sites in source database
        available_sites = service.get_available_sites_in_source()
        console.print(f"\n[cyan]Available sites in source database:[/cyan] {', '.join(available_sites[:10])}")
        if len(available_sites) > 10:
            console.print(f"[dim]... and {len(available_sites) - 10} more[/dim]")

        # Filter sites
        site_filter = list(sites) if sites else None
        if site_filter:
            console.print(f"\n[yellow]Importing only sites:[/yellow] {', '.join(site_filter)}")

        # Determine what to import
        tables_to_import = list(tables)
        if 'all' in tables_to_import:
            tables_to_import = ['sites', 'us', 'inventario', 'periodizzazione', 'thesaurus']

        # Dry run warning
        if dry_run:
            console.print("\n[yellow]DRY RUN MODE - No changes will be made[/yellow]\n")
            return

        # Confirm import
        if not Confirm.ask(f"\n[bold]Import {', '.join(tables_to_import)} from PyArchInit database?[/bold]"):
            console.print("[yellow]Import cancelled[/yellow]")
            return

        # Track overall statistics
        overall_stats = {}

        # Import Sites
        if 'sites' in tables_to_import:
            console.print("\n[bold cyan]═══ Importing Sites ═══[/bold cyan]")
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Importing sites...", total=None)
                stats = service.import_sites(site_filter)
                progress.remove_task(task)

            overall_stats['sites'] = stats
            _display_import_stats("Sites", stats)

        # Import US
        if 'us' in tables_to_import:
            console.print("\n[bold cyan]═══ Importing US (Stratigraphic Units) ═══[/bold cyan]")
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Importing US...", total=None)
                stats = service.import_us(site_filter, import_relationships)
                progress.remove_task(task)

            overall_stats['us'] = stats
            _display_import_stats("US", stats)

            if import_relationships and stats.get('relationships_created', 0) > 0:
                console.print(f"[green]  ✓ {stats['relationships_created']} relationships created[/green]")

        # Import Inventario Materiali
        if 'inventario' in tables_to_import:
            console.print("\n[bold cyan]═══ Importing Inventario Materiali ═══[/bold cyan]")
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Importing inventario...", total=None)
                stats = service.import_inventario(site_filter)
                progress.remove_task(task)

            overall_stats['inventario'] = stats
            _display_import_stats("Inventario", stats)

        # Import Periodizzazione
        if 'periodizzazione' in tables_to_import:
            console.print("\n[bold cyan]═══ Importing Periodizzazione ═══[/bold cyan]")
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Importing periodizzazione...", total=None)
                stats = service.import_periodizzazione(site_filter)
                progress.remove_task(task)

            overall_stats['periodizzazione'] = stats
            _display_import_stats("Periodizzazione", stats)

        # Import Thesaurus
        if 'thesaurus' in tables_to_import:
            console.print("\n[bold cyan]═══ Importing Thesaurus ═══[/bold cyan]")
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Importing thesaurus...", total=None)
                stats = service.import_thesaurus()
                progress.remove_task(task)

            overall_stats['thesaurus'] = stats
            _display_import_stats("Thesaurus", stats)

        # Display overall summary
        console.print("\n[bold green]═══════════════════════════════════════[/bold green]")
        console.print("[bold green]Import Summary[/bold green]")
        console.print("[bold green]═══════════════════════════════════════[/bold green]\n")

        summary_table = Table(show_header=True, header_style="bold cyan")
        summary_table.add_column("Table", style="cyan")
        summary_table.add_column("Imported", style="green")
        summary_table.add_column("Updated", style="yellow")
        summary_table.add_column("Skipped", style="dim")
        summary_table.add_column("Errors", style="red")

        for table_name, stats in overall_stats.items():
            summary_table.add_row(
                table_name.capitalize(),
                str(stats.get('imported', 0)),
                str(stats.get('updated', 0)),
                str(stats.get('skipped', 0)),
                str(len(stats.get('errors', [])))
            )

        console.print(summary_table)
        console.print("\n[bold green]✓ Import completed successfully![/bold green]\n")

    except Exception as e:
        console.print(f"\n[red]✗ Error during import: {e}[/red]")
        raise click.Abort()


# ============================================================================
# EXPORT COMMANDS
# ============================================================================

@pyarchinit.command('export-to-pyarchinit')
@click.option('--source-db', '-s', envvar='DATABASE_URL',
              help='Source PyArchInit-Mini database (default: sqlite:///./pyarchinit_mini.db)')
@click.option('--target-db', '-t', required=True,
              help='Target PyArchInit database connection string')
@click.option('--tables', '-T', multiple=True,
              type=click.Choice(['sites', 'us', 'inventario', 'periodizzazione', 'thesaurus', 'all']),
              default=['all'],
              help='Tables to export (can specify multiple)')
@click.option('--sites', multiple=True,
              help='Filter by specific site names (can specify multiple)')
@click.option('--export-relationships/--no-export-relationships', default=True,
              help='Export US relationships (default: yes)')
@click.option('--dry-run/--no-dry-run', default=False,
              help='Preview export without making changes')
def export_to_pyarchinit(source_db, target_db, tables, sites, export_relationships, dry_run):
    """
    Export data from PyArchInit-Mini to PyArchInit (full version)

    Examples:

      # Export all data to PyArchInit SQLite database
      pyarchinit-mini-import export-to-pyarchinit -t sqlite:////path/to/pyarchinit_db.sqlite

      # Export only US for specific sites
      pyarchinit-mini-import export-to-pyarchinit \\
        -t sqlite:////path/to/pyarchinit_db.sqlite \\
        -T us --sites Pompei
    """
    try:
        from pyarchinit_mini.services.import_export_service import ImportExportService

        # Setup source database
        source_db_url = source_db or "sqlite:///./pyarchinit_mini.db"
        service = ImportExportService(source_db_url)

        # Validate target database connection
        console.print(f"[cyan]Validating target database connection...[/cyan]")
        if not service.validate_database_connection(target_db):
            console.print("[red]✗ Failed to connect to target database[/red]")
            raise click.Abort()

        console.print("[green]✓ Target database connection valid[/green]")

        # Filter sites
        site_filter = list(sites) if sites else None
        if site_filter:
            console.print(f"\n[yellow]Exporting only sites:[/yellow] {', '.join(site_filter)}")

        # Determine what to export
        tables_to_export = list(tables)
        if 'all' in tables_to_export:
            tables_to_export = ['sites', 'us']  # Only export tables that make sense

        # Dry run warning
        if dry_run:
            console.print("\n[yellow]DRY RUN MODE - No changes will be made[/yellow]\n")
            return

        # Confirm export
        if not Confirm.ask(f"\n[bold]Export {', '.join(tables_to_export)} to PyArchInit database?[/bold]"):
            console.print("[yellow]Export cancelled[/yellow]")
            return

        # Track overall statistics
        overall_stats = {}

        # Export Sites
        if 'sites' in tables_to_export:
            console.print("\n[bold cyan]═══ Exporting Sites ═══[/bold cyan]")
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Exporting sites...", total=None)
                stats = service.export_sites(target_db, site_filter)
                progress.remove_task(task)

            overall_stats['sites'] = stats
            _display_export_stats("Sites", stats)

        # Export US
        if 'us' in tables_to_export:
            console.print("\n[bold cyan]═══ Exporting US (Stratigraphic Units) ═══[/bold cyan]")
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Exporting US...", total=None)
                stats = service.export_us(target_db, site_filter, export_relationships)
                progress.remove_task(task)

            overall_stats['us'] = stats
            _display_export_stats("US", stats)

        # Display overall summary
        console.print("\n[bold green]═══════════════════════════════════════[/bold green]")
        console.print("[bold green]Export Summary[/bold green]")
        console.print("[bold green]═══════════════════════════════════════[/bold green]\n")

        summary_table = Table(show_header=True, header_style="bold cyan")
        summary_table.add_column("Table", style="cyan")
        summary_table.add_column("Exported", style="green")
        summary_table.add_column("Updated", style="yellow")
        summary_table.add_column("Skipped", style="dim")
        summary_table.add_column("Errors", style="red")

        for table_name, stats in overall_stats.items():
            summary_table.add_row(
                table_name.capitalize(),
                str(stats.get('exported', 0)),
                str(stats.get('updated', 0)),
                str(stats.get('skipped', 0)),
                str(len(stats.get('errors', [])))
            )

        console.print(summary_table)
        console.print("\n[bold green]✓ Export completed successfully![/bold green]\n")

    except Exception as e:
        console.print(f"\n[red]✗ Error during export: {e}[/red]")
        raise click.Abort()


# ============================================================================
# UTILITY COMMANDS
# ============================================================================

@pyarchinit.command('list-sites')
@click.option('--database', '-d', required=True,
              help='PyArchInit database connection string')
def list_sites(database):
    """List all available sites in a PyArchInit database"""
    try:
        from pyarchinit_mini.services.import_export_service import ImportExportService

        # Setup service
        service = ImportExportService("sqlite:///./pyarchinit_mini.db")  # Dummy target

        # Validate connection
        console.print(f"[cyan]Connecting to database...[/cyan]")
        if not service.validate_database_connection(database):
            console.print("[red]✗ Failed to connect to database[/red]")
            raise click.Abort()

        service.set_source_database(database)

        # Get sites
        sites = service.get_available_sites_in_source()

        if not sites:
            console.print("[yellow]No sites found in database[/yellow]")
            return

        # Display sites
        console.print(f"\n[bold green]Found {len(sites)} sites:[/bold green]\n")

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim", width=6)
        table.add_column("Site Name", style="green")

        for i, site in enumerate(sites, 1):
            table.add_row(str(i), site)

        console.print(table)

    except Exception as e:
        console.print(f"\n[red]✗ Error: {e}[/red]")
        raise click.Abort()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _display_import_stats(table_name: str, stats: dict):
    """Display import statistics"""
    console.print(f"  [green]Imported:[/green] {stats.get('imported', 0)}")
    console.print(f"  [yellow]Updated:[/yellow] {stats.get('updated', 0)}")
    console.print(f"  [dim]Skipped:[/dim] {stats.get('skipped', 0)}")

    if stats.get('errors'):
        console.print(f"  [red]Errors:[/red] {len(stats['errors'])}")
        if len(stats['errors']) <= 5:
            for error in stats['errors']:
                console.print(f"    [dim]- {error}[/dim]")
        else:
            for error in stats['errors'][:3]:
                console.print(f"    [dim]- {error}[/dim]")
            console.print(f"    [dim]... and {len(stats['errors']) - 3} more errors[/dim]")


def _display_export_stats(table_name: str, stats: dict):
    """Display export statistics"""
    console.print(f"  [green]Exported:[/green] {stats.get('exported', 0)}")
    console.print(f"  [yellow]Updated:[/yellow] {stats.get('updated', 0)}")
    console.print(f"  [dim]Skipped:[/dim] {stats.get('skipped', 0)}")

    if stats.get('errors'):
        console.print(f"  [red]Errors:[/red] {len(stats['errors'])}")
        if len(stats['errors']) <= 5:
            for error in stats['errors']:
                console.print(f"    [dim]- {error}[/dim]")
        else:
            for error in stats['errors'][:3]:
                console.print(f"    [dim]- {error}[/dim]")
            console.print(f"    [dim]... and {len(stats['errors']) - 3} more errors[/dim]")


if __name__ == '__main__':
    pyarchinit()
