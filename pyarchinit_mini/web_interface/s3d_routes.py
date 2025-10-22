"""
3D Model Viewer Routes for PyArchInit-Mini Web Interface
"""

from flask import Blueprint, render_template, request, send_file, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
from pathlib import Path

# Import s3d integration
import sys
sys.path.append('..')
from pyarchinit_mini.s3d_integration import S3DConverter, Model3DManager

# Create blueprint
s3d_bp = Blueprint('s3d', __name__, url_prefix='/3d')


def init_s3d_routes(app, db_manager, media_handler):
    """Initialize 3D routes with app context"""

    # Initialize Model3DManager with absolute path
    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    # Convert to absolute path if relative
    upload_folder_abs = Path(upload_folder)
    if not upload_folder_abs.is_absolute():
        # If path starts with web_interface/, remove it since we're already in that dir
        if upload_folder.startswith('web_interface/'):
            upload_folder = upload_folder.replace('web_interface/', '', 1)
        # Make absolute using Flask app root
        upload_folder_abs = Path(app.root_path) / upload_folder

    model_manager = Model3DManager(str(upload_folder_abs))

    @s3d_bp.route('/model/<path:model_path>')
    @login_required
    def viewer(model_path):
        """
        Display 3D model viewer

        Args:
            model_path: Relative path to the 3D model
        """
        # Get model metadata from path
        parts = Path(model_path).parts
        site_name = parts[1] if len(parts) > 1 else 'Unknown'
        us_folder = parts[2] if len(parts) > 2 else None
        filename = parts[-1]

        us_name = None
        if us_folder and us_folder.startswith('US_'):
            us_name = us_folder.replace('US_', '')

        # Get model file info
        model_file = Path(upload_folder) / model_path
        model_size = model_file.stat().st_size if model_file.exists() else 0
        model_format = model_file.suffix.lower()[1:]  # Remove dot

        # Get site ID for back button
        site_id = None
        try:
            from pyarchinit_mini.models.site import Site as SiteModel
            with db_manager.connection.get_session() as session:
                site = session.query(SiteModel).filter(
                    SiteModel.sito == site_name
                ).first()
                if site:
                    site_id = site.id_sito
        except Exception as e:
            print(f"Error getting site ID: {e}")

        return render_template(
            '3d_viewer/viewer.html',
            model_url=f'/static/uploads/{model_path}',
            download_url=f'/static/uploads/{model_path}',
            site_name=site_name,
            us_name=us_name,
            filename=filename,
            model_format=model_format,
            model_size=model_size,
            site_id=site_id
        )

    @s3d_bp.route('/upload', methods=['POST'])
    @login_required
    def upload_model():
        """Upload 3D model for a US or site"""
        if 'model_file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['model_file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Get metadata
        site_name = request.form.get('site_name')
        us_id = request.form.get('us_id')

        if not site_name:
            return jsonify({'error': 'Site name is required'}), 400

        # Check if file is a 3D model
        if not model_manager.is_3d_model(file.filename):
            return jsonify({'error': 'Invalid 3D model format'}), 400

        try:
            # Save file temporarily
            filename = secure_filename(file.filename)
            temp_path = Path(app.config['UPLOAD_FOLDER']) / 'temp' / filename
            temp_path.parent.mkdir(parents=True, exist_ok=True)
            file.save(str(temp_path))

            # Save model using Model3DManager
            model_metadata = model_manager.save_model(
                str(temp_path),
                us_id=us_id,
                site_name=site_name
            )

            # Remove temp file
            temp_path.unlink()

            # Return success with viewer URL
            viewer_url = url_for('s3d.viewer', model_path=model_metadata['path'])

            return jsonify({
                'success': True,
                'message': '3D model uploaded successfully',
                'model': model_metadata,
                'viewer_url': viewer_url
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @s3d_bp.route('/models/<site_name>')
    @login_required
    def list_models(site_name):
        """List all 3D models for a site"""
        try:
            models = model_manager.get_models_for_site(site_name)
            return jsonify({
                'success': True,
                'site': site_name,
                'models': models
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @s3d_bp.route('/models/<site_name>/us/<us_id>')
    @login_required
    def list_us_models(site_name, us_id):
        """List all 3D models for a specific US"""
        try:
            models = model_manager.get_models_for_us(us_id, site_name)
            return jsonify({
                'success': True,
                'site': site_name,
                'us': us_id,
                'models': models
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @s3d_bp.route('/export/graphml/<site_name>')
    @login_required
    def export_graphml(site_name):
        """Export site stratigraphy as s3dgraphy GraphML"""
        try:
            # Get all US for the site
            from pyarchinit_mini.models.us import US as USModel
            with db_manager.connection.get_session() as session:
                us_list = session.query(USModel).filter(
                    USModel.sito == site_name
                ).all()

                # Convert to dictionaries
                us_data = []
                for us in us_list:
                    us_dict = {}
                    for column in us.__table__.columns:
                        us_dict[column.name] = getattr(us, column.name)
                    us_data.append(us_dict)

            # Create s3dgraphy graph
            converter = S3DConverter()
            graph = converter.create_graph_from_us(us_data, site_name)

            # Export to GraphML
            output_path = Path(app.config['UPLOAD_FOLDER']) / 'graphml' / f"{site_name}_stratigraphy.graphml"
            output_path.parent.mkdir(parents=True, exist_ok=True)

            converter.export_to_graphml(graph, str(output_path))

            # Send file
            return send_file(
                str(output_path),
                as_attachment=True,
                download_name=f"{site_name}_stratigraphy.graphml",
                mimetype='application/xml'
            )

        except Exception as e:
            flash(f'Error exporting GraphML: {str(e)}', 'error')
            return redirect(request.referrer or url_for('index'))

    @s3d_bp.route('/export/json/<site_name>')
    @login_required
    def export_json(site_name):
        """Export site stratigraphy as s3dgraphy JSON"""
        try:
            # Get all US for the site
            from pyarchinit_mini.models.us import US as USModel
            with db_manager.connection.get_session() as session:
                us_list = session.query(USModel).filter(
                    USModel.sito == site_name
                ).all()

                # Convert to dictionaries
                us_data = []
                for us in us_list:
                    us_dict = {}
                    for column in us.__table__.columns:
                        us_dict[column.name] = getattr(us, column.name)
                    us_data.append(us_dict)

            # Create s3dgraphy graph
            converter = S3DConverter()
            graph = converter.create_graph_from_us(us_data, site_name)

            # Export to JSON
            output_path = Path(app.config['UPLOAD_FOLDER']) / 'graphml' / f"{site_name}_stratigraphy.json"
            output_path.parent.mkdir(parents=True, exist_ok=True)

            converter.export_to_json(graph, str(output_path))

            # Send file
            return send_file(
                str(output_path),
                as_attachment=True,
                download_name=f"{site_name}_stratigraphy.json",
                mimetype='application/json'
            )

        except Exception as e:
            flash(f'Error exporting JSON: {str(e)}', 'error')
            return redirect(request.referrer or url_for('index'))

    @s3d_bp.route('/viewer/<site_name>')
    @login_required
    def stratigraph_viewer(site_name):
        """Interactive stratigraph viewer with Extended Matrix colors"""
        try:
            # Get all US for the site
            from pyarchinit_mini.models.us import US as USModel
            with db_manager.connection.get_session() as session:
                us_list = session.query(USModel).filter(
                    USModel.sito == site_name
                ).all()

                # Convert to dictionaries
                us_data = []
                for us in us_list:
                    us_dict = {}
                    for column in us.__table__.columns:
                        us_dict[column.name] = getattr(us, column.name)
                    us_data.append(us_dict)

            # Create s3dgraphy graph
            converter = S3DConverter()
            graph = converter.create_graph_from_us(us_data, site_name)

            # Convert to NetworkX and then to JSON
            nx_graph = converter._convert_to_networkx(graph)

            # Prepare JSON data for D3.js
            import networkx as nx
            graph_data = nx.node_link_data(nx_graph, edges='edges')

            # Convert to JSON string for template
            import json
            graph_json = json.dumps(graph_data, ensure_ascii=False)

            # Get available 3D models for site
            models = model_manager.get_models_for_site(site_name)

            return render_template(
                'harris_matrix/viewer_3d_integrated.html',
                site_name=site_name,
                graph_json=graph_json,
                models=models
            )

        except Exception as e:
            flash(f'Error loading stratigraph viewer: {str(e)}', 'error')
            return redirect(url_for('export_harris_graphml'))

    # Register blueprint
    app.register_blueprint(s3d_bp)

    return s3d_bp
