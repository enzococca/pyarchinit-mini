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

from pyarchinit_mini.services.relationship_sync_service import RelationshipSyncService
from pyarchinit_mini.config.em_node_config_manager import get_config_manager

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
                    'unit_type': us.unita_tipo or 'US',
                    'description': us.d_stratigrafica or '',
                    'area': us.area or '',
                    'period': us.periodo_iniziale or '',
                    'phase': us.fase_iniziale or '',
                    'datazione': us.datazione or '',  # datazione_estesa from periodizzazione
                    'file_path': us.file_path or ''
                })

            # Load relationships
            relationships = db.query(USRelationships).filter_by(sito=site_name).all()
            for rel in relationships:
                existing_relationships.append({
                    'from_us': rel.us_from,
                    'to_us': rel.us_to,
                    'relationship': rel.relationship_type
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
                    us.unita_tipo = node_data.get('unit_type', 'US')
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
                        'unita_tipo': node_data.get('unit_type', 'US'),
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

    from pyarchinit_mini.harris_matrix.matrix_generator import HarrisMatrixGenerator

    try:
        with get_db_session() as db:
            # Generate matrix
            # Note: HarrisMatrixGenerator expects a DatabaseManager and USService
            # We'll use the app's db_manager if available
            if hasattr(current_app, 'db_manager'):
                db_manager = current_app.db_manager
                from pyarchinit_mini.services.us_service import USService
                us_service = USService(db_manager)
                generator = HarrisMatrixGenerator(db_manager, us_service)
            else:
                # Fallback: create temporary manager
                from pyarchinit_mini.database.manager import DatabaseManager
                from pyarchinit_mini.database.connection import DatabaseConnection
                from pyarchinit_mini.services.us_service import USService
                db_url = os.getenv("DATABASE_URL", "sqlite:///pyarchinit_mini.db")
                conn = DatabaseConnection.from_url(db_url)
                db_manager = DatabaseManager(conn)
                us_service = USService(db_manager)
                generator = HarrisMatrixGenerator(db_manager, us_service)

            graph = generator.generate_matrix(site_name)

            if not graph or graph.number_of_nodes() == 0:
                return jsonify({'success': False, 'message': 'No nodes found for this site'}), 404

            # Export
            import tempfile
            output_dir = tempfile.mkdtemp()
            base_name = site_name.replace(' ', '_').replace('/', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{base_name}_{timestamp}.{format}"
            output_path = os.path.join(output_dir, filename)

            if format == 'graphml':
                # export_to_graphml returns the path (or empty string on error)
                result_path = generator.export_to_graphml(
                    graph=graph,
                    output_path=output_path,
                    use_extended_labels=True,
                    site_name=site_name,
                    include_periods=True
                )
                if not result_path:
                    return jsonify({'success': False, 'message': 'GraphML export failed'}), 500
            else:  # dot
                # For DOT, use graphml_exporter directly
                from pyarchinit_mini.graphml_converter.graphml_exporter import GraphMLExporter
                exporter = GraphMLExporter()
                dot_path = output_path.replace('.dot', '') + '.dot'
                try:
                    exporter.export_to_dot(graph, dot_path, site_name=site_name)
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
    """Get list of relationship types with descriptions"""
    relationship_types = [
        # Standard stratigraphic relationships
        {'value': 'Covers', 'label': 'Covers (above/sopra)', 'symbol': 'Copre', 'style': 'solid', 'arrow': 'triangle'},
        {'value': 'Covered_by', 'label': 'Covered by (below/sotto)', 'symbol': 'Coperto da', 'style': 'solid', 'arrow': 'triangle'},
        {'value': 'Fills', 'label': 'Fills (riempie)', 'symbol': 'Riempie', 'style': 'solid', 'arrow': 'triangle'},
        {'value': 'Filled_by', 'label': 'Filled by (riempito da)', 'symbol': 'Riempito da', 'style': 'solid', 'arrow': 'triangle'},
        {'value': 'Cuts', 'label': 'Cuts (taglia)', 'symbol': 'Taglia', 'style': 'dashed', 'arrow': 'triangle'},
        {'value': 'Cut_by', 'label': 'Cut by (tagliato da)', 'symbol': 'Tagliato da', 'style': 'dashed', 'arrow': 'triangle'},
        {'value': 'Bonds_to', 'label': 'Bonds to (si lega a)', 'symbol': 'Si lega a', 'style': 'solid', 'arrow': 'triangle'},
        {'value': 'Equal_to', 'label': 'Equal to (uguale a)', 'symbol': 'Uguale a', 'style': 'solid', 'arrow': 'triangle'},
        {'value': 'Leans_on', 'label': 'Leans on (si appoggia a)', 'symbol': 'Si appoggia a', 'style': 'solid', 'arrow': 'triangle'},

        # Extended Matrix symbols
        {'value': '>', 'label': '> - Connection to single-symbol unit', 'symbol': '>', 'style': 'dotted', 'arrow': 'triangle'},
        {'value': '<', 'label': '< - From single-symbol unit', 'symbol': '<', 'style': 'dotted', 'arrow': 'triangle'},
        {'value': '>>', 'label': '>> - Connection to double-symbol unit', 'symbol': '>>', 'style': 'dotted', 'arrow': 'triangle'},
        {'value': '<<', 'label': '<< - From double-symbol unit', 'symbol': '<<', 'style': 'dotted', 'arrow': 'triangle'},

        # Special
        {'value': 'Continuity', 'label': 'Continuity (contemporary units)', 'symbol': 'Continuity', 'style': 'solid', 'arrow': 'none'},
    ]
    return jsonify(relationship_types)


@harris_creator_bp.route('/api/periods')
def get_periods():
    """Get list of periods and phases from period_table"""
    from pyarchinit_mini.models.harris_matrix import Period

    with get_db_session() as db:
        periods = db.query(Period).order_by(Period.period_name, Period.phase_name).all()

        # Group by period_name
        periods_dict = {}
        for period in periods:
            period_name = period.period_name
            phase_name = period.phase_name or ''

            if period_name not in periods_dict:
                periods_dict[period_name] = {
                    'period': period_name,
                    'phases': []
                }

            if phase_name and phase_name not in periods_dict[period_name]['phases']:
                periods_dict[period_name]['phases'].append(phase_name)

        # Convert to list
        result = []
        for period_data in periods_dict.values():
            result.append(period_data)

        return jsonify(result)