"""
Flask Routes for Extended Matrix Node Type Configuration
Provides web UI for managing EM node types via YAML configuration
"""

import os
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required
from pyarchinit_mini.web_interface.auth_routes import write_permission_required
from pyarchinit_mini.config.em_node_config_manager import get_config_manager, reset_config_manager

# Create blueprint
em_node_config_bp = Blueprint('em_node_config', __name__, url_prefix='/em-node-config')


@em_node_config_bp.route('/')
@login_required
def index():
    """Main EM node configuration page"""
    config_manager = get_config_manager()

    # Get all node types grouped by category
    all_types = config_manager.get_all_node_types()
    stratigraphic_types = []
    non_stratigraphic_types = []

    for tipo_id, config in all_types.items():
        type_info = {
            'id': tipo_id,
            'name': config.get('name', tipo_id),
            'description': config.get('description', ''),
            'symbol_type': config.get('symbol_type', 'single_arrow'),
            'label_format': config.get('label_format', 'US{number}'),
            'custom': config.get('custom', False),
            'visual': config.get('visual', {})
        }

        if config.get('category') == 'stratigraphic':
            stratigraphic_types.append(type_info)
        else:
            non_stratigraphic_types.append(type_info)

    # Get available shapes
    shapes = config_manager.shapes
    symbol_types = config_manager.symbol_types

    return render_template(
        'em_node_config/index.html',
        stratigraphic_types=stratigraphic_types,
        non_stratigraphic_types=non_stratigraphic_types,
        shapes=shapes,
        symbol_types=symbol_types
    )


@em_node_config_bp.route('/api/node-types', methods=['GET'])
@login_required
def get_node_types():
    """API endpoint to get all node types"""
    config_manager = get_config_manager()
    all_types = config_manager.get_all_node_types()

    # Convert to JSON-friendly format
    types_list = []
    for tipo_id, config in all_types.items():
        types_list.append({
            'id': tipo_id,
            'name': config.get('name', tipo_id),
            'description': config.get('description', ''),
            'category': config.get('category', 'stratigraphic'),
            'symbol_type': config.get('symbol_type', 'single_arrow'),
            'label_format': config.get('label_format', 'US{number}'),
            'custom': config.get('custom', False),
            'visual': config.get('visual', {})
        })

    return jsonify({'node_types': types_list})


@em_node_config_bp.route('/api/node-types/<tipo_id>', methods=['GET'])
@login_required
def get_node_type(tipo_id):
    """API endpoint to get a specific node type"""
    config_manager = get_config_manager()
    config = config_manager.get_node_type(tipo_id)

    if not config:
        return jsonify({'error': 'Node type not found'}), 404

    return jsonify({
        'id': tipo_id,
        'name': config.get('name', tipo_id),
        'description': config.get('description', ''),
        'category': config.get('category', 'stratigraphic'),
        'symbol_type': config.get('symbol_type', 'single_arrow'),
        'label_format': config.get('label_format', 'US{number}'),
        'custom': config.get('custom', False),
        'visual': config.get('visual', {})
    })


@em_node_config_bp.route('/api/node-types', methods=['POST'])
@login_required
@write_permission_required
def create_node_type():
    """API endpoint to create a new custom node type"""
    data = request.get_json()

    # Validate required fields
    required_fields = ['tipo_id', 'name', 'category', 'symbol_type', 'visual', 'label_format']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    config_manager = get_config_manager()

    # Create visual configuration
    visual = {
        'shape': data['visual'].get('shape', 'rectangle'),
        'fill_color': data['visual'].get('fill_color', '#FFFFFF'),
        'border_color': data['visual'].get('border_color', '#000000'),
        'border_width': float(data['visual'].get('border_width', 1.0)),
        'text_color': data['visual'].get('text_color', '#000000'),
        'font_family': data['visual'].get('font_family', 'DialogInput'),
        'font_size': int(data['visual'].get('font_size', 12)),
        'font_style': data['visual'].get('font_style', 'plain')
    }

    # Add optional size fields
    if 'width' in data['visual']:
        visual['width'] = float(data['visual']['width'])
    if 'height' in data['visual']:
        visual['height'] = float(data['visual']['height'])
    if 'svg_refid' in data['visual']:
        visual['svg_refid'] = int(data['visual']['svg_refid'])

    # Add custom node type
    success = config_manager.add_custom_node_type(
        tipo_id=data['tipo_id'],
        name=data['name'],
        description=data.get('description', ''),
        category=data['category'],
        symbol_type=data['symbol_type'],
        visual=visual,
        label_format=data['label_format']
    )

    if not success:
        return jsonify({'error': 'Failed to create node type (validation failed)'}), 400

    # Save configuration
    if config_manager.save_config():
        # Reset global config manager to reload changes
        reset_config_manager()
        return jsonify({'success': True, 'message': 'Node type created successfully'}), 201
    else:
        return jsonify({'error': 'Failed to save configuration'}), 500


@em_node_config_bp.route('/api/node-types/<tipo_id>', methods=['PUT'])
@login_required
@write_permission_required
def update_node_type(tipo_id):
    """API endpoint to update a custom node type"""
    data = request.get_json()

    config_manager = get_config_manager()

    # Check if node type exists
    existing = config_manager.get_node_type(tipo_id)
    if not existing:
        return jsonify({'error': 'Node type not found'}), 404

    # Only allow editing custom types
    if not existing.get('custom', False):
        return jsonify({'error': 'Cannot edit built-in node type'}), 403

    # Remove old custom type
    config_manager.remove_custom_node_type(tipo_id)

    # Create updated visual configuration
    visual = {
        'shape': data['visual'].get('shape', existing['visual'].get('shape', 'rectangle')),
        'fill_color': data['visual'].get('fill_color', existing['visual'].get('fill_color', '#FFFFFF')),
        'border_color': data['visual'].get('border_color', existing['visual'].get('border_color', '#000000')),
        'border_width': float(data['visual'].get('border_width', existing['visual'].get('border_width', 1.0))),
        'text_color': data['visual'].get('text_color', existing['visual'].get('text_color', '#000000')),
        'font_family': data['visual'].get('font_family', existing['visual'].get('font_family', 'DialogInput')),
        'font_size': int(data['visual'].get('font_size', existing['visual'].get('font_size', 12))),
        'font_style': data['visual'].get('font_style', existing['visual'].get('font_style', 'plain'))
    }

    # Add optional fields
    if 'width' in data['visual']:
        visual['width'] = float(data['visual']['width'])
    if 'height' in data['visual']:
        visual['height'] = float(data['visual']['height'])
    if 'svg_refid' in data['visual']:
        visual['svg_refid'] = int(data['visual']['svg_refid'])

    # Re-add with updates
    success = config_manager.add_custom_node_type(
        tipo_id=tipo_id,
        name=data.get('name', existing.get('name', tipo_id)),
        description=data.get('description', existing.get('description', '')),
        category=data.get('category', existing.get('category', 'stratigraphic')),
        symbol_type=data.get('symbol_type', existing.get('symbol_type', 'single_arrow')),
        visual=visual,
        label_format=data.get('label_format', existing.get('label_format', 'US{number}'))
    )

    if not success:
        return jsonify({'error': 'Failed to update node type (validation failed)'}), 400

    # Save configuration
    if config_manager.save_config():
        # Reset global config manager to reload changes
        reset_config_manager()
        return jsonify({'success': True, 'message': 'Node type updated successfully'})
    else:
        return jsonify({'error': 'Failed to save configuration'}), 500


@em_node_config_bp.route('/api/node-types/<tipo_id>', methods=['DELETE'])
@login_required
@write_permission_required
def delete_node_type(tipo_id):
    """API endpoint to delete a custom node type"""
    config_manager = get_config_manager()

    # Check if node type exists
    existing = config_manager.get_node_type(tipo_id)
    if not existing:
        return jsonify({'error': 'Node type not found'}), 404

    # Only allow deleting custom types
    if not existing.get('custom', False):
        return jsonify({'error': 'Cannot delete built-in node type'}), 403

    # Remove custom type
    if config_manager.remove_custom_node_type(tipo_id):
        # Save configuration
        if config_manager.save_config():
            # Reset global config manager to reload changes
            reset_config_manager()
            return jsonify({'success': True, 'message': 'Node type deleted successfully'})
        else:
            return jsonify({'error': 'Failed to save configuration'}), 500
    else:
        return jsonify({'error': 'Failed to delete node type'}), 500


@em_node_config_bp.route('/api/shapes', methods=['GET'])
@login_required
def get_shapes():
    """API endpoint to get available shapes"""
    config_manager = get_config_manager()
    return jsonify({'shapes': config_manager.shapes})


@em_node_config_bp.route('/api/symbol-types', methods=['GET'])
@login_required
def get_symbol_types():
    """API endpoint to get available symbol types"""
    config_manager = get_config_manager()
    return jsonify({'symbol_types': config_manager.symbol_types})


@em_node_config_bp.route('/reload', methods=['POST'])
@login_required
@write_permission_required
def reload_config():
    """Reload configuration from file"""
    try:
        reset_config_manager()
        flash('Configuration reloaded successfully', 'success')
    except Exception as e:
        flash(f'Error reloading configuration: {str(e)}', 'error')

    return redirect(url_for('em_node_config.index'))
