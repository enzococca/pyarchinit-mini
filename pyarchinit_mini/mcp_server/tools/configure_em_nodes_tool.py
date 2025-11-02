"""
Configure Extended Matrix Nodes Tool

Manage Extended Matrix node type configurations (create, update, delete, list).
Allows customizing visual appearance and properties of stratigraphic node types.
"""

import logging
from typing import Dict, Any, Optional
from .base_tool import BaseTool, ToolDescription

logger = logging.getLogger(__name__)


class ConfigureEMNodesTool(BaseTool):
    """Configure Extended Matrix Nodes - Manage node type configurations"""

    def __init__(self, db_session, config):
        """Initialize with db_session and config"""
        super().__init__(db_session, config)
        # This tool doesn't need db_manager, just config

    def to_tool_description(self) -> ToolDescription:
        return ToolDescription(
            name="configure_em_nodes",
            description=(
                "Configure Extended Matrix node types for stratigraphic visualizations. "
                "Manage built-in and custom node types with visual properties (shapes, colors, fonts). "
                "Operations: list all node types, get specific type, create/update/delete custom types, "
                "list available shapes and symbol types."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["list", "get", "create", "update", "delete", "list_shapes", "list_symbols"],
                        "description": "Action to perform: list (all types), get (specific type), create/update/delete (custom type), list_shapes/list_symbols (available options)"
                    },
                    "tipo_id": {
                        "type": "string",
                        "description": "Node type ID (required for get, update, delete actions). Examples: US, USM, USVA, TU, SF, etc."
                    },
                    "node_config": {
                        "type": "object",
                        "description": "Node configuration (required for create/update)",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Display name for the node type"
                            },
                            "description": {
                                "type": "string",
                                "description": "Description of the node type"
                            },
                            "category": {
                                "type": "string",
                                "enum": ["stratigraphic", "non-stratigraphic"],
                                "description": "Category: stratigraphic or non-stratigraphic"
                            },
                            "symbol_type": {
                                "type": "string",
                                "enum": ["single_arrow", "double_arrow", "no_arrows"],
                                "description": "Symbol type for relationships: single_arrow (>), double_arrow (>>), no_arrows"
                            },
                            "label_format": {
                                "type": "string",
                                "description": "Label format template (e.g., 'US{number}', 'USM{number}')"
                            },
                            "visual": {
                                "type": "object",
                                "description": "Visual configuration",
                                "properties": {
                                    "shape": {
                                        "type": "string",
                                        "description": "GraphML shape: rectangle, ellipse, roundrectangle, triangle, diamond, trapezium, etc."
                                    },
                                    "fill_color": {
                                        "type": "string",
                                        "description": "Fill color (hex format, e.g., '#FFFFFF')"
                                    },
                                    "border_color": {
                                        "type": "string",
                                        "description": "Border color (hex format)"
                                    },
                                    "border_width": {
                                        "type": "number",
                                        "description": "Border width (default: 1.0)"
                                    },
                                    "text_color": {
                                        "type": "string",
                                        "description": "Text color (hex format)"
                                    },
                                    "font_family": {
                                        "type": "string",
                                        "description": "Font family (default: DialogInput)"
                                    },
                                    "font_size": {
                                        "type": "integer",
                                        "description": "Font size (default: 12)"
                                    },
                                    "font_style": {
                                        "type": "string",
                                        "enum": ["plain", "bold", "italic", "bold_italic"],
                                        "description": "Font style"
                                    },
                                    "width": {
                                        "type": "number",
                                        "description": "Node width (optional)"
                                    },
                                    "height": {
                                        "type": "number",
                                        "description": "Node height (optional)"
                                    }
                                }
                            }
                        }
                    }
                },
                "required": ["action"],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute EM node configuration action"""
        try:
            action = arguments.get("action")
            tipo_id = arguments.get("tipo_id")
            node_config = arguments.get("node_config", {})

            logger.info(f"EM Node Config: action={action}, tipo_id={tipo_id}")

            # Validate action-specific requirements
            if action in ["get", "update", "delete"] and not tipo_id:
                return self._format_error(f"Action '{action}' requires 'tipo_id'")

            if action in ["create", "update"] and not node_config:
                return self._format_error(f"Action '{action}' requires 'node_config'")

            # Execute action
            if action == "list":
                return await self._list_node_types()
            elif action == "get":
                return await self._get_node_type(tipo_id)
            elif action == "create":
                return await self._create_node_type(tipo_id, node_config)
            elif action == "update":
                return await self._update_node_type(tipo_id, node_config)
            elif action == "delete":
                return await self._delete_node_type(tipo_id)
            elif action == "list_shapes":
                return await self._list_shapes()
            elif action == "list_symbols":
                return await self._list_symbol_types()
            else:
                return self._format_error(f"Unknown action: {action}")

        except Exception as e:
            logger.error(f"EM node configuration error: {str(e)}", exc_info=True)
            return self._format_error(f"Configuration failed: {str(e)}")

    async def _list_node_types(self) -> Dict[str, Any]:
        """List all configured node types"""
        from pyarchinit_mini.config.em_node_config_manager import get_config_manager

        try:
            config_manager = get_config_manager()
            all_types = config_manager.get_all_node_types()

            # Group by category
            stratigraphic_types = []
            non_stratigraphic_types = []

            for tipo_id, config in all_types.items():
                type_info = {
                    'tipo_id': tipo_id,
                    'name': config.get('name', tipo_id),
                    'description': config.get('description', ''),
                    'category': config.get('category', 'stratigraphic'),
                    'symbol_type': config.get('symbol_type', 'single_arrow'),
                    'label_format': config.get('label_format', 'US{number}'),
                    'custom': config.get('custom', False),
                    'visual': config.get('visual', {})
                }

                if config.get('category') == 'stratigraphic':
                    stratigraphic_types.append(type_info)
                else:
                    non_stratigraphic_types.append(type_info)

            result = {
                'total_count': len(all_types),
                'stratigraphic_count': len(stratigraphic_types),
                'non_stratigraphic_count': len(non_stratigraphic_types),
                'stratigraphic_types': stratigraphic_types,
                'non_stratigraphic_types': non_stratigraphic_types
            }

            return self._format_success(
                result,
                f"Retrieved {len(all_types)} node types ({len(stratigraphic_types)} stratigraphic, {len(non_stratigraphic_types)} non-stratigraphic)"
            )

        except Exception as e:
            return self._format_error(f"Failed to list node types: {str(e)}")

    async def _get_node_type(self, tipo_id: str) -> Dict[str, Any]:
        """Get configuration for a specific node type"""
        from pyarchinit_mini.config.em_node_config_manager import get_config_manager

        try:
            config_manager = get_config_manager()
            config = config_manager.get_node_type(tipo_id)

            if not config:
                return self._format_error(f"Node type '{tipo_id}' not found")

            result = {
                'tipo_id': tipo_id,
                'name': config.get('name', tipo_id),
                'description': config.get('description', ''),
                'category': config.get('category', 'stratigraphic'),
                'symbol_type': config.get('symbol_type', 'single_arrow'),
                'label_format': config.get('label_format', 'US{number}'),
                'custom': config.get('custom', False),
                'visual': config.get('visual', {})
            }

            return self._format_success(result, f"Retrieved configuration for node type '{tipo_id}'")

        except Exception as e:
            return self._format_error(f"Failed to get node type: {str(e)}")

    async def _create_node_type(self, tipo_id: str, node_config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new custom node type"""
        from pyarchinit_mini.config.em_node_config_manager import get_config_manager, reset_config_manager

        try:
            # Validate required fields
            required_fields = ['name', 'category', 'symbol_type', 'visual', 'label_format']
            missing_fields = [field for field in required_fields if field not in node_config]
            if missing_fields:
                return self._format_error(f"Missing required fields: {', '.join(missing_fields)}")

            config_manager = get_config_manager()

            # Prepare visual configuration
            visual_config = node_config['visual']
            visual = {
                'shape': visual_config.get('shape', 'rectangle'),
                'fill_color': visual_config.get('fill_color', '#FFFFFF'),
                'border_color': visual_config.get('border_color', '#000000'),
                'border_width': float(visual_config.get('border_width', 1.0)),
                'text_color': visual_config.get('text_color', '#000000'),
                'font_family': visual_config.get('font_family', 'DialogInput'),
                'font_size': int(visual_config.get('font_size', 12)),
                'font_style': visual_config.get('font_style', 'plain')
            }

            # Add optional size fields
            if 'width' in visual_config:
                visual['width'] = float(visual_config['width'])
            if 'height' in visual_config:
                visual['height'] = float(visual_config['height'])

            # Add custom node type
            success = config_manager.add_custom_node_type(
                tipo_id=tipo_id,
                name=node_config['name'],
                description=node_config.get('description', ''),
                category=node_config['category'],
                symbol_type=node_config['symbol_type'],
                visual=visual,
                label_format=node_config['label_format']
            )

            if not success:
                return self._format_error("Failed to create node type (validation failed)")

            # Save configuration
            if not config_manager.save_config():
                return self._format_error("Failed to save configuration to file")

            # Reset global config manager to reload changes
            reset_config_manager()

            return self._format_success(
                {'tipo_id': tipo_id, 'created': True},
                f"Successfully created custom node type '{tipo_id}'"
            )

        except Exception as e:
            return self._format_error(f"Failed to create node type: {str(e)}")

    async def _update_node_type(self, tipo_id: str, node_config: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing custom node type"""
        from pyarchinit_mini.config.em_node_config_manager import get_config_manager, reset_config_manager

        try:
            config_manager = get_config_manager()

            # Check if exists
            existing = config_manager.get_node_type(tipo_id)
            if not existing:
                return self._format_error(f"Node type '{tipo_id}' not found")

            # Only allow editing custom types
            if not existing.get('custom', False):
                return self._format_error(f"Cannot edit built-in node type '{tipo_id}'")

            # Remove old custom type
            config_manager.remove_custom_node_type(tipo_id)

            # Prepare updated visual configuration
            visual_config = node_config.get('visual', {})
            visual = {
                'shape': visual_config.get('shape', existing['visual'].get('shape', 'rectangle')),
                'fill_color': visual_config.get('fill_color', existing['visual'].get('fill_color', '#FFFFFF')),
                'border_color': visual_config.get('border_color', existing['visual'].get('border_color', '#000000')),
                'border_width': float(visual_config.get('border_width', existing['visual'].get('border_width', 1.0))),
                'text_color': visual_config.get('text_color', existing['visual'].get('text_color', '#000000')),
                'font_family': visual_config.get('font_family', existing['visual'].get('font_family', 'DialogInput')),
                'font_size': int(visual_config.get('font_size', existing['visual'].get('font_size', 12))),
                'font_style': visual_config.get('font_style', existing['visual'].get('font_style', 'plain'))
            }

            # Add optional fields
            if 'width' in visual_config:
                visual['width'] = float(visual_config['width'])
            if 'height' in visual_config:
                visual['height'] = float(visual_config['height'])

            # Re-add with updates
            success = config_manager.add_custom_node_type(
                tipo_id=tipo_id,
                name=node_config.get('name', existing.get('name', tipo_id)),
                description=node_config.get('description', existing.get('description', '')),
                category=node_config.get('category', existing.get('category', 'stratigraphic')),
                symbol_type=node_config.get('symbol_type', existing.get('symbol_type', 'single_arrow')),
                visual=visual,
                label_format=node_config.get('label_format', existing.get('label_format', 'US{number}'))
            )

            if not success:
                return self._format_error("Failed to update node type (validation failed)")

            # Save configuration
            if not config_manager.save_config():
                return self._format_error("Failed to save configuration to file")

            # Reset global config manager to reload changes
            reset_config_manager()

            return self._format_success(
                {'tipo_id': tipo_id, 'updated': True},
                f"Successfully updated custom node type '{tipo_id}'"
            )

        except Exception as e:
            return self._format_error(f"Failed to update node type: {str(e)}")

    async def _delete_node_type(self, tipo_id: str) -> Dict[str, Any]:
        """Delete a custom node type"""
        from pyarchinit_mini.config.em_node_config_manager import get_config_manager, reset_config_manager

        try:
            config_manager = get_config_manager()

            # Check if exists
            existing = config_manager.get_node_type(tipo_id)
            if not existing:
                return self._format_error(f"Node type '{tipo_id}' not found")

            # Only allow deleting custom types
            if not existing.get('custom', False):
                return self._format_error(f"Cannot delete built-in node type '{tipo_id}'")

            # Remove custom type
            if not config_manager.remove_custom_node_type(tipo_id):
                return self._format_error("Failed to remove node type from configuration")

            # Save configuration
            if not config_manager.save_config():
                return self._format_error("Failed to save configuration to file")

            # Reset global config manager to reload changes
            reset_config_manager()

            return self._format_success(
                {'tipo_id': tipo_id, 'deleted': True},
                f"Successfully deleted custom node type '{tipo_id}'"
            )

        except Exception as e:
            return self._format_error(f"Failed to delete node type: {str(e)}")

    async def _list_shapes(self) -> Dict[str, Any]:
        """List available GraphML shapes"""
        from pyarchinit_mini.config.em_node_config_manager import get_config_manager

        try:
            config_manager = get_config_manager()
            shapes = config_manager.shapes

            return self._format_success(
                {'shapes': shapes, 'count': len(shapes)},
                f"Retrieved {len(shapes)} available shapes"
            )

        except Exception as e:
            return self._format_error(f"Failed to list shapes: {str(e)}")

    async def _list_symbol_types(self) -> Dict[str, Any]:
        """List available symbol types"""
        from pyarchinit_mini.config.em_node_config_manager import get_config_manager

        try:
            config_manager = get_config_manager()
            symbol_types = config_manager.symbol_types

            return self._format_success(
                {'symbol_types': symbol_types, 'count': len(symbol_types)},
                f"Retrieved {len(symbol_types)} symbol types"
            )

        except Exception as e:
            return self._format_error(f"Failed to list symbol types: {str(e)}")
