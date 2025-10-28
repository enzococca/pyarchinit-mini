"""
Extended Matrix Node Configuration Manager

This module manages node type configurations for GraphML export.
Supports loading from YAML files and adding custom node types.
"""

import os
import re
import yaml
from typing import Dict, List, Optional, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class EMNodeConfigManager:
    """Manager for Extended Matrix node type configurations"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager

        Args:
            config_path: Path to YAML configuration file
                        If None, uses default config from package
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config: Dict[str, Any] = {}
        self.node_types: Dict[str, Dict] = {}
        self.shapes: Dict[str, str] = {}
        self.symbol_types: Dict[str, Dict] = {}
        self.defaults: Dict[str, Any] = {}
        self.validation: Dict[str, Any] = {}

        # Load configuration
        self.load_config()

    def _get_default_config_path(self) -> str:
        """Get path to default configuration file"""
        # Get the directory where this module is located
        module_dir = Path(__file__).parent
        config_file = module_dir / "em_node_types.yaml"

        if not config_file.exists():
            logger.warning(f"Default config not found at {config_file}")
            # Create empty config
            return None

        return str(config_file)

    def load_config(self) -> bool:
        """
        Load configuration from YAML file

        Returns:
            True if successful, False otherwise
        """
        if not self.config_path or not os.path.exists(self.config_path):
            logger.error(f"Config file not found: {self.config_path}")
            self._load_fallback_config()
            return False

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)

            # Extract sections
            self.node_types = self.config.get('node_types', {})
            self.shapes = self.config.get('shapes', {})
            self.symbol_types = self.config.get('symbol_types', {})
            self.defaults = self.config.get('defaults', {})
            self.validation = self.config.get('validation', {})

            logger.info(f"Loaded {len(self.node_types)} node types from {self.config_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            self._load_fallback_config()
            return False

    def _load_fallback_config(self):
        """Load minimal fallback configuration"""
        self.node_types = {
            'US': {
                'name': 'Stratigraphic Unit',
                'category': 'stratigraphic',
                'symbol_type': 'single_arrow',
                'visual': {
                    'shape': 'rectangle',
                    'fill_color': '#FFFFFF',
                    'border_color': '#9B3333',
                    'border_width': 3.0,
                    'width': 90.0,
                    'height': 30.0,
                    'font_family': 'DialogInput',
                    'font_size': 24,
                    'font_style': 'bold',
                    'text_color': '#000000'
                },
                'label_format': 'US{number}'
            }
        }
        self.defaults = {
            'fallback_type': 'US',
            'default_label_format': 'US{number}'
        }

    def get_node_type(self, tipo: str) -> Optional[Dict]:
        """
        Get configuration for a node type

        Args:
            tipo: Node type identifier (e.g., 'US', 'DOC', 'property')

        Returns:
            Dictionary with node type configuration, or None if not found
        """
        return self.node_types.get(tipo)

    def get_all_node_types(self) -> Dict[str, Dict]:
        """Get all node type configurations"""
        return self.node_types.copy()

    def get_node_type_names(self) -> List[str]:
        """Get list of all node type identifiers"""
        return list(self.node_types.keys())

    def get_stratigraphic_types(self) -> List[str]:
        """Get list of stratigraphic node types"""
        return [
            tipo for tipo, config in self.node_types.items()
            if config.get('category') == 'stratigraphic'
        ]

    def get_non_stratigraphic_types(self) -> List[str]:
        """Get list of non-stratigraphic node types"""
        return [
            tipo for tipo, config in self.node_types.items()
            if config.get('category') == 'non_stratigraphic'
        ]

    def get_visual_style(self, tipo: str) -> Dict:
        """
        Get visual style configuration for a node type

        Args:
            tipo: Node type identifier

        Returns:
            Dictionary with visual properties
        """
        node_config = self.get_node_type(tipo)
        if node_config:
            return node_config.get('visual', {})

        # Return default visual style
        return self.defaults.get('default_visual', {})

    def get_label_format(self, tipo: str) -> str:
        """
        Get label format string for a node type

        Args:
            tipo: Node type identifier

        Returns:
            Label format string (e.g., "US{number}", "D.{number}")
        """
        node_config = self.get_node_type(tipo)
        if node_config:
            return node_config.get('label_format', 'US{number}')

        # Return default label format
        return self.defaults.get('default_label_format', 'US{number}')

    def format_label(self, tipo: str, us_number: str, description: str = "") -> str:
        """
        Format node label according to type configuration

        Args:
            tipo: Node type identifier
            us_number: US number (numeric part)
            description: Node description (for special formatting)

        Returns:
            Formatted label string
        """
        label_format = self.get_label_format(tipo)

        # Replace placeholders
        label = label_format.replace('{number}', str(us_number))

        # Handle special formats
        if '{first_word}' in label_format and description:
            # Extract first word from description
            words = description.strip().split()
            first_word = words[0] if words else str(us_number)
            label = label_format.replace('{first_word}', first_word)

        return label

    def get_symbol_type(self, tipo: str) -> str:
        """
        Get symbol type for a node type (single_arrow or double_arrow)

        Args:
            tipo: Node type identifier

        Returns:
            'single_arrow' or 'double_arrow'
        """
        node_config = self.get_node_type(tipo)
        if node_config:
            return node_config.get('symbol_type', 'single_arrow')
        return 'single_arrow'

    def get_edge_symbol(self, tipo: str, direction: str) -> str:
        """
        Get edge symbol for a node type and direction

        Args:
            tipo: Node type identifier
            direction: 'above' or 'below'

        Returns:
            Edge symbol ('>', '<', '>>', '<<')
        """
        symbol_type = self.get_symbol_type(tipo)
        symbol_config = self.symbol_types.get(symbol_type, {})

        if direction == 'above':
            return symbol_config.get('above', '>')
        elif direction == 'below':
            return symbol_config.get('below', '<')
        else:
            return '>'

    def add_custom_node_type(
        self,
        tipo_id: str,
        name: str,
        description: str,
        category: str,
        symbol_type: str,
        visual: Dict,
        label_format: str
    ) -> bool:
        """
        Add a custom node type configuration

        Args:
            tipo_id: Unique identifier for the type
            name: Display name
            description: Description
            category: 'stratigraphic' or 'non_stratigraphic'
            symbol_type: 'single_arrow' or 'double_arrow'
            visual: Visual style dictionary
            label_format: Label format string

        Returns:
            True if added successfully, False otherwise
        """
        # Validate inputs
        if not self._validate_custom_type(tipo_id, name, category, symbol_type, visual):
            return False

        # Create configuration
        self.node_types[tipo_id] = {
            'name': name,
            'description': description,
            'category': category,
            'symbol_type': symbol_type,
            'visual': visual,
            'label_format': label_format,
            'custom': True  # Mark as custom type
        }

        logger.info(f"Added custom node type: {tipo_id}")
        return True

    def _validate_custom_type(
        self,
        tipo_id: str,
        name: str,
        category: str,
        symbol_type: str,
        visual: Dict
    ) -> bool:
        """Validate custom node type inputs"""

        # Check if tipo_id already exists
        if tipo_id in self.node_types:
            logger.warning(f"Node type {tipo_id} already exists, will overwrite")

        # Validate category
        valid_categories = self.validation.get('valid_categories', ['stratigraphic', 'non_stratigraphic'])
        if category not in valid_categories:
            logger.error(f"Invalid category: {category}. Must be one of {valid_categories}")
            return False

        # Validate symbol_type
        valid_symbol_types = self.validation.get('valid_symbol_types', ['single_arrow', 'double_arrow'])
        if symbol_type not in valid_symbol_types:
            logger.error(f"Invalid symbol_type: {symbol_type}. Must be one of {valid_symbol_types}")
            return False

        # Validate visual properties
        if 'shape' not in visual:
            logger.error("Visual configuration must include 'shape'")
            return False

        valid_shapes = self.validation.get('valid_shapes', [])
        if valid_shapes and visual['shape'] not in valid_shapes:
            logger.error(f"Invalid shape: {visual['shape']}. Must be one of {valid_shapes}")
            return False

        # Validate colors (if present)
        color_pattern = self.validation.get('color_pattern', r'^#[0-9A-Fa-f]{6}$')
        for color_key in ['fill_color', 'border_color', 'text_color']:
            if color_key in visual:
                if not re.match(color_pattern, visual[color_key]):
                    logger.error(f"Invalid color format for {color_key}: {visual[color_key]}")
                    return False

        # Validate sizes (if present)
        size_range = self.validation.get('size_range', {})
        for size_key in ['width', 'height']:
            if size_key in visual and size_key in size_range:
                min_val, max_val = size_range[size_key]
                if not (min_val <= visual[size_key] <= max_val):
                    logger.error(f"{size_key} must be between {min_val} and {max_val}")
                    return False

        return True

    def save_config(self, output_path: Optional[str] = None) -> bool:
        """
        Save configuration to YAML file

        Args:
            output_path: Path to save configuration
                        If None, saves to original config_path

        Returns:
            True if successful, False otherwise
        """
        save_path = output_path or self.config_path

        if not save_path:
            logger.error("No output path specified")
            return False

        try:
            # Reconstruct full config
            full_config = {
                'version': self.config.get('version', '1.0'),
                'node_types': self.node_types,
                'shapes': self.shapes,
                'symbol_types': self.symbol_types,
                'defaults': self.defaults,
                'validation': self.validation,
                'metadata': self.config.get('metadata', {})
            }

            # Update metadata
            from datetime import datetime
            full_config['metadata']['last_modified'] = datetime.now().strftime('%Y-%m-%d')

            # Write to file
            with open(save_path, 'w', encoding='utf-8') as f:
                yaml.dump(full_config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

            logger.info(f"Configuration saved to {save_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False

    def remove_custom_node_type(self, tipo_id: str) -> bool:
        """
        Remove a custom node type

        Args:
            tipo_id: Node type identifier to remove

        Returns:
            True if removed, False if not found or is built-in type
        """
        if tipo_id not in self.node_types:
            logger.warning(f"Node type {tipo_id} not found")
            return False

        node_config = self.node_types[tipo_id]
        if not node_config.get('custom', False):
            logger.warning(f"Cannot remove built-in node type: {tipo_id}")
            return False

        del self.node_types[tipo_id]
        logger.info(f"Removed custom node type: {tipo_id}")
        return True

    def get_category_display_name(self, category: str) -> str:
        """Get display name for a category"""
        category_names = {
            'stratigraphic': 'Stratigraphic Units',
            'non_stratigraphic': 'Non-Stratigraphic Units'
        }
        return category_names.get(category, category)

    def get_shape_display_name(self, shape: str) -> str:
        """Get display name for a shape"""
        shape_names = {
            'rectangle': 'Rectangle',
            'roundrectangle': 'Rounded Rectangle',
            'parallelogram': 'Parallelogram',
            'hexagon': 'Hexagon',
            'ellipse': 'Ellipse',
            'triangle': 'Triangle',
            'diamond': 'Diamond',
            'octagon': 'Octagon',
            'trapezoid': 'Trapezoid',
            'bpmn_artifact': 'BPMN Artifact',
            'svg': 'SVG Custom'
        }
        return shape_names.get(shape, shape.title())


# Global instance
_global_config_manager = None


def get_config_manager() -> EMNodeConfigManager:
    """
    Get global configuration manager instance

    Returns:
        Singleton EMNodeConfigManager instance
    """
    global _global_config_manager
    if _global_config_manager is None:
        _global_config_manager = EMNodeConfigManager()
    return _global_config_manager


def reset_config_manager():
    """Reset global configuration manager (useful for testing)"""
    global _global_config_manager
    _global_config_manager = None
