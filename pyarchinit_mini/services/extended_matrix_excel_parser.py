"""
Extended Matrix Excel Parser for PyArchInit-Mini
=================================================

Parser for structured Excel files with Extended Matrix format containing:
- Stratigraphic Units (US/USM)
- Definitions and descriptions
- Chronological phases
- Stratigraphic relationships (is_before, covers, cuts, etc.)

Excel Format Expected:
- ID: US identifier (can be multiple comma-separated)
- DEFINITION: Short definition
- LONG_DESCRIPTION: Detailed description
- PHASE: Archaeological phase/period
- is_before, covers, is_covered_by, cuts, is_cut_by, leans_on, equals, fills: Relationships
- NOTES: Additional notes

Author: PyArchInit Team
License: GPL v2
"""

import pandas as pd
from typing import Dict, List, Tuple, Optional, Set
from pathlib import Path
import re
import os
from datetime import datetime

from pyarchinit_mini.models.us import US
from pyarchinit_mini.models.site import Site
from pyarchinit_mini.database.connection import DatabaseConnection


def safe_int(value) -> Optional[int]:
    """
    Convert value to int or None if empty/invalid.
    Handles pandas NaN, empty strings, and None.
    """
    if pd.isna(value) or value == '' or value is None:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def safe_float(value) -> Optional[float]:
    """
    Convert value to float or None if empty/invalid.
    Handles pandas NaN, empty strings, and None.
    """
    if pd.isna(value) or value == '' or value is None:
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


class ExtendedMatrixExcelParser:
    """
    Parser for Extended Matrix Excel files.

    Reads structured Excel files and:
    1. Creates/updates US records in database
    2. Creates stratigraphic relationships
    3. Generates GraphML for Extended Matrix visualization
    """

    # Mapping from Excel columns to PyArchInit relationship types
    RELATIONSHIP_MAPPING = {
        'is_before': 'Anteriore a',
        'covers': 'Copre',
        'is_covered_by': 'Coperto da',
        'cuts': 'Taglia',
        'is_cut_by': 'Tagliato da',
        'leans_on': 'Si appoggia a',
        'equals': 'Uguale a',
        'fills': 'Riempie',
        # Also accept Italian variations (case-insensitive matching done in code)
        'anteriore a': 'Anteriore a',
        'copre': 'Copre',
        'coperto da': 'Coperto da',
        'taglia': 'Taglia',
        'tagliato da': 'Tagliato da',
        'si appoggia a': 'Si appoggia a',
        'uguale a': 'Uguale a',
        'riempie': 'Riempie'
    }

    def __init__(self, excel_path: str, site_name: str, db_connection: Optional[DatabaseConnection] = None):
        """
        Initialize parser.

        Args:
            excel_path: Path to Excel file
            site_name: Archaeological site name
            db_connection: Database connection (optional, will create default if not provided)
        """
        self.excel_path = Path(excel_path)
        self.site_name = site_name

        # Get or create database connection
        if db_connection is None:
            # Use default SQLite database
            db_path = os.path.expanduser('~/.pyarchinit_mini/data/pyarchinit_mini.db')
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            connection_string = f"sqlite:///{db_path}"
            self.db_connection = DatabaseConnection(connection_string)
        else:
            self.db_connection = db_connection

        self.df = None
        self.statistics = {
            'total_rows': 0,
            'us_created': 0,
            'us_updated': 0,
            'relationships_created': 0,
            'errors': []
        }

    def parse_us_id(self, us_id_str: str) -> List[str]:
        """
        Parse US ID string which may contain multiple IDs separated by comma.

        Args:
            us_id_str: US ID string (e.g., "US2210,US2199" or "USM2193")

        Returns:
            List of US IDs
        """
        if pd.isna(us_id_str) or not us_id_str:
            return []

        # Split by comma and clean
        ids = [id.strip() for id in str(us_id_str).split(',')]
        return [id for id in ids if id]

    def extract_us_number(self, us_id: str) -> str:
        """
        Extract US number from full ID.

        Args:
            us_id: Full US ID (e.g., "USM2193", "US2210")

        Returns:
            US number (e.g., "2193", "2210")
        """
        # Extract numbers from US identifier
        match = re.search(r'\d+', us_id)
        return match.group() if match else us_id

    def determine_unit_type(self, us_id: str) -> str:
        """
        Determine unit type from US ID.

        Args:
            us_id: US identifier

        Returns:
            Unit type (US, USM, etc.)
        """
        us_id_upper = us_id.upper()

        if 'USM' in us_id_upper:
            return 'USM'
        elif 'VSF' in us_id_upper:
            return 'VSF'
        elif 'SF' in us_id_upper:
            return 'SF'
        elif 'USD' in us_id_upper:
            return 'USD'
        elif 'CON' in us_id_upper:
            return 'CON'
        elif 'DOC' in us_id_upper:
            return 'DOC'
        else:
            return 'US'

    def parse_phase(self, phase_str: str) -> Tuple[str, str]:
        """
        Parse phase string into period and fase.

        Args:
            phase_str: Phase string (e.g., "Periodo 1, Fase VII (età traianea)")

        Returns:
            Tuple of (period, fase)
        """
        if pd.isna(phase_str) or not phase_str:
            return (None, None)

        phase_str = str(phase_str)
        period = None
        fase = None

        # Try to extract "Periodo X"
        period_match = re.search(r'Periodo\s+(\d+|[IVXLCDM]+)', phase_str, re.IGNORECASE)
        if period_match:
            period = period_match.group(1)

        # Try to extract "Fase Y"
        fase_match = re.search(r'Fase\s+([IVXLCDM]+|\d+)', phase_str, re.IGNORECASE)
        if fase_match:
            fase = fase_match.group(1)

        return (period, fase)

    def load_excel(self) -> pd.DataFrame:
        """
        Load Excel file.

        Returns:
            DataFrame with Excel data
        """
        try:
            self.df = pd.read_excel(self.excel_path)
            self.statistics['total_rows'] = len(self.df)
            print(f"✓ Loaded {len(self.df)} rows from {self.excel_path.name}")
            return self.df
        except Exception as e:
            error_msg = f"Error loading Excel: {e}"
            self.statistics['errors'].append(error_msg)
            raise RuntimeError(error_msg)

    def init_database(self):
        """Initialize database tables if they don't exist."""
        from pyarchinit_mini.models.base import BaseModel

        # Create all tables
        BaseModel.metadata.create_all(self.db_connection.engine)
        print(f"✓ Database tables initialized")

    def ensure_site_exists(self):
        """Ensure the site exists in database, create if not."""
        with self.db_connection.get_session() as session:
            site = session.query(Site).filter_by(sito=self.site_name).first()

            if not site:
                site = Site(
                    sito=self.site_name,
                    nazione='Italia',
                    descrizione=f'Site imported from Extended Matrix Excel: {self.excel_path.name}'
                )
                session.add(site)
                # Commit is done automatically by context manager
                print(f"✓ Created site: {self.site_name}")
            else:
                print(f"✓ Using existing site: {self.site_name}")

    def parse_relationship_targets(self, relationship_str: str) -> List[str]:
        """
        Parse relationship target US IDs from string.

        Args:
            relationship_str: Comma-separated US IDs

        Returns:
            List of US numbers
        """
        if pd.isna(relationship_str) or not relationship_str:
            return []

        # Split by comma and extract numbers
        targets = [self.extract_us_number(id.strip())
                  for id in str(relationship_str).split(',')]
        return [t for t in targets if t]

    def import_us_records(self):
        """Import US records from Excel to database."""
        print(f"\n📦 Importing US records...")

        for idx, row in self.df.iterrows():
            try:
                with self.db_connection.get_session() as session:
                    # Parse US IDs (can be multiple)
                    us_ids = self.parse_us_id(row['ID'])

                    if not us_ids:
                        continue

                    # Process each US ID
                    for us_id in us_ids:
                        us_number = self.extract_us_number(us_id)
                        unit_type = self.determine_unit_type(us_id)

                        # Check if US already exists
                        existing_us = session.query(US).filter_by(
                            sito=self.site_name,
                            us=us_number
                        ).first()

                        # Parse phase
                        period, fase = self.parse_phase(row.get('PHASE'))

                        # Build datazione text for us_table
                        datazione_text = ""
                        if period and fase:
                            datazione_text = f"Periodo {period}, Fase {fase}"
                        elif period:
                            datazione_text = f"Periodo {period}"
                        elif fase:
                            datazione_text = f"Fase {fase}"

                        if existing_us:
                            # Update existing US
                            existing_us.unita_tipo = unit_type
                            existing_us.d_stratigrafica = str(row.get('DEFINITION', ''))[:250]
                            existing_us.d_interpretativa = str(row.get('LONG_DESCRIPTION', ''))
                            existing_us.periodo_iniziale = period
                            existing_us.fase_iniziale = fase
                            existing_us.periodo_finale = period  # Same as iniziale
                            existing_us.fase_finale = fase  # Same as iniziale
                            existing_us.datazione = datazione_text
                            existing_us.descrizione = str(row.get('NOTES', ''))
                            # Update INTEGER/FLOAT fields if provided
                            if 'anno_scavo' in row:
                                existing_us.anno_scavo = safe_int(row.get('anno_scavo'))
                            if 'order_layer' in row:
                                existing_us.order_layer = safe_int(row.get('order_layer'))
                            if 'quota_relativa' in row:
                                existing_us.quota_relativa = safe_float(row.get('quota_relativa'))
                            if 'quota_abs' in row:
                                existing_us.quota_abs = safe_float(row.get('quota_abs'))
                            if 'lunghezza_max' in row:
                                existing_us.lunghezza_max = safe_float(row.get('lunghezza_max'))
                            if 'altezza_max' in row:
                                existing_us.altezza_max = safe_float(row.get('altezza_max'))
                            if 'altezza_min' in row:
                                existing_us.altezza_min = safe_float(row.get('altezza_min'))
                            if 'profondita_max' in row:
                                existing_us.profondita_max = safe_float(row.get('profondita_max'))
                            if 'profondita_min' in row:
                                existing_us.profondita_min = safe_float(row.get('profondita_min'))
                            if 'larghezza_media' in row:
                                existing_us.larghezza_media = safe_float(row.get('larghezza_media'))

                            self.statistics['us_updated'] += 1
                            print(f"  ↻ Updated {unit_type} {us_number}")
                        else:
                            # Create new US (id_us will be auto-generated)
                            new_us = US(
                                sito=self.site_name,
                                us=us_number,
                                unita_tipo=unit_type,
                                d_stratigrafica=str(row.get('DEFINITION', ''))[:250],
                                d_interpretativa=str(row.get('LONG_DESCRIPTION', '')),
                                periodo_iniziale=period,
                                fase_iniziale=fase,
                                periodo_finale=period,  # Same as iniziale
                                fase_finale=fase,  # Same as iniziale
                                datazione=datazione_text,
                                descrizione=str(row.get('NOTES', '')),
                                # INTEGER fields - explicitly set to None if not provided
                                anno_scavo=safe_int(row.get('anno_scavo')),
                                order_layer=safe_int(row.get('order_layer')),
                                # FLOAT fields - explicitly set to None if not provided
                                quota_relativa=safe_float(row.get('quota_relativa')),
                                quota_abs=safe_float(row.get('quota_abs')),
                                lunghezza_max=safe_float(row.get('lunghezza_max')),
                                altezza_max=safe_float(row.get('altezza_max')),
                                altezza_min=safe_float(row.get('altezza_min')),
                                profondita_max=safe_float(row.get('profondita_max')),
                                profondita_min=safe_float(row.get('profondita_min')),
                                larghezza_media=safe_float(row.get('larghezza_media')),
                                data_schedatura=None  # Let SQLite handle default or set to None
                            )
                            session.add(new_us)
                            self.statistics['us_created'] += 1
                            print(f"  + Created {unit_type} {us_number}")

                        # Create or update periodizzazione record if period/fase specified
                        if period or fase:
                            from pyarchinit_mini.models.harris_matrix import Periodizzazione

                            # Build datazione_estesa text
                            if period and fase:
                                datazione_estesa = f"Periodo {period}, Fase {fase}"
                            elif period:
                                datazione_estesa = f"Periodo {period}"
                            else:
                                datazione_estesa = f"Fase {fase}"

                            # Check if periodizzazione exists
                            periodizzazione = session.query(Periodizzazione).filter_by(
                                sito=self.site_name,
                                us=us_number
                            ).first()

                            if periodizzazione:
                                # Update existing
                                periodizzazione.periodo_iniziale = period
                                periodizzazione.fase_iniziale = fase
                                periodizzazione.datazione_estesa = datazione_estesa
                            else:
                                # Create new
                                periodizzazione = Periodizzazione(
                                    sito=self.site_name,
                                    us=us_number,
                                    periodo_iniziale=period,
                                    fase_iniziale=fase,
                                    datazione_estesa=datazione_estesa
                                )
                                session.add(periodizzazione)

                    # Commit is done automatically by context manager

            except Exception as e:
                error_msg = f"Error processing row {idx}: {e}"
                self.statistics['errors'].append(error_msg)
                print(f"  ✗ {error_msg}")
                continue

    def import_relationships(self):
        """Import stratigraphic relationships from Excel."""
        print(f"\n🔗 Importing relationships...")

        from pyarchinit_mini.models.harris_matrix import USRelationships

        for idx, row in self.df.iterrows():
            try:
                with self.db_connection.get_session() as session:
                    # Parse source US IDs
                    source_us_ids = self.parse_us_id(row['ID'])

                    if not source_us_ids:
                        continue

                    # Process each source US
                    for source_us_id in source_us_ids:
                        source_us_number = self.extract_us_number(source_us_id)

                        # Process each relationship type
                        for excel_col, pyarch_rel in self.RELATIONSHIP_MAPPING.items():
                            target_us_numbers = self.parse_relationship_targets(row.get(excel_col))

                            for target_us_number in target_us_numbers:
                                # Check if relationship already exists
                                existing_rel = session.query(USRelationships).filter_by(
                                    sito=self.site_name,
                                    us_from=source_us_number,
                                    us_to=target_us_number,
                                    relationship_type=pyarch_rel
                                ).first()

                                if not existing_rel:
                                    new_rel = USRelationships(
                                        sito=self.site_name,
                                        us_from=source_us_number,
                                        us_to=target_us_number,
                                        relationship_type=pyarch_rel
                                    )
                                    session.add(new_rel)
                                    self.statistics['relationships_created'] += 1
                                    print(f"  + Created: {source_us_number} {pyarch_rel} {target_us_number}")

                    # Commit is done automatically by context manager

            except Exception as e:
                error_msg = f"Error processing relationships for row {idx}: {e}"
                self.statistics['errors'].append(error_msg)
                print(f"  ✗ {error_msg}")
                continue

    def update_rapporti_field(self):
        """Update rapporti field in us_table with relationship descriptions."""
        print(f"\n📝 Updating rapporti field in US records...")

        from pyarchinit_mini.models.harris_matrix import USRelationships
        from collections import defaultdict

        try:
            with self.db_connection.get_session() as session:
                # Get all relationships for this site
                relationships = session.query(USRelationships).filter_by(
                    sito=self.site_name
                ).all()

                # Group relationships by US
                us_rels_from = defaultdict(lambda: defaultdict(list))  # {us_number: {rel_type: [target_us]}}

                for rel in relationships:
                    us_rels_from[rel.us_from][rel.relationship_type].append(rel.us_to)

                # Update each US with its rapporti text
                for us_number in us_rels_from.keys():
                    rapporti_parts = []

                    # Add relationships in correct format: "Copre 1, Copre 2, Taglia 3"
                    # Each relationship type is repeated for each target US
                    for rel_type, targets in sorted(us_rels_from[us_number].items()):
                        # For each target, add "RelType target_number"
                        for target in sorted(targets):
                            rapporti_parts.append(f"{rel_type} {target}")

                    # Build rapporti string with comma separator
                    rapporti_text = ", ".join(rapporti_parts) if rapporti_parts else ""

                    if rapporti_text:
                        # Update US record
                        us_record = session.query(US).filter_by(
                            sito=self.site_name,
                            us=us_number
                        ).first()

                        if us_record:
                            us_record.rapporti = rapporti_text
                            print(f"  ↻ Updated rapporti for US {us_number}")

                # Commit is done automatically
                print(f"✓ Rapporti field updated for all US")

        except Exception as e:
            error_msg = f"Error updating rapporti field: {e}"
            self.statistics['errors'].append(error_msg)
            print(f"✗ {error_msg}")

    def generate_graphml(self, output_path: Optional[str] = None, reverse_edges: bool = False) -> str:
        """
        Generate GraphML file for Extended Matrix visualization.

        Args:
            output_path: Optional output path for GraphML file
            reverse_edges: Reverse edge direction in GraphML (default: False)

        Returns:
            Path to generated GraphML file
        """
        print(f"\n🎨 Generating GraphML for Extended Matrix...")

        from pyarchinit_mini.database.manager import DatabaseManager
        from pyarchinit_mini.services.us_service import USService
        from pyarchinit_mini.harris_matrix import HarrisMatrixGenerator

        try:
            # Create database manager
            db_manager = DatabaseManager(self.db_connection)

            # Create US service
            us_service = USService(db_manager)

            # Create Harris Matrix generator
            generator = HarrisMatrixGenerator(db_manager, us_service)

            # Generate matrix graph
            graph = generator.generate_matrix(self.site_name)

            if not graph or graph.number_of_nodes() == 0:
                error_msg = "No nodes in graph to export"
                self.statistics['errors'].append(error_msg)
                print(f"✗ {error_msg}")
                return None

            # Set output path
            if not output_path:
                output_path = f"{self.site_name.replace(' ', '_')}_extended_matrix.graphml"

            # Export to GraphML using generator's export method
            result_path = generator.export_to_graphml(
                graph=graph,
                output_path=output_path,
                use_extended_labels=True,
                site_name=self.site_name,
                include_periods=True,
                reverse_epochs=reverse_edges
            )

            if result_path:
                print(f"✓ GraphML exported to: {result_path}")
                return result_path
            else:
                error_msg = "GraphML export failed"
                self.statistics['errors'].append(error_msg)
                print(f"✗ {error_msg}")
                return None

        except Exception as e:
            error_msg = f"Error generating GraphML: {e}"
            self.statistics['errors'].append(error_msg)
            print(f"✗ {error_msg}")
            raise

    def run(self, generate_graphml: bool = True, output_dir: Optional[str] = None, reverse_edges: bool = False) -> Dict:
        """
        Run complete import process.

        Args:
            generate_graphml: Whether to generate GraphML file (default: True)
            output_dir: Output directory for GraphML file (optional)
            reverse_edges: Reverse edge direction in GraphML (default: False)

        Returns:
            Dictionary with import statistics
        """
        print(f"\n{'='*60}")
        print(f"Extended Matrix Excel Parser")
        print(f"{'='*60}")
        print(f"File: {self.excel_path.name}")
        print(f"Site: {self.site_name}")
        print(f"{'='*60}\n")

        try:
            # Step 1: Initialize database
            self.init_database()

            # Step 2: Load Excel
            self.load_excel()

            # Step 3: Ensure site exists
            self.ensure_site_exists()

            # Step 3: Import US records
            self.import_us_records()

            # Step 4: Import relationships
            self.import_relationships()

            # Step 5: Update rapporti field in US records
            self.update_rapporti_field()

            # Step 6: Generate GraphML (optional)
            graphml_path = None
            if generate_graphml:
                # Build output path
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)
                    output_path = os.path.join(output_dir, f"{self.site_name.replace(' ', '_')}_extended_matrix.graphml")
                else:
                    output_path = None

                graphml_path = self.generate_graphml(output_path=output_path, reverse_edges=reverse_edges)
                self.statistics['graphml_path'] = graphml_path

            # Print summary
            print(f"\n{'='*60}")
            print(f"Import Summary")
            print(f"{'='*60}")
            print(f"Total rows processed: {self.statistics['total_rows']}")
            print(f"US created: {self.statistics['us_created']}")
            print(f"US updated: {self.statistics['us_updated']}")
            print(f"Relationships created: {self.statistics['relationships_created']}")
            if graphml_path:
                print(f"GraphML generated: {graphml_path}")

            if self.statistics['errors']:
                print(f"\nErrors encountered: {len(self.statistics['errors'])}")
                for error in self.statistics['errors'][:5]:  # Show first 5 errors
                    print(f"  - {error}")
            else:
                print(f"\n✓ Import completed successfully!")

            print(f"{'='*60}\n")

            return self.statistics

        except Exception as e:
            print(f"\n✗ Import failed: {e}")
            raise


def import_extended_matrix_excel(
    excel_path: str,
    site_name: str,
    db_url: str = None,
    generate_graphml: bool = True,
    db_connection: Optional[DatabaseConnection] = None,
    output_dir: Optional[str] = None,
    reverse_edges: bool = False
) -> Dict:
    """
    Convenience function to import Extended Matrix Excel file.

    Args:
        excel_path: Path to Excel file
        site_name: Archaeological site name
        db_url: Database URL string (optional, for backwards compatibility)
        generate_graphml: Whether to generate GraphML (default: True)
        db_connection: Database connection (optional)
        output_dir: Output directory for GraphML file (optional)
        reverse_edges: Reverse edge direction in GraphML (default: False)

    Returns:
        Dictionary with import statistics

    Example:
        >>> stats = import_extended_matrix_excel(
        ...     excel_path='data/MetroC_AmbaAradam.xlsx',
        ...     site_name='Metro C - Amba Aradam',
        ...     generate_graphml=True,
        ...     reverse_edges=False
        ... )
        >>> print(f"Imported {stats['us_created']} US records")
    """
    # Handle db_url for backwards compatibility
    if db_url and not db_connection:
        db_connection = DatabaseConnection.from_url(db_url)

    parser = ExtendedMatrixExcelParser(
        excel_path=excel_path,
        site_name=site_name,
        db_connection=db_connection
    )
    return parser.run(
        generate_graphml=generate_graphml,
        output_dir=output_dir,
        reverse_edges=reverse_edges
    )
