"""
PyArchInit Import/Export Routes for Web Interface
"""

from flask import Blueprint, render_template, request, jsonify, session, current_app
from flask_babel import gettext as _
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

pyarchinit_import_export_bp = Blueprint('pyarchinit_import_export', __name__)


@pyarchinit_import_export_bp.route('/')
def index():
    """Main import/export page"""
    return render_template('pyarchinit_import_export/index.html')


@pyarchinit_import_export_bp.route('/api/pyarchinit/browse-files', methods=['POST'])
def browse_files():
    """Browse filesystem for SQLite database files"""
    try:
        data = request.get_json()
        if data is None:
            logger.error("File browser: No JSON data received")
            return jsonify({
                'success': False,
                'message': _('Invalid request: no JSON data')
            }), 400

        requested_path = data.get('path', '')

        # If empty or None, use home directory
        if not requested_path or requested_path.strip() == '':
            current_path = os.path.expanduser('~')
        else:
            current_path = requested_path

        # Security: expand and normalize path
        current_path = os.path.abspath(os.path.expanduser(current_path))

        logger.info(f"File browser requested path: {requested_path} -> normalized: {current_path}")

        # Security: prevent access to sensitive directories
        forbidden_paths = ['/etc', '/var', '/sys', '/proc', '/root']
        if any(current_path.startswith(forbidden) for forbidden in forbidden_paths):
            return jsonify({
                'success': False,
                'message': _('Access to this directory is not allowed')
            }), 403

        # Check if path exists
        if not os.path.exists(current_path):
            logger.warning(f"File browser: Path does not exist: {current_path}")
            return jsonify({
                'success': False,
                'message': _('Path does not exist') + f': {current_path}'
            }), 404

        # Check if path is a directory
        if not os.path.isdir(current_path):
            logger.warning(f"File browser: Path is not a directory: {current_path}")
            return jsonify({
                'success': False,
                'message': _('Path is not a directory') + f': {current_path}'
            }), 400

        # List directory contents
        items = []

        try:
            for entry in os.scandir(current_path):
                try:
                    # Get file info
                    stat_info = entry.stat()

                    # Determine if it's a directory or SQLite file
                    is_dir = entry.is_dir()
                    is_sqlite = False

                    if not is_dir and entry.is_file():
                        # Check if it's a SQLite database file
                        ext = os.path.splitext(entry.name)[1].lower()
                        is_sqlite = ext in ['.db', '.sqlite', '.sqlite3', '.db3']

                    # Only include directories and SQLite files
                    if is_dir or is_sqlite:
                        items.append({
                            'name': entry.name,
                            'path': entry.path,
                            'is_dir': is_dir,
                            'is_sqlite': is_sqlite,
                            'size': stat_info.st_size if not is_dir else 0,
                            'modified': datetime.fromtimestamp(stat_info.st_mtime).isoformat()
                        })
                except (PermissionError, OSError):
                    # Skip files/directories we can't access
                    continue

            # Sort: directories first, then files, alphabetically
            items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))

            # Get parent directory
            parent_path = os.path.dirname(current_path) if current_path != '/' else None

            return jsonify({
                'success': True,
                'current_path': current_path,
                'parent_path': parent_path,
                'items': items
            })

        except PermissionError:
            return jsonify({
                'success': False,
                'message': _('Permission denied to access this directory')
            }), 403

    except Exception as e:
        logger.error(f"File browsing failed: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@pyarchinit_import_export_bp.route('/api/pyarchinit/test-connection', methods=['POST'])
def test_connection():
    """Test connection to PyArchInit database"""
    try:
        data = request.get_json()
        db_type = data.get('db_type', 'sqlite')

        # Build connection string
        if db_type == 'sqlite':
            db_path = data.get('db_path')
            if not db_path:
                return jsonify({'success': False, 'message': _('Please provide database path')}), 400

            # Expand user home directory if needed
            db_path = os.path.expanduser(db_path)

            # Convert to absolute path if relative
            if not os.path.isabs(db_path):
                db_path = os.path.abspath(db_path)

            # Check if file exists
            if not os.path.exists(db_path):
                return jsonify({'success': False, 'message': _('Database file not found') + f': {db_path}'}), 400

            # Build connection string (SQLite uses 4 slashes for absolute paths on Unix/Mac)
            # Format: sqlite:////absolute/path/to/file.db
            conn_string = f"sqlite:///{db_path}"
        else:  # PostgreSQL
            host = data.get('pg_host', 'localhost')
            port = data.get('pg_port', '5432')
            database = data.get('pg_database')
            user = data.get('pg_user')
            password = data.get('pg_password')

            if not all([host, port, database, user]):
                return jsonify({'success': False, 'message': _('Missing PostgreSQL connection details')}), 400

            conn_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"

        # Test connection
        from pyarchinit_mini.services.import_export_service import ImportExportService

        # Use CURRENT_DATABASE_URL to respect database switching
        mini_db_url = current_app.config.get('CURRENT_DATABASE_URL')
        if not mini_db_url:
            mini_db_url = current_app.config.get('DATABASE_URL', 'sqlite:///./pyarchinit_mini.db')
        service = ImportExportService(mini_db_url)

        if not service.validate_database_connection(conn_string):
            return jsonify({
                'success': False,
                'message': _('Failed to connect to database')
            }), 400

        # Get available sites
        service.set_source_database(conn_string)
        sites = service.get_available_sites_in_source()

        return jsonify({
            'success': True,
            'message': _('Connection successful'),
            'sites_count': len(sites),
            'sites': sites
        })

    except Exception as e:
        logger.error(f"Connection test failed: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@pyarchinit_import_export_bp.route('/api/pyarchinit/import', methods=['POST'])
def start_import():
    """Start import from PyArchInit database"""
    try:
        data = request.get_json()

        # Build connection string
        db_type = data.get('db_type', 'sqlite')
        if db_type == 'sqlite':
            db_path = data.get('db_path')
            if not db_path:
                return jsonify({'success': False, 'message': _('Please provide database path')}), 400

            # Expand user home directory and convert to absolute path
            db_path = os.path.abspath(os.path.expanduser(db_path))

            if not os.path.exists(db_path):
                return jsonify({'success': False, 'message': _('Database file not found') + f': {db_path}'}), 400

            conn_string = f"sqlite:///{db_path}"
        else:
            host = data.get('pg_host', 'localhost')
            port = data.get('pg_port', '5432')
            database = data.get('pg_database')
            user = data.get('pg_user')
            password = data.get('pg_password')
            conn_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"

        # Get options
        import_sites = data.get('import_sites', False)
        import_us = data.get('import_us', False)
        import_inventario = data.get('import_inventario', False)
        import_periodizzazione = data.get('import_periodizzazione', False)
        import_thesaurus = data.get('import_thesaurus', False)
        import_relationships = data.get('import_relationships', True)
        site_filter = data.get('site_filter', [])

        if not any([import_sites, import_us, import_inventario, import_periodizzazione, import_thesaurus]):
            return jsonify({
                'success': False,
                'message': _('Please select at least one table to import')
            }), 400

        # Initialize service
        from pyarchinit_mini.services.import_export_service import ImportExportService

        # Use CURRENT_DATABASE_URL to respect database switching
        mini_db_url = current_app.config.get('CURRENT_DATABASE_URL')
        if not mini_db_url:
            mini_db_url = current_app.config.get('DATABASE_URL', 'sqlite:///./pyarchinit_mini.db')

        logger.info(f"Importing to database: {mini_db_url}")
        service = ImportExportService(mini_db_url, conn_string)

        # Prepare site filter
        site_filter_list = site_filter if site_filter else None

        # Track results
        results = {}

        # Import sites
        if import_sites:
            logger.info("Importing sites...")
            stats = service.import_sites(site_filter_list)
            results['sites'] = stats

        # Import US
        if import_us:
            logger.info("Importing US...")
            stats = service.import_us(site_filter_list, import_relationships)
            results['us'] = stats

        # Import inventario
        if import_inventario:
            logger.info("Importing inventario...")
            stats = service.import_inventario(site_filter_list)
            results['inventario'] = stats

        # Import periodizzazione
        if import_periodizzazione:
            logger.info("Importing periodizzazione...")
            stats = service.import_periodizzazione(site_filter_list)
            results['periodizzazione'] = stats

            # Automatically sync datazioni from periodizzazione
            logger.info("Syncing datazioni from periodizzazione...")
            sync_stats = service.sync_datazioni_from_periodizzazione()
            results['datazioni_sync'] = sync_stats
            logger.info(f"Datazioni sync: {sync_stats['created']} created, {sync_stats['skipped']} skipped")

            # Automatically sync datazioni from US table values
            logger.info("Syncing datazioni from US table values...")
            us_sync_stats = service.sync_datazioni_from_us_values()
            results['us_values_sync'] = us_sync_stats
            logger.info(f"US values sync: {us_sync_stats['created']} created, {us_sync_stats['skipped']} skipped")

            # Automatically update US datazione field from periodizzazione
            logger.info("Updating US datazione from periodizzazione...")
            update_stats = service.update_us_datazione_from_periodizzazione(site_filter_list)
            results['us_datazione_update'] = update_stats
            logger.info(f"US datazione update: {update_stats['updated']} updated, {update_stats['skipped']} skipped")

        # Import thesaurus
        if import_thesaurus:
            logger.info("Importing thesaurus...")
            stats = service.import_thesaurus()
            results['thesaurus'] = stats

        return jsonify({
            'success': True,
            'message': _('Import completed successfully'),
            'results': results
        })

    except Exception as e:
        logger.error(f"Import failed: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@pyarchinit_import_export_bp.route('/api/pyarchinit/sync-datazioni', methods=['POST'])
def sync_datazioni():
    """Manually synchronize datazioni from periodizzazione data"""
    try:
        # Initialize service
        from pyarchinit_mini.services.import_export_service import ImportExportService

        # Use CURRENT_DATABASE_URL to respect database switching
        mini_db_url = current_app.config.get('CURRENT_DATABASE_URL')
        if not mini_db_url:
            mini_db_url = current_app.config.get('DATABASE_URL', 'sqlite:///./pyarchinit_mini.db')

        logger.info(f"Syncing datazioni for database: {mini_db_url}")
        service = ImportExportService(mini_db_url)

        # Get optional site filter
        data = request.get_json() or {}
        site_filter = data.get('site_filter', [])
        site_filter_list = site_filter if site_filter else None

        # Sync datazioni from periodizzazione
        logger.info("Syncing datazioni from periodizzazione...")
        sync_stats = service.sync_datazioni_from_periodizzazione()
        logger.info(f"Datazioni sync: {sync_stats['created']} created, {sync_stats['skipped']} skipped")

        # Sync datazioni from US table values (ensures all US datazione values are available in dropdown)
        logger.info("Syncing datazioni from US table values...")
        us_sync_stats = service.sync_datazioni_from_us_values()
        logger.info(f"US values sync: {us_sync_stats['created']} created, {us_sync_stats['skipped']} skipped")

        # Update US datazione field from periodizzazione
        logger.info("Updating US datazione from periodizzazione...")
        update_stats = service.update_us_datazione_from_periodizzazione(site_filter_list)
        logger.info(f"US datazione update: {update_stats['updated']} updated, {update_stats['skipped']} skipped")

        return jsonify({
            'success': True,
            'message': _('Datazioni synchronized successfully'),
            'results': {
                'datazioni_sync': sync_stats,
                'us_values_sync': us_sync_stats,
                'us_datazione_update': update_stats
            }
        })

    except Exception as e:
        logger.error(f"Datazioni sync failed: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@pyarchinit_import_export_bp.route('/api/pyarchinit/export', methods=['POST'])
def start_export():
    """Start export to PyArchInit database"""
    try:
        data = request.get_json()

        # Build connection string for target database
        db_type = data.get('db_type', 'sqlite')
        if db_type == 'sqlite':
            db_path = data.get('db_path')
            if not db_path:
                return jsonify({'success': False, 'message': _('Please specify database path')}), 400

            # Expand user home directory and convert to absolute path
            db_path = os.path.abspath(os.path.expanduser(db_path))

            target_conn_string = f"sqlite:///{db_path}"
        else:
            host = data.get('pg_host', 'localhost')
            port = data.get('pg_port', '5432')
            database = data.get('pg_database')
            user = data.get('pg_user')
            password = data.get('pg_password')
            target_conn_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"

        # Get options
        export_sites = data.get('export_sites', False)
        export_us = data.get('export_us', False)
        export_relationships = data.get('export_relationships', True)
        site_filter = data.get('site_filter', [])

        if not any([export_sites, export_us]):
            return jsonify({
                'success': False,
                'message': _('Please select at least one table to export')
            }), 400

        # Initialize service
        from pyarchinit_mini.services.import_export_service import ImportExportService

        # Use CURRENT_DATABASE_URL to respect database switching
        mini_db_url = current_app.config.get('CURRENT_DATABASE_URL')
        if not mini_db_url:
            mini_db_url = current_app.config.get('DATABASE_URL', 'sqlite:///./pyarchinit_mini.db')

        logger.info(f"Exporting from database: {mini_db_url}")
        service = ImportExportService(mini_db_url)

        # Prepare site filter
        site_filter_list = site_filter if site_filter else None

        # Track results
        results = {}

        # Export sites
        if export_sites:
            logger.info("Exporting sites...")
            stats = service.export_sites(target_conn_string, site_filter_list)
            results['sites'] = stats

        # Export US
        if export_us:
            logger.info("Exporting US...")
            stats = service.export_us(target_conn_string, site_filter_list, export_relationships)
            results['us'] = stats

        return jsonify({
            'success': True,
            'message': _('Export completed successfully'),
            'results': results
        })

    except Exception as e:
        logger.error(f"Export failed: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@pyarchinit_import_export_bp.route('/api/pyarchinit/create-database', methods=['POST'])
def create_database():
    """Create empty PyArchInit database with full schema"""
    try:
        data = request.get_json()
        db_type = data.get('db_type', 'sqlite')
        overwrite = data.get('overwrite', False)
        use_default_path = data.get('use_default_path', False)

        from pyarchinit_mini.database.database_creator import create_empty_database

        if db_type == 'sqlite':
            db_path = data.get('db_path')

            # If use_default_path is True, allow empty db_path
            if not db_path and not use_default_path:
                return jsonify({'success': False, 'message': _('Please provide database path')}), 400

            # If db_path is provided but use_default_path is True, just use the filename
            if db_path and not use_default_path:
                # Expand user home directory and convert to absolute path
                db_path = os.path.abspath(os.path.expanduser(db_path))

            logger.info(f"Creating empty SQLite database (use_default_path={use_default_path})")
            result = create_empty_database('sqlite', db_path, overwrite=overwrite, use_default_path=use_default_path)

        else:  # PostgreSQL
            host = data.get('pg_host', 'localhost')
            port = data.get('pg_port', '5432')
            database = data.get('pg_database')
            user = data.get('pg_user')
            password = data.get('pg_password')

            if not all([host, port, database, user]):
                return jsonify({'success': False, 'message': _('Missing PostgreSQL connection details')}), 400

            config = {
                'host': host,
                'port': int(port),
                'database': database,
                'username': user,
                'password': password or ''
            }

            logger.info(f"Creating empty PostgreSQL database: {database} on {host}:{port}")
            result = create_empty_database('postgresql', config, overwrite=overwrite)

        return jsonify({
            'success': True,
            'message': result['message'],
            'tables_created': result['tables_created'],
            'db_type': result['db_type']
        })

    except FileExistsError as e:
        return jsonify({
            'success': False,
            'message': _('Database already exists. Enable overwrite to replace it.')
        }), 400
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': _('Database already exists. Enable overwrite to replace it.')
        }), 400
    except Exception as e:
        logger.error(f"Database creation failed: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@pyarchinit_import_export_bp.route('/api/pyarchinit/preview-migration-conflicts', methods=['POST'])
def preview_migration_conflicts():
    """Preview conflicts between source and target databases before migration"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'message': _('Invalid request: no JSON data')}), 400

        # Get source database URL (same logic as migrate_database)
        source_type = data.get('source_type')

        if source_type == 'current':
            source_db_url = current_app.config.get('CURRENT_DATABASE_URL')
            if not source_db_url:
                source_db_url = current_app.config.get('DATABASE_URL', 'sqlite:///./pyarchinit_mini.db')
        else:
            source_db_type = data.get('source_db_type', 'sqlite')

            if source_db_type == 'sqlite':
                source_db_path = data.get('source_db_path')
                if not source_db_path:
                    return jsonify({'success': False, 'message': _('Please provide source database path')}), 400

                source_db_path = os.path.abspath(os.path.expanduser(source_db_path))
                if not os.path.exists(source_db_path):
                    return jsonify({'success': False, 'message': _('Source database file not found') + f': {source_db_path}'}), 400

                source_db_url = f"sqlite:///{source_db_path}"
            else:  # PostgreSQL
                source_host = data.get('source_pg_host', 'localhost')
                source_port = data.get('source_pg_port', '5432')
                source_database = data.get('source_pg_database')
                source_user = data.get('source_pg_user')
                source_password = data.get('source_pg_password')

                if not all([source_host, source_port, source_database, source_user]):
                    return jsonify({'success': False, 'message': _('Missing source PostgreSQL connection details')}), 400

                source_db_url = f"postgresql://{source_user}:{source_password}@{source_host}:{source_port}/{source_database}"

        # Get target database details
        target_db_type = data.get('target_db_type', 'sqlite')

        if target_db_type == 'sqlite':
            target_db_path = data.get('target_db_path')
            if not target_db_path:
                return jsonify({'success': False, 'message': _('Please provide target database path')}), 400

            use_default_path = data.get('use_default_path', False)
            if not use_default_path:
                target_db_path = os.path.abspath(os.path.expanduser(target_db_path))

            target_db_url = f"sqlite:///{target_db_path}"
        else:  # PostgreSQL
            target_host = data.get('target_pg_host', 'localhost')
            target_port = data.get('target_pg_port', '5432')
            target_database = data.get('target_pg_database')
            target_user = data.get('target_pg_user')
            target_password = data.get('target_pg_password')

            if not all([target_host, target_port, target_database, target_user]):
                return jsonify({'success': False, 'message': _('Missing target PostgreSQL connection details')}), 400

            target_db_url = f"postgresql://{target_user}:{target_password}@{target_host}:{target_port}/{target_database}"

        # Detect conflicts
        from pyarchinit_mini.services.import_export_service import ImportExportService

        logger.info(f"Analyzing conflicts between databases: {source_db_url} → {target_db_url}")

        conflicts = ImportExportService._detect_conflicts(source_db_url, target_db_url)

        return jsonify({
            'success': True,
            'has_conflicts': conflicts['has_conflicts'],
            'total_conflicts': conflicts['total_conflicts'],
            'total_new_records': conflicts['total_new_records'],
            'tables': conflicts['tables'],
            'errors': conflicts['errors']
        })

    except Exception as e:
        logger.error(f"Error previewing migration conflicts: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': _('Failed to analyze conflicts') + f': {str(e)}'
        }), 500


@pyarchinit_import_export_bp.route('/api/pyarchinit/migrate-database', methods=['POST'])
def migrate_database():
    """Migrate all data from source database to target database (SQLite ↔ PostgreSQL)"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'success': False, 'message': _('Invalid request: no JSON data')}), 400

        # Get source database URL (current database)
        source_type = data.get('source_type')  # 'current' or 'custom'

        if source_type == 'current':
            # Use current active database as source
            source_db_url = current_app.config.get('CURRENT_DATABASE_URL')
            if not source_db_url:
                source_db_url = current_app.config.get('DATABASE_URL', 'sqlite:///./pyarchinit_mini.db')
        else:
            # Build custom source connection string
            source_db_type = data.get('source_db_type', 'sqlite')

            if source_db_type == 'sqlite':
                source_db_path = data.get('source_db_path')
                if not source_db_path:
                    return jsonify({'success': False, 'message': _('Please provide source database path')}), 400

                source_db_path = os.path.abspath(os.path.expanduser(source_db_path))
                if not os.path.exists(source_db_path):
                    return jsonify({'success': False, 'message': _('Source database file not found') + f': {source_db_path}'}), 400

                source_db_url = f"sqlite:///{source_db_path}"
            else:  # PostgreSQL
                source_host = data.get('source_pg_host', 'localhost')
                source_port = data.get('source_pg_port', '5432')
                source_database = data.get('source_pg_database')
                source_user = data.get('source_pg_user')
                source_password = data.get('source_pg_password')

                if not all([source_host, source_port, source_database, source_user]):
                    return jsonify({'success': False, 'message': _('Missing source PostgreSQL connection details')}), 400

                source_db_url = f"postgresql://{source_user}:{source_password}@{source_host}:{source_port}/{source_database}"

        # Get target database details
        target_db_type = data.get('target_db_type', 'sqlite')

        if target_db_type == 'sqlite':
            target_db_path = data.get('target_db_path')
            if not target_db_path:
                return jsonify({'success': False, 'message': _('Please provide target database path')}), 400

            # Handle default path option
            use_default_path = data.get('use_default_path', False)
            if not use_default_path:
                target_db_path = os.path.abspath(os.path.expanduser(target_db_path))

            target_db_url = f"sqlite:///{target_db_path}"
        else:  # PostgreSQL
            target_host = data.get('target_pg_host', 'localhost')
            target_port = data.get('target_pg_port', '5432')
            target_database = data.get('target_pg_database')
            target_user = data.get('target_pg_user')
            target_password = data.get('target_pg_password')

            if not all([target_host, target_port, target_database, target_user]):
                return jsonify({'success': False, 'message': _('Missing target PostgreSQL connection details')}), 400

            target_db_url = f"postgresql://{target_user}:{target_password}@{target_host}:{target_port}/{target_database}"

        # Get options
        overwrite_target = data.get('overwrite_target', False)
        merge_strategy = data.get('merge_strategy', 'skip')  # 'skip', 'overwrite', or 'renumber'
        auto_backup = data.get('auto_backup', True)

        # Validate merge_strategy
        if merge_strategy not in ['skip', 'overwrite', 'renumber']:
            return jsonify({
                'success': False,
                'message': _('Invalid merge strategy. Must be: skip, overwrite, or renumber')
            }), 400

        # Perform migration
        from pyarchinit_mini.services.import_export_service import ImportExportService

        logger.info(f"Starting database migration: {source_db_url} → {target_db_url} (strategy: {merge_strategy})")

        result = ImportExportService.migrate_database(
            source_db_url=source_db_url,
            target_db_url=target_db_url,
            create_target=True,
            overwrite_target=overwrite_target,
            auto_backup=auto_backup,
            merge_strategy=merge_strategy
        )

        if result['success']:
            return jsonify({
                'success': True,
                'message': _('Database migration completed successfully'),
                'tables_migrated': result['tables_migrated'],
                'total_rows_copied': result['total_rows_copied'],
                'rows_per_table': result['rows_per_table'],
                'duration_seconds': result['duration_seconds'],
                'backup_created': result.get('backup_created', False),
                'backup_path': result.get('backup_path'),
                'backup_size_mb': result.get('backup_size_mb', 0.0),
                'errors': result['errors']
            })
        else:
            return jsonify({
                'success': False,
                'message': _('Database migration failed'),
                'errors': result['errors']
            }), 500

    except Exception as e:
        logger.error(f"Database migration failed: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


# ============================================================
# Saved Connections Management
# ============================================================

@pyarchinit_import_export_bp.route('/api/connections/list', methods=['GET'])
def list_saved_connections():
    """Get list of all saved database connections"""
    try:
        from pyarchinit_mini.config.connection_manager import get_connection_manager

        conn_manager = get_connection_manager()
        connections = conn_manager.list_connections()

        return jsonify({
            'success': True,
            'connections': connections,
            'count': len(connections)
        })

    except Exception as e:
        logger.error(f"Failed to list connections: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@pyarchinit_import_export_bp.route('/api/connections/add', methods=['POST'])
def add_saved_connection():
    """Save a new database connection"""
    try:
        data = request.get_json()

        name = data.get('name', '').strip()
        db_type = data.get('db_type', '').strip()
        description = data.get('description', '').strip()

        # Build connection string based on type
        if db_type == 'sqlite':
            db_path = data.get('db_path', '').strip()
            if not db_path:
                return jsonify({
                    'success': False,
                    'message': _('Database path is required')
                }), 400

            # Expand user home directory
            db_path = os.path.expanduser(db_path)
            if not os.path.isabs(db_path):
                db_path = os.path.abspath(db_path)

            connection_string = f"sqlite:///{db_path}"

        elif db_type == 'postgresql':
            host = data.get('pg_host', 'localhost').strip()
            port = data.get('pg_port', '5432').strip()
            database = data.get('pg_database', '').strip()
            user = data.get('pg_user', '').strip()
            password = data.get('pg_password', '')

            if not all([host, port, database, user]):
                return jsonify({
                    'success': False,
                    'message': _('Missing PostgreSQL connection details')
                }), 400

            connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"

        else:
            return jsonify({
                'success': False,
                'message': _('Invalid database type')
            }), 400

        # Save connection
        from pyarchinit_mini.config.connection_manager import get_connection_manager

        conn_manager = get_connection_manager()
        result = conn_manager.add_connection(
            name=name,
            db_type=db_type,
            connection_string=connection_string,
            description=description
        )

        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400

    except Exception as e:
        logger.error(f"Failed to save connection: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@pyarchinit_import_export_bp.route('/api/connections/<connection_name>', methods=['GET'])
def get_saved_connection(connection_name):
    """Get connection string for a saved connection"""
    try:
        from pyarchinit_mini.config.connection_manager import get_connection_manager

        conn_manager = get_connection_manager()
        connection_string = conn_manager.get_connection_string(connection_name)

        if connection_string:
            return jsonify({
                'success': True,
                'connection_string': connection_string
            })
        else:
            return jsonify({
                'success': False,
                'message': _('Connection not found')
            }), 404

    except Exception as e:
        logger.error(f"Failed to get connection: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@pyarchinit_import_export_bp.route('/api/connections/<connection_name>', methods=['DELETE'])
def remove_saved_connection(connection_name):
    """Remove a saved connection"""
    try:
        from pyarchinit_mini.config.connection_manager import get_connection_manager

        conn_manager = get_connection_manager()
        result = conn_manager.remove_connection(connection_name)

        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 404

    except Exception as e:
        logger.error(f"Failed to remove connection: {str(e)}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
