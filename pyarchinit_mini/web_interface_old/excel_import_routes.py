"""
Excel Import Routes for Harris Matrix
Supports both Excel formats:
1. Harris Matrix Template (sheet-based with NODES + RELATIONSHIPS)
2. Extended Matrix Parser (inline with relationship columns)
"""

from flask import Blueprint, render_template, request, jsonify, session, current_app, send_file
from flask_babel import gettext as _
from werkzeug.utils import secure_filename
import os
import tempfile
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

excel_import_bp = Blueprint('excel_import', __name__)

# Allowed extensions
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv'}


def allowed_file(filename: str) -> bool:
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@excel_import_bp.route('/')
def index():
    """Excel import main page"""
    return render_template('excel_import/index.html')


@excel_import_bp.route('/api/import', methods=['POST'])
def import_excel():
    """
    Import Excel file using selected format

    Form data:
        - file: Excel file upload
        - format: 'harris_template' or 'extended_matrix'
        - site_name: Archaeological site name
        - generate_graphml: boolean (optional)
    """
    try:
        # Validate file upload
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': _('No file uploaded')
            }), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({
                'success': False,
                'message': _('No file selected')
            }), 400

        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'message': _('Invalid file format. Use .xlsx, .xls, or .csv')
            }), 400

        # Get form parameters
        import_format = request.form.get('format', 'harris_template')
        site_name = request.form.get('site_name', '').strip()
        generate_graphml = request.form.get('generate_graphml', 'false').lower() == 'true'

        if not site_name:
            return jsonify({
                'success': False,
                'message': _('Site name is required')
            }), 400

        # Save file temporarily
        temp_dir = tempfile.mkdtemp()
        filename = secure_filename(file.filename)
        filepath = os.path.join(temp_dir, filename)
        file.save(filepath)

        logger.info(f"Excel import: format={import_format}, site={site_name}, file={filename}")

        # Import based on format
        if import_format == 'harris_template':
            result = import_harris_template_format(filepath, site_name, generate_graphml, temp_dir)
        elif import_format == 'extended_matrix':
            result = import_extended_matrix_format(filepath, site_name, generate_graphml, temp_dir)
        else:
            return jsonify({
                'success': False,
                'message': _('Invalid import format')
            }), 400

        # Cleanup temp file
        try:
            os.remove(filepath)
        except:
            pass

        return jsonify(result)

    except Exception as e:
        logger.error(f"Excel import error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': _('Import failed') + f': {str(e)}'
        }), 500


def import_harris_template_format(filepath: str, site_name: str, generate_graphml: bool, temp_dir: str) -> Dict[str, Any]:
    """
    Import using Harris Matrix Template format (NODES + RELATIONSHIPS sheets)
    """
    from pyarchinit_mini.database.connection import DatabaseConnection
    from pyarchinit_mini.database.manager import DatabaseManager
    from pyarchinit_mini.cli.harris_import import HarrisMatrixImporter
    from pyarchinit_mini.models.base import BaseModel
    from flask import current_app
    import os

    # Use the SAME database as the main web interface
    db_url = current_app.config.get('CURRENT_DATABASE_URL')
    if not db_url:
        # Fallback: use project root database (same as app.py default)
        default_db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pyarchinit_mini.db')
        db_url = f"sqlite:///{default_db_path}"

    connection = DatabaseConnection.from_url(db_url)
    db_manager = DatabaseManager(connection)

    # Initialize database schema (create missing tables/columns)
    BaseModel.metadata.create_all(connection.engine)

    try:
        with db_manager.connection.get_session() as db_session:
            importer = HarrisMatrixImporter(db_session, db_manager)

            # Perform import
            success = importer.import_matrix(
                file_path=filepath,
                site_name=site_name,
                export_graphml=generate_graphml,
                export_dot=False,
                output_dir=temp_dir if generate_graphml else None
            )

            if not success:
                error_msgs = '\n'.join(importer.errors) if importer.errors else 'Unknown error'
                return {
                    'success': False,
                    'message': f'Import failed:\n{error_msgs}'
                }

            # Count imported data
            from pyarchinit_mini.models.us import US
            from pyarchinit_mini.models.harris_matrix import USRelationships

            us_count = db_session.query(US).filter_by(sito=site_name).count()
            rel_count = db_session.query(USRelationships).filter_by(sito=site_name).count()

            result = {
                'success': True,
                'message': _('Import completed successfully'),
                'statistics': {
                    'us_count': us_count,
                    'relationships_count': rel_count
                }
            }

            # Check for GraphML file
            if generate_graphml:
                graphml_path = os.path.join(temp_dir, f"{site_name.replace(' ', '_')}.graphml")
                if os.path.exists(graphml_path):
                    result['graphml_file'] = graphml_path
                    result['graphml_available'] = True

            return result

    except Exception as e:
        logger.error(f"Harris template import error: {str(e)}", exc_info=True)
        return {
            'success': False,
            'message': f'Import failed: {str(e)}'
        }


def import_extended_matrix_format(filepath: str, site_name: str, generate_graphml: bool, temp_dir: str) -> Dict[str, Any]:
    """
    Import using Extended Matrix Parser format (inline relationship columns)
    """
    from pyarchinit_mini.services.extended_matrix_excel_parser import import_extended_matrix_excel
    from pyarchinit_mini.database.connection import DatabaseConnection
    from pyarchinit_mini.models.base import BaseModel
    from flask import current_app
    import os

    # Use the SAME database as the main web interface
    db_url = current_app.config.get('CURRENT_DATABASE_URL')
    if not db_url:
        # Fallback: use project root database (same as app.py default)
        default_db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pyarchinit_mini.db')
        db_url = f"sqlite:///{default_db_path}"

    connection = DatabaseConnection.from_url(db_url)

    # Initialize database schema (create missing tables/columns)
    BaseModel.metadata.create_all(connection.engine)

    try:
        # Perform import with the same database connection
        stats = import_extended_matrix_excel(
            excel_path=filepath,
            site_name=site_name,
            generate_graphml=generate_graphml,
            db_connection=connection
        )

        if stats.get('errors'):
            error_msgs = '\n'.join(stats['errors'][:5])  # Show first 5 errors
            return {
                'success': False,
                'message': f'Import completed with errors:\n{error_msgs}',
                'statistics': stats
            }

        result = {
            'success': True,
            'message': _('Import completed successfully'),
            'statistics': {
                'us_created': stats.get('us_created', 0),
                'us_updated': stats.get('us_updated', 0),
                'relationships_created': stats.get('relationships_created', 0)
            }
        }

        # Check for GraphML file
        if generate_graphml and stats.get('graphml_path'):
            result['graphml_file'] = stats['graphml_path']
            result['graphml_available'] = True

        return result

    except Exception as e:
        logger.error(f"Extended matrix import error: {str(e)}", exc_info=True)
        return {
            'success': False,
            'message': f'Import failed: {str(e)}'
        }


@excel_import_bp.route('/api/download-graphml/<path:filename>')
def download_graphml(filename):
    """Download generated GraphML file"""
    try:
        # Security: only allow files from temp directory
        if not os.path.exists(filename) or '../' in filename:
            return jsonify({
                'success': False,
                'message': _('File not found')
            }), 404

        return send_file(
            filename,
            as_attachment=True,
            download_name=os.path.basename(filename),
            mimetype='application/graphml+xml'
        )

    except Exception as e:
        logger.error(f"GraphML download error: {str(e)}")
        return jsonify({
            'success': False,
            'message': _('Download failed')
        }), 500


@excel_import_bp.route('/api/generate-template', methods=['POST'])
def generate_template():
    """Generate Harris Matrix Template Excel file"""
    try:
        data = request.get_json()
        include_examples = data.get('include_examples', True)

        # Generate template using harris_template module
        import pandas as pd
        from pyarchinit_mini.cli.harris_template import create_template_data, create_instructions

        temp_dir = tempfile.mkdtemp()
        template_path = os.path.join(temp_dir, 'harris_matrix_template.xlsx')

        # Create template data
        if include_examples:
            nodes_df, relationships_df = create_template_data()
        else:
            nodes_df = pd.DataFrame({
                'us_number': [],
                'unit_type': [],
                'description': [],
                'area': [],
                'period': [],
                'phase': [],
                'file_path': []
            })
            relationships_df = pd.DataFrame({
                'from_us': [],
                'to_us': [],
                'relationship': [],
                'notes': []
            })

        instructions_df = create_instructions()

        # Write Excel file
        with pd.ExcelWriter(template_path, engine='openpyxl') as writer:
            instructions_df.to_excel(writer, sheet_name='INSTRUCTIONS', index=False)
            nodes_df.to_excel(writer, sheet_name='NODES', index=False)
            relationships_df.to_excel(writer, sheet_name='RELATIONSHIPS', index=False)

        return send_file(
            template_path,
            as_attachment=True,
            download_name='harris_matrix_template.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        logger.error(f"Template generation error: {str(e)}")
        return jsonify({
            'success': False,
            'message': _('Template generation failed') + f': {str(e)}'
        }), 500
