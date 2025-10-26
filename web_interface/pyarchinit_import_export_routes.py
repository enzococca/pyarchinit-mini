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

        mini_db_url = current_app.config.get('DATABASE_URL', 'sqlite:///./pyarchinit_mini.db')
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

        mini_db_url = current_app.config.get('DATABASE_URL', 'sqlite:///./pyarchinit_mini.db')
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
