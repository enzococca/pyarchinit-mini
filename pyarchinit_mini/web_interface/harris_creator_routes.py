#!/usr/bin/env python3
"""
Harris Matrix Interactive Creator Routes
========================================

Web-based visual editor for creating Harris Matrix diagrams.

Features:
- Drag-and-drop node creation
- Visual relationship connections
- Extended Matrix node type support
- Real-time preview
- Save to database
- Export to GraphML/DOT formats
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, session as flask_session, current_app
from sqlalchemy.orm import Session
from datetime import datetime
import json
import os
import logging

logger = logging.getLogger(__name__)

from pyarchinit_mini.services.relationship_sync_service import RelationshipSyncService
from pyarchinit_mini.config.em_node_config_manager import get_config_manager
from pyarchinit_mini.vocab.provider import VocabProvider
from pyarchinit_mini.graphml_io.writer import write_graphml
from pyarchinit_mini.graphproj.projector import GraphProjector

# Create Blueprint
harris_creator_bp = Blueprint('harris_creator', __name__, url_prefix='/harris-creator')

# Helper function to get database session
def get_db_session():
    """Get database session from Flask app context"""
    if hasattr(current_app, 'db_manager'):
        db_manager = current_app.db_manager
        return db_manager.connection.get_session()
    else:
        # Fallback: create connection from environment
        from pyarchinit_mini.database.connection import DatabaseConnection
        db_url = os.getenv("DATABASE_URL", "sqlite:///pyarchinit_mini.db")
        conn = DatabaseConnection.from_url(db_url)
        return conn.get_session()


@harris_creator_bp.route('/')
def index():
    """Show list of sites to choose from or create new"""
    from pyarchinit_mini.models.site import Site

    with get_db_session() as db:
        sites = db.query(Site).order_by(Site.sito).all()
        return render_template('harris_creator/index.html', sites=sites)


@harris_creator_bp.route('/editor')
def editor():
    """
    Harris Matrix visual editor

    Query parameters:
        site: Site name (optional, creates new if not exists)
        mode: 'new' or 'edit' (default: 'new')
    """
    from pyarchinit_mini.models.site import Site
    from pyarchinit_mini.models.us import US
    from pyarchinit_mini.models.harris_matrix import USRelationships

    site_name = request.args.get('site', '')
    mode = request.args.get('mode', 'new')

    if not site_name:
        flash('Please select or create a site first', 'warning')
        return redirect(url_for('harris_creator.index'))

    with get_db_session() as db:
        # Get or create site
        site = db.query(Site).filter_by(sito=site_name).first()

        if not site:
            site = Site(sito=site_name, definizione_sito='Created via Harris Matrix Creator')
            db.add(site)
            db.flush()
            flash(f'Created new site: {site_name}', 'success')

        # If editing, load existing matrix
        existing_nodes = []
        existing_relationships = []

        if mode == 'edit':
            # Load existing US nodes
            us_list = db.query(US).filter_by(sito=site_name).all()
            for us in us_list:
                existing_nodes.append({
                    'id': f'us_{us.us}',
                    'us_number': us.us,
                    'unit_type': us.unita_tipo or 'US',  # default per VocabProvider canonical types
                    'description': us.d_stratigrafica or '',
                    'area': us.area or '',
                    'period': us.periodo_iniziale or '',
                    'phase': us.fase_iniziale or '',
                    'datazione': us.datazione or '',  # datazione_estesa from periodizzazione
                    'file_path': us.file_path or ''
                })

            # Load relationships from the dedicated table
            relationships = db.query(USRelationships).filter_by(sito=site_name).all()
            for rel in relationships:
                existing_relationships.append({
                    'from_us': rel.us_from,
                    'to_us': rel.us_to,
                    'relationship': rel.relationship_type
                })
            # Fallback: when us_relationships_table is empty for this site
            # (data imported from QGIS pyarchinit only fills us.rapporti),
            # parse the rapporti field of each US as a python literal.
            if not existing_relationships:
                import ast
                for us in us_list:
                    rap = (us.rapporti or '').strip()
                    if not rap or rap in ('[]', 'null', 'None'):
                        continue
                    try:
                        parsed = ast.literal_eval(rap)
                    except Exception:
                        continue
                    if not isinstance(parsed, (list, tuple)):
                        continue
                    for item in parsed:
                        if not isinstance(item, (list, tuple)) or len(item) < 2:
                            continue
                        rel_type = str(item[0]).strip()
                        us_to = str(item[1]).strip()
                        if rel_type and us_to:
                            existing_relationships.append({
                                'from_us': str(us.us),
                                'to_us': us_to,
                                'relationship': rel_type,
                            })

        return render_template('harris_creator/editor.html',
                             site_name=site_name,
                             mode=mode,
                             existing_nodes=json.dumps(existing_nodes),
                             existing_relationships=json.dumps(existing_relationships))


@harris_creator_bp.route('/api/save', methods=['POST'])
def save_matrix():
    """
    Save Harris Matrix to database

    POST JSON body:
        {
            "site_name": "Site Name",
            "nodes": [
                {
                    "us_number": "1001",
                    "unit_type": "US",
                    "description": "...",
                    "area": "Area A",
                    "period": "Medieval",
                    "phase": "Late",
                    "file_path": ""
                },
                ...
            ],
            "relationships": [
                {
                    "from_us": "1001",
                    "to_us": "1002",
                    "relationship": "Covers"
                },
                ...
            ]
        }

    Returns:
        {
            "success": true,
            "message": "...",
            "nodes_created": 10,
            "relationships_created": 15
        }
    """
    # TODO(Spec-3): replace debug print() calls with logger.debug per
    # final review nit. Lines below contain prints kept from initial dev.

    # Debug logging
    print(f"[DEBUG] Content-Type: {request.content_type}")
    print(f"[DEBUG] Request data: {request.data}")

    data = request.get_json(force=True)  # Force JSON parsing even without Content-Type
    print(f"[DEBUG] Parsed data: {data}")

    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    site_name = data.get('site_name')
    nodes = data.get('nodes', [])
    relationships = data.get('relationships', [])

    print(f"[DEBUG] site_name: {site_name}")
    print(f"[DEBUG] nodes count: {len(nodes)}")
    print(f"[DEBUG] relationships count: {len(relationships)}")

    if not site_name:
        return jsonify({'success': False, 'message': 'Site name is required'}), 400

    from pyarchinit_mini.models.site import Site
    from pyarchinit_mini.models.us import US
    from pyarchinit_mini.models.harris_matrix import USRelationships, Periodizzazione

    try:
        # Use db_manager for proper model creation
        if not hasattr(current_app, 'db_manager'):
            return jsonify({'success': False, 'message': 'Database manager not available'}), 500

        db_manager = current_app.db_manager

        with db_manager.connection.get_session() as db:
            # Get or create site
            site = db.query(Site).filter_by(sito=site_name).first()
            if not site:
                site = Site(sito=site_name)
                db.add(site)
                db.flush()

            nodes_created = 0
            nodes_updated = 0

            # Save nodes
            for node_data in nodes:
                us_number = node_data.get('us_number')
                if not us_number:
                    continue

                # Check if exists
                us = db.query(US).filter_by(
                    sito=site_name,
                    us=us_number
                ).first()

                if us:
                    # Update existing US
                    nodes_updated += 1
                    us.unita_tipo = node_data.get('unit_type', 'US')  # default per VocabProvider canonical types
                    us.d_stratigrafica = node_data.get('description', '') if node_data.get('description') else None
                    us.area = node_data.get('area', '') if node_data.get('area') else None
                    us.periodo_iniziale = node_data.get('period', '') if node_data.get('period') else None
                    us.fase_iniziale = node_data.get('phase', '') if node_data.get('phase') else None
                    us.file_path = node_data.get('file_path', '') if node_data.get('file_path') else None
                else:
                    # Create new US - id_us is auto-incremented by database
                    nodes_created += 1

                    us_create_data = {
                        # Do NOT set id_us - it's auto-incremented by the database
                        'sito': site_name,
                        'us': us_number,
                        'unita_tipo': node_data.get('unit_type', 'US'),  # default per VocabProvider canonical types
                        'd_stratigrafica': node_data.get('description', '') if node_data.get('description') else None,
                        'area': node_data.get('area', '') if node_data.get('area') else None,
                        'periodo_iniziale': node_data.get('period', '') if node_data.get('period') else None,
                        'fase_iniziale': node_data.get('phase', '') if node_data.get('phase') else None,
                        'file_path': node_data.get('file_path', '') if node_data.get('file_path') else None
                    }
                    us = db_manager.create(US, us_create_data)

                # Create or update periodizzazione record if period/phase are specified
                periodo = node_data.get('period', '')
                fase = node_data.get('phase', '')

                if periodo or fase:
                    # Create datazione_estesa
                    if periodo and fase:
                        datazione_estesa = f"{periodo} - {fase}"
                    elif periodo:
                        datazione_estesa = periodo
                    else:
                        datazione_estesa = fase

                    # Check if periodizzazione exists
                    periodizzazione = db.query(Periodizzazione).filter_by(
                        sito=site_name,
                        us=us_number
                    ).first()

                    if periodizzazione:
                        # Update existing
                        periodizzazione.periodo_iniziale = periodo if periodo else None
                        periodizzazione.fase_iniziale = fase if fase else None
                        periodizzazione.datazione_estesa = datazione_estesa
                        periodizzazione.area = node_data.get('area', '') or None
                    else:
                        # Create new
                        periodizzazione = Periodizzazione(
                            sito=site_name,
                            area=node_data.get('area', '') or None,
                            us=us_number,
                            periodo_iniziale=periodo if periodo else None,
                            fase_iniziale=fase if fase else None,
                            datazione_estesa=datazione_estesa
                        )
                        db.add(periodizzazione)

            db.flush()

            relationships_created = 0
            relationships_updated = 0

            # Save relationships
            for rel_data in relationships:
                from_us = rel_data.get('from_us')
                to_us = rel_data.get('to_us')
                rel_type = rel_data.get('relationship')

                if not all([from_us, to_us, rel_type]):
                    continue

                # Check if exists
                existing_rel = db.query(USRelationships).filter_by(
                    sito=site_name,
                    us_from=from_us,
                    us_to=to_us
                ).first()

                if existing_rel:
                    existing_rel.relationship_type = rel_type
                    relationships_updated += 1
                else:
                    relationship = USRelationships(
                        sito=site_name,
                        us_from=from_us,
                        us_to=to_us,
                        relationship_type=rel_type
                    )
                    db.add(relationship)
                    relationships_created += 1

            # Synchronize us_relationships_table to rapporti field for all affected US
            try:
                # Get list of all US numbers that have relationships
                affected_us = set()
                for rel in db.query(USRelationships).filter_by(sito=site_name).all():
                    affected_us.add(rel.us_from)

                # Update rapporti field for each US
                from pyarchinit_mini.models.us import US
                sync_service = RelationshipSyncService(current_app.db_manager)

                for us_number in affected_us:
                    rapporti_text = sync_service.sync_relationships_table_to_rapporti(
                        sito=site_name,
                        us_number=us_number,
                        session=db
                    )

                    # Update the us_table.rapporti field
                    us_record = db.query(US).filter_by(sito=site_name, us=us_number).first()
                    if us_record:
                        us_record.rapporti = rapporti_text

                db.flush()

            except Exception as sync_error:
                print(f"Warning: Failed to sync relationships to rapporti field: {sync_error}")

            # Explicitly commit all changes
            db.commit()

            # Spec 2: auto-regen stratigraphy.graphml after Harris Creator save.
            # Best-effort; _trigger_graph_regen already catches its own errors.
            try:
                from pyarchinit_mini.graphproj.auto_regen import _trigger_graph_regen
                _trigger_graph_regen(site_name, session=db)
            except Exception:
                pass

            return jsonify({
                'success': True,
                'message': f'Successfully saved Harris Matrix',
                'nodes_created': nodes_created,
                'nodes_updated': nodes_updated,
                'relationships_created': relationships_created,
                'relationships_updated': relationships_updated
            })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@harris_creator_bp.route('/api/export/<format>')
def export_matrix(format):
    """
    Export Harris Matrix to GraphML or DOT format

    Query parameters:
        site: Site name (required)

    Returns:
        File download of the exported matrix
    """
    site_name = request.args.get('site')

    if not site_name:
        return jsonify({'success': False, 'message': 'Site name is required'}), 400

    if format not in ['graphml', 'dot']:
        return jsonify({'success': False, 'message': 'Invalid format. Use "graphml" or "dot"'}), 400

    try:
        with get_db_session() as db:
            # Export
            import tempfile
            from pathlib import Path as _Path
            output_dir = tempfile.mkdtemp()
            base_name = site_name.replace(' ', '_').replace('/', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{base_name}_{timestamp}.{format}"
            output_path = os.path.join(output_dir, filename)

            if format == 'graphml':
                # Build s3dgraphy.Graph via GraphProjector then write with
                # graphml_io.writer (bypasses the GraphMLBuilder.to_string bug).
                graph = GraphProjector.populate_graph(db, site_name)

                if not graph.nodes:
                    return jsonify({'success': False, 'message': 'No nodes found for this site'}), 404

                write_graphml(graph, _Path(output_path))
            else:  # dot
                # DOT export: build networkx graph via HarrisMatrixGenerator
                # and delegate to GraphMLExporter (no GraphMLBuilder involved).
                from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator
                from pyarchinit_mini.graphml_converter.graphml_exporter import GraphMLExporter

                if hasattr(current_app, 'db_manager'):
                    db_manager = current_app.db_manager
                    from pyarchinit_mini.services.us_service import USService
                    us_service = USService(db_manager)
                    generator = HarrisMatrixGenerator(db_manager, us_service)
                else:
                    from pyarchinit_mini.database.manager import DatabaseManager
                    from pyarchinit_mini.database.connection import DatabaseConnection
                    from pyarchinit_mini.services.us_service import USService
                    db_url = os.getenv("DATABASE_URL", "sqlite:///pyarchinit_mini.db")
                    conn = DatabaseConnection.from_url(db_url)
                    db_manager = DatabaseManager(conn)
                    us_service = USService(db_manager)
                    generator = HarrisMatrixGenerator(db_manager, us_service)

                nx_graph = generator.generate_matrix(site_name)

                if not nx_graph or nx_graph.number_of_nodes() == 0:
                    return jsonify({'success': False, 'message': 'No nodes found for this site'}), 404

                exporter = GraphMLExporter()
                dot_path = output_path.replace('.dot', '') + '.dot'
                try:
                    exporter.export_to_dot(nx_graph, dot_path, site_name=site_name)
                    output_path = dot_path
                except Exception as e:
                    return jsonify({'success': False, 'message': f'DOT export failed: {str(e)}'}), 500

            # Send file
            from flask import send_file
            return send_file(
                output_path,
                as_attachment=True,
                download_name=filename,
                mimetype='application/xml' if format == 'graphml' else 'text/plain'
            )

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@harris_creator_bp.route('/api/node-types')
def get_node_types():
    """
    Get list of Extended Matrix node types with descriptions
    Now dynamically loaded from YAML configuration
    """
    # Map GraphML/yEd shapes to Cytoscape.js compatible shapes
    SHAPE_MAP = {
        'note': 'roundrectangle',      # Document shape -> rounded rectangle
        'trapezium': 'triangle',        # Trapezoid -> triangle
        'trapezium2': 'vee',            # Inverted trapezoid -> vee
        'parallelogram': 'rhomboid',    # Parallelogram -> rhomboid
        # Valid Cytoscape shapes pass through unchanged
        'rectangle': 'rectangle',
        'roundrectangle': 'roundrectangle',
        'ellipse': 'ellipse',
        'triangle': 'triangle',
        'pentagon': 'pentagon',
        'hexagon': 'hexagon',
        'heptagon': 'heptagon',
        'octagon': 'octagon',
        'star': 'star',
        'diamond': 'diamond',
        'vee': 'vee',
        'rhomboid': 'rhomboid'
    }

    try:
        config_manager = get_config_manager()
        all_types = config_manager.get_all_node_types()

        # Default colors for visual editor (can be customized in config)
        default_colors = {
            'US': '#90CAF9', 'USM': '#FFAB91', 'USVA': '#CE93D8',
            'USVB': '#E1BEE7', 'USVC': '#F48FB1', 'TU': '#80CBC4',
            'USD': '#A5D6A7', 'SF': '#FFD54F', 'VSF': '#FFE082',
            'CON': '#BCAAA4', 'DOC': '#B0BEC5', 'Extractor': '#EF9A9A',
            'Combinar': '#9FA8DA', 'property': '#CFD8DC'
        }

        node_types = []
        for tipo_id, config in all_types.items():
            visual = config.get('visual', {})

            # Build label
            label = f"{tipo_id} - {config.get('name', tipo_id)}"
            if config.get('description'):
                label += f" ({config.get('description')})"

            # Get shape from config and map to Cytoscape-compatible shape
            config_shape = visual.get('shape', 'rectangle')
            cytoscape_shape = SHAPE_MAP.get(config_shape, 'rectangle')

            node_types.append({
                'value': tipo_id,
                'label': label,
                'color': default_colors.get(tipo_id, '#B0BEC5'),  # Use default or gray
                'shape': cytoscape_shape,
                'custom': config.get('custom', False)
            })

        return jsonify(node_types)

    except Exception as e:
        # Fallback to minimal list if config fails
        return jsonify([
            {'value': 'US', 'label': 'US - Standard Stratigraphic Unit', 'color': '#90CAF9', 'shape': 'rectangle'}
        ])


@harris_creator_bp.route('/api/relationship-types')
def get_relationship_types():
    """Get list of relationship types with descriptions, localized by current language"""
    from pyarchinit_mini.i18n import get_locale
    try:
        lang = get_locale()
    except Exception:
        lang = 'it'

    if lang == 'en':
        relationship_types = [
            {'value': 'Covers', 'label': 'Covers', 'symbol': 'Covers', 'style': 'solid', 'arrow': 'triangle'},
            {'value': 'Covered_by', 'label': 'Covered by', 'symbol': 'Covered by', 'style': 'solid', 'arrow': 'triangle'},
            {'value': 'Fills', 'label': 'Fills', 'symbol': 'Fills', 'style': 'solid', 'arrow': 'triangle'},
            {'value': 'Filled_by', 'label': 'Filled by', 'symbol': 'Filled by', 'style': 'solid', 'arrow': 'triangle'},
            {'value': 'Cuts', 'label': 'Cuts', 'symbol': 'Cuts', 'style': 'dashed', 'arrow': 'triangle'},
            {'value': 'Cut_by', 'label': 'Cut by', 'symbol': 'Cut by', 'style': 'dashed', 'arrow': 'triangle'},
            {'value': 'Bonds_to', 'label': 'Connected to', 'symbol': 'Connected to', 'style': 'solid', 'arrow': 'triangle'},
            {'value': 'Equal_to', 'label': 'Same as', 'symbol': 'Same as', 'style': 'solid', 'arrow': 'triangle'},
            {'value': 'Leans_on', 'label': 'Supports', 'symbol': 'Supports', 'style': 'solid', 'arrow': 'triangle'},
            {'value': '>', 'label': '> - Connection to single-symbol unit', 'symbol': '>', 'style': 'dotted', 'arrow': 'triangle'},
            {'value': '<', 'label': '< - From single-symbol unit', 'symbol': '<', 'style': 'dotted', 'arrow': 'triangle'},
            {'value': '>>', 'label': '>> - Connection to double-symbol unit', 'symbol': '>>', 'style': 'dotted', 'arrow': 'triangle'},
            {'value': '<<', 'label': '<< - From double-symbol unit', 'symbol': '<<', 'style': 'dotted', 'arrow': 'triangle'},
            {'value': 'Continuity', 'label': 'Continuity (contemporary units)', 'symbol': 'Continuity', 'style': 'solid', 'arrow': 'none'},
        ]
    else:
        relationship_types = [
            {'value': 'Covers', 'label': 'Copre (sopra)', 'symbol': 'Copre', 'style': 'solid', 'arrow': 'triangle'},
            {'value': 'Covered_by', 'label': 'Coperto da (sotto)', 'symbol': 'Coperto da', 'style': 'solid', 'arrow': 'triangle'},
            {'value': 'Fills', 'label': 'Riempie', 'symbol': 'Riempie', 'style': 'solid', 'arrow': 'triangle'},
            {'value': 'Filled_by', 'label': 'Riempito da', 'symbol': 'Riempito da', 'style': 'solid', 'arrow': 'triangle'},
            {'value': 'Cuts', 'label': 'Taglia', 'symbol': 'Taglia', 'style': 'dashed', 'arrow': 'triangle'},
            {'value': 'Cut_by', 'label': 'Tagliato da', 'symbol': 'Tagliato da', 'style': 'dashed', 'arrow': 'triangle'},
            {'value': 'Bonds_to', 'label': 'Si lega a', 'symbol': 'Si lega a', 'style': 'solid', 'arrow': 'triangle'},
            {'value': 'Equal_to', 'label': 'Uguale a', 'symbol': 'Uguale a', 'style': 'solid', 'arrow': 'triangle'},
            {'value': 'Leans_on', 'label': 'Si appoggia a', 'symbol': 'Si appoggia a', 'style': 'solid', 'arrow': 'triangle'},
            {'value': '>', 'label': '> - Connessione a unità simbolo singolo', 'symbol': '>', 'style': 'dotted', 'arrow': 'triangle'},
            {'value': '<', 'label': '< - Da unità simbolo singolo', 'symbol': '<', 'style': 'dotted', 'arrow': 'triangle'},
            {'value': '>>', 'label': '>> - Connessione a unità simbolo doppio', 'symbol': '>>', 'style': 'dotted', 'arrow': 'triangle'},
            {'value': '<<', 'label': '<< - Da unità simbolo doppio', 'symbol': '<<', 'style': 'dotted', 'arrow': 'triangle'},
            {'value': 'Continuity', 'label': 'Continuità (unità contemporanee)', 'symbol': 'Continuità', 'style': 'solid', 'arrow': 'none'},
        ]
    return jsonify(relationship_types)


@harris_creator_bp.route('/api/periods')
def get_periods():
    """Get list of periods and phases from period_table"""
    try:
        from pyarchinit_mini.models.harris_matrix import Period
        from sqlalchemy import text as sa_text

        with get_db_session() as db:
            # Use raw SQL to avoid ORM touching BaseModel columns not yet migrated
            rows = db.execute(
                sa_text("SELECT period_name, phase_name FROM period_table ORDER BY period_name, phase_name")
            ).fetchall()

            periods_dict = {}
            for row in rows:
                period_name = row[0] or ''
                phase_name = row[1] or ''
                if not period_name:
                    continue
                if period_name not in periods_dict:
                    periods_dict[period_name] = {'period': period_name, 'phases': []}
                if phase_name and phase_name not in periods_dict[period_name]['phases']:
                    periods_dict[period_name]['phases'].append(phase_name)

            return jsonify(list(periods_dict.values()))

    except Exception as e:
        logger.warning(f"get_periods failed (non-fatal): {e}")
        return jsonify([])  # Return empty list — periods dropdown is optional


# === Spec 3-bis: Harris Swimlane Editor endpoints ===

from flask import g

from pyarchinit_mini.harris_swimlane.row_provider import RowProvider
from pyarchinit_mini.harris_swimlane.swimlane_state import SwimlaneState
from pyarchinit_mini.harris_swimlane.exceptions import SwimlaneError, RowProviderError
from pyarchinit_mini.harris_swimlane.period_sync_service import PeriodSyncService
from pyarchinit_mini.harris_swimlane.exceptions import PeriodSyncError


def _get_session():
    """Get the request-bound SQLAlchemy session.

    Requires the Flask app to set g.db_session in a before_request hook
    (the production app does this; tests do too). Raises if not set —
    fails loud rather than silently returning a context-manager generator
    that downstream callers will treat as a Session.
    """
    db = getattr(g, "db_session", None)
    if db is None:
        raise RuntimeError(
            "g.db_session not set. The Flask app must set it in a "
            "before_request hook before invoking Spec 3-bis endpoints."
        )
    return db


@harris_creator_bp.get("/api/swimlanes/<site>")
def api_get_swimlanes(site: str):
    """List swimlane rows for the site."""
    try:
        session = _get_session()
        provider = RowProvider(session, site)
        rows = provider.list_rows()
        return jsonify([{
            "row_id": r.row_id,
            "period_name": r.period_name,
            "phase_name": r.phase_name,
            "start_date": r.start_date,
            "end_date": r.end_date,
            "color": r.color,
            "source": r.source,
        } for r in rows]), 200
    except RowProviderError as e:
        return jsonify({"error": "row_provider", "message": str(e)}), 500
    except Exception as e:
        logger.exception("api_get_swimlanes failed")
        return jsonify({"error": "internal", "message": str(e)}), 500


@harris_creator_bp.get("/api/load/<site>")
def api_load_state(site: str):
    """Load full editor state (rows + nodes + edges) as Cytoscape JSON."""
    try:
        session = _get_session()
        state = SwimlaneState.load(session, site)
        return jsonify({
            "site": state.site,
            "rows": [{
                "row_id": r.row_id,
                "period_name": r.period_name,
                "phase_name": r.phase_name,
                "color": r.color,
                "start_date": r.start_date,
                "end_date": r.end_date,
                "source": r.source,
            } for r in state.rows],
            "nodes": [{
                "data": el.data,
                "classes": el.classes,
                "position": el.position,
            } for el in state.nodes],
            "edges": [{
                "data": el.data,
                "classes": el.classes,
            } for el in state.edges],
            "pending_changes": state.pending_changes,
        }), 200
    except SwimlaneError as e:
        return jsonify({"error": "swimlane", "message": str(e)}), 500
    except Exception as e:
        logger.exception("api_load_state failed")
        return jsonify({"error": "internal", "message": str(e)}), 500


@harris_creator_bp.post("/api/save/<site>")
def api_save_state(site: str):
    """Save pending_changes for site. Triggers Spec 2 auto_regen on success."""
    try:
        payload = request.get_json(silent=True) or {}
        session = _get_session()
        result = SwimlaneState.save(session, site, payload)
        return jsonify({
            "updated": result.updated,
            "inserted": result.inserted,
            "deleted": result.deleted,
            "errors": list(result.errors),
        }), 200
    except SwimlaneError as e:
        return jsonify({"error": "swimlane", "message": str(e)}), 500
    except Exception as e:
        logger.exception("api_save_state failed")
        return jsonify({"error": "internal", "message": str(e)}), 500


@harris_creator_bp.post("/api/swimlanes/<site>")
def api_create_row(site: str):
    """Create a new swimlane row (upsert period_table). site param is for
    URL consistency; period_table is currently cross-site."""
    payload = request.get_json(silent=True) or {}
    period_name = payload.get("period_name", "")
    phase_name = payload.get("phase_name") or None
    start_date = payload.get("start_date")
    end_date = payload.get("end_date")
    try:
        session = _get_session()
        svc = PeriodSyncService(session)
        row = svc.upsert_row(
            period_name=period_name, phase_name=phase_name,
            start_date=start_date, end_date=end_date,
        )
        return jsonify({
            "row_id": row.row_id,
            "period_name": row.period_name,
            "phase_name": row.phase_name,
            "start_date": row.start_date,
            "end_date": row.end_date,
            "color": row.color,
            "source": row.source,
        }), 201
    except PeriodSyncError as e:
        return jsonify({
            "error": "validation",
            "message": str(e),
            "period_name": e.period_name,
            "phase_name": e.phase_name,
        }), 400
    except Exception as e:
        logger.exception("api_create_row failed")
        return jsonify({"error": "internal", "message": str(e)}), 500


from pathlib import Path as _Path
from datetime import datetime as _datetime
import json as _json
from flask import send_file as _send_file

from pyarchinit_mini.graphml_io.yed_writer import write_yed_graphml
from pyarchinit_mini.harris_swimlane.exceptions import YEDWriterError
from pyarchinit_mini.graphproj.filesystem import slugify


@harris_creator_bp.get("/api/export/<site>/yed-graphml")
def api_export_yed(site: str):
    """Export current swimlane state as yEd-flavored GraphML. On-demand."""
    try:
        session = _get_session()
        state = SwimlaneState.load(session, site)

        out_dir = _Path("data/exports/harris_yed")
        out_dir.mkdir(parents=True, exist_ok=True)
        site_slug = slugify(site)
        out_path = out_dir / f"{site_slug}-harris-yed.graphml"
        write_yed_graphml(state, out_path)

        idx_path = out_dir / "_index.json"
        entries = []
        if idx_path.exists():
            try:
                entries = _json.loads(idx_path.read_text(encoding="utf-8"))
            except Exception:
                entries = []
        entries.append({
            "site": site,
            "site_slug": site_slug,
            "file_path": str(out_path),
            "file_size": out_path.stat().st_size,
            "timestamp": _datetime.now().isoformat(),
        })
        idx_path.write_text(_json.dumps(entries, indent=2), encoding="utf-8")

        return _send_file(
            out_path.resolve(),
            as_attachment=True,
            download_name=f"{site_slug}-harris-yed.graphml",
            mimetype="application/xml",
        )
    except YEDWriterError as e:
        return jsonify({"error": "yed_writer", "message": str(e)}), 500
    except SwimlaneError as e:
        return jsonify({"error": "swimlane", "message": str(e)}), 500
    except Exception as e:
        logger.exception("api_export_yed failed")
        return jsonify({"error": "internal", "message": str(e)}), 500