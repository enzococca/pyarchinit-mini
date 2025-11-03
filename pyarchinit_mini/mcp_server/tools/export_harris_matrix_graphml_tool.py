"""
Export Harris Matrix to GraphML Tool

Auto-generates GraphML files from stratigraphic data in the database.
Retrieves all US units and relationships for a site and exports to yEd-compatible GraphML format.
"""

import logging
import os
import tempfile
from typing import Dict, Any, Optional
from .base_tool import BaseTool, ToolDescription

logger = logging.getLogger(__name__)


class ExportHarrisMatrixGraphMLTool(BaseTool):
    """Auto-export Harris Matrix to GraphML format"""

    def __init__(self, db_session, config):
        """Initialize with db_session and config, create db_manager and services"""
        super().__init__(db_session, config)
        # Create db_manager from session's bind (engine)
        from pyarchinit_mini.database.manager import DatabaseManager
        from pyarchinit_mini.database.connection import DatabaseConnection
        from pyarchinit_mini.services.us_service import USService
        # Get database URL from config or environment
        import os
        db_url = getattr(config, 'database_url', None) or os.getenv('DATABASE_URL', 'sqlite:///pyarchinit_mini.db')
        connection = DatabaseConnection.from_url(db_url)
        self.db_manager = DatabaseManager(connection)
        self.us_service = USService(self.db_manager)

    def to_tool_description(self) -> ToolDescription:
        return ToolDescription(
            name="export_harris_matrix_graphml",
            description=(
                "Automatically generate and export Harris Matrix to GraphML format for a given site. "
                "This tool retrieves all stratigraphic units (US) and their relationships from the database "
                "and generates a yEd-compatible GraphML file. No manual input of nodes/relationships needed - "
                "everything is automatically extracted from the database."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "site_name": {
                        "type": "string",
                        "description": "Name of the archaeological site to export"
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Optional output file path (default: creates temp file in ~/.pyarchinit_mini/graphml/)",
                        "default": None
                    },
                    "title": {
                        "type": "string",
                        "description": "Optional title for the diagram (default: '<site_name> - Harris Matrix')",
                        "default": None
                    },
                    "reverse_epochs": {
                        "type": "boolean",
                        "description": "Reverse epoch ordering in the visualization (default: true)",
                        "default": True
                    }
                },
                "required": ["site_name"],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute GraphML export"""
        try:
            site_name = arguments.get("site_name")
            output_path = arguments.get("output_path")
            title = arguments.get("title") or f"{site_name} - Harris Matrix"
            reverse_epochs = arguments.get("reverse_epochs", True)

            # Validate inputs
            if not site_name:
                return self._format_error("Site name is required")

            logger.info(f"Exporting Harris Matrix to GraphML: site={site_name}")

            # Generate GraphML
            graphml_path = self._generate_graphml(
                site_name=site_name,
                output_path=output_path,
                title=title,
                reverse_epochs=reverse_epochs
            )

            if not graphml_path:
                return self._format_error(f"Failed to generate GraphML for site: {site_name}")

            # Check file size
            file_size = os.path.getsize(graphml_path) if os.path.exists(graphml_path) else 0
            file_size_kb = file_size / 1024

            return self._format_success(
                result={
                    "graphml_path": graphml_path,
                    "file_size_kb": round(file_size_kb, 2),
                    "site_name": site_name
                },
                message=f"Successfully exported Harris Matrix to GraphML ({file_size_kb:.2f} KB)"
            )

        except Exception as e:
            logger.error(f"GraphML export error: {str(e)}", exc_info=True)
            return self._format_error(f"Export failed: {str(e)}")

    def _generate_graphml(
        self,
        site_name: str,
        output_path: Optional[str] = None,
        title: str = "",
        reverse_epochs: bool = True
    ) -> Optional[str]:
        """
        Generate GraphML file for a site using PureNetworkXExporter

        Args:
            site_name: Name of the site
            output_path: Optional output file path
            title: Diagram title
            reverse_epochs: Whether to reverse epoch ordering

        Returns:
            Path to generated GraphML file, or None if failed
        """
        try:
            from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator
            from pathlib import Path

            # Create matrix generator with db_manager and us_service
            matrix_generator = HarrisMatrixGenerator(self.db_manager, self.us_service)

            # Generate Harris Matrix graph from database
            graph = matrix_generator.generate_matrix(site_name)

            if not graph or graph.number_of_nodes() == 0:
                logger.error(f"No stratigraphic units found for site {site_name}")
                return None

            # Determine output path
            if not output_path:
                # Create default output directory
                home_dir = Path.home() / '.pyarchinit_mini' / 'graphml'
                home_dir.mkdir(parents=True, exist_ok=True)

                # Create temp file in the directory
                import tempfile
                temp_file = tempfile.NamedTemporaryFile(
                    mode='w',
                    suffix='.graphml',
                    prefix=f"{site_name.replace(' ', '_')}_",
                    delete=False,
                    dir=str(home_dir)
                )
                output_path = temp_file.name
                temp_file.close()

            # Export to GraphML using PureNetworkXExporter (no Graphviz required)
            result_path = matrix_generator.export_to_graphml(
                graph=graph,
                output_path=output_path,
                site_name=site_name,
                title=title or f"{site_name} - Harris Matrix",
                use_extended_labels=True,
                include_periods=True,
                reverse_epochs=reverse_epochs,
                use_graphviz=False  # Use pure NetworkX (documented approach)
            )

            if not result_path or not os.path.exists(result_path):
                logger.error(f"GraphML export failed for site {site_name}")
                return None

            logger.info(f"GraphML generated successfully: {result_path}")
            return result_path

        except Exception as e:
            logger.error(f"Error generating GraphML: {str(e)}", exc_info=True)
            return None
