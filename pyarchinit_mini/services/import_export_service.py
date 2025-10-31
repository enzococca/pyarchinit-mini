"""
PyArchInit Import/Export Service

Handles data import and export between PyArchInit (full version)
and PyArchInit-Mini databases.

Supports:
- Site data
- US (Stratigraphic Units) data with relationship mapping
- Inventario Materiali data
- Periodizzazione data
- Thesaurus data

Database support: SQLite and PostgreSQL (both source and target)
"""

import ast
import json
import shutil
import os
from datetime import datetime, date
from typing import Dict, List, Optional, Tuple, Any
import logging
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImportExportService:
    """Service for importing and exporting data between PyArchInit and PyArchInit-Mini"""

    def __init__(self, mini_db_connection: str, source_db_connection: Optional[str] = None):
        """
        Initialize ImportExport service

        Args:
            mini_db_connection: Connection string for PyArchInit-Mini database
            source_db_connection: Connection string for source PyArchInit database (for import)
        """
        self.mini_engine = create_engine(mini_db_connection)
        self.mini_session_maker = sessionmaker(bind=self.mini_engine)

        self.source_engine = None
        self.source_session_maker = None
        self._backup_created = False  # Track if backup was already created for this session
        self._backup_path = None  # Store backup path

        if source_db_connection:
            self.source_engine = create_engine(source_db_connection)
            self.source_session_maker = sessionmaker(bind=self.source_engine)

    def set_source_database(self, source_db_connection: str):
        """Set or change the source database connection"""
        self.source_engine = create_engine(source_db_connection)
        self.source_session_maker = sessionmaker(bind=self.source_engine)

    def _backup_source_database(self) -> Optional[str]:
        """
        Create a backup of the source database before migration

        For SQLite: Copies the database file with timestamp
        For PostgreSQL: Uses pg_dump to create SQL backup

        Returns:
            Path to backup file, or None if backup failed
        """
        if not self.source_engine:
            logger.warning("No source database configured, skipping backup")
            return None

        connection_string = str(self.source_engine.url)

        # SQLite backup
        if connection_string.startswith('sqlite:///'):
            # Extract file path from connection string
            # Format: sqlite:///path/to/file.db or sqlite:////absolute/path/to/file.db
            db_path = connection_string.replace('sqlite:///', '')

            # Handle absolute paths (start with /)
            if not db_path.startswith('/'):
                db_path = '/' + db_path

            if not os.path.exists(db_path):
                logger.error(f"Source database file not found: {db_path}")
                return None

            # Create backup with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{db_path}.backup_{timestamp}"

            try:
                shutil.copy2(db_path, backup_path)
                file_size = os.path.getsize(backup_path) / (1024 * 1024)  # MB
                logger.info(f"✓ Database backup created: {backup_path} ({file_size:.2f} MB)")
                return backup_path
            except Exception as e:
                logger.error(f"Failed to create backup: {e}")
                return None

        # PostgreSQL backup
        elif connection_string.startswith('postgresql'):
            try:
                import subprocess

                # Extract connection details
                url = self.source_engine.url
                host = url.host or 'localhost'
                port = url.port or 5432
                database = url.database
                user = url.username
                password = url.password

                # Create backup file path
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = f"{database}_backup_{timestamp}.sql"

                # Set password environment variable
                env = os.environ.copy()
                if password:
                    env['PGPASSWORD'] = password

                # Run pg_dump
                cmd = [
                    'pg_dump',
                    '-h', host,
                    '-p', str(port),
                    '-U', user,
                    '-F', 'p',  # Plain SQL format
                    '-f', backup_path,
                    database
                ]

                result = subprocess.run(cmd, env=env, capture_output=True, text=True)

                if result.returncode == 0:
                    file_size = os.path.getsize(backup_path) / (1024 * 1024)  # MB
                    logger.info(f"✓ Database backup created: {backup_path} ({file_size:.2f} MB)")
                    return backup_path
                else:
                    logger.error(f"pg_dump failed: {result.stderr}")
                    return None

            except Exception as e:
                logger.error(f"Failed to create PostgreSQL backup: {e}")
                return None

        else:
            logger.warning(f"Unsupported database type for backup: {connection_string}")
            return None

    def _check_i18n_columns_exist(self, table_name: str) -> Dict[str, bool]:
        """
        Check which i18n columns exist in the source database table

        Args:
            table_name: Name of the table to check

        Returns:
            Dictionary with column_name: exists mapping
        """
        if not self.source_engine:
            raise ValueError("Source database not configured")

        inspector = inspect(self.source_engine)
        columns = [col['name'] for col in inspector.get_columns(table_name)]

        # Define i18n columns for each table
        i18n_columns = {
            'site_table': [
                'definizione_sito_en', 'descrizione_en'
            ],
            'us_table': [
                'd_stratigrafica_en', 'd_interpretativa_en', 'descrizione_en',
                'interpretazione_en', 'formazione_en', 'stato_di_conservazione_en',
                'colore_en', 'consistenza_en', 'struttura_en', 'inclusi_en',
                'campioni_en', 'documentazione_en', 'osservazioni_en'
            ],
            'inventario_materiali_table': [
                'tipo_reperto_en', 'definizione_reperto_en', 'descrizione_en',
                'tecnologia_en', 'forma_en', 'stato_conservazione_en',
                'osservazioni_en'
            ]
        }

        result = {}
        for col in i18n_columns.get(table_name, []):
            result[col] = col in columns

        return result

    def _add_missing_i18n_columns(self, table_name: str) -> Dict[str, Any]:
        """
        Add missing i18n (_en) columns to source database table

        Args:
            table_name: Name of the table to migrate

        Returns:
            Dictionary with migration statistics
        """
        if not self.source_engine:
            raise ValueError("Source database not configured")

        stats = {'columns_added': 0, 'columns_skipped': 0, 'errors': []}

        # Check which columns are missing
        missing_columns = {k: v for k, v in self._check_i18n_columns_exist(table_name).items() if not v}

        if not missing_columns:
            logger.info(f"Table {table_name} already has all i18n columns")
            return stats

        logger.info(f"Adding {len(missing_columns)} missing i18n columns to {table_name}: {list(missing_columns.keys())}")

        with self.source_engine.begin() as conn:
            for col_name in missing_columns.keys():
                try:
                    # Add TEXT column with NULL default
                    sql = text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} TEXT")
                    conn.execute(sql)
                    stats['columns_added'] += 1
                    logger.info(f"Added column {col_name} to {table_name}")
                except Exception as e:
                    error_msg = f"Failed to add column {col_name} to {table_name}: {str(e)}"
                    logger.error(error_msg)
                    stats['errors'].append(error_msg)
                    stats['columns_skipped'] += 1

        return stats

    def migrate_source_database(self, tables: Optional[List[str]] = None,
                                auto_backup: bool = True) -> Dict[str, Any]:
        """
        Migrate source PyArchInit database to add i18n columns

        This is called automatically before import to ensure compatibility.

        Args:
            tables: List of tables to migrate (None = all tables)
            auto_backup: If True, create automatic backup before migration

        Returns:
            Dictionary with migration statistics including backup_path
        """
        if not self.source_engine:
            raise ValueError("Source database not configured")

        all_tables = ['site_table', 'us_table', 'inventario_materiali_table']
        tables_to_migrate = tables if tables else all_tables

        total_stats = {
            'tables_migrated': 0,
            'columns_added': 0,
            'errors': [],
            'backup_path': None
        }

        # Create backup before migration if requested (only once per session)
        if auto_backup and not self._backup_created:
            logger.info("Creating database backup before migration...")
            backup_path = self._backup_source_database()
            self._backup_path = backup_path
            self._backup_created = True

            if backup_path:
                logger.info(f"✓ Backup created successfully: {backup_path}")
            else:
                logger.warning("⚠ Backup failed, but continuing with migration...")

        total_stats['backup_path'] = self._backup_path

        for table in tables_to_migrate:
            try:
                logger.info(f"Migrating table: {table}")
                stats = self._add_missing_i18n_columns(table)
                total_stats['columns_added'] += stats['columns_added']
                total_stats['errors'].extend(stats['errors'])
                if stats['columns_added'] > 0:
                    total_stats['tables_migrated'] += 1
            except Exception as e:
                error_msg = f"Failed to migrate table {table}: {str(e)}"
                logger.error(error_msg)
                total_stats['errors'].append(error_msg)

        logger.info(f"Migration complete: {total_stats['tables_migrated']} tables migrated, {total_stats['columns_added']} columns added")
        return total_stats

    # ============================================================================
    # SITE TABLE IMPORT/EXPORT
    # ============================================================================

    def import_sites(self, sito_filter: Optional[List[str]] = None,
                    auto_migrate: bool = True,
                    auto_backup: bool = True) -> Dict[str, Any]:
        """
        Import sites from PyArchInit to PyArchInit-Mini

        Args:
            sito_filter: List of site names to import (None = import all)
            auto_migrate: If True, automatically add missing i18n columns to source database
            auto_backup: If True, create backup before database migration

        Returns:
            Dictionary with import statistics including backup_path
        """
        if not self.source_engine:
            raise ValueError("Source database not configured")

        # Auto-migrate source database to add i18n columns if needed
        if auto_migrate:
            logger.info("Checking source database for missing i18n columns...")
            migration_stats = self.migrate_source_database(tables=['site_table'], auto_backup=auto_backup)
            if migration_stats['columns_added'] > 0:
                logger.info(f"Added {migration_stats['columns_added']} i18n columns to source database")
            if migration_stats.get('backup_path'):
                logger.info(f"Database backup: {migration_stats['backup_path']}")

        stats = {'imported': 0, 'updated': 0, 'skipped': 0, 'errors': []}

        source_session = self.source_session_maker()
        mini_session = self.mini_session_maker()

        try:
            # Query sites from PyArchInit
            query = "SELECT * FROM site_table"
            if sito_filter:
                placeholders = ','.join([f"'{s}'" for s in sito_filter])
                query += f" WHERE sito IN ({placeholders})"

            result = source_session.execute(text(query))
            source_sites = result.fetchall()

            for site_row in source_sites:
                try:
                    site_data = dict(site_row._mapping)

                    # Check if site already exists
                    existing = mini_session.execute(
                        text("SELECT id_sito FROM site_table WHERE sito = :sito"),
                        {'sito': site_data['sito']}
                    ).fetchone()

                    if existing:
                        # Update existing site
                        update_query = text("""
                            UPDATE site_table
                            SET nazione = :nazione,
                                regione = :regione,
                                comune = :comune,
                                provincia = :provincia,
                                definizione_sito = :definizione_sito,
                                descrizione = :descrizione,
                                sito_path = :sito_path,
                                find_check = :find_check,
                                updated_at = :updated_at
                            WHERE sito = :sito
                        """)

                        mini_session.execute(update_query, {
                            'sito': site_data['sito'],
                            'nazione': site_data.get('nazione'),
                            'regione': site_data.get('regione'),
                            'comune': site_data.get('comune'),
                            'provincia': site_data.get('provincia'),
                            'definizione_sito': site_data.get('definizione_sito'),
                            'descrizione': site_data.get('descrizione'),
                            'sito_path': site_data.get('sito_path'),
                            'find_check': site_data.get('find_check', 0),
                            'updated_at': datetime.now()
                        })
                        stats['updated'] += 1
                    else:
                        # Insert new site
                        insert_query = text("""
                            INSERT INTO site_table
                            (sito, nazione, regione, comune, provincia, definizione_sito,
                             descrizione, sito_path, find_check, created_at, updated_at)
                            VALUES
                            (:sito, :nazione, :regione, :comune, :provincia, :definizione_sito,
                             :descrizione, :sito_path, :find_check, :created_at, :updated_at)
                        """)

                        mini_session.execute(insert_query, {
                            'sito': site_data['sito'],
                            'nazione': site_data.get('nazione'),
                            'regione': site_data.get('regione'),
                            'comune': site_data.get('comune'),
                            'provincia': site_data.get('provincia'),
                            'definizione_sito': site_data.get('definizione_sito'),
                            'descrizione': site_data.get('descrizione'),
                            'sito_path': site_data.get('sito_path'),
                            'find_check': site_data.get('find_check', 0),
                            'created_at': datetime.now(),
                            'updated_at': datetime.now()
                        })
                        stats['imported'] += 1

                    mini_session.commit()

                except Exception as e:
                    mini_session.rollback()
                    error_msg = f"Error importing site {site_data.get('sito', 'unknown')}: {str(e)}"
                    logger.error(error_msg)
                    stats['errors'].append(error_msg)
                    stats['skipped'] += 1

            return stats

        except Exception as e:
            logger.error(f"Import sites failed: {str(e)}")
            raise
        finally:
            source_session.close()
            mini_session.close()

    def export_sites(self, target_db_connection: str, sito_filter: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Export sites from PyArchInit-Mini to PyArchInit

        Args:
            target_db_connection: Connection string for target PyArchInit database
            sito_filter: List of site names to export (None = export all)

        Returns:
            Dictionary with export statistics
        """
        stats = {'exported': 0, 'updated': 0, 'skipped': 0, 'errors': []}

        target_engine = create_engine(target_db_connection)
        target_session = sessionmaker(bind=target_engine)()
        mini_session = self.mini_session_maker()

        try:
            # Query sites from PyArchInit-Mini
            query = "SELECT * FROM site_table"
            if sito_filter:
                placeholders = ','.join([f"'{s}'" for s in sito_filter])
                query += f" WHERE sito IN ({placeholders})"

            result = mini_session.execute(text(query))
            mini_sites = result.fetchall()

            for site_row in mini_sites:
                try:
                    site_data = dict(site_row._mapping)

                    # Check if site exists in target
                    existing = target_session.execute(
                        text("SELECT id_sito FROM site_table WHERE sito = :sito"),
                        {'sito': site_data['sito']}
                    ).fetchone()

                    if existing:
                        # Update existing
                        update_query = text("""
                            UPDATE site_table
                            SET nazione = :nazione,
                                regione = :regione,
                                comune = :comune,
                                provincia = :provincia,
                                definizione_sito = :definizione_sito,
                                descrizione = :descrizione,
                                sito_path = :sito_path,
                                find_check = :find_check
                            WHERE sito = :sito
                        """)

                        target_session.execute(update_query, {
                            'sito': site_data['sito'],
                            'nazione': site_data.get('nazione'),
                            'regione': site_data.get('regione'),
                            'comune': site_data.get('comune'),
                            'provincia': site_data.get('provincia'),
                            'definizione_sito': site_data.get('definizione_sito'),
                            'descrizione': site_data.get('descrizione'),
                            'sito_path': site_data.get('sito_path'),
                            'find_check': site_data.get('find_check', 0)
                        })
                        stats['updated'] += 1
                    else:
                        # Insert new
                        insert_query = text("""
                            INSERT INTO site_table
                            (sito, nazione, regione, comune, provincia, definizione_sito,
                             descrizione, sito_path, find_check)
                            VALUES
                            (:sito, :nazione, :regione, :comune, :provincia, :definizione_sito,
                             :descrizione, :sito_path, :find_check)
                        """)

                        target_session.execute(insert_query, {
                            'sito': site_data['sito'],
                            'nazione': site_data.get('nazione'),
                            'regione': site_data.get('regione'),
                            'comune': site_data.get('comune'),
                            'provincia': site_data.get('provincia'),
                            'definizione_sito': site_data.get('definizione_sito'),
                            'descrizione': site_data.get('descrizione'),
                            'sito_path': site_data.get('sito_path'),
                            'find_check': site_data.get('find_check', 0)
                        })
                        stats['exported'] += 1

                    target_session.commit()

                except Exception as e:
                    target_session.rollback()
                    error_msg = f"Error exporting site {site_data.get('sito', 'unknown')}: {str(e)}"
                    logger.error(error_msg)
                    stats['errors'].append(error_msg)
                    stats['skipped'] += 1

            return stats

        except Exception as e:
            logger.error(f"Export sites failed: {str(e)}")
            raise
        finally:
            target_session.close()
            mini_session.close()

    # ============================================================================
    # US TABLE IMPORT/EXPORT WITH RELATIONSHIP MAPPING
    # ============================================================================

    def _parse_pyarchinit_rapporti(self, rapporti_str: str) -> List[Tuple[str, str]]:
        """
        Parse PyArchInit rapporti field (list of lists format)

        Args:
            rapporti_str: String like "[['Copre', '2'], ['Copre', '8']]"

        Returns:
            List of tuples: [(relationship_type, us_number), ...]
        """
        if not rapporti_str or rapporti_str == '[]':
            return []

        try:
            # Parse the string as Python literal
            rapporti_list = ast.literal_eval(rapporti_str)

            # Extract only relationship type and US number (ignore area and site)
            relationships = []
            for item in rapporti_list:
                if isinstance(item, list) and len(item) >= 2:
                    rel_type = item[0]  # e.g., 'Copre', 'Coperto da'
                    us_num = str(item[1])  # US number
                    relationships.append((rel_type, us_num))

            return relationships

        except (ValueError, SyntaxError) as e:
            logger.warning(f"Failed to parse rapporti: {rapporti_str} - {str(e)}")
            return []

    def _convert_relationships_to_pyarchinit_format(self, sito: str, us: str,
                                                     mini_session: Session) -> str:
        """
        Convert PyArchInit-Mini us_relationships_table to PyArchInit rapporti format

        Args:
            sito: Site name
            us: US number
            mini_session: Session for PyArchInit-Mini database

        Returns:
            String in PyArchInit format: "[['Copre', '2'], ['Coperto da', '3']]"
        """
        try:
            # Get relationships from PyArchInit-Mini
            query = text("""
                SELECT relationship_type, us_to
                FROM us_relationships_table
                WHERE sito = :sito AND us_from = :us
            """)

            result = mini_session.execute(query, {'sito': sito, 'us': int(us)})
            relationships = result.fetchall()

            if not relationships:
                return '[]'

            # Convert to PyArchInit format (list of lists)
            rapporti_list = [[rel.relationship_type, str(rel.us_to)] for rel in relationships]

            return str(rapporti_list)

        except Exception as e:
            logger.error(f"Error converting relationships: {str(e)}")
            return '[]'

    def import_us(self, sito_filter: Optional[List[str]] = None,
                  import_relationships: bool = True,
                  auto_migrate: bool = True,
                  auto_backup: bool = True) -> Dict[str, Any]:
        """
        Import US (Stratigraphic Units) from PyArchInit to PyArchInit-Mini

        Args:
            sito_filter: List of site names to import (None = import all)
            import_relationships: If True, parse rapporti field and create relationships
            auto_migrate: If True, automatically add missing i18n columns to source database
            auto_backup: If True, create backup before database migration

        Returns:
            Dictionary with import statistics including backup_path
        """
        if not self.source_engine:
            raise ValueError("Source database not configured")

        # Auto-migrate source database to add i18n columns if needed
        if auto_migrate:
            logger.info("Checking source database for missing i18n columns...")
            migration_stats = self.migrate_source_database(tables=['us_table'], auto_backup=auto_backup)
            if migration_stats['columns_added'] > 0:
                logger.info(f"Added {migration_stats['columns_added']} i18n columns to source database")
            if migration_stats.get('backup_path'):
                logger.info(f"Database backup: {migration_stats['backup_path']}")

        stats = {
            'imported': 0,
            'updated': 0,
            'skipped': 0,
            'relationships_created': 0,
            'errors': []
        }

        source_session = self.source_session_maker()
        mini_session = self.mini_session_maker()

        try:
            # Query US from PyArchInit
            query = "SELECT * FROM us_table"
            if sito_filter:
                placeholders = ','.join([f"'{s}'" for s in sito_filter])
                query += f" WHERE sito IN ({placeholders})"

            result = source_session.execute(text(query))
            source_us_list = result.fetchall()

            for us_row in source_us_list:
                try:
                    us_data = dict(us_row._mapping)

                    # Check if US already exists using raw SQL (avoids ORM metadata issues)
                    existing = mini_session.execute(
                        text("SELECT id_us FROM us_table WHERE sito = :sito AND us = :us LIMIT 1"),
                        {'sito': us_data['sito'], 'us': us_data['us']}
                    ).fetchone()

                    # Map fields from PyArchInit to PyArchInit-Mini
                    mapped_data = self._map_us_fields_import(us_data)

                    if existing:
                        # Update existing US
                        self._update_us_mini(mini_session, mapped_data)
                        stats['updated'] += 1
                    else:
                        # Insert new US
                        self._insert_us_mini(mini_session, mapped_data)
                        stats['imported'] += 1

                    # Handle relationships
                    if import_relationships:
                        rapporti_field = us_data.get('rapporti')
                        if rapporti_field:
                            logger.info(f"Processing relationships for US {us_data['sito']}/{us_data['us']}: {rapporti_field}")
                            relationships = self._parse_pyarchinit_rapporti(rapporti_field)
                            logger.info(f"Parsed {len(relationships)} relationships: {relationships}")

                            for rel_type, us_to in relationships:
                                try:
                                    # Check if relationship already exists
                                    existing_rel = mini_session.execute(
                                        text("""SELECT id_relationship FROM us_relationships_table
                                                WHERE sito = :sito AND us_from = :us_from AND us_to = :us_to
                                                AND relationship_type = :rel_type"""),
                                        {
                                            'sito': us_data['sito'],
                                            'us_from': int(us_data['us']),
                                            'us_to': int(us_to),
                                            'rel_type': rel_type
                                        }
                                    ).fetchone()

                                    if existing_rel:
                                        logger.debug(f"Relationship already exists: {us_data['sito']} US {us_data['us']} -{rel_type}-> {us_to}")
                                        continue

                                    # Insert relationship
                                    rel_query = text("""
                                        INSERT INTO us_relationships_table
                                        (sito, us_from, us_to, relationship_type, created_at, updated_at)
                                        VALUES (:sito, :us_from, :us_to, :rel_type, :created_at, :updated_at)
                                    """)

                                    mini_session.execute(rel_query, {
                                        'sito': us_data['sito'],
                                        'us_from': int(us_data['us']),
                                        'us_to': int(us_to),
                                        'rel_type': rel_type,
                                        'created_at': datetime.now(),
                                        'updated_at': datetime.now()
                                    })
                                    stats['relationships_created'] += 1
                                    logger.info(f"Created relationship: {us_data['sito']} US {us_data['us']} -{rel_type}-> {us_to}")

                                except Exception as e:
                                    logger.warning(f"Failed to create relationship {us_data['sito']} US {us_data['us']} -{rel_type}-> {us_to}: {str(e)}")
                        else:
                            logger.debug(f"No rapporti field for US {us_data['sito']}/{us_data['us']}")

                    mini_session.commit()

                except Exception as e:
                    mini_session.rollback()
                    error_msg = f"Error importing US {us_data.get('sito')}/{us_data.get('us')}: {str(e)}"
                    logger.error(error_msg)
                    stats['errors'].append(error_msg)
                    stats['skipped'] += 1

            return stats

        except Exception as e:
            logger.error(f"Import US failed: {str(e)}")
            raise
        finally:
            source_session.close()
            mini_session.close()

    def _convert_rapporti_to_mini_format(self, rapporti_str: str) -> str:
        """
        Convert PyArchInit rapporti format to PyArchInit-Mini format

        PyArchInit: [['Copre', '3', '1', 'Scavo archeologico'], ['Copre', '11', '1', 'Scavo archeologico']]
        PyArchInit-Mini: Copre 3, Copre 11
        """
        if not rapporti_str or rapporti_str == '[]':
            return ''

        try:
            relationships = self._parse_pyarchinit_rapporti(rapporti_str)
            # Format as "Relationship US, Relationship US, ..."
            formatted = ', '.join([f"{rel_type} {us_num}" for rel_type, us_num in relationships])
            return formatted
        except Exception as e:
            logger.warning(f"Failed to convert rapporti format: {rapporti_str} - {str(e)}")
            return rapporti_str  # Return original if conversion fails

    def _map_us_fields_import(self, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map US fields from PyArchInit to PyArchInit-Mini format"""

        # Handle date conversion
        data_schedatura = source_data.get('data_schedatura')
        if data_schedatura and isinstance(data_schedatura, str):
            # Try to parse date string (common formats: YYYY-MM-DD, DD/MM/YYYY)
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%Y/%m/%d', '%d-%m-%Y']:
                try:
                    data_schedatura = datetime.strptime(data_schedatura, fmt).date()
                    break
                except (ValueError, AttributeError):
                    continue
            else:
                # If parsing fails, set to None
                data_schedatura = None
        elif not isinstance(data_schedatura, (type(None), date)):
            # If it's not None or date, set to None
            data_schedatura = None

        mapped = {
            # Core fields
            'sito': source_data.get('sito'),
            'area': source_data.get('area'),
            'us': source_data.get('us'),
            'd_stratigrafica': source_data.get('d_stratigrafica'),
            'd_interpretativa': source_data.get('d_interpretativa'),
            'descrizione': source_data.get('descrizione'),
            'interpretazione': source_data.get('interpretazione'),

            # Period fields
            'periodo_iniziale': source_data.get('periodo_iniziale'),
            'fase_iniziale': source_data.get('fase_iniziale'),
            'periodo_finale': source_data.get('periodo_finale'),
            'fase_finale': source_data.get('fase_finale'),

            # Excavation fields
            'scavato': source_data.get('scavato'),
            'attivita': source_data.get('attivita'),
            'anno_scavo': source_data.get('anno_scavo'),
            'metodo_di_scavo': source_data.get('metodo_di_scavo'),
            'data_schedatura': data_schedatura,
            'schedatore': source_data.get('schedatore'),

            # Physical description
            'formazione': source_data.get('formazione'),
            'stato_di_conservazione': source_data.get('stato_di_conservazione'),
            'colore': source_data.get('colore'),
            'consistenza': source_data.get('consistenza'),
            'struttura': source_data.get('struttura'),

            # Text fields
            'inclusi': source_data.get('inclusi'),
            'campioni': source_data.get('campioni'),
            'rapporti': self._convert_rapporti_to_mini_format(source_data.get('rapporti', '')),  # Convert to readable format
            'documentazione': source_data.get('documentazione'),
            'cont_per': source_data.get('cont_per'),

            # Administrative
            'order_layer': source_data.get('order_layer'),
            'unita_tipo': source_data.get('unita_tipo', 'US'),
            'settore': source_data.get('settore'),
            'quad_par': source_data.get('quad_par'),
            'ambient': source_data.get('ambient'),
            'saggio': source_data.get('saggio'),
            'n_catalogo_generale': source_data.get('n_catalogo_generale'),
            'n_catalogo_interno': source_data.get('n_catalogo_interno'),
            'n_catalogo_internazionale': source_data.get('n_catalogo_internazionale'),
            'soprintendenza': source_data.get('soprintendenza'),

            # Measurements
            'quota_relativa': source_data.get('quota_relativa'),
            'quota_abs': source_data.get('quota_abs'),
            'lunghezza_max': source_data.get('lunghezza_max'),
            'altezza_max': source_data.get('altezza_max'),
            'altezza_min': source_data.get('altezza_min'),
            'profondita_max': source_data.get('profondita_max'),
            'profondita_min': source_data.get('profondita_min'),
            'larghezza_media': source_data.get('larghezza_media'),

            # Additional
            'osservazioni': source_data.get('osservazioni'),
            'datazione': source_data.get('datazione'),
            'flottazione': source_data.get('flottazione'),
            'setacciatura': source_data.get('setacciatura'),
            'affidabilita': source_data.get('affidabilita'),
            'direttore_us': source_data.get('direttore_us'),
            'responsabile_us': source_data.get('responsabile_us'),

            # Timestamps
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }

        return mapped

    def _insert_us_mini(self, session: Session, data: Dict[str, Any]):
        """Insert US into PyArchInit-Mini database"""
        # Generate next id_us (VARCHAR field, sequential)
        max_id_result = session.execute(text("SELECT MAX(CAST(id_us AS INTEGER)) FROM us_table")).fetchone()
        next_id = (max_id_result[0] or 0) + 1 if max_id_result else 1
        data['id_us'] = str(next_id)

        # Build INSERT with all fields including id_us
        fields = list(data.keys())
        placeholders = [f':{k}' for k in fields]

        query = text(f"""
            INSERT INTO us_table ({', '.join(fields)})
            VALUES ({', '.join(placeholders)})
        """)

        session.execute(query, data)

    def _update_us_mini(self, session: Session, data: Dict[str, Any]):
        """Update US in PyArchInit-Mini database using raw SQL"""
        # Build UPDATE query dynamically based on provided fields
        # Exclude identity fields (sito, us, id_us) from update
        update_fields = {k: v for k, v in data.items() if k not in ['sito', 'us', 'id_us']}

        if update_fields:
            set_clause = ', '.join([f"{k} = :{k}" for k in update_fields.keys()])
            query = text(f"""
                UPDATE us_table
                SET {set_clause}
                WHERE sito = :sito AND us = :us
            """)

            # Combine update fields with identity fields for WHERE clause
            params = {**update_fields, 'sito': data['sito'], 'us': data['us']}
            session.execute(query, params)

    def export_us(self, target_db_connection: str, sito_filter: Optional[List[str]] = None,
                  export_relationships: bool = True) -> Dict[str, Any]:
        """
        Export US from PyArchInit-Mini to PyArchInit

        Args:
            target_db_connection: Connection string for target PyArchInit database
            sito_filter: List of site names to export (None = export all)
            export_relationships: If True, convert relationships to rapporti format

        Returns:
            Dictionary with export statistics
        """
        stats = {'exported': 0, 'updated': 0, 'skipped': 0, 'errors': []}

        target_engine = create_engine(target_db_connection)
        target_session = sessionmaker(bind=target_engine)()
        mini_session = self.mini_session_maker()

        try:
            # Query US from PyArchInit-Mini
            query = "SELECT * FROM us_table"
            if sito_filter:
                placeholders = ','.join([f"'{s}'" for s in sito_filter])
                query += f" WHERE sito IN ({placeholders})"

            result = mini_session.execute(text(query))
            mini_us_list = result.fetchall()

            for us_row in mini_us_list:
                try:
                    us_data = dict(us_row._mapping)

                    # Convert relationships if needed
                    rapporti_str = '[]'
                    if export_relationships:
                        rapporti_str = self._convert_relationships_to_pyarchinit_format(
                            us_data['sito'], us_data['us'], mini_session
                        )

                    # Map fields from PyArchInit-Mini to PyArchInit
                    mapped_data = self._map_us_fields_export(us_data, rapporti_str)

                    # Check if US exists in target
                    existing = target_session.execute(
                        text("SELECT id_us FROM us_table WHERE sito = :sito AND us = :us"),
                        {'sito': us_data['sito'], 'us': us_data['us']}
                    ).fetchone()

                    if existing:
                        self._update_us_pyarchinit(target_session, mapped_data)
                        stats['updated'] += 1
                    else:
                        self._insert_us_pyarchinit(target_session, mapped_data)
                        stats['exported'] += 1

                    target_session.commit()

                except Exception as e:
                    target_session.rollback()
                    error_msg = f"Error exporting US {us_data.get('sito')}/{us_data.get('us')}: {str(e)}"
                    logger.error(error_msg)
                    stats['errors'].append(error_msg)
                    stats['skipped'] += 1

            return stats

        except Exception as e:
            logger.error(f"Export US failed: {str(e)}")
            raise
        finally:
            target_session.close()
            mini_session.close()

    def _map_us_fields_export(self, source_data: Dict[str, Any], rapporti: str) -> Dict[str, Any]:
        """Map US fields from PyArchInit-Mini to PyArchInit format"""
        return {
            'sito': source_data.get('sito'),
            'area': source_data.get('area'),
            'us': source_data.get('us'),
            'd_stratigrafica': source_data.get('d_stratigrafica'),
            'd_interpretativa': source_data.get('d_interpretativa'),
            'descrizione': source_data.get('descrizione'),
            'interpretazione': source_data.get('interpretazione'),
            'periodo_iniziale': source_data.get('periodo_iniziale'),
            'fase_iniziale': source_data.get('fase_iniziale'),
            'periodo_finale': source_data.get('periodo_finale'),
            'fase_finale': source_data.get('fase_finale'),
            'scavato': source_data.get('scavato'),
            'attivita': source_data.get('attivita'),
            'anno_scavo': source_data.get('anno_scavo'),
            'metodo_di_scavo': source_data.get('metodo_di_scavo'),
            'data_schedatura': source_data.get('data_schedatura'),
            'schedatore': source_data.get('schedatore'),
            'formazione': source_data.get('formazione'),
            'stato_di_conservazione': source_data.get('stato_di_conservazione'),
            'colore': source_data.get('colore'),
            'consistenza': source_data.get('consistenza'),
            'struttura': source_data.get('struttura'),
            'inclusi': source_data.get('inclusi'),
            'campioni': source_data.get('campioni'),
            'rapporti': rapporti,  # Converted relationships
            'documentazione': source_data.get('documentazione'),
            'cont_per': source_data.get('cont_per'),
            'order_layer': source_data.get('order_layer'),
            'unita_tipo': source_data.get('unita_tipo', 'US'),
            'settore': source_data.get('settore'),
            'quad_par': source_data.get('quad_par'),
            'ambient': source_data.get('ambient'),
            'saggio': source_data.get('saggio'),
            'n_catalogo_generale': source_data.get('n_catalogo_generale'),
            'n_catalogo_interno': source_data.get('n_catalogo_interno'),
            'n_catalogo_internazionale': source_data.get('n_catalogo_internazionale'),
            'soprintendenza': source_data.get('soprintendenza'),
            'quota_relativa': source_data.get('quota_relativa'),
            'quota_abs': source_data.get('quota_abs'),
            'lunghezza_max': source_data.get('lunghezza_max'),
            'altezza_max': source_data.get('altezza_max'),
            'altezza_min': source_data.get('altezza_min'),
            'profondita_max': source_data.get('profondita_max'),
            'profondita_min': source_data.get('profondita_min'),
            'larghezza_media': source_data.get('larghezza_media'),
            'osservazioni': source_data.get('osservazioni'),
            'datazione': source_data.get('datazione'),
            'flottazione': source_data.get('flottazione'),
            'setacciatura': source_data.get('setacciatura'),
            'affidabilita': source_data.get('affidabilita'),
            'direttore_us': source_data.get('direttore_us'),
            'responsabile_us': source_data.get('responsabile_us')
        }

    def _insert_us_pyarchinit(self, session: Session, data: Dict[str, Any]):
        """Insert US into PyArchInit database"""
        query = text("""
            INSERT INTO us_table
            (sito, area, us, d_stratigrafica, d_interpretativa, descrizione, interpretazione,
             periodo_iniziale, fase_iniziale, periodo_finale, fase_finale,
             scavato, attivita, anno_scavo, metodo_di_scavo, data_schedatura, schedatore,
             formazione, stato_di_conservazione, colore, consistenza, struttura,
             inclusi, campioni, rapporti, documentazione, cont_per, order_layer,
             unita_tipo, settore, quad_par, ambient, saggio,
             n_catalogo_generale, n_catalogo_interno, n_catalogo_internazionale, soprintendenza,
             quota_relativa, quota_abs, lunghezza_max, altezza_max, altezza_min,
             profondita_max, profondita_min, larghezza_media,
             osservazioni, datazione, flottazione, setacciatura, affidabilita,
             direttore_us, responsabile_us)
            VALUES
            (:sito, :area, :us, :d_stratigrafica, :d_interpretativa, :descrizione, :interpretazione,
             :periodo_iniziale, :fase_iniziale, :periodo_finale, :fase_finale,
             :scavato, :attivita, :anno_scavo, :metodo_di_scavo, :data_schedatura, :schedatore,
             :formazione, :stato_di_conservazione, :colore, :consistenza, :struttura,
             :inclusi, :campioni, :rapporti, :documentazione, :cont_per, :order_layer,
             :unita_tipo, :settore, :quad_par, :ambient, :saggio,
             :n_catalogo_generale, :n_catalogo_interno, :n_catalogo_internazionale, :soprintendenza,
             :quota_relativa, :quota_abs, :lunghezza_max, :altezza_max, :altezza_min,
             :profondita_max, :profondita_min, :larghezza_media,
             :osservazioni, :datazione, :flottazione, :setacciatura, :affidabilita,
             :direttore_us, :responsabile_us)
        """)

        session.execute(query, data)

    def _update_us_pyarchinit(self, session: Session, data: Dict[str, Any]):
        """Update US in PyArchInit database"""
        query = text("""
            UPDATE us_table
            SET area = :area, d_stratigrafica = :d_stratigrafica,
                d_interpretativa = :d_interpretativa, descrizione = :descrizione,
                interpretazione = :interpretazione, periodo_iniziale = :periodo_iniziale,
                fase_iniziale = :fase_iniziale, periodo_finale = :periodo_finale,
                fase_finale = :fase_finale, scavato = :scavato, attivita = :attivita,
                anno_scavo = :anno_scavo, metodo_di_scavo = :metodo_di_scavo,
                data_schedatura = :data_schedatura, schedatore = :schedatore,
                formazione = :formazione, stato_di_conservazione = :stato_di_conservazione,
                colore = :colore, consistenza = :consistenza, struttura = :struttura,
                inclusi = :inclusi, campioni = :campioni, rapporti = :rapporti,
                documentazione = :documentazione, cont_per = :cont_per,
                order_layer = :order_layer, unita_tipo = :unita_tipo,
                settore = :settore, quad_par = :quad_par, ambient = :ambient,
                saggio = :saggio, n_catalogo_generale = :n_catalogo_generale,
                n_catalogo_interno = :n_catalogo_interno,
                n_catalogo_internazionale = :n_catalogo_internazionale,
                soprintendenza = :soprintendenza, quota_relativa = :quota_relativa,
                quota_abs = :quota_abs, lunghezza_max = :lunghezza_max,
                altezza_max = :altezza_max, altezza_min = :altezza_min,
                profondita_max = :profondita_max, profondita_min = :profondita_min,
                larghezza_media = :larghezza_media, osservazioni = :osservazioni,
                datazione = :datazione, flottazione = :flottazione,
                setacciatura = :setacciatura, affidabilita = :affidabilita,
                direttore_us = :direttore_us, responsabile_us = :responsabile_us
            WHERE sito = :sito AND us = :us
        """)

        session.execute(query, data)

    # ============================================================================
    # INVENTARIO MATERIALI IMPORT/EXPORT
    # ============================================================================

    def import_inventario(self, sito_filter: Optional[List[str]] = None,
                         auto_migrate: bool = True,
                         auto_backup: bool = True) -> Dict[str, Any]:
        """
        Import Inventario Materiali from PyArchInit to PyArchInit-Mini

        Args:
            sito_filter: List of site names to import (None = import all)
            auto_migrate: If True, automatically add missing i18n columns to source database
            auto_backup: If True, create backup before database migration

        Returns:
            Dictionary with import statistics including backup_path
        """
        if not self.source_engine:
            raise ValueError("Source database not configured")

        # Auto-migrate source database to add i18n columns if needed
        if auto_migrate:
            logger.info("Checking source database for missing i18n columns...")
            migration_stats = self.migrate_source_database(tables=['inventario_materiali_table'], auto_backup=auto_backup)
            if migration_stats['columns_added'] > 0:
                logger.info(f"Added {migration_stats['columns_added']} i18n columns to source database")
            if migration_stats.get('backup_path'):
                logger.info(f"Database backup: {migration_stats['backup_path']}")

        stats = {'imported': 0, 'updated': 0, 'skipped': 0, 'errors': []}

        source_session = self.source_session_maker()
        mini_session = self.mini_session_maker()

        try:
            # Find correct table name (might be backup table)
            inspector = inspect(self.source_engine)
            tables = inspector.get_table_names()

            inv_table = None
            for table in tables:
                if 'inventario_materiali_table' in table and 'backup' in table:
                    # Use most recent backup
                    if inv_table is None or table > inv_table:
                        inv_table = table

            if inv_table is None:
                # Try without backup
                inv_table = 'inventario_materiali_table_toimp' if 'inventario_materiali_table_toimp' in tables else None

            if inv_table is None:
                raise ValueError("Could not find inventario_materiali table in source database")

            # Query inventario from PyArchInit
            query = f"SELECT * FROM {inv_table}"
            if sito_filter:
                placeholders = ','.join([f"'{s}'" for s in sito_filter])
                query += f" WHERE sito IN ({placeholders})"

            result = source_session.execute(text(query))
            source_inv_list = result.fetchall()

            for inv_row in source_inv_list:
                try:
                    inv_data = dict(inv_row._mapping)

                    # Check if record exists
                    existing = mini_session.execute(
                        text("""SELECT id_invmat FROM inventario_materiali_table
                                WHERE sito = :sito AND numero_inventario = :numero_inventario"""),
                        {'sito': inv_data['sito'], 'numero_inventario': inv_data['numero_inventario']}
                    ).fetchone()

                    # Map fields
                    mapped_data = self._map_inventario_fields(inv_data)

                    if existing:
                        self._update_inventario_mini(mini_session, mapped_data)
                        stats['updated'] += 1
                    else:
                        self._insert_inventario_mini(mini_session, mapped_data)
                        stats['imported'] += 1

                    mini_session.commit()

                except Exception as e:
                    mini_session.rollback()
                    error_msg = f"Error importing inventario {inv_data.get('sito')}/{inv_data.get('numero_inventario')}: {str(e)}"
                    logger.error(error_msg)
                    stats['errors'].append(error_msg)
                    stats['skipped'] += 1

            return stats

        except Exception as e:
            logger.error(f"Import inventario failed: {str(e)}")
            raise
        finally:
            source_session.close()
            mini_session.close()

    def _map_inventario_fields(self, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """Map inventario fields from PyArchInit to PyArchInit-Mini"""
        return {
            'sito': source_data.get('sito'),
            'numero_inventario': source_data.get('numero_inventario'),
            'tipo_reperto': source_data.get('tipo_reperto'),
            'criterio_schedatura': source_data.get('criterio_schedatura'),
            'definizione': source_data.get('definizione'),
            'descrizione': source_data.get('descrizione'),
            'area': source_data.get('area'),
            'us': source_data.get('us'),
            'lavato': source_data.get('lavato'),
            'nr_cassa': source_data.get('nr_cassa'),
            'luogo_conservazione': source_data.get('luogo_conservazione'),
            'stato_conservazione': source_data.get('stato_conservazione'),
            'datazione_reperto': source_data.get('datazione_reperto'),
            'elementi_reperto': source_data.get('elementi_reperto'),
            'misurazioni': source_data.get('misurazioni'),
            'rif_biblio': source_data.get('rif_biblio'),
            'tecnologie': source_data.get('tecnologie'),
            'forme_minime': source_data.get('forme_minime'),
            'forme_massime': source_data.get('forme_massime'),
            'totale_frammenti': source_data.get('totale_frammenti'),
            'corpo_ceramico': source_data.get('corpo_ceramico'),
            'rivestimento': source_data.get('rivestimento'),
            'diametro_orlo': source_data.get('diametro_orlo'),
            'peso': source_data.get('peso'),
            'tipo': source_data.get('tipo'),
            'eve_orlo': source_data.get('eve_orlo'),
            'repertato': source_data.get('repertato'),
            'diagnostico': source_data.get('diagnostico'),
            'n_reperto': source_data.get('n_reperto'),
            'tipo_contenitore': source_data.get('tipo_contenitore'),
            'struttura': source_data.get('struttura'),
            'years': source_data.get('years'),
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }

    def _insert_inventario_mini(self, session: Session, data: Dict[str, Any]):
        """Insert inventario into PyArchInit-Mini database"""
        query = text("""
            INSERT INTO inventario_materiali_table
            (sito, numero_inventario, tipo_reperto, criterio_schedatura, definizione,
             descrizione, area, us, lavato, nr_cassa, luogo_conservazione,
             stato_conservazione, datazione_reperto, elementi_reperto, misurazioni,
             rif_biblio, tecnologie, forme_minime, forme_massime, totale_frammenti,
             corpo_ceramico, rivestimento, diametro_orlo, peso, tipo, eve_orlo,
             repertato, diagnostico, n_reperto, tipo_contenitore, struttura, years,
             created_at, updated_at)
            VALUES
            (:sito, :numero_inventario, :tipo_reperto, :criterio_schedatura, :definizione,
             :descrizione, :area, :us, :lavato, :nr_cassa, :luogo_conservazione,
             :stato_conservazione, :datazione_reperto, :elementi_reperto, :misurazioni,
             :rif_biblio, :tecnologie, :forme_minime, :forme_massime, :totale_frammenti,
             :corpo_ceramico, :rivestimento, :diametro_orlo, :peso, :tipo, :eve_orlo,
             :repertato, :diagnostico, :n_reperto, :tipo_contenitore, :struttura, :years,
             :created_at, :updated_at)
        """)

        session.execute(query, data)

    def _update_inventario_mini(self, session: Session, data: Dict[str, Any]):
        """Update inventario in PyArchInit-Mini database"""
        query = text("""
            UPDATE inventario_materiali_table
            SET tipo_reperto = :tipo_reperto, criterio_schedatura = :criterio_schedatura,
                definizione = :definizione, descrizione = :descrizione, area = :area,
                us = :us, lavato = :lavato, nr_cassa = :nr_cassa,
                luogo_conservazione = :luogo_conservazione,
                stato_conservazione = :stato_conservazione,
                datazione_reperto = :datazione_reperto, elementi_reperto = :elementi_reperto,
                misurazioni = :misurazioni, rif_biblio = :rif_biblio,
                tecnologie = :tecnologie, forme_minime = :forme_minime,
                forme_massime = :forme_massime, totale_frammenti = :totale_frammenti,
                corpo_ceramico = :corpo_ceramico, rivestimento = :rivestimento,
                diametro_orlo = :diametro_orlo, peso = :peso, tipo = :tipo,
                eve_orlo = :eve_orlo, repertato = :repertato, diagnostico = :diagnostico,
                n_reperto = :n_reperto, tipo_contenitore = :tipo_contenitore,
                struttura = :struttura, years = :years, updated_at = :updated_at
            WHERE sito = :sito AND numero_inventario = :numero_inventario
        """)

        session.execute(query, data)

    # ============================================================================
    # PERIODIZZAZIONE IMPORT/EXPORT
    # ============================================================================

    def import_periodizzazione(self, sito_filter: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Import Periodizzazione from PyArchInit to PyArchInit-Mini

        Args:
            sito_filter: List of site names to import (None = import all)

        Returns:
            Dictionary with import statistics
        """
        if not self.source_engine:
            raise ValueError("Source database not configured")

        stats = {'imported': 0, 'updated': 0, 'skipped': 0, 'errors': []}

        source_session = self.source_session_maker()
        mini_session = self.mini_session_maker()

        try:
            # Query periodizzazione from PyArchInit
            query = "SELECT * FROM periodizzazione_table"
            if sito_filter:
                placeholders = ','.join([f"'{s}'" for s in sito_filter])
                query += f" WHERE sito IN ({placeholders})"

            result = source_session.execute(text(query))
            source_period_list = result.fetchall()

            for period_row in source_period_list:
                try:
                    period_data = dict(period_row._mapping)

                    # Map and insert/update
                    mapped_data = {
                        'sito': period_data.get('sito'),
                        'area': period_data.get('area'),
                        'us': period_data.get('us'),
                        'periodo_iniziale': period_data.get('periodo'),
                        'fase_iniziale': period_data.get('fase'),
                        'datazione_estesa': period_data.get('datazione_estesa'),
                        'created_at': datetime.now(),
                        'updated_at': datetime.now()
                    }

                    # Check if exists
                    existing = mini_session.execute(
                        text("""SELECT id_periodizzazione FROM periodizzazione_table
                                WHERE sito = :sito AND us = :us"""),
                        {'sito': mapped_data['sito'], 'us': mapped_data.get('us')}
                    ).fetchone()

                    if not existing:
                        insert_query = text("""
                            INSERT INTO periodizzazione_table
                            (sito, area, us, periodo_iniziale, fase_iniziale,
                             datazione_estesa, created_at, updated_at)
                            VALUES
                            (:sito, :area, :us, :periodo_iniziale, :fase_iniziale,
                             :datazione_estesa, :created_at, :updated_at)
                        """)
                        mini_session.execute(insert_query, mapped_data)
                        stats['imported'] += 1
                    else:
                        stats['skipped'] += 1

                    mini_session.commit()

                except Exception as e:
                    mini_session.rollback()
                    error_msg = f"Error importing periodizzazione: {str(e)}"
                    logger.error(error_msg)
                    stats['errors'].append(error_msg)
                    stats['skipped'] += 1

            return stats

        except Exception as e:
            logger.error(f"Import periodizzazione failed: {str(e)}")
            raise
        finally:
            source_session.close()
            mini_session.close()

    # ============================================================================
    # THESAURUS IMPORT/EXPORT
    # ============================================================================

    def import_thesaurus(self) -> Dict[str, Any]:
        """
        Import Thesaurus from PyArchInit to PyArchInit-Mini

        Returns:
            Dictionary with import statistics
        """
        if not self.source_engine:
            raise ValueError("Source database not configured")

        stats = {'imported': 0, 'updated': 0, 'skipped': 0, 'errors': []}

        source_session = self.source_session_maker()
        mini_session = self.mini_session_maker()

        try:
            # Query thesaurus from PyArchInit
            result = source_session.execute(text("SELECT * FROM pyarchinit_thesaurus_sigle"))
            source_thesaurus_list = result.fetchall()

            for thesaurus_row in source_thesaurus_list:
                try:
                    thes_data = dict(thesaurus_row._mapping)

                    # Check if exists
                    existing = mini_session.execute(
                        text("""SELECT id_thesaurus_sigle FROM pyarchinit_thesaurus_sigle
                                WHERE nome_tabella = :nome_tabella AND sigla = :sigla"""),
                        {'nome_tabella': thes_data['nome_tabella'], 'sigla': thes_data['sigla']}
                    ).fetchone()

                    if existing:
                        stats['skipped'] += 1
                        continue

                    # Insert new thesaurus entry
                    insert_query = text("""
                        INSERT INTO pyarchinit_thesaurus_sigle
                        (nome_tabella, sigla, sigla_estesa, descrizione, tipologia_sigla,
                         lingua, created_at, updated_at)
                        VALUES
                        (:nome_tabella, :sigla, :sigla_estesa, :descrizione, :tipologia_sigla,
                         :lingua, :created_at, :updated_at)
                    """)

                    mini_session.execute(insert_query, {
                        'nome_tabella': thes_data.get('nome_tabella'),
                        'sigla': thes_data.get('sigla'),
                        'sigla_estesa': thes_data.get('sigla_estesa'),
                        'descrizione': thes_data.get('descrizione'),
                        'tipologia_sigla': thes_data.get('tipologia_sigla'),
                        'lingua': thes_data.get('lingua', ''),
                        'created_at': datetime.now(),
                        'updated_at': datetime.now()
                    })
                    stats['imported'] += 1

                    mini_session.commit()

                except Exception as e:
                    mini_session.rollback()
                    error_msg = f"Error importing thesaurus: {str(e)}"
                    logger.error(error_msg)
                    stats['errors'].append(error_msg)
                    stats['skipped'] += 1

            return stats

        except Exception as e:
            logger.error(f"Import thesaurus failed: {str(e)}")
            raise
        finally:
            source_session.close()
            mini_session.close()

    # ============================================================================
    # UTILITY METHODS
    # ============================================================================

    def get_available_sites_in_source(self) -> List[str]:
        """Get list of available sites in source database"""
        if not self.source_engine:
            raise ValueError("Source database not configured")

        session = self.source_session_maker()
        try:
            result = session.execute(text("SELECT DISTINCT sito FROM site_table ORDER BY sito"))
            return [row[0] for row in result.fetchall()]
        finally:
            session.close()

    def validate_database_connection(self, connection_string: str) -> bool:
        """Validate database connection string"""
        try:
            engine = create_engine(connection_string)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database validation failed: {str(e)}")
            return False

    def sync_datazioni_from_periodizzazione(self) -> Dict[str, Any]:
        """
        Synchronize datazioni_table from unique periodo values in periodizzazione_table

        This creates entries in datazioni_table for each unique periodo found in
        periodizzazione, if they don't already exist.

        Returns:
            Dictionary with sync statistics
        """
        stats = {'created': 0, 'skipped': 0, 'errors': []}

        mini_session = self.mini_session_maker()

        try:
            # Get unique periodo values from periodizzazione_table
            result = mini_session.execute(text("""
                SELECT DISTINCT periodo_iniziale, datazione_estesa
                FROM periodizzazione_table
                WHERE periodo_iniziale IS NOT NULL AND periodo_iniziale != ''
                ORDER BY periodo_iniziale
            """))

            unique_periodi = result.fetchall()
            logger.info(f"Found {len(unique_periodi)} unique periodi in periodizzazione")

            for periodo_row in unique_periodi:
                periodo_nome = periodo_row[0]
                datazione_estesa = periodo_row[1] or ''

                try:
                    # Check if datazione already exists
                    existing = mini_session.execute(
                        text("SELECT id_datazione FROM datazioni_table WHERE nome_datazione = :nome"),
                        {'nome': periodo_nome}
                    ).fetchone()

                    if not existing:
                        # Insert new datazione
                        mini_session.execute(text("""
                            INSERT INTO datazioni_table (nome_datazione, descrizione, created_at, updated_at)
                            VALUES (:nome, :descrizione, :created, :updated)
                        """), {
                            'nome': periodo_nome,
                            'descrizione': datazione_estesa,
                            'created': datetime.now(),
                            'updated': datetime.now()
                        })
                        mini_session.commit()
                        stats['created'] += 1
                        logger.info(f"Created datazione: {periodo_nome}")
                    else:
                        stats['skipped'] += 1

                except Exception as e:
                    mini_session.rollback()
                    error_msg = f"Error syncing datazione '{periodo_nome}': {str(e)}"
                    logger.error(error_msg)
                    stats['errors'].append(error_msg)

            return stats

        except Exception as e:
            logger.error(f"Sync datazioni failed: {str(e)}")
            raise
        finally:
            mini_session.close()

    def sync_datazioni_from_us_values(self) -> Dict[str, Any]:
        """
        Synchronize datazioni_table from unique datazione values in us_table

        This creates entries in datazioni_table for each unique datazione value
        found in us_table, if they don't already exist. This ensures that all
        datazione values from imported US records are available in the dropdown.

        Returns:
            Dictionary with sync statistics
        """
        stats = {'created': 0, 'skipped': 0, 'errors': []}

        mini_session = self.mini_session_maker()

        try:
            # Get unique datazione values from us_table
            result = mini_session.execute(text("""
                SELECT DISTINCT datazione
                FROM us_table
                WHERE datazione IS NOT NULL AND datazione != ''
                ORDER BY datazione
            """))

            unique_datazioni = result.fetchall()
            logger.info(f"Found {len(unique_datazioni)} unique datazione values in us_table")

            for datazione_row in unique_datazioni:
                datazione_value = datazione_row[0]

                try:
                    # Check if datazione already exists
                    existing = mini_session.execute(
                        text("SELECT id_datazione FROM datazioni_table WHERE nome_datazione = :nome"),
                        {'nome': datazione_value}
                    ).fetchone()

                    if not existing:
                        # Insert new datazione
                        mini_session.execute(text("""
                            INSERT INTO datazioni_table (nome_datazione, descrizione, created_at, updated_at)
                            VALUES (:nome, :descrizione, :created, :updated)
                        """), {
                            'nome': datazione_value,
                            'descrizione': datazione_value,  # Use same value for description
                            'created': datetime.now(),
                            'updated': datetime.now()
                        })
                        mini_session.commit()
                        stats['created'] += 1
                        logger.info(f"Created datazione from US: {datazione_value}")
                    else:
                        stats['skipped'] += 1

                except Exception as e:
                    mini_session.rollback()
                    error_msg = f"Error syncing datazione '{datazione_value}': {str(e)}"
                    logger.error(error_msg)
                    stats['errors'].append(error_msg)

            return stats

        except Exception as e:
            logger.error(f"Sync datazioni from US failed: {str(e)}")
            raise
        finally:
            mini_session.close()

    def update_us_datazione_from_periodizzazione(self, sito_filter: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Update datazione field in us_table based on periodizzazione_table data

        For each US, finds the corresponding periodo_iniziale from periodizzazione
        and sets it as the datazione field in us_table.

        Args:
            sito_filter: List of site names to update (None = update all)

        Returns:
            Dictionary with update statistics
        """
        stats = {'updated': 0, 'skipped': 0, 'errors': []}

        mini_session = self.mini_session_maker()

        try:
            # Build query for US with sito filter
            us_query = "SELECT sito, us FROM us_table"
            if sito_filter:
                placeholders = ','.join([f"'{s}'" for s in sito_filter])
                us_query += f" WHERE sito IN ({placeholders})"

            result = mini_session.execute(text(us_query))
            us_list = result.fetchall()

            logger.info(f"Updating datazione for {len(us_list)} US from periodizzazione")

            for us_row in us_list:
                sito = us_row[0]
                us_num = us_row[1]

                try:
                    # Get periodo_iniziale from periodizzazione for this US
                    periodo_result = mini_session.execute(text("""
                        SELECT periodo_iniziale
                        FROM periodizzazione_table
                        WHERE sito = :sito AND us = :us
                        LIMIT 1
                    """), {'sito': sito, 'us': us_num})

                    periodo_row = periodo_result.fetchone()

                    if periodo_row and periodo_row[0]:
                        periodo_iniziale = periodo_row[0]

                        # Update us_table datazione field
                        mini_session.execute(text("""
                            UPDATE us_table
                            SET datazione = :datazione, updated_at = :updated
                            WHERE sito = :sito AND us = :us
                        """), {
                            'datazione': periodo_iniziale,
                            'updated': datetime.now(),
                            'sito': sito,
                            'us': us_num
                        })
                        mini_session.commit()
                        stats['updated'] += 1
                    else:
                        stats['skipped'] += 1

                except Exception as e:
                    mini_session.rollback()
                    error_msg = f"Error updating US {sito}/{us_num}: {str(e)}"
                    logger.error(error_msg)
                    stats['errors'].append(error_msg)

            logger.info(f"Updated {stats['updated']} US with datazione from periodizzazione")
            return stats

        except Exception as e:
            logger.error(f"Update US datazione failed: {str(e)}")
            raise
        finally:
            mini_session.close()

    # ============================================================================
    # DATABASE MIGRATION (SQLite ↔ PostgreSQL)
    # ============================================================================

    @staticmethod
    def migrate_database(source_db_url: str, target_db_url: str,
                        create_target: bool = True,
                        overwrite_target: bool = False,
                        auto_backup: bool = True,
                        backup_dir: Optional[str] = None,
                        merge_strategy: str = 'skip') -> Dict[str, Any]:
        """
        Migrate all data from source database to target database

        Supports:
        - SQLite → PostgreSQL
        - PostgreSQL → SQLite
        - SQLite → SQLite (copy/backup)
        - PostgreSQL → PostgreSQL (copy/backup)

        Args:
            source_db_url: Source database connection string
            target_db_url: Target database connection string
            create_target: If True, create target database with schema if it doesn't exist
            overwrite_target: If True and create_target=True, overwrite existing target database
            auto_backup: If True, automatically create a backup of source database before migration
            backup_dir: Optional directory for backups (defaults to same dir as source)
            merge_strategy: How to handle ID conflicts: 'skip', 'overwrite', or 'renumber'
                - 'skip': Skip records with conflicting IDs (default)
                - 'overwrite': Update existing records with new data
                - 'renumber': Generate new IDs for conflicting records

        Returns:
            Dictionary with migration statistics including backup info
        """
        stats = {
            'success': False,
            'tables_migrated': 0,
            'total_rows_copied': 0,
            'rows_per_table': {},
            'errors': [],
            'duration_seconds': 0,
            'backup_created': False,
            'backup_path': None,
            'backup_size_mb': 0.0
        }

        import time
        start_time = time.time()

        try:
            # Create backup of source database if requested
            if auto_backup:
                logger.info("Creating backup of source database...")
                backup_result = ImportExportService._create_backup(source_db_url, backup_dir)

                if backup_result['success']:
                    stats['backup_created'] = True
                    stats['backup_path'] = backup_result['path']
                    stats['backup_size_mb'] = backup_result['size_mb']
                    logger.info(f"✓ Backup created: {backup_result['path']}")
                else:
                    logger.warning(f"⚠ Backup failed: {backup_result['message']}")
                    stats['errors'].append(f"Backup warning: {backup_result['message']}")
                    # Continue with migration even if backup fails (user chose auto_backup=True)
            else:
                logger.info("Skipping backup (auto_backup=False)")

            # Create target database with schema if requested
            if create_target:
                logger.info(f"Creating target database with schema...")
                from pyarchinit_mini.database.database_creator import create_empty_database

                # Determine target database type
                if target_db_url.startswith('sqlite:///'):
                    # Extract path from SQLite URL
                    db_path = target_db_url.replace('sqlite:///', '')
                    if not db_path.startswith('/'):
                        db_path = '/' + db_path

                    create_result = create_empty_database('sqlite', db_path, overwrite=overwrite_target)
                    if not create_result['success']:
                        raise RuntimeError(f"Failed to create target SQLite database: {create_result['message']}")

                elif target_db_url.startswith('postgresql'):
                    # Parse PostgreSQL URL: postgresql://user:pass@host:port/database
                    from sqlalchemy.engine.url import make_url
                    url = make_url(target_db_url)

                    pg_config = {
                        'host': url.host or 'localhost',
                        'port': url.port or 5432,
                        'database': url.database,
                        'username': url.username,
                        'password': url.password or ''
                    }

                    create_result = create_empty_database('postgresql', pg_config, overwrite=overwrite_target)
                    if not create_result['success']:
                        raise RuntimeError(f"Failed to create target PostgreSQL database: {create_result['message']}")
                else:
                    raise ValueError(f"Unsupported target database type: {target_db_url}")

                logger.info(f"Target database created with {create_result['tables_created']} tables")

            # Connect to both databases
            source_engine = create_engine(source_db_url)
            target_engine = create_engine(target_db_url)

            source_session_maker = sessionmaker(bind=source_engine)
            target_session_maker = sessionmaker(bind=target_engine)

            # Get list of tables to migrate (in correct order to handle foreign keys)
            # Order matters: create tables without dependencies first
            tables_order = [
                'users_table',
                'site_table',
                'datazioni_table',
                'us_table',
                'us_relationships_table',
                'periodizzazione_table',
                'inventario_materiali_table',
                'pyarchinit_thesaurus_sigle',
                'media_table',
                'harris_matrix_table',
                'periods_table',
                'extended_matrix_nodes_table'
            ]

            # Migrate each table
            for table_name in tables_order:
                try:
                    rows_copied = ImportExportService._migrate_table(
                        table_name,
                        source_session_maker,
                        target_session_maker,
                        merge_strategy=merge_strategy
                    )

                    if rows_copied > 0:
                        stats['tables_migrated'] += 1
                        stats['total_rows_copied'] += rows_copied
                        stats['rows_per_table'][table_name] = rows_copied
                        logger.info(f"✓ Migrated {table_name}: {rows_copied} rows")
                    else:
                        logger.info(f"○ Skipped {table_name}: empty or not found")

                except Exception as e:
                    error_msg = f"Error migrating table {table_name}: {str(e)}"
                    logger.error(error_msg)
                    stats['errors'].append(error_msg)
                    # Continue with other tables even if one fails

            # Reset PostgreSQL sequences after migration
            if target_db_url.startswith('postgresql'):
                logger.info("Resetting PostgreSQL sequences...")
                sequence_stats = ImportExportService._reset_postgresql_sequences(target_engine)
                logger.info(f"Reset {sequence_stats['sequences_reset']} sequences")
                if sequence_stats['errors']:
                    stats['errors'].extend(sequence_stats['errors'])

            stats['success'] = stats['tables_migrated'] > 0
            stats['duration_seconds'] = time.time() - start_time

            logger.info(f"Migration complete: {stats['tables_migrated']} tables, {stats['total_rows_copied']} rows in {stats['duration_seconds']:.2f}s")

            return stats

        except Exception as e:
            logger.error(f"Database migration failed: {str(e)}")
            stats['errors'].append(str(e))
            stats['duration_seconds'] = time.time() - start_time
            return stats

    @staticmethod
    def _create_backup(db_url: str, backup_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a backup of a database before migration

        Args:
            db_url: Database connection string
            backup_dir: Optional directory for backup (defaults to same dir as source)

        Returns:
            Dictionary with backup info: {'success': bool, 'path': str, 'size_mb': float, 'message': str}
        """
        result = {
            'success': False,
            'path': None,
            'size_mb': 0.0,
            'message': ''
        }

        try:
            # SQLite backup
            if db_url.startswith('sqlite:///'):
                # Extract file path from connection string
                db_path = db_url.replace('sqlite:///', '')

                # Handle absolute paths (start with /)
                if not db_path.startswith('/'):
                    db_path = '/' + db_path

                if not os.path.exists(db_path):
                    result['message'] = f"Source database file not found: {db_path}"
                    return result

                # Create backup with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

                if backup_dir:
                    os.makedirs(backup_dir, exist_ok=True)
                    backup_filename = os.path.basename(db_path)
                    backup_path = os.path.join(backup_dir, f"{backup_filename}.backup_{timestamp}")
                else:
                    backup_path = f"{db_path}.backup_{timestamp}"

                shutil.copy2(db_path, backup_path)
                file_size = os.path.getsize(backup_path) / (1024 * 1024)  # MB

                result['success'] = True
                result['path'] = backup_path
                result['size_mb'] = round(file_size, 2)
                result['message'] = f"SQLite backup created ({result['size_mb']} MB)"
                logger.info(f"✓ Database backup: {backup_path} ({result['size_mb']} MB)")

            # PostgreSQL backup
            elif db_url.startswith('postgresql'):
                import subprocess
                from sqlalchemy.engine.url import make_url

                # Parse connection URL
                url = make_url(db_url)
                host = url.host or 'localhost'
                port = url.port or 5432
                database = url.database
                user = url.username
                password = url.password

                # Create backup file path
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

                if backup_dir:
                    os.makedirs(backup_dir, exist_ok=True)
                    backup_path = os.path.join(backup_dir, f"{database}_backup_{timestamp}.sql")
                else:
                    backup_path = f"{database}_backup_{timestamp}.sql"

                # Set password environment variable
                env = os.environ.copy()
                if password:
                    env['PGPASSWORD'] = password

                # Run pg_dump
                cmd = [
                    'pg_dump',
                    '-h', host,
                    '-p', str(port),
                    '-U', user,
                    '-F', 'p',  # Plain SQL format
                    '-f', backup_path,
                    database
                ]

                pg_result = subprocess.run(cmd, env=env, capture_output=True, text=True)

                if pg_result.returncode == 0:
                    file_size = os.path.getsize(backup_path) / (1024 * 1024)  # MB
                    result['success'] = True
                    result['path'] = backup_path
                    result['size_mb'] = round(file_size, 2)
                    result['message'] = f"PostgreSQL backup created ({result['size_mb']} MB)"
                    logger.info(f"✓ PostgreSQL backup: {backup_path} ({result['size_mb']} MB)")
                else:
                    result['message'] = f"pg_dump failed: {pg_result.stderr}"
                    logger.error(result['message'])
            else:
                result['message'] = f"Unsupported database type for backup: {db_url}"

        except Exception as e:
            result['message'] = f"Backup failed: {str(e)}"
            logger.error(result['message'])

        return result

    @staticmethod
    def _detect_conflicts(source_db_url: str, target_db_url: str) -> Dict[str, Any]:
        """
        Detect conflicts between source and target databases before migration

        Analyzes both databases to find:
        - Duplicate IDs (primary key conflicts)
        - New records that don't exist in target
        - Records that exist in both databases

        Args:
            source_db_url: Source database connection string
            target_db_url: Target database connection string

        Returns:
            Dictionary with conflict analysis:
            {
                'has_conflicts': bool,
                'total_conflicts': int,
                'total_new_records': int,
                'tables': {
                    'table_name': {
                        'conflicts': int,
                        'new_records': int,
                        'conflicting_ids': [list of IDs],
                        'exists_in_target': bool
                    }
                }
            }
        """
        result = {
            'has_conflicts': False,
            'total_conflicts': 0,
            'total_new_records': 0,
            'tables': {},
            'errors': []
        }

        try:
            # Connect to both databases
            source_engine = create_engine(source_db_url)
            target_engine = create_engine(target_db_url)

            source_session_maker = sessionmaker(bind=source_engine)
            target_session_maker = sessionmaker(bind=target_engine)

            # Tables to check (in same order as migration)
            tables_order = [
                'users_table',
                'site_table',
                'datazioni_table',
                'us_table',
                'us_relationships_table',
                'periodizzazione_table',
                'inventario_materiali_table',
                'pyarchinit_thesaurus_sigle',
                'media_table',
                'harris_matrix_table',
                'periods_table',
                'extended_matrix_nodes_table'
            ]

            for table_name in tables_order:
                source_session = source_session_maker()
                target_session = target_session_maker()

                try:
                    # Get primary key column name for this table
                    inspector = inspect(source_engine)
                    pk_columns = inspector.get_pk_constraint(table_name).get('constrained_columns', [])

                    if not pk_columns:
                        logger.warning(f"No primary key found for {table_name}, skipping")
                        continue

                    pk_column = pk_columns[0]  # Use first PK column

                    # Check if table exists in source
                    try:
                        source_result = source_session.execute(text(f"SELECT {pk_column} FROM {table_name}"))
                        source_ids = set(row[0] for row in source_result.fetchall())
                    except Exception:
                        # Table doesn't exist in source or has no data
                        continue

                    if not source_ids:
                        continue  # Skip empty tables

                    # Check if table exists in target
                    target_ids = set()
                    table_exists_in_target = False
                    try:
                        target_result = target_session.execute(text(f"SELECT {pk_column} FROM {table_name}"))
                        target_ids = set(row[0] for row in target_result.fetchall())
                        table_exists_in_target = True
                    except Exception:
                        # Table doesn't exist in target or is empty - all records are new
                        table_exists_in_target = False

                    # Find conflicts (IDs that exist in both)
                    conflicting_ids = source_ids & target_ids
                    new_ids = source_ids - target_ids

                    # Store results for this table
                    result['tables'][table_name] = {
                        'conflicts': len(conflicting_ids),
                        'new_records': len(new_ids),
                        'conflicting_ids': sorted(list(conflicting_ids)),
                        'exists_in_target': table_exists_in_target,
                        'total_source_records': len(source_ids)
                    }

                    # Update totals
                    result['total_conflicts'] += len(conflicting_ids)
                    result['total_new_records'] += len(new_ids)

                    if len(conflicting_ids) > 0:
                        result['has_conflicts'] = True
                        logger.info(f"⚠️  {table_name}: {len(conflicting_ids)} conflicts, {len(new_ids)} new")
                    else:
                        logger.info(f"✓ {table_name}: {len(new_ids)} new records, no conflicts")

                except Exception as e:
                    error_msg = f"Error analyzing {table_name}: {str(e)}"
                    logger.error(error_msg)
                    result['errors'].append(error_msg)
                finally:
                    source_session.close()
                    target_session.close()

            logger.info(f"Conflict detection complete: {result['total_conflicts']} conflicts, {result['total_new_records']} new records")

        except Exception as e:
            error_msg = f"Conflict detection failed: {str(e)}"
            logger.error(error_msg)
            result['errors'].append(error_msg)

        return result

    @staticmethod
    def _reset_postgresql_sequences(target_engine) -> Dict[str, Any]:
        """
        Reset PostgreSQL sequences to max(id) + 1 after migration

        This fixes the issue where sequences are not updated during data migration,
        causing IntegrityError when inserting new records.

        Args:
            target_engine: Target database engine

        Returns:
            Dictionary with reset statistics
        """
        stats = {'sequences_reset': 0, 'errors': []}

        # Only reset if target is PostgreSQL
        if not str(target_engine.url).startswith('postgresql'):
            return stats

        # Define tables with auto-increment primary keys (SERIAL columns)
        # Format: (table_name, id_column_name, sequence_name)
        sequences = [
            ('site_table', 'id_sito', 'site_table_id_sito_seq'),
            ('inventario_materiali_table', 'id_invmat', 'inventario_materiali_table_id_invmat_seq'),
            ('media_table', 'id_media', 'media_table_id_media_seq'),
            ('users_table', 'id_user', 'users_table_id_user_seq'),
            ('datazioni_table', 'id_datazione', 'datazioni_table_id_datazione_seq'),
            ('periodizzazione_table', 'id_periodizzazione', 'periodizzazione_table_id_periodizzazione_seq'),
            ('us_relationships_table', 'id_relationship', 'us_relationships_table_id_relationship_seq'),
            ('pyarchinit_thesaurus_sigle', 'id_thesaurus_sigle', 'pyarchinit_thesaurus_sigle_id_thesaurus_sigle_seq'),
            ('harris_matrix_table', 'id_matrix', 'harris_matrix_table_id_matrix_seq'),
            ('periods_table', 'id', 'periods_table_id_seq'),
            ('extended_matrix_nodes_table', 'id', 'extended_matrix_nodes_table_id_seq'),
        ]

        with target_engine.connect() as conn:
            for table_name, id_column, sequence_name in sequences:
                try:
                    # Get max ID from table
                    result = conn.execute(text(f"SELECT MAX({id_column}) FROM {table_name}"))
                    max_id = result.scalar()

                    if max_id is not None:
                        # Reset sequence to max_id + 1
                        conn.execute(text(f"SELECT setval('{sequence_name}', :max_id, true)"), {'max_id': max_id})
                        conn.commit()
                        stats['sequences_reset'] += 1
                        logger.info(f"Reset sequence {sequence_name} to {max_id + 1}")

                except Exception as e:
                    error_msg = f"Failed to reset sequence for {table_name}: {str(e)}"
                    logger.warning(error_msg)
                    stats['errors'].append(error_msg)
                    # Continue with other sequences

        return stats

    @staticmethod
    def _convert_boolean_fields(table_name: str, row_data: Dict[str, Any],
                                 target_engine) -> Dict[str, Any]:
        """
        Convert integer boolean values (0/1) to Python boolean (False/True) for PostgreSQL

        Args:
            table_name: Name of the table
            row_data: Row data dictionary
            target_engine: Target database engine

        Returns:
            Row data with converted boolean fields
        """
        # Only convert if target is PostgreSQL
        if not str(target_engine.url).startswith('postgresql'):
            return row_data

        # Define boolean columns for each table
        boolean_columns = {
            'site_table': ['find_check'],
            'media_table': ['is_primary', 'is_public'],
            'harris_matrix_table': ['is_final', 'is_public'],
            'users_table': ['is_active', 'is_superuser']
        }

        # Get boolean columns for this table
        bool_cols = boolean_columns.get(table_name, [])

        # Convert integer values to boolean
        converted_data = row_data.copy()
        for col in bool_cols:
            if col in converted_data and converted_data[col] is not None:
                # Convert 0/1 to False/True
                if isinstance(converted_data[col], int):
                    converted_data[col] = bool(converted_data[col])

        return converted_data

    @staticmethod
    def _migrate_table(table_name: str, source_session_maker, target_session_maker,
                      merge_strategy: str = 'skip') -> int:
        """
        Migrate data from one table to another with conflict resolution

        Args:
            table_name: Name of the table to migrate
            source_session_maker: Source database session maker
            target_session_maker: Target database session maker
            merge_strategy: How to handle ID conflicts: 'skip', 'overwrite', or 'renumber'

        Returns:
            Number of rows copied/updated
        """
        source_session = source_session_maker()
        target_session = target_session_maker()

        rows_processed = 0
        rows_skipped = 0
        rows_updated = 0
        rows_renumbered = 0

        try:
            # Check if table exists in source
            try:
                source_session.execute(text(f"SELECT 1 FROM {table_name} LIMIT 1"))
            except Exception:
                # Table doesn't exist in source, skip it
                return 0

            # Get primary key column for this table
            from sqlalchemy import inspect
            source_engine = source_session.get_bind()
            inspector = inspect(source_engine)
            pk_columns = inspector.get_pk_constraint(table_name).get('constrained_columns', [])

            if not pk_columns:
                logger.warning(f"No primary key found for {table_name}, using simple INSERT strategy")
                pk_column = None
            else:
                pk_column = pk_columns[0]  # Use first PK column
                logger.debug(f"Using primary key column '{pk_column}' for {table_name}")

            # Get all rows from source table
            result = source_session.execute(text(f"SELECT * FROM {table_name}"))
            rows = result.fetchall()

            if not rows:
                return 0

            # Get column names
            column_names = list(rows[0]._mapping.keys())

            # Get target engine for boolean conversion
            target_engine = target_session.get_bind()

            # Get existing IDs in target (for conflict detection)
            existing_ids = set()
            if pk_column:
                try:
                    existing_result = target_session.execute(
                        text(f"SELECT {pk_column} FROM {table_name}")
                    )
                    existing_ids = {row[0] for row in existing_result.fetchall()}
                    logger.debug(f"Found {len(existing_ids)} existing records in target {table_name}")
                except Exception:
                    # Target table might be empty or not exist
                    existing_ids = set()

            # Find max ID in target (for renumber strategy)
            max_id = 0
            if pk_column and merge_strategy == 'renumber':
                try:
                    max_result = target_session.execute(
                        text(f"SELECT MAX({pk_column}) FROM {table_name}")
                    )
                    max_id = max_result.scalar() or 0
                    logger.debug(f"Max ID in target {table_name}: {max_id}")
                except Exception:
                    max_id = 0

            # Process each row
            for row in rows:
                row_data = dict(row._mapping)

                # Convert boolean fields if needed (SQLite -> PostgreSQL)
                row_data = ImportExportService._convert_boolean_fields(
                    table_name, row_data, target_engine
                )

                # Check for conflict
                record_id = row_data.get(pk_column) if pk_column else None
                has_conflict = pk_column and record_id in existing_ids

                try:
                    if has_conflict:
                        # Handle conflict based on strategy
                        if merge_strategy == 'skip':
                            # Skip this record
                            rows_skipped += 1
                            logger.debug(f"Skipping {table_name} ID {record_id} (already exists)")
                            continue

                        elif merge_strategy == 'overwrite':
                            # Update existing record
                            set_clause = ', '.join([f"{col} = :{col}" for col in column_names if col != pk_column])
                            update_query = text(f"""
                                UPDATE {table_name}
                                SET {set_clause}
                                WHERE {pk_column} = :_pk_value
                            """)

                            # Add PK value for WHERE clause
                            update_params = row_data.copy()
                            update_params['_pk_value'] = record_id

                            target_session.execute(update_query, update_params)
                            rows_updated += 1
                            rows_processed += 1
                            logger.debug(f"Updated {table_name} ID {record_id}")

                        elif merge_strategy == 'renumber':
                            # Generate new ID and insert
                            max_id += 1
                            row_data[pk_column] = max_id
                            existing_ids.add(max_id)  # Track new ID

                            # Build INSERT query
                            columns = ', '.join(column_names)
                            placeholders = ', '.join([f':{col}' for col in column_names])
                            insert_query = text(f"""
                                INSERT INTO {table_name} ({columns})
                                VALUES ({placeholders})
                            """)

                            target_session.execute(insert_query, row_data)
                            rows_renumbered += 1
                            rows_processed += 1
                            logger.debug(f"Renumbered {table_name} ID {record_id} -> {max_id}")

                    else:
                        # No conflict, insert normally
                        columns = ', '.join(column_names)
                        placeholders = ', '.join([f':{col}' for col in column_names])
                        insert_query = text(f"""
                            INSERT INTO {table_name} ({columns})
                            VALUES ({placeholders})
                        """)

                        target_session.execute(insert_query, row_data)
                        rows_processed += 1

                        # Track new ID if applicable
                        if pk_column and record_id:
                            existing_ids.add(record_id)

                except Exception as e:
                    # Log error but continue with other rows
                    logger.warning(f"Failed to process row in {table_name}: {str(e)}")
                    target_session.rollback()
                    continue

            # Commit all changes for this table
            target_session.commit()

            # Log summary
            if rows_skipped > 0 or rows_updated > 0 or rows_renumbered > 0:
                logger.info(
                    f"{table_name} merge summary: "
                    f"{rows_processed} processed, "
                    f"{rows_skipped} skipped, "
                    f"{rows_updated} updated, "
                    f"{rows_renumbered} renumbered"
                )

            return rows_processed

        except Exception as e:
            target_session.rollback()
            logger.error(f"Error migrating table {table_name}: {str(e)}")
            raise
        finally:
            source_session.close()
            target_session.close()
