"""
3D Builder Routes

API endpoints for 3D stratigraphic model generation and manipulation.
Integrates with MCP server, Blender client, and GraphML parser.
"""

from flask import Blueprint, request, jsonify, session, render_template, current_app
from flask_login import login_required, current_user
import logging
import uuid
import os
import tempfile
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional

from pyarchinit_mini.mcp_server.graphml_parser import GraphMLParser
from pyarchinit_mini.mcp_server.proxy_generator import ProxyGenerator
from pyarchinit_mini.mcp_server.blender_client import BlenderClient, BlenderConnectionError
from pyarchinit_mini.mcp_server.event_stream import get_event_stream
from pyarchinit_mini.models.extended_matrix import ExtendedMatrix
from pyarchinit_mini.models.site import Site
from pyarchinit_mini.models.us import US
from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator
from pyarchinit_mini.services.command_parser import CommandParser
from pyarchinit_mini.services.mcp_executor import get_executor

logger = logging.getLogger(__name__)

# Create blueprints
three_d_builder_bp = Blueprint('three_d_builder', __name__, url_prefix='/api/3d-builder')
three_d_builder_ui_bp = Blueprint('three_d_builder_ui', __name__, url_prefix='/3d-builder')

# In-memory storage for build sessions (TODO: Move to database/Redis)
build_sessions: Dict[str, Dict[str, Any]] = {}


# ============================================================================
# UI Routes
# ============================================================================

@three_d_builder_ui_bp.route('/')
@login_required
def index():
    """
    3D Builder main page
    """
    try:
        with get_db_session() as db_session:
            # Get all sites
            sites = db_session.query(Site).all()

            # Get all GraphML files
            graphml_files = db_session.query(ExtendedMatrix).order_by(
                ExtendedMatrix.id.desc()
            ).limit(20).all()

            # Get total US count
            total_us = db_session.query(US).count()

            return render_template(
                '3d_builder/index.html',
                sites=sites,
                graphml_files=graphml_files,
                total_us=total_us
            )

    except Exception as e:
        logger.error(f"Error loading 3D Builder page: {e}", exc_info=True)
        return render_template(
            '3d_builder/index.html',
            sites=[],
            graphml_files=[],
            total_us=0
        )


# ============================================================================
# Helper Functions
# ============================================================================

def get_db_session():
    """Get database session from app context"""
    from flask import current_app
    return current_app.db_manager.connection.get_session()


def get_latest_graphml(db_session) -> Optional[ExtendedMatrix]:
    """Get latest GraphML file"""
    return db_session.query(ExtendedMatrix).order_by(ExtendedMatrix.id.desc()).first()


def generate_graphml_for_site(db_session, site_name: str) -> Optional[str]:
    """
    Generate GraphML file for a site and save it

    Args:
        db_session: Database session
        site_name: Name of the site

    Returns:
        Path to generated GraphML file, or None if failed
    """
    try:
        logger.info(f"Auto-generating GraphML for site: {site_name}")

        # Get matrix generator from current_app
        matrix_generator = HarrisMatrixGenerator(current_app.db_manager)

        # Generate Harris Matrix graph
        graph = matrix_generator.generate_matrix(site_name)
        has_relationships = graph and graph.number_of_edges() > 0

        if not graph or graph.number_of_nodes() == 0:
            logger.warning(f"No stratigraphic relationships found for site {site_name}, creating minimal GraphML")
            # Create a minimal GraphML with just the nodes (no relationships)
            import networkx as nx
            graph = nx.DiGraph()

            # Add nodes from US table (without relationships)
            from pyarchinit_mini.models.us import US as USModel
            us_records = db_session.query(USModel).filter(USModel.sito == site_name).all()
            for us in us_records:
                # Add node with basic attributes for compatibility
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

        # Create temp file for GraphML
        temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.graphml',
            delete=False,
            dir='/tmp'
        )
        temp_path = temp_file.name
        temp_file.close()

        # Export to GraphML - use simple format for minimal graphs
        if has_relationships:
            # Use yEd exporter for full Harris Matrix with relationships
            result_path = matrix_generator.export_to_graphml(
                graph=graph,
                output_path=temp_path,
                site_name=site_name,
                title=f"{site_name} - Harris Matrix (Auto-generated)",
                reverse_epochs=True
            )
        else:
            # Use basic NetworkX export for simple graphs (more compatible)
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


# ============================================================================
# API Endpoints
# ============================================================================

@three_d_builder_bp.route('/sites/<int:site_id>/us', methods=['GET'])
@login_required
def get_site_us(site_id):
    """
    Get all US for a specific site

    GET /api/3d-builder/sites/<site_id>/us

    Returns:
    {
        "success": true,
        "site_id": 1,
        "site_name": "Ancient Harbor",
        "us": [
            {"id_us": 5, "us": 5, "d_stratigr": "Layer", ...},
            ...
        ]
    }
    """
    try:
        with get_db_session() as db_session:
            # Get site
            site = db_session.query(Site).filter(Site.id_sito == site_id).first()
            if not site:
                return jsonify({
                    'success': False,
                    'error': 'Site not found'
                }), 404

            # Get all US for site
            us_list = db_session.query(US).filter(US.sito == site.sito).order_by(US.us).all()

            return jsonify({
                'success': True,
                'site_id': site.id_sito,
                'site_name': site.sito,
                'us': [
                    {
                        'id_us': u.id_us,
                        'us': u.us,
                        'unita_tipo': u.unita_tipo,
                        'descrizione': u.descrizione
                    }
                    for u in us_list
                ]
            })

    except Exception as e:
        logger.error(f"Error getting site US: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@three_d_builder_bp.route('/generate', methods=['POST'])
@login_required
def generate_3d_model():
    """
    Generate 3D stratigraphic model

    POST /api/3d-builder/generate
    {
        "prompt": "Create 3D model of Bronze Age layers",
        "site_id": 1,
        "us_ids": [5, 6, 7],
        "graphml_id": 15,
        "options": {
            "positioning": "graphml",
            "auto_color": true,
            "auto_material": true
        }
    }

    Returns:
    {
        "success": true,
        "session_id": "uuid",
        "proxies_count": 3,
        "message": "3D model generation started"
    }
    """
    try:
        data = request.get_json()

        # Validate input
        if not data.get('us_ids'):
            return jsonify({
                'success': False,
                'error': 'us_ids is required'
            }), 400

        # Extract parameters
        us_ids = data.get('us_ids', [])
        graphml_id = data.get('graphml_id')
        site_id = data.get('site_id')
        options = data.get('options', {})
        prompt = data.get('prompt', '')

        # Get database session
        with get_db_session() as db_session:
            # Get site name if site_id provided
            site_name = None
            if site_id:
                site = db_session.query(Site).filter(Site.id_sito == site_id).first()
                if site:
                    site_name = site.sito

            # Get GraphML file
            if graphml_id:
                graphml_record = db_session.query(ExtendedMatrix).filter(
                    ExtendedMatrix.id == graphml_id
                ).first()
            else:
                graphml_record = get_latest_graphml(db_session)

            # If no GraphML found and we have a site, generate it automatically
            graphml_filepath = None
            if not graphml_record or not graphml_record.filepath:
                if site_name:
                    logger.info(f"No GraphML found, generating automatically for site: {site_name}")
                    graphml_filepath = generate_graphml_for_site(db_session, site_name)
                    if not graphml_filepath:
                        return jsonify({
                            'success': False,
                            'error': f'Failed to generate GraphML for site {site_name}'
                        }), 500
                else:
                    return jsonify({
                        'success': False,
                        'error': 'GraphML file not found. Please specify a site_id to auto-generate.'
                    }), 404
            else:
                graphml_filepath = graphml_record.filepath

            # Load GraphML parser
            parser = GraphMLParser(db_session)
            if not parser.load_graphml(graphml_filepath):
                return jsonify({
                    'success': False,
                    'error': 'Failed to load GraphML file'
                }), 500

            # Generate session ID
            session_id = str(uuid.uuid4())

            # Generate proxy metadata
            generator = ProxyGenerator(
                parser,
                positioning=options.get('positioning', 'graphml'),
                auto_color=options.get('auto_color', True),
                auto_material=options.get('auto_material', True),
            )

            proxies = generator.generate_all_proxies(us_ids, session_id)

            if not proxies:
                return jsonify({
                    'success': False,
                    'error': 'No proxies generated'
                }), 500

            # Store session info
            build_sessions[session_id] = {
                'session_id': session_id,
                'user_id': current_user.id,
                'site_id': site_id,
                'graphml_id': graphml_record.id if graphml_record else None,
                'graphml_filepath': graphml_filepath,
                'us_ids': us_ids,
                'proxies': [p.to_dict() for p in proxies],
                'status': 'ready',
                'prompt': prompt,
                'options': options,
            }

            logger.info(
                f"Generated 3D model session {session_id} with {len(proxies)} proxies"
            )

            return jsonify({
                'success': True,
                'session_id': session_id,
                'proxies_count': len(proxies),
                'message': '3D model generation completed',
            })

    except Exception as e:
        logger.error(f"Error generating 3D model: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@three_d_builder_bp.route('/progress', methods=['GET'])
@login_required
def get_progress():
    """
    Get construction progress from Blender

    GET /api/3d-builder/progress

    Returns:
    {
        "success": true,
        "messages": [
            {"type": "progress", "action": "creating_geometry", "us_id": 1, ...},
            ...
        ],
        "count": 5
    }
    """
    try:
        # Connect to Blender and request progress
        blender_host = os.environ.get('BLENDER_HOST', 'localhost')
        blender_port = int(os.environ.get('BLENDER_PORT', '9876'))

        with BlenderClient(host=blender_host, port=blender_port, timeout=5) as client:
            result = client.send_command("get_progress", {})

            if result.status == "success":
                return jsonify({
                    'success': True,
                    'messages': result.result.get('messages', []),
                    'count': result.result.get('count', 0)
                })
            else:
                return jsonify({
                    'success': False,
                    'error': result.message,
                    'messages': [],
                    'count': 0
                })

    except BlenderConnectionError:
        # Blender not available - return empty
        return jsonify({
            'success': False,
            'error': 'Blender not connected',
            'messages': [],
            'count': 0
        })
    except Exception as e:
        logger.error(f"Error getting progress: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'messages': [],
            'count': 0
        })


@three_d_builder_bp.route('/chat', methods=['POST'])
@login_required
def chat_command():
    """
    Chat-based 3D model generation using natural language commands

    POST /api/3d-builder/chat
    {
        "message": "Crea US 1,2,3",
        "session_id": "uuid",  // optional - for existing session
        "site_id": 1           // optional - for context
    }

    Returns:
    {
        "success": true,
        "message": "Executed: build_3d",
        "tool_calls": [
            {
                "tool": "build_3d",
                "arguments": {"us_ids": [1,2,3], "mode": "selected"},
                "result": { ... }
            }
        ],
        "session_id": "uuid"
    }
    """
    try:
        data = request.get_json()

        # Validate input
        message = data.get('message', '').strip()
        if not message:
            return jsonify({
                'success': False,
                'error': 'message is required'
            }), 400

        session_id = data.get('session_id')
        site_id = data.get('site_id')

        # Initialize parser and executor
        parser = CommandParser()
        database_url = current_app.config.get('DATABASE_URL')
        executor = get_executor(database_url)

        # Parse command
        tool_calls = parser.parse(message)

        if not tool_calls:
            # No pattern matched, return help
            help_text = parser.get_help()
            return jsonify({
                'success': False,
                'error': 'Command not recognized',
                'help': help_text,
                'message': 'Try commands like: "Crea US 1,2,3" or "Mostra solo periodo Romano"'
            }), 400

        # Execute tool calls
        results = []
        for tool_name, arguments in tool_calls:
            try:
                # Add site_id to build_3d arguments if missing and available
                if tool_name == 'build_3d' and 'site_id' not in arguments and site_id:
                    arguments['site_id'] = site_id
                    logger.info(f"Auto-added site_id {site_id} to build_3d arguments")

                # If still missing site_id for build_3d, try to get first site from database
                if tool_name == 'build_3d' and 'site_id' not in arguments:
                    with get_db_session() as db_session:
                        first_site = db_session.query(Site).first()
                        if first_site:
                            arguments['site_id'] = first_site.id_sito
                            logger.info(f"Auto-detected site_id {first_site.id_sito} (first site in database)")

                # Execute tool asynchronously
                result = asyncio.run(executor.execute_tool(tool_name, arguments))

                # Unwrap nested result structure from BaseTool._format_success
                # If result has structure {"success": True, "result": {...}}, unwrap it
                tool_result = result
                if isinstance(result, dict) and 'result' in result and 'success' in result:
                    tool_result = result['result']  # Unwrap the inner result

                results.append({
                    'tool': tool_name,
                    'arguments': arguments,
                    'result': tool_result,
                    'success': True
                })
                logger.info(f"Executed tool {tool_name} from chat: {arguments}")

            except Exception as e:
                logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)
                results.append({
                    'tool': tool_name,
                    'arguments': arguments,
                    'error': str(e),
                    'success': False
                })

        # Generate or use existing session
        if not session_id and results:
            session_id = str(uuid.uuid4())

        # Build response message
        executed_tools = [r['tool'] for r in results if r['success']]
        failed_tools = [r['tool'] for r in results if not r['success']]

        response_message = ""
        if executed_tools:
            response_message = f"Executed: {', '.join(executed_tools)}"
        if failed_tools:
            if response_message:
                response_message += f"; Failed: {', '.join(failed_tools)}"
            else:
                response_message = f"Failed: {', '.join(failed_tools)}"

        return jsonify({
            'success': len(executed_tools) > 0,
            'message': response_message,
            'tool_calls': results,
            'session_id': session_id,
            'parsed_command': {
                'original': message,
                'tool_calls_count': len(tool_calls)
            }
        })

    except Exception as e:
        logger.error(f"Error processing chat command: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@three_d_builder_bp.route('/filter', methods=['POST'])
@login_required
def filter_proxies():
    """
    Filter proxies in 3D model

    POST /api/3d-builder/filter
    {
        "session_id": "uuid",
        "filters": {
            "period_range": {"start": -1200, "end": -800},
            "visible_us": [5, 6, 7],
            "transparency": 0.75,
            "highlight_us": [5]
        }
    }

    Returns:
    {
        "success": true,
        "updated_count": 3,
        "visible_count": 3,
        "hidden_count": 0
    }
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        filters = data.get('filters', {})

        if not session_id or session_id not in build_sessions:
            return jsonify({
                'success': False,
                'error': 'Invalid session_id'
            }), 404

        session_data = build_sessions[session_id]
        proxies = session_data['proxies']

        # Apply filters
        visible_us = filters.get('visible_us')
        period_range = filters.get('period_range')
        transparency = filters.get('transparency', 1.0)
        highlight_us = filters.get('highlight_us', [])

        updated_count = 0
        visible_count = 0
        hidden_count = 0

        for proxy in proxies:
            us_id = proxy['us_id']
            updated = False

            # Visibility filter
            if visible_us is not None:
                proxy['visualization']['visible'] = us_id in visible_us
                updated = True

            # Period range filter
            if period_range:
                dating_start = proxy['chronology'].get('dating_start')
                dating_end = proxy['chronology'].get('dating_end')

                if dating_start and dating_end:
                    in_range = (
                        dating_start >= period_range.get('start', -9999) and
                        dating_end <= period_range.get('end', 9999)
                    )
                    proxy['visualization']['visible'] = in_range
                    updated = True

            # Transparency
            if transparency != 1.0:
                proxy['visualization']['opacity'] = transparency
                updated = True

            # Highlighting
            proxy['visualization']['highlight'] = us_id in highlight_us

            if updated:
                updated_count += 1

            if proxy['visualization']['visible']:
                visible_count += 1
            else:
                hidden_count += 1

        logger.info(
            f"Applied filters to session {session_id}: "
            f"{visible_count} visible, {hidden_count} hidden"
        )

        return jsonify({
            'success': True,
            'updated_count': updated_count,
            'visible_count': visible_count,
            'hidden_count': hidden_count,
        })

    except Exception as e:
        logger.error(f"Error filtering proxies: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@three_d_builder_bp.route('/proxy/<int:us_id>', methods=['GET'])
@login_required
def get_proxy_info(us_id: int):
    """
    Get proxy information by US ID

    GET /api/3d-builder/proxy/5

    Returns:
    {
        "success": true,
        "proxy": { ... proxy metadata ... }
    }
    """
    try:
        session_id = request.args.get('session_id')

        if not session_id or session_id not in build_sessions:
            return jsonify({
                'success': False,
                'error': 'Invalid session_id'
            }), 404

        session_data = build_sessions[session_id]
        proxies = session_data['proxies']

        # Find proxy
        proxy = next((p for p in proxies if p['us_id'] == us_id), None)

        if not proxy:
            return jsonify({
                'success': False,
                'error': f'Proxy for US {us_id} not found'
            }), 404

        return jsonify({
            'success': True,
            'proxy': proxy,
        })

    except Exception as e:
        logger.error(f"Error getting proxy info: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@three_d_builder_bp.route('/proxy/<int:us_id>/visibility', methods=['PATCH'])
@login_required
def update_proxy_visibility(us_id: int):
    """
    Update proxy visibility

    PATCH /api/3d-builder/proxy/5/visibility
    {
        "session_id": "uuid",
        "visible": false
    }

    Returns:
    {
        "success": true,
        "proxy_id": "proxy_us_5",
        "visible": false
    }
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        visible = data.get('visible', True)

        if not session_id or session_id not in build_sessions:
            return jsonify({
                'success': False,
                'error': 'Invalid session_id'
            }), 404

        session_data = build_sessions[session_id]
        proxies = session_data['proxies']

        # Find and update proxy
        proxy = next((p for p in proxies if p['us_id'] == us_id), None)

        if not proxy:
            return jsonify({
                'success': False,
                'error': f'Proxy for US {us_id} not found'
            }), 404

        proxy['visualization']['visible'] = visible

        return jsonify({
            'success': True,
            'proxy_id': proxy['proxy_id'],
            'visible': visible,
        })

    except Exception as e:
        logger.error(f"Error updating visibility: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@three_d_builder_bp.route('/proxy/<int:us_id>/transparency', methods=['PATCH'])
@login_required
def update_proxy_transparency(us_id: int):
    """
    Update proxy transparency

    PATCH /api/3d-builder/proxy/5/transparency
    {
        "session_id": "uuid",
        "opacity": 0.5
    }

    Returns:
    {
        "success": true,
        "proxy_id": "proxy_us_5",
        "opacity": 0.5
    }
    """
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        opacity = data.get('opacity', 1.0)

        # Validate opacity
        if not 0.0 <= opacity <= 1.0:
            return jsonify({
                'success': False,
                'error': 'Opacity must be between 0.0 and 1.0'
            }), 400

        if not session_id or session_id not in build_sessions:
            return jsonify({
                'success': False,
                'error': 'Invalid session_id'
            }), 404

        session_data = build_sessions[session_id]
        proxies = session_data['proxies']

        # Find and update proxy
        proxy = next((p for p in proxies if p['us_id'] == us_id), None)

        if not proxy:
            return jsonify({
                'success': False,
                'error': f'Proxy for US {us_id} not found'
            }), 404

        proxy['visualization']['opacity'] = opacity

        return jsonify({
            'success': True,
            'proxy_id': proxy['proxy_id'],
            'opacity': opacity,
        })

    except Exception as e:
        logger.error(f"Error updating transparency: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@three_d_builder_bp.route('/session/<session_id>', methods=['GET'])
@login_required
def get_session_info(session_id: str):
    """
    Get build session information

    GET /api/3d-builder/session/{session_id}

    Returns:
    {
        "success": true,
        "session": { ... session data ... }
    }
    """
    try:
        if session_id not in build_sessions:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404

        session_data = build_sessions[session_id]

        # Return session without full proxy data (too large)
        session_summary = {
            'session_id': session_data['session_id'],
            'user_id': session_data['user_id'],
            'site_id': session_data['site_id'],
            'graphml_id': session_data['graphml_id'],
            'us_ids': session_data['us_ids'],
            'proxies_count': len(session_data['proxies']),
            'status': session_data['status'],
            'prompt': session_data['prompt'],
            'options': session_data['options'],
        }

        return jsonify({
            'success': True,
            'session': session_summary,
        })

    except Exception as e:
        logger.error(f"Error getting session info: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@three_d_builder_bp.route('/session/<session_id>/proxies', methods=['GET'])
@login_required
def get_session_proxies(session_id: str):
    """
    Get all proxies for a session

    GET /api/3d-builder/session/{session_id}/proxies

    Returns:
    {
        "success": true,
        "proxies": [ ... full proxy metadata array ... ],
        "count": 5
    }
    """
    try:
        if session_id not in build_sessions:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404

        session_data = build_sessions[session_id]

        return jsonify({
            'success': True,
            'proxies': session_data['proxies'],
            'count': len(session_data['proxies'])
        })

    except Exception as e:
        logger.error(f"Error getting session proxies: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@three_d_builder_bp.route('/session/<session_id>', methods=['DELETE'])
@login_required
def delete_session(session_id: str):
    """
    Delete build session

    DELETE /api/3d-builder/session/{session_id}

    Returns:
    {
        "success": true,
        "message": "Session deleted"
    }
    """
    try:
        if session_id not in build_sessions:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404

        # Check ownership
        session_data = build_sessions[session_id]
        if session_data['user_id'] != current_user.id and not current_user.is_admin:
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 403

        del build_sessions[session_id]

        logger.info(f"Deleted session {session_id}")

        return jsonify({
            'success': True,
            'message': 'Session deleted',
        })

    except Exception as e:
        logger.error(f"Error deleting session: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@three_d_builder_bp.route('/sessions', methods=['GET'])
@login_required
def list_sessions():
    """
    List all sessions for current user

    GET /api/3d-builder/sessions

    Returns:
    {
        "success": true,
        "sessions": [ ... ]
    }
    """
    try:
        user_sessions = []

        for session_id, session_data in build_sessions.items():
            if session_data['user_id'] == current_user.id or current_user.is_admin:
                user_sessions.append({
                    'session_id': session_id,
                    'site_id': session_data['site_id'],
                    'proxies_count': len(session_data['proxies']),
                    'status': session_data['status'],
                    'prompt': session_data.get('prompt', ''),
                })

        return jsonify({
            'success': True,
            'sessions': user_sessions,
            'count': len(user_sessions),
        })

    except Exception as e:
        logger.error(f"Error listing sessions: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# Blender Integration Endpoints (Optional - for direct Blender control)
# ============================================================================

@three_d_builder_bp.route('/blender/test-connection', methods=['GET'])
@login_required
def test_blender_connection():
    """
    Test connection to Blender

    GET /api/3d-builder/blender/test-connection

    Returns:
    {
        "success": true,
        "message": "Connected to Blender",
        "scene_name": "Scene"
    }
    """
    try:
        with BlenderClient() as client:
            scene_info = client.get_scene_info()

            return jsonify({
                'success': True,
                'message': 'Connected to Blender',
                'scene_name': scene_info.get('name', 'Unknown'),
            })

    except BlenderConnectionError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 503

    except Exception as e:
        logger.error(f"Error testing Blender connection: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================================
# Real-time Event Stream (SSE)
# ============================================================================

@three_d_builder_bp.route('/events')
@login_required
def event_stream():
    """
    Server-Sent Events endpoint for real-time Blender updates

    Query params:
        session_id: Optional session filter (only receive events for this session)

    Returns:
        SSE stream with events:
        - proxy_created
        - proxy_updated
        - visibility_changed
        - transparency_changed
        - material_applied
        - scene_cleared
        - export_complete
        - batch_complete
        - error
    """
    from flask import Response, stream_with_context

    session_id = request.args.get('session_id')
    event_stream_instance = get_event_stream()

    # Register client
    client_id = event_stream_instance.add_client(session_id=session_id)
    logger.info(f"SSE client {client_id} connected (session: {session_id})")

    def generate():
        """Generate SSE events"""
        try:
            for event in event_stream_instance.stream_events(client_id):
                yield event
        except GeneratorExit:
            logger.info(f"SSE client {client_id} disconnected")
        except Exception as e:
            logger.error(f"Error streaming events to client {client_id}: {e}", exc_info=True)
        finally:
            event_stream_instance.remove_client(client_id)

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )


@three_d_builder_bp.route('/events/stats')
@login_required
def event_stream_stats():
    """
    Get event stream statistics

    Returns:
        JSON with connected clients count and details
    """
    stats = get_event_stream().get_stats()
    return jsonify({
        'success': True,
        'stats': stats
    })


# ============================================================================
# PUBLIC VIEWER (No login required)
# ============================================================================

@three_d_builder_bp.route('/viewer', methods=['GET'])
def blender_viewer():
    """
    Standalone Blender 3D Viewer

    Real-time streaming from Blender with archaeological data query interface.
    No authentication required - designed for Claude Desktop + Blender workflow.

    Features:
    - Real-time Socket.IO connection to Blender
    - Query archaeological data via REST API
    - Interactive 3D scene with Three.js
    - Site and US data browser

    GET /api/3d-builder/viewer

    Returns:
        HTML page with embedded viewer
    """
    return render_template('blender_viewer.html')


# ============================================================================
# PUBLIC API ENDPOINTS (For Claude Desktop / External Tools)
# ============================================================================

@three_d_builder_bp.route('/archaeological-data', methods=['GET'])
def get_archaeological_data():
    """
    Get archaeological data from currently connected database

    This endpoint is accessible without authentication to allow Claude Desktop
    and other external tools to query the database via HTTP.

    Query Parameters:
        site (str): Site name to filter data (optional, returns all sites if not specified)
        include_em (bool): Include Extended Matrix nodes (default: True)
        include_dimensions (bool): Include dimensional data (default: True)

    GET /api/3d-builder/archaeological-data?site=Tempio%20Fortuna&include_em=true

    Returns:
        JSON with complete archaeological dataset for 3D reconstruction:
        {
            "success": true,
            "database": {
                "type": "sqlite" | "postgresql",
                "connected": true
            },
            "sites": [...],
            "us_data": [...],
            "em_nodes": [...],
            "relationships": [...],
            "dimensions": {...}
        }
    """
    try:
        # Get query parameters
        site_filter = request.args.get('site', None)
        include_em = request.args.get('include_em', 'true').lower() == 'true'
        include_dimensions = request.args.get('include_dimensions', 'true').lower() == 'true'

        with get_db_session() as db_session:
            result = {
                'success': True,
                'database': {
                    'type': current_app.config.get('DB_TYPE', 'sqlite'),
                    'connected': True
                },
                'query_params': {
                    'site_filter': site_filter,
                    'include_em': include_em,
                    'include_dimensions': include_dimensions
                }
            }

            # Get sites
            if site_filter:
                sites = db_session.query(Site).filter(Site.sito == site_filter).all()
            else:
                sites = db_session.query(Site).all()

            result['sites'] = [{
                'id': site.id_sito,
                'nome': site.sito,
                'nazione': site.nazione,
                'regione': site.regione,
                'comune': site.comune,
                'descrizione': site.descrizione
            } for site in sites]

            # Get US data with complete information
            us_query = db_session.query(US)
            if site_filter:
                us_query = us_query.filter(US.sito == site_filter)

            us_list = us_query.order_by(US.us).all()

            result['us_data'] = [{
                'id_us': us.id_us,
                'sito': us.sito,
                'area': us.area,
                'us': us.us,
                'unita_tipo': getattr(us, 'unita_tipo', None),
                'descrizione': getattr(us, 'descrizione', None),
                'interpretazione': getattr(us, 'interpretazione', None),
                'd_stratigrafica': getattr(us, 'd_stratigrafica', None),
                'd_interpretativa': getattr(us, 'd_interpretativa', None),
                'unita_misura_lung': getattr(us, 'unita_misura_lung', None),
                'lunghezza_max': float(us.lunghezza_max) if hasattr(us, 'lunghezza_max') and us.lunghezza_max else None,
                'lunghezza_min': float(us.lunghezza_min) if hasattr(us, 'lunghezza_min') and us.lunghezza_min else None,
                'larghezza_media': float(us.larghezza_media) if hasattr(us, 'larghezza_media') and us.larghezza_media else None,
                'larghezza_max': float(us.larghezza_max) if hasattr(us, 'larghezza_max') and us.larghezza_max else None,
                'larghezza_min': float(us.larghezza_min) if hasattr(us, 'larghezza_min') and us.larghezza_min else None,
                'altezza_max': float(us.altezza_max) if hasattr(us, 'altezza_max') and us.altezza_max else None,
                'altezza_min': float(us.altezza_min) if hasattr(us, 'altezza_min') and us.altezza_min else None,
                'profondita_max': float(us.profondita_max) if hasattr(us, 'profondita_max') and us.profondita_max else None,
                'profondita_min': float(us.profondita_min) if hasattr(us, 'profondita_min') and us.profondita_min else None,
                'quota_relativa': float(us.quota_relativa) if hasattr(us, 'quota_relativa') and us.quota_relativa else None,
                'quota_abs': float(us.quota_abs) if hasattr(us, 'quota_abs') and us.quota_abs else None,
                'consistenza': getattr(us, 'consistenza', None),
                'colore': getattr(us, 'colore', None),
                'inclusi_materiali_usati': getattr(us, 'inclusi_materiali_usati', None),
                'dati_strutturali': getattr(us, 'dati_strutturali', None),
            } for us in us_list]

            # Get Extended Matrix nodes if requested
            if include_em:
                em_query = db_session.query(ExtendedMatrix)
                if site_filter:
                    em_query = em_query.filter(ExtendedMatrix.sito == site_filter)

                em_nodes = em_query.all()

                result['em_nodes'] = [{
                    'id': em.id,
                    'sito': em.sito,
                    'node_id': em.node_id,
                    'node_type': em.node_type,
                    'label': em.label,
                    'description': em.description,
                    'graphml_data': em.graphml_data if hasattr(em, 'graphml_data') else None,
                    'created_at': em.created_at.isoformat() if hasattr(em, 'created_at') and em.created_at else None
                } for em in em_nodes]

            # Add summary statistics
            result['summary'] = {
                'total_sites': len(result['sites']),
                'total_us': len(result['us_data']),
                'total_em_nodes': len(result.get('em_nodes', [])),
                'us_by_type': {}
            }

            # Count US by type
            for us in us_list:
                us_type = us.unita_tipo or 'Unknown'
                if us_type not in result['summary']['us_by_type']:
                    result['summary']['us_by_type'][us_type] = 0
                result['summary']['us_by_type'][us_type] += 1

            logger.info(f"Archaeological data request: site={site_filter}, returned {len(us_list)} US records")

            return jsonify(result)

    except Exception as e:
        logger.error(f"Error retrieving archaeological data: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }), 500


# ============================================================================
# CRUD Operations for US/USM
# ============================================================================

@three_d_builder_bp.route('/create-us', methods=['POST'])
@login_required
def create_us():
    """
    Create a new stratigraphic unit (US or USM)

    POST /api/3d-builder/create-us
    {
        "sito": "Tempio Fortuna",
        "area": "Area 1",
        "us": "13",
        "tipo": "us" | "usm",
        "d_stratigrafica": "Foundation layer",
        "d_interpretativa": "Temple foundation",
        "colore": "Brown",
        "consistenza": "Compact",
        "length": 5.5,
        "width": 3.2,
        "height": 0.8
    }
    """
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('sito') or not data.get('us'):
            return jsonify({
                'success': False,
                'error': 'Missing required fields: sito, us'
            }), 400

        with get_db_session() as db_session:
            # Check if US already exists
            existing = db_session.query(US).filter(
                US.sito == data['sito'],
                US.area == data.get('area', ''),
                US.us == int(data['us'])
            ).first()

            if existing:
                return jsonify({
                    'success': False,
                    'error': f'US {data["us"]} already exists for this site/area'
                }), 400

            # Create new US
            new_us = US()
            new_us.sito = data['sito']
            new_us.area = data.get('area', '')
            new_us.us = int(data['us'])
            new_us.unita_tipo = 'USM' if data.get('tipo') == 'usm' else 'US'
            new_us.d_stratigrafica = data.get('d_stratigrafica', '')
            new_us.d_interpretativa = data.get('d_interpretativa', '')
            new_us.colore = data.get('colore', '')
            new_us.consistenza = data.get('consistenza', '')

            # Set dimensions if provided
            if data.get('length'):
                new_us.length = float(data['length'])
            if data.get('width'):
                new_us.width = float(data['width'])
            if data.get('height'):
                new_us.height = float(data['height'])

            db_session.add(new_us)
            db_session.commit()

            logger.info(f"Created new US: {data['sito']}/{data.get('area')}/US{data['us']}")

            return jsonify({
                'success': True,
                'message': f'US {data["us"]} created successfully',
                'id_us': new_us.id_us
            })

    except ValueError as e:
        logger.error(f"Validation error creating US: {e}")
        return jsonify({
            'success': False,
            'error': f'Invalid data: {str(e)}'
        }), 400
    except Exception as e:
        logger.error(f"Error creating US: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@three_d_builder_bp.route('/update-us', methods=['POST'])
@login_required
def update_us():
    """
    Update an existing stratigraphic unit

    POST /api/3d-builder/update-us
    {
        "sito": "Tempio Fortuna",
        "area": "Area 1",
        "us": "13",
        "d_stratigrafica": "Updated description",
        "d_interpretativa": "Updated interpretation",
        "colore": "Dark Brown",
        "consistenza": "Very Compact",
        "length": 5.8,
        "width": 3.5,
        "height": 0.9
    }
    """
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('sito') or not data.get('us'):
            return jsonify({
                'success': False,
                'error': 'Missing required fields: sito, us'
            }), 400

        with get_db_session() as db_session:
            # Find existing US
            us_record = db_session.query(US).filter(
                US.sito == data['sito'],
                US.area == data.get('area', ''),
                US.us == int(data['us'])
            ).first()

            if not us_record:
                return jsonify({
                    'success': False,
                    'error': f'US {data["us"]} not found'
                }), 404

            # Update fields
            if 'd_stratigrafica' in data:
                us_record.d_stratigrafica = data['d_stratigrafica']
            if 'd_interpretativa' in data:
                us_record.d_interpretativa = data['d_interpretativa']
            if 'colore' in data:
                us_record.colore = data['colore']
            if 'consistenza' in data:
                us_record.consistenza = data['consistenza']

            # Update dimensions if provided
            if 'length' in data and data['length']:
                us_record.length = float(data['length'])
            if 'width' in data and data['width']:
                us_record.width = float(data['width'])
            if 'height' in data and data['height']:
                us_record.height = float(data['height'])

            db_session.commit()

            logger.info(f"Updated US: {data['sito']}/{data.get('area')}/US{data['us']}")

            return jsonify({
                'success': True,
                'message': f'US {data["us"]} updated successfully'
            })

    except ValueError as e:
        logger.error(f"Validation error updating US: {e}")
        return jsonify({
            'success': False,
            'error': f'Invalid data: {str(e)}'
        }), 400
    except Exception as e:
        logger.error(f"Error updating US: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@three_d_builder_bp.route('/delete-us', methods=['POST'])
@login_required
def delete_us():
    """
    Delete a stratigraphic unit

    POST /api/3d-builder/delete-us
    {
        "sito": "Tempio Fortuna",
        "area": "Area 1",
        "us": "13"
    }
    """
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('sito') or not data.get('us'):
            return jsonify({
                'success': False,
                'error': 'Missing required fields: sito, us'
            }), 400

        with get_db_session() as db_session:
            # Find existing US
            us_record = db_session.query(US).filter(
                US.sito == data['sito'],
                US.area == data.get('area', ''),
                US.us == int(data['us'])
            ).first()

            if not us_record:
                return jsonify({
                    'success': False,
                    'error': f'US {data["us"]} not found'
                }), 404

            # Delete the US
            db_session.delete(us_record)
            db_session.commit()

            logger.info(f"Deleted US: {data['sito']}/{data.get('area')}/US{data['us']}")

            return jsonify({
                'success': True,
                'message': f'US {data["us"]} deleted successfully'
            })

    except ValueError as e:
        logger.error(f"Validation error deleting US: {e}")
        return jsonify({
            'success': False,
            'error': f'Invalid data: {str(e)}'
        }), 400
    except Exception as e:
        logger.error(f"Error deleting US: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
