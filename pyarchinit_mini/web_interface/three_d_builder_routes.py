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
        if not graph or graph.number_of_nodes() == 0:
            logger.warning(f"No nodes found for site {site_name}")
            return None

        # Create temp file for GraphML
        temp_file = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.graphml',
            delete=False,
            dir='/tmp'
        )
        temp_path = temp_file.name
        temp_file.close()

        # Export to GraphML
        result_path = matrix_generator.export_to_graphml(
            graph=graph,
            output_path=temp_path,
            site_name=site_name,
            title=f"{site_name} - Harris Matrix (Auto-generated)",
            reverse_epochs=True
        )

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
                        'd_stratigr': u.d_stratigr,
                        'descrizione_us': u.descrizione_us
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
