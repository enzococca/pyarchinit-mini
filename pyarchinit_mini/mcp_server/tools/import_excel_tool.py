"""
Excel Import Tool

Imports archaeological data from Excel files in two formats:
1. Harris Matrix Template (NODES + RELATIONSHIPS sheets)
2. Extended Matrix Parser (inline relationship columns)
"""

import os
import tempfile
import base64
import logging
from typing import Dict, Any
from .base_tool import BaseTool, ToolDescription

logger = logging.getLogger(__name__)


class ImportExcelTool(BaseTool):
    """Excel Import Tool - Imports stratigraphic data from Excel files"""

    def __init__(self, db_session, config):
        """Initialize with db_session and config, create db_manager"""
        super().__init__(db_session, config)
        # Create db_manager from session's bind (engine)
        from pyarchinit_mini.database.manager import DatabaseManager
        from pyarchinit_mini.database.connection import DatabaseConnection
        # Get database URL from config or environment
        import os
        db_url = getattr(config, 'database_url', None) or os.getenv('DATABASE_URL', 'sqlite:///pyarchinit_mini.db')
        connection = DatabaseConnection.from_url(db_url)
        self.db_manager = DatabaseManager(connection)

    def to_tool_description(self) -> ToolDescription:
        return ToolDescription(
            name="import_excel",
            description=(
                "⚡ IMMEDIATE ACTION: Import Harris Matrix stratigraphic data from Excel. "
                "Automatically creates US records, relationships, and GraphML visualization. "
                "Supports 'harris_template' (NODES/RELATIONSHIPS sheets) and 'extended_matrix' (single sheet with relationship columns). "
                "DO NOT analyze or validate - call immediately. "
                "Use file_id from upload_file tool OR excel_base64 directly."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "format": {
                        "type": "string",
                        "enum": ["harris_template", "extended_matrix"],
                        "description": "Excel format: 'harris_template' or 'extended_matrix'"
                    },
                    "site_name": {
                        "type": "string",
                        "description": "Site name"
                    },
                    "excel_base64": {
                        "type": "string",
                        "description": "Base64-encoded Excel file (or use file_id)"
                    },
                    "file_id": {
                        "type": "string",
                        "description": "File ID from upload_file tool (or use excel_base64)"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Filename"
                    },
                    "generate_graphml": {
                        "type": "boolean",
                        "description": "Generate GraphML (default: true)",
                        "default": True
                    },
                    "reverse_edges": {
                        "type": "boolean",
                        "description": "Reverse edges (default: false)",
                        "default": False
                    }
                },
                "required": ["format", "site_name"],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Excel import"""
        try:
            import_format = arguments.get("format")
            site_name = arguments.get("site_name")
            excel_base64 = arguments.get("excel_base64")
            file_id = arguments.get("file_id")
            filename = arguments.get("filename", "import.xlsx")
            generate_graphml = arguments.get("generate_graphml", True)
            reverse_edges = arguments.get("reverse_edges", False)

            # Validate inputs
            if not import_format or not site_name:
                return self._format_error("Missing required parameters: format and site_name")

            if not excel_base64 and not file_id:
                return self._format_error("Must provide either excel_base64 or file_id")

            if import_format not in ["harris_template", "extended_matrix"]:
                return self._format_error("Invalid format. Use 'harris_template' or 'extended_matrix'")

            # Get file data from file_id or base64
            if file_id:
                # Use uploaded file
                from .upload_file_tool import get_uploaded_file_path
                filepath = get_uploaded_file_path(file_id)
                if not filepath or not os.path.exists(filepath):
                    return self._format_error(f"File not found for file_id: {file_id}")

                # File already exists, just use it
                temp_dir = os.path.dirname(filepath)
                logger.info(f"Excel import using file_id: {file_id}, format={import_format}, site={site_name}")
            else:
                # Decode base64 Excel file
                try:
                    excel_data = base64.b64decode(excel_base64)
                except Exception as e:
                    return self._format_error(f"Failed to decode Excel file: {str(e)}")

                # Create temp directory and save file
                temp_dir = tempfile.mkdtemp()
                filepath = os.path.join(temp_dir, filename)

                with open(filepath, 'wb') as f:
                    f.write(excel_data)

                logger.info(f"Excel import from base64: format={import_format}, site={site_name}, file={filename}, reverse_edges={reverse_edges}")

            # Perform import based on format
            if import_format == "harris_template":
                result = self._import_harris_template(filepath, site_name, generate_graphml, reverse_edges, temp_dir)
            else:  # extended_matrix
                result = self._import_extended_matrix(filepath, site_name, generate_graphml, reverse_edges, temp_dir)

            # Cleanup temp file (only if we created it)
            if not file_id:
                try:
                    os.remove(filepath)
                except:
                    pass
            else:
                # Cleanup uploaded file
                from .upload_file_tool import cleanup_uploaded_file
                cleanup_uploaded_file(file_id)

            return self._format_success(
                result,
                f"Excel import completed: {result.get('statistics', {})}"
            )

        except Exception as e:
            logger.error(f"Excel import error: {str(e)}", exc_info=True)
            return self._format_error(f"Import failed: {str(e)}")

    def _import_harris_template(self, filepath: str, site_name: str,
                                 generate_graphml: bool, reverse_edges: bool, temp_dir: str) -> Dict[str, Any]:
        """Import using Harris Matrix Template format"""
        from pyarchinit_mini.database.connection import DatabaseConnection
        from pyarchinit_mini.database.manager import DatabaseManager
        from pyarchinit_mini.cli.harris_import import HarrisMatrixImporter
        from pyarchinit_mini.models.base import BaseModel
        import os

        # Get database connection from config
        db_url = self.db_manager.connection.connection_string if hasattr(self, 'db_manager') else os.getenv('DATABASE_URL')

        if not db_url:
            return {'success': False, 'message': 'Database URL not configured'}

        connection = DatabaseConnection.from_url(db_url)
        db_manager = DatabaseManager(connection)

        # Initialize database schema
        BaseModel.metadata.create_all(connection.engine)

        try:
            with db_manager.connection.get_session() as db_session:
                importer = HarrisMatrixImporter(db_session, db_manager)

                # Perform import with reverse_edges parameter
                success = importer.import_matrix(
                    file_path=filepath,
                    site_name=site_name,
                    export_graphml=generate_graphml,
                    export_dot=False,
                    output_dir=temp_dir if generate_graphml else None,
                    reverse_edges=reverse_edges
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
                    'message': 'Import completed successfully',
                    'statistics': {
                        'us_count': us_count,
                        'relationships_count': rel_count,
                        'site_name': site_name
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

    def _import_extended_matrix(self, filepath: str, site_name: str,
                                 generate_graphml: bool, reverse_edges: bool, temp_dir: str) -> Dict[str, Any]:
        """Import using Extended Matrix Parser format"""
        from pyarchinit_mini.services.extended_matrix_excel_parser import import_extended_matrix_excel
        from pyarchinit_mini.database.connection import DatabaseConnection
        from pyarchinit_mini.models.base import BaseModel
        import os

        # Get database URL
        db_url = self.db_manager.connection.connection_string if hasattr(self, 'db_manager') else os.getenv('DATABASE_URL')

        if not db_url:
            return {'success': False, 'message': 'Database URL not configured'}

        # Convert URL to string for function call
        if hasattr(db_url, 'render_as_string'):
            db_url_str = db_url.render_as_string(hide_password=False)
        else:
            db_url_str = str(db_url)

        try:
            # Perform import with corrected parameter names
            result = import_extended_matrix_excel(
                excel_path=filepath,
                site_name=site_name,
                db_url=db_url_str,
                generate_graphml=generate_graphml,
                output_dir=temp_dir if generate_graphml else None,
                reverse_edges=reverse_edges
            )

            return result

        except Exception as e:
            logger.error(f"Extended matrix import error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'message': f'Import failed: {str(e)}'
            }
