#!/usr/bin/env python3
"""
Harris Matrix CSV/Excel Import Tool
===================================

This tool allows you to create a complete Harris Matrix by importing data
from CSV or Excel files. The import includes:
- Site information
- US (Stratigraphic Unit) nodes with Extended Matrix types
- Relationships between nodes
- Period (datazione) and area grouping

The data is saved to the database and can be exported to GraphML/DOT formats.

Template Structure:
------------------
The Excel/CSV template has two sections (sheets in Excel):

1. NODES sheet - Define all US nodes
2. RELATIONSHIPS sheet - Define connections between nodes

Usage:
------
    pyarchinit-harris-import template.xlsx --site "My Site"
    pyarchinit-harris-import matrix.csv --site "Archaeological Site" --export-graphml
"""

import click
import pandas as pd
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from sqlalchemy.orm import Session

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.database.manager import DatabaseManager
from pyarchinit_mini.models.site import Site
from pyarchinit_mini.models.us import US
from pyarchinit_mini.models.harris_matrix import USRelationships, Periodizzazione
from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator
from pyarchinit_mini.services.us_service import USService


class HarrisMatrixImporter:
    """
    Import Harris Matrix data from CSV/Excel files
    """

    # Extended Matrix node types
    EM_NODE_TYPES = [
        'US',        # Standard stratigraphic unit (default)
        'USM',       # Mural stratigraphic unit
        'USVA',      # Virtual US type A
        'USVB',      # Virtual US type B
        'USVC',      # Virtual US type C
        'TU',        # Topographic unit
        'USD',       # Stratigraphic unit (special)
        'SF',        # Special finds
        'VSF',       # Virtual special finds
        'CON',       # Context
        'DOC',       # Document (requires file_path)
        'Extractor', # Extractor node (special aggregation)
        'Combiner',  # Combiner node (special aggregation)
        'property'   # Property node
    ]

    # Relationship types (Extended Matrix)
    RELATIONSHIP_TYPES = {
        # Standard stratigraphic (for US/USM)
        'Covers': 'Copre',
        'Covered_by': 'Coperto da',
        'Fills': 'Riempie',
        'Filled_by': 'Riempito da',
        'Cuts': 'Taglia',
        'Cut_by': 'Tagliato da',
        'Bonds_to': 'Si lega a',
        'Equal_to': 'Uguale a',
        'Leans_on': 'Si appoggia a',

        # Extended Matrix symbols
        '>': '>',    # Connection to single-symbol units (USVA, USVB, etc.)
        '<': '<',    # Reverse connection from single-symbol units
        '>>': '>>', # Connection to double-symbol units (Extractor, Combiner, DOC)
        '<<': '<<', # Reverse connection from double-symbol units

        # Special
        'Continuity': 'Continuity',  # Contemporary units (no arrow)
    }

    def __init__(self, session: Session, db_manager=None):
        self.session = session
        self.db_manager = db_manager
        self.errors = []
        self.warnings = []

    def validate_file(self, file_path: str) -> bool:
        """Validate input file exists and has correct format"""
        if not os.path.exists(file_path):
            self.errors.append(f"File not found: {file_path}")
            return False

        ext = os.path.splitext(file_path)[1].lower()
        if ext not in ['.csv', '.xlsx', '.xls']:
            self.errors.append(f"Unsupported file format: {ext}. Use .csv, .xlsx, or .xls")
            return False

        return True

    def read_file(self, file_path: str) -> Tuple[Optional[pd.DataFrame], Optional[pd.DataFrame]]:
        """
        Read CSV or Excel file and return nodes and relationships dataframes

        Returns:
            (nodes_df, relationships_df) or (None, None) on error
        """
        ext = os.path.splitext(file_path)[1].lower()

        try:
            if ext == '.csv':
                # For CSV, we expect two sections separated by empty line
                # Section 1: NODES
                # Section 2: RELATIONSHIPS
                df = pd.read_csv(file_path)

                # Find split point (empty row between sections)
                split_idx = None
                for idx, row in df.iterrows():
                    if row.isna().all():
                        split_idx = idx
                        break

                if split_idx is None:
                    self.errors.append("CSV must have two sections (NODES and RELATIONSHIPS) separated by empty line")
                    return None, None

                nodes_df = df[:split_idx].copy()
                relationships_df = df[split_idx+1:].copy()

                # Remove header markers if present
                if nodes_df.iloc[0,0] == 'NODES':
                    nodes_df = nodes_df[1:]
                if relationships_df.iloc[0,0] == 'RELATIONSHIPS':
                    relationships_df = relationships_df[1:]

            else:  # Excel
                # Read both sheets
                excel_file = pd.ExcelFile(file_path)

                if 'NODES' not in excel_file.sheet_names:
                    self.errors.append("Excel file must have 'NODES' sheet")
                    return None, None

                if 'RELATIONSHIPS' not in excel_file.sheet_names:
                    self.errors.append("Excel file must have 'RELATIONSHIPS' sheet")
                    return None, None

                nodes_df = pd.read_excel(file_path, sheet_name='NODES')
                relationships_df = pd.read_excel(file_path, sheet_name='RELATIONSHIPS')

            # Clean dataframes
            nodes_df = nodes_df.dropna(how='all')  # Remove completely empty rows
            relationships_df = relationships_df.dropna(how='all')

            return nodes_df, relationships_df

        except Exception as e:
            self.errors.append(f"Error reading file: {str(e)}")
            return None, None

    def validate_nodes(self, nodes_df: pd.DataFrame) -> bool:
        """Validate nodes dataframe structure and content"""
        required_columns = ['us_number', 'unit_type']

        # Check required columns
        for col in required_columns:
            if col not in nodes_df.columns:
                self.errors.append(f"NODES section missing required column: {col}")
                return False

        # Validate each node
        for idx, row in nodes_df.iterrows():
            us_num = row.get('us_number')
            unit_type = row.get('unit_type', 'US')

            # Check US number
            if pd.isna(us_num):
                self.errors.append(f"Row {idx+2}: us_number is required")
                continue

            # Check unit type
            if unit_type not in self.EM_NODE_TYPES:
                self.warnings.append(f"Row {idx+2}: Unknown unit_type '{unit_type}', defaulting to 'US'")

            # Check DOC type has file_path
            if unit_type == 'DOC' and pd.isna(row.get('file_path')):
                self.warnings.append(f"Row {idx+2}: DOC unit type should have file_path")

        return True

    def validate_relationships(self, relationships_df: pd.DataFrame, valid_us_numbers: set) -> bool:
        """Validate relationships dataframe"""
        required_columns = ['from_us', 'to_us', 'relationship']

        # Check required columns
        for col in required_columns:
            if col not in relationships_df.columns:
                self.errors.append(f"RELATIONSHIPS section missing required column: {col}")
                return False

        # Validate each relationship
        for idx, row in relationships_df.iterrows():
            from_us = row.get('from_us')
            to_us = row.get('to_us')
            rel_type = row.get('relationship')

            # Check all fields present
            if pd.isna(from_us) or pd.isna(to_us) or pd.isna(rel_type):
                self.errors.append(f"Row {idx+2}: from_us, to_us, and relationship are all required")
                continue

            # Check US numbers exist in nodes
            if str(from_us) not in valid_us_numbers:
                self.errors.append(f"Row {idx+2}: from_us '{from_us}' not defined in NODES section")

            if str(to_us) not in valid_us_numbers:
                self.errors.append(f"Row {idx+2}: to_us '{to_us}' not defined in NODES section")

            # Check relationship type
            if rel_type not in self.RELATIONSHIP_TYPES and rel_type not in self.RELATIONSHIP_TYPES.values():
                self.warnings.append(f"Row {idx+2}: Unknown relationship type '{rel_type}'")

        return True

    def import_matrix(self, file_path: str, site_name: str,
                     export_graphml: bool = False,
                     export_dot: bool = False,
                     output_dir: Optional[str] = None,
                     reverse_edges: bool = False) -> bool:
        """
        Import complete Harris Matrix from file

        Args:
            file_path: Path to CSV or Excel file
            site_name: Name of archaeological site
            export_graphml: Export to GraphML format after import
            export_dot: Export to DOT format after import
            output_dir: Directory for exports (default: current directory)
            reverse_edges: Reverse edge direction in GraphML (default: False)

        Returns:
            True if successful, False otherwise
        """
        # Validate file
        if not self.validate_file(file_path):
            return False

        # Read file
        click.echo(f"📖 Reading file: {file_path}")
        nodes_df, relationships_df = self.read_file(file_path)

        if nodes_df is None or relationships_df is None:
            return False

        click.echo(f"   Found {len(nodes_df)} nodes and {len(relationships_df)} relationships")

        # Validate structure
        valid_us_numbers = set(str(us) for us in nodes_df['us_number'].dropna())

        if not self.validate_nodes(nodes_df):
            return False

        if not self.validate_relationships(relationships_df, valid_us_numbers):
            return False

        # Print warnings
        for warning in self.warnings:
            click.echo(f"⚠️  {warning}", err=True)

        if self.errors:
            click.echo(f"\n❌ Found {len(self.errors)} errors:", err=True)
            for error in self.errors:
                click.echo(f"   - {error}", err=True)
            return False

        # Get or create site
        click.echo(f"\n🏛️  Site: {site_name}")
        site = self.session.query(Site).filter_by(sito=site_name).first()

        if not site:
            click.echo(f"   Creating new site...")
            site = Site(sito=site_name)
            self.session.add(site)
            self.session.flush()
        else:
            click.echo(f"   Using existing site (ID: {site.id_sito})")

        # Import nodes
        click.echo(f"\n📥 Importing nodes...")
        node_map = {}  # us_number -> US object

        for idx, row in nodes_df.iterrows():
            us_number = str(row['us_number'])
            unit_type = row.get('unit_type', 'US')
            description = row.get('description', '')
            area = row.get('area', '')
            period = row.get('period', '')
            phase = row.get('phase', '')
            file_path_val = row.get('file_path', '')

            # Check if US already exists
            us = self.session.query(US).filter_by(
                sito=site_name,
                area=area if area else None,
                us=us_number
            ).first()

            if us:
                click.echo(f"   ⟳ US {us_number}: Already exists, updating...")
            else:
                us = US()
                click.echo(f"   ✓ US {us_number}: Created")

            # Set fields
            us.sito = site_name
            us.area = area if area else None
            us.us = us_number
            us.d_stratigrafica = description if description else None
            us.unita_tipo = unit_type if unit_type in self.EM_NODE_TYPES else 'US'
            us.periodo_iniziale = period if period else None
            us.fase_iniziale = phase if phase else None

            # Add new US to session (id_us will be auto-generated)
            if not us.id_us:
                self.session.add(us)

            # DOC specific fields
            if unit_type == 'DOC' and file_path_val:
                us.file_path = file_path_val
                # Try to determine document type from extension
                ext = os.path.splitext(file_path_val)[1].lower()
                doc_types = {
                    '.pdf': 'PDF',
                    '.docx': 'DOCX',
                    '.doc': 'DOC',
                    '.csv': 'CSV',
                    '.xlsx': 'Excel',
                    '.xls': 'Excel',
                    '.txt': 'TXT',
                    '.jpg': 'image',
                    '.jpeg': 'image',
                    '.png': 'image'
                }
                us.tipo_documento = doc_types.get(ext, 'unknown')

            node_map[us_number] = us

            # Create periodizzazione record if period/phase specified
            if period or phase:
                datazione_estesa = f"{period} - {phase}" if (period and phase) else (period or phase)

                # Check if periodizzazione exists
                periodizzazione = self.session.query(Periodizzazione).filter_by(
                    sito=site_name,
                    us=us_number
                ).first()

                if periodizzazione:
                    periodizzazione.periodo_iniziale = period if period else None
                    periodizzazione.fase_iniziale = phase if phase else None
                    periodizzazione.datazione_estesa = datazione_estesa
                    periodizzazione.area = area if area else None
                else:
                    periodizzazione = Periodizzazione(
                        sito=site_name,
                        area=area if area else None,
                        us=us_number,
                        periodo_iniziale=period if period else None,
                        fase_iniziale=phase if phase else None,
                        datazione_estesa=datazione_estesa
                    )
                    self.session.add(periodizzazione)

        # Flush to get IDs
        self.session.flush()

        # Import relationships
        click.echo(f"\n🔗 Importing relationships...")

        for idx, row in relationships_df.iterrows():
            from_us = str(row['from_us'])
            to_us = str(row['to_us'])
            rel_type = row['relationship']

            # Map English names to Italian if needed
            if rel_type in self.RELATIONSHIP_TYPES:
                rel_type = self.RELATIONSHIP_TYPES[rel_type]

            # Check if relationship already exists
            existing = self.session.query(USRelationships).filter_by(
                sito=site_name,
                us_from=from_us,
                us_to=to_us,
                relationship_type=rel_type
            ).first()

            if existing:
                click.echo(f"   ⟳ {from_us} -> {to_us} ({rel_type}): Already exists")
                continue

            relationship = USRelationships(
                sito=site_name,
                us_from=from_us,
                us_to=to_us,
                relationship_type=rel_type
            )
            self.session.add(relationship)
            click.echo(f"   ✓ {from_us} -> {to_us} ({rel_type})")

        # Commit to database
        try:
            self.session.commit()
            click.echo(f"\n✅ Successfully imported Harris Matrix to database")
        except Exception as e:
            self.session.rollback()
            self.errors.append(f"Database error: {str(e)}")
            return False

        # Export if requested
        if export_graphml or export_dot:
            click.echo(f"\n📤 Exporting...")
            self._export_matrix(site_name, export_graphml, export_dot, output_dir, reverse_edges)

        return True

    def _export_matrix(self, site_name: str, export_graphml: bool, export_dot: bool, output_dir: Optional[str], reverse_edges: bool = False):
        """Export matrix to GraphML and/or DOT formats"""
        if output_dir is None:
            output_dir = '.'

        os.makedirs(output_dir, exist_ok=True)

        if not self.db_manager:
            click.echo("⚠️  Database manager not available for export", err=True)
            return

        # Create services
        us_service = USService(self.db_manager)
        generator = HarrisMatrixGenerator(self.db_manager, us_service)

        # Generate matrix
        graph = generator.generate_matrix(site_name)

        if not graph or graph.number_of_nodes() == 0:
            click.echo("⚠️  No nodes to export", err=True)
            return

        base_name = site_name.replace(' ', '_').replace('/', '_')

        # Export GraphML
        if export_graphml:
            graphml_path = os.path.join(output_dir, f"{base_name}.graphml")
            try:
                result_path = generator.export_to_graphml(
                    graph=graph,
                    output_path=graphml_path,
                    use_extended_labels=True,
                    site_name=site_name,
                    include_periods=True,
                    reverse_epochs=reverse_edges
                )
                if result_path:
                    click.echo(f"   ✓ GraphML: {graphml_path}")
                else:
                    click.echo(f"   ✗ GraphML export failed", err=True)
            except Exception as e:
                click.echo(f"   ✗ GraphML export failed: {str(e)}", err=True)

        # Export DOT
        if export_dot:
            dot_path = os.path.join(output_dir, f"{base_name}.dot")
            try:
                from pyarchinit_mini.graphml_converter.graphml_exporter import GraphMLExporter
                exporter = GraphMLExporter()
                exporter.export_to_dot(graph, dot_path, site_name=site_name)
                click.echo(f"   ✓ DOT: {dot_path}")
            except Exception as e:
                click.echo(f"   ✗ DOT export failed: {str(e)}", err=True)


@click.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--site', '-s', required=True, help='Archaeological site name')
@click.option('--export-graphml', '-g', is_flag=True, help='Export to GraphML format')
@click.option('--export-dot', '-d', is_flag=True, help='Export to DOT format')
@click.option('--output-dir', '-o', help='Output directory for exports (default: current directory)')
@click.option('--db', help='Database URL (default: from environment or pyarchinit_mini.db)')
def import_harris_matrix(file_path, site, export_graphml, export_dot, output_dir, db):
    """
    Import Harris Matrix from CSV or Excel file

    The file must contain two sections:

    \b
    1. NODES - Define stratigraphic units
       Required columns: us_number, unit_type
       Optional columns: description, area, period, phase, file_path

    \b
    2. RELATIONSHIPS - Define connections between units
       Required columns: from_us, to_us, relationship

    \b
    Examples:
        # Import from Excel
        pyarchinit-harris-import site1_matrix.xlsx --site "Site 1"

        # Import and export to GraphML
        pyarchinit-harris-import matrix.csv --site "My Site" --export-graphml

        # Import and export both formats
        pyarchinit-harris-import data.xlsx -s "Site 2" -g -d -o ./exports

    To generate a template file, use:
        pyarchinit-harris-template
    """
    click.echo("=" * 60)
    click.echo("PyArchInit-Mini - Harris Matrix Import Tool")
    click.echo("=" * 60)

    # Get database connection
    if db:
        db_url = db
    else:
        import os
        db_url = os.getenv("DATABASE_URL", "sqlite:///pyarchinit_mini.db")

    connection = DatabaseConnection.from_url(db_url)
    db_manager = DatabaseManager(connection)

    try:
        with db_manager.connection.get_session() as session:
            importer = HarrisMatrixImporter(session, db_manager)
            success = importer.import_matrix(
                file_path=file_path,
                site_name=site,
                export_graphml=export_graphml,
                export_dot=export_dot,
                output_dir=output_dir
            )

            if success:
                click.echo("\n" + "=" * 60)
                click.echo("✅ Import completed successfully!")
                click.echo("=" * 60)
                sys.exit(0)
            else:
                click.echo("\n" + "=" * 60)
                click.echo("❌ Import failed")
                click.echo("=" * 60)
                sys.exit(1)

    except Exception as e:
        click.echo(f"\n❌ Unexpected error: {str(e)}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    import_harris_matrix()