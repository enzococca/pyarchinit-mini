"""
Build 3D Tool

Generates 3D stratigraphic model in Blender from US list.
"""

import uuid
import os
import tempfile
import logging
import networkx as nx
from typing import Dict, Any, List, Optional
from .base_tool import BaseTool, ToolDescription
from ..graphml_parser import GraphMLParser
from ..proxy_generator import ProxyGenerator
from ..blender_client import BlenderClient, BlenderConnectionError
from ...models.site import Site
from ...models.us import US
from ...models.extended_matrix import ExtendedMatrix
from ...harris_matrix.matrix_generator import HarrisMatrixGenerator

logger = logging.getLogger(__name__)


class Build3DTool(BaseTool):
    """
    Build 3D Model Tool

    Generates 3D stratigraphic model in Blender from list of US IDs.
    Communicates with Blender MCP addon to create proxy objects.
    """

    def to_tool_description(self) -> ToolDescription:
        return ToolDescription(
            name="build_3d_from_us",
            description=(
                "Build a 3D stratigraphic model in Blender from a list of stratigraphic units (US). "
                "Creates proxy objects with correct positioning based on stratigraphic relationships, "
                "applies materials based on periods, and tags proxies with US metadata."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "site_id": {
                        "type": "integer",
                        "description": "Site ID to build model for",
                    },
                    "us_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "List of US IDs to include in 3D model",
                    },
                    "graphml_id": {
                        "type": "integer",
                        "description": "Optional GraphML ID to use for relationships",
                    },
                    "options": {
                        "type": "object",
                        "properties": {
                            "positioning": {
                                "type": "string",
                                "enum": ["graphml", "grid", "force_directed"],
                                "default": "graphml",
                                "description": "Positioning algorithm to use",
                            },
                            "auto_color": {
                                "type": "boolean",
                                "default": True,
                                "description": "Auto-apply colors based on periods",
                            },
                            "auto_material": {
                                "type": "boolean",
                                "default": True,
                                "description": "Auto-apply materials based on formation type",
                            },
                        },
                    },
                },
                "required": ["site_id", "us_ids"],
            },
        )

    def _generate_graphml_for_site(self, site_name: str) -> Optional[str]:
        """Generate GraphML file for a site"""
        try:
            from ...database.connection import DatabaseConnection
            from ...database.manager import DatabaseManager
            from ...services.us_service import USService

            logger.info(f"Auto-generating GraphML for site: {site_name}")

            # Get database URL from existing session's engine
            engine = self.db_session.get_bind()
            db_url = str(engine.url)

            # Create database connection and manager using the same URL
            db_connection = DatabaseConnection(db_url)
            db_manager = DatabaseManager(db_connection)

            # Create US service for matrix generator
            us_service = USService(db_manager)

            # Get matrix generator WITH us_service
            matrix_generator = HarrisMatrixGenerator(db_manager, us_service=us_service)

            # Generate Harris Matrix graph
            graph = matrix_generator.generate_matrix(site_name)
            has_relationships = graph and graph.number_of_edges() > 0

            if not graph or graph.number_of_nodes() == 0:
                logger.warning(f"No stratigraphic relationships found for site {site_name}")
                # Create minimal GraphML with just nodes
                import networkx as nx
                graph = nx.DiGraph()

                from ...models.us import US as USModel
                us_records = self.db_session.query(USModel).filter(USModel.sito == site_name).all()
                for us in us_records:
                    graph.add_node(
                        str(us.us),
                        label=f"US {us.us}",
                        description=us.descrizione or "",
                        unita_tipo=us.unita_tipo or "US"
                    )

                if graph.number_of_nodes() == 0:
                    logger.error(f"No US records found for site {site_name}")
                    return None

                has_relationships = False

            # Create temp file
            temp_file = tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.graphml',
                delete=False,
                dir='/tmp'
            )
            temp_path = temp_file.name
            temp_file.close()

            # Export to GraphML
            if has_relationships:
                result_path = matrix_generator.export_to_graphml(
                    graph=graph,
                    output_path=temp_path,
                    site_name=site_name,
                    title=f"{site_name} - Harris Matrix (Auto-generated)",
                    reverse_epochs=True
                )
            else:
                import networkx as nx
                nx.write_graphml(graph, temp_path)
                result_path = temp_path

            if not result_path or not os.path.exists(result_path):
                logger.error(f"GraphML export failed for site {site_name}")
                return None

            logger.info(f"GraphML generated successfully: {result_path}")
            return result_path

        except Exception as e:
            logger.error(f"Error generating GraphML for site {site_name}: {e}", exc_info=True)
            return None

    def _fetch_complete_us_data(self, us_ids: List[int], site_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch complete US data from database

        Returns all archaeological data for each US including:
        - descrizione, interpretazione
        - unita_tipo (critical for geometry type)
        - periodo (for coloring)
        - colore, formazione, struttura
        - physical measurements
        - relationships
        """
        try:
            # Query US records
            query = self.db_session.query(US).filter(US.us.in_([str(uid) for uid in us_ids]))

            if site_name:
                query = query.filter(US.sito == site_name)

            us_records = query.all()

            if not us_records:
                logger.warning(f"No US records found for IDs: {us_ids}")
                return []

            # Build complete US data dictionaries
            complete_data = []
            for us_record in us_records:
                us_data = {
                    # Identity
                    'us_id': us_record.us,
                    'id_us': us_record.id_us,
                    'sito': us_record.sito,
                    'area': us_record.area,

                    # Critical for geometry creation
                    'unita_tipo': us_record.unita_tipo or 'US',

                    # Descriptions (use English if available, fallback to Italian)
                    'descrizione': us_record.descrizione_en or us_record.descrizione or '',
                    'interpretazione': us_record.interpretazione_en or us_record.interpretazione or '',
                    'd_stratigrafica': us_record.d_stratigrafica_en or us_record.d_stratigrafica or '',
                    'd_interpretativa': us_record.d_interpretativa_en or us_record.d_interpretativa or '',

                    # Chronology (for coloring)
                    'periodo': us_record.periodo_iniziale or us_record.periodo_finale or 'Unknown',
                    'periodo_iniziale': us_record.periodo_iniziale,
                    'periodo_finale': us_record.periodo_finale,
                    'fase_iniziale': us_record.fase_iniziale,
                    'fase_finale': us_record.fase_finale,

                    # Physical characteristics (for materials)
                    'colore': us_record.colore_en or us_record.colore,
                    'formazione': us_record.formazione_en or us_record.formazione,
                    'struttura': us_record.struttura_en or us_record.struttura,
                    'consistenza': us_record.consistenza_en or us_record.consistenza,
                    'stato_di_conservazione': us_record.stato_di_conservazione_en or us_record.stato_di_conservazione,

                    # Inclusions and samples
                    'inclusi': us_record.inclusi_en or us_record.inclusi,
                    'campioni': us_record.campioni_en or us_record.campioni,

                    # Measurements (for sizing)
                    'quota_relativa': us_record.quota_relativa,
                    'quota_abs': us_record.quota_abs,
                    'lunghezza_max': us_record.lunghezza_max,
                    'altezza_max': us_record.altezza_max,
                    'altezza_min': us_record.altezza_min,
                    'profondita_max': us_record.profondita_max,
                    'profondita_min': us_record.profondita_min,

                    # Excavation context
                    'scavato': us_record.scavato,
                    'attivita': us_record.attivita,
                    'anno_scavo': us_record.anno_scavo,
                    'metodo_di_scavo': us_record.metodo_di_scavo,
                    'schedatore': us_record.schedatore,

                    # Relationships
                    'rapporti': us_record.rapporti,
                    'order_layer': us_record.order_layer,

                    # Documentation
                    'documentazione': us_record.documentazione_en or us_record.documentazione,
                    'tipo_documento': us_record.tipo_documento,
                    'file_path': us_record.file_path,
                }

                complete_data.append(us_data)

            logger.info(f"Fetched complete data for {len(complete_data)} US records")
            return complete_data

        except Exception as e:
            logger.error(f"Error fetching US data: {e}", exc_info=True)
            return []

    def _send_to_blender(
        self,
        session_id: str,
        site_name: str,
        proxies: List[Any],
        complete_us_data: List[Dict[str, Any]],
        graphml_edges: List[Dict[str, Any]],
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send complete data to Blender for REAL geometry creation

        Uses BlenderClient to communicate with Blender MCP addon
        """
        try:
            # Get Blender connection settings from environment
            blender_host = os.environ.get('BLENDER_HOST', 'localhost')
            blender_port = int(os.environ.get('BLENDER_PORT', '9876'))

            logger.info(f"Connecting to Blender at {blender_host}:{blender_port}")

            # Prepare proxy data with complete US information
            enhanced_proxies = []
            for proxy, us_data in zip(proxies, complete_us_data):
                proxy_dict = proxy.to_dict()
                proxy_dict['us_data'] = us_data  # Include ALL archaeological data
                enhanced_proxies.append(proxy_dict)

            # Connect to Blender and send command
            with BlenderClient(host=blender_host, port=blender_port, timeout=60) as client:
                logger.info(f"Connected to Blender successfully")

                # Send build command with complete data
                result = client.send_command(
                    "build_stratigraphic_model",
                    {
                        "session_id": session_id,
                        "site_name": site_name,
                        "proxies": enhanced_proxies,
                        "graphml_edges": graphml_edges,
                        "options": options,
                    }
                )

                logger.info(f"Blender build completed: {result.status}")

                if result.status == "success":
                    return {
                        "success": True,
                        "blender_result": result.result,
                        "message": result.message,
                    }
                else:
                    return {
                        "success": False,
                        "error": result.message,
                    }

        except BlenderConnectionError as e:
            logger.error(f"Blender connection error: {e}")
            return {
                "success": False,
                "error": f"Could not connect to Blender: {e}. Make sure Blender is running with MCP addon enabled.",
            }
        except Exception as e:
            logger.error(f"Error sending to Blender: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
            }

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute build 3D action

        Args:
            arguments: {us_ids, mode?, site_id?, graphml_id?, options?}

        Returns:
            Build result with session ID and proxy metadata
        """
        try:
            # Extract arguments
            us_ids = arguments.get('us_ids', [])
            mode = arguments.get('mode', 'selected')
            site_id = arguments.get('site_id')
            graphml_id = arguments.get('graphml_id')
            options = arguments.get('options', {})

            # Validate us_ids
            if not us_ids and mode == 'selected':
                return self._format_error("ValidationError", "us_ids is required for mode 'selected'")

            # Get site name if site_id provided
            site_name = None
            if site_id:
                site = self.db_session.query(Site).filter(Site.id_sito == site_id).first()
                if site:
                    site_name = site.sito

            # Get GraphML file
            graphml_filepath = None
            if graphml_id:
                graphml_record = self.db_session.query(ExtendedMatrix).filter(
                    ExtendedMatrix.id == graphml_id
                ).first()
                if graphml_record:
                    graphml_filepath = graphml_record.filepath
            else:
                # Get latest GraphML or generate for site
                graphml_record = self.db_session.query(ExtendedMatrix).order_by(
                    ExtendedMatrix.id.desc()
                ).first()
                if graphml_record:
                    graphml_filepath = graphml_record.filepath

            # Auto-generate GraphML if not found and we have a site
            if not graphml_filepath and site_name:
                logger.info(f"No GraphML found, generating for site: {site_name}")
                graphml_filepath = self._generate_graphml_for_site(site_name)
                if not graphml_filepath:
                    return self._format_error(
                        "GraphMLError",
                        f"Failed to generate GraphML for site {site_name}"
                    )

            if not graphml_filepath:
                return self._format_error(
                    "GraphMLError",
                    "GraphML file not found. Please specify a site_id to auto-generate."
                )

            # Load GraphML
            parser = GraphMLParser(self.db_session)
            if not parser.load_graphml(graphml_filepath):
                return self._format_error("GraphMLError", "Failed to load GraphML file")

            # Extract US IDs from GraphML if mode is 'all'
            if mode == 'all' and parser.graph:
                # Get all node IDs from GraphML and convert to integers
                graphml_us_ids = []
                for node_id in parser.graph.nodes():
                    try:
                        # Node IDs in GraphML are strings like "1001", "1002"
                        graphml_us_ids.append(int(node_id))
                    except (ValueError, TypeError):
                        logger.warning(f"Skipping non-numeric node ID: {node_id}")
                        continue

                if graphml_us_ids:
                    us_ids = graphml_us_ids
                    logger.info(f"Extracted {len(us_ids)} US IDs from GraphML: {us_ids}")
                else:
                    return self._format_error(
                        "GraphMLError",
                        "No valid US nodes found in GraphML"
                    )

            # Generate session ID
            session_id = str(uuid.uuid4())

            # Generate proxies
            generator = ProxyGenerator(
                parser,
                positioning=options.get('positioning', 'graphml'),
                auto_color=options.get('auto_color', True),
                auto_material=options.get('auto_material', True),
            )

            proxies = generator.generate_all_proxies(us_ids, session_id)

            if not proxies:
                return self._format_error("GenerationError", "No proxies generated")

            # Fetch complete US data from database
            logger.info(f"Fetching complete US data from database for {len(us_ids)} units")
            complete_us_data = self._fetch_complete_us_data(us_ids, site_name)

            if not complete_us_data:
                logger.warning("No complete US data found, using proxy data only")
                complete_us_data = [{"us_id": uid, "unita_tipo": "US"} for uid in us_ids]

            # Extract GraphML edges for relationships
            graphml_edges = []
            if parser.graph:
                for edge in parser.graph.edges(data=True):
                    source, target, attrs = edge
                    graphml_edges.append({
                        "source": source,
                        "target": target,
                        "relationship": attrs.get('relationship', 'unknown')
                    })

            # Format proxy data
            proxy_data = [p.to_dict() for p in proxies]

            logger.info(f"Generated {len(proxies)} proxies for session {session_id}")

            # Send to Blender for REAL geometry creation
            blender_enabled = options.get('use_blender', True)

            if blender_enabled:
                logger.info("Sending data to Blender for real geometry creation")
                blender_result = self._send_to_blender(
                    session_id=session_id,
                    site_name=site_name or "Unknown",
                    proxies=proxies,
                    complete_us_data=complete_us_data,
                    graphml_edges=graphml_edges,
                    options=options
                )

                if blender_result.get('success'):
                    logger.info("Blender geometry creation successful")
                    return self._format_success(
                        {
                            "session_id": session_id,
                            "proxies": proxy_data,
                            "proxies_count": len(proxies),
                            "site_name": site_name,
                            "graphml_filepath": graphml_filepath,
                            "blender_enabled": True,
                            "blender_status": "success",
                            "blender_result": blender_result.get('blender_result'),
                        },
                        message=f"Created {len(proxies)} 3D objects in Blender successfully",
                    )
                else:
                    # Blender failed, but return proxies anyway
                    logger.warning(f"Blender failed: {blender_result.get('error')}")
                    return self._format_success(
                        {
                            "session_id": session_id,
                            "proxies": proxy_data,
                            "proxies_count": len(proxies),
                            "site_name": site_name,
                            "graphml_filepath": graphml_filepath,
                            "blender_enabled": True,
                            "blender_status": "failed",
                            "blender_error": blender_result.get('error'),
                        },
                        message=f"Generated {len(proxies)} proxies (Blender unavailable: {blender_result.get('error')})",
                    )
            else:
                # Blender disabled, return proxies only
                logger.info("Blender disabled, returning proxy metadata only")
                return self._format_success(
                    {
                        "session_id": session_id,
                        "proxies": proxy_data,
                        "proxies_count": len(proxies),
                        "site_name": site_name,
                        "graphml_filepath": graphml_filepath,
                        "blender_enabled": False,
                    },
                    message=f"Generated {len(proxies)} 3D proxies successfully",
                )

        except Exception as e:
            logger.error(f"Error in Build3DTool execution: {e}", exc_info=True)
            return self._format_error("ExecutionError", str(e))
