"""
Extended Matrix Palette
Defines colors and shapes for different stratigraphic unit types

Now powered by YAML configuration system for easy customization.
"""

from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# Import configuration manager
try:
    from pyarchinit_mini.config.em_node_config_manager import get_config_manager
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False
    logger.warning("Configuration manager not available, using fallback styles")


class EMPalette:
    """Extended Matrix visual styling for nodes - now with YAML configuration"""

    # Fallback palette if configuration system unavailable
    # This ensures backward compatibility
    PALETTE = {
        # Standard units (US, SU, WSU)
        'US': {
            'fill_color': '#FFFFFF',
            'border_color': '#9B3333',  # Red-brown border
            'border_width': '3.0',
            'shape': 'rectangle',
            'text_color': '#000000',
            'font_family': 'DialogInput',
            'font_size': '24',
            'font_style': 'bold'
        },
        'SU': {
            'fill_color': '#FFFFFF',
            'border_color': '#9B3333',
            'border_width': '3.0',
            'shape': 'rectangle',
            'text_color': '#000000',
            'font_family': 'DialogInput',
            'font_size': '24',
            'font_style': 'bold'
        },
        'WSU': {
            'fill_color': '#C0C0C0',  # Gray fill
            'border_color': '#9B3333',
            'border_width': '3.0',
            'shape': 'rectangle',
            'text_color': '#000000',
            'font_family': 'DialogInput',
            'font_size': '24',
            'font_style': 'bold'
        },

        # Masonry units (USM) - Like US but gray inside
        'USM': {
            'fill_color': '#C0C0C0',  # Gray fill
            'border_color': '#9B3333',
            'border_width': '3.0',
            'shape': 'rectangle',  # Same as US, not ellipse
            'text_color': '#000000',
            'font_family': 'DialogInput',
            'font_size': '24',
            'font_style': 'bold'
        },

        # Negative units - variants (USV)
        'USVA': {
            'fill_color': '#000000',
            'border_color': '#248FE7',  # Blue border
            'border_width': '3.0',
            'shape': 'parallelogram',  # Fixed: was hexagon
            'text_color': '#FFFFFF',
            'font_family': 'Dialog',
            'font_size': '12',
            'font_style': 'plain'
        },
        'USVB': {
            'fill_color': '#000000',
            'border_color': '#31792D',  # Green border
            'border_width': '3.0',
            'shape': 'hexagon',  # Fixed: was ellipse
            'text_color': '#FFFFFF',
            'font_family': 'Dialog',
            'font_size': '12',
            'font_style': 'plain'
        },
        'USVC': {
            'fill_color': '#000000',
            'border_color': '#31792D',  # Green border
            'border_width': '3.0',
            'shape': 'ellipse',  # Fixed: was parallelogram
            'text_color': '#FFFFFF',
            'font_family': 'Dialog',
            'font_size': '12',
            'font_style': 'plain'
        },

        # Structure units (SF)
        'SF': {
            'fill_color': '#FFFFFF',
            'border_color': '#D8BD30',  # Gold border (not red-brown)
            'border_width': '3.0',
            'shape': 'octagon',
            'text_color': '#000000',
            'font_family': 'DialogInput',
            'font_size': '12',  # Size 12, not 24
            'font_style': 'bold'
        },
        'SFA': {
            'fill_color': '#000000',
            'border_color': '#D8BD30',  # Gold border
            'border_width': '3.0',
            'shape': 'octagon',
            'text_color': '#FFFFFF',
            'font_family': 'Dialog',
            'font_size': '12',
            'font_style': 'plain'
        },

        # Documentary units (USD)
        'USD': {
            'fill_color': '#FFFFFF',
            'border_color': '#D86400',  # Orange border
            'border_width': '3.0',
            'shape': 'roundrectangle',
            'text_color': '#000000',
            'font_family': 'Dialog',
            'font_size': '12',
            'font_style': 'plain'
        },

        # Temporary stratigraphic units (TSU)
        'TSU': {
            'fill_color': '#FFFFFF',
            'border_color': '#9B3333',
            'border_width': '3.0',
            'shape': 'roundrectangle',
            'text_color': '#000000',
            'font_family': 'DialogInput',
            'font_size': '24',
            'font_style': 'bold'
        },

        # Tomb units (UST)
        'UST': {
            'fill_color': '#FFFFFF',
            'border_color': '#9B3333',
            'border_width': '3.0',
            'shape': 'diamond',
            'text_color': '#000000',
            'font_family': 'DialogInput',
            'font_size': '24',
            'font_style': 'bold'
        },

        # Connection/Context units (CON) - Black diamond
        'CON': {
            'fill_color': '#000000',  # Black fill
            'border_color': '#000000',  # Black border
            'border_width': '3.0',
            'shape': 'diamond',
            'text_color': '#FFFFFF',  # White text on black
            'font_family': 'DialogInput',
            'font_size': '24',
            'font_style': 'bold'
        },

        # Topographic units (TU)
        'TU': {
            'fill_color': '#FFFFFF',
            'border_color': '#9B3333',
            'border_width': '3.0',
            'shape': 'rectangle',
            'text_color': '#000000',
            'font_family': 'DialogInput',
            'font_size': '24',
            'font_style': 'bold'
        },

        # Virtual special finds (VSF)
        'VSF': {
            'fill_color': '#000000',  # Black fill
            'border_color': '#B19F61',  # Tan/gold border
            'border_width': '3.0',
            'shape': 'octagon',
            'text_color': '#FFFFFF',  # White text on black
            'font_family': 'DialogInput',
            'font_size': '12',
            'font_style': 'bold'
        },

        # Document nodes (DOC) - BPMN artifact
        'DOC': {
            'fill_color': '#FFFFFF',  # White fill (not yellow!)
            'border_color': '#000000',  # Black border
            'border_width': '1.0',  # Thin border
            'shape': 'note',  # Document/note shape
            'text_color': '#000000',
            'font_family': 'DialogInput',
            'font_size': '12',
            'font_style': 'bold'
        },

        # Extended Matrix aggregation nodes - SVG shapes
        'EXTRACTOR': {
            'fill_color': '#CCCCFF',  # Light blue (not lavender!)
            'border_color': '#000000',  # Black border
            'border_width': '1.0',  # Thin border
            'shape': 'trapezium',  # Aggregation shape
            'text_color': '#000000',
            'font_family': 'Dialog',
            'font_size': '10',
            'font_style': 'plain'
        },

        'COMBINER': {
            'fill_color': '#CCCCFF',  # Light blue
            'border_color': '#000000',  # Black border
            'border_width': '1.0',  # Thin border
            'shape': 'trapezium2',  # Inverted trapezium
            'text_color': '#000000',
            'font_family': 'Dialog',
            'font_size': '10',
            'font_style': 'plain'
        },

        # Property node - BPMN annotation
        'PROPERTY': {
            'fill_color': '#FFFFFFE6',  # White with transparency
            'border_color': '#000000',  # Black border
            'border_width': '1.0',  # Thin border
            'shape': 'parallelogram',
            'text_color': '#000000',
            'font_family': 'DialogInput',
            'font_size': '12',
            'font_style': 'plain'  # Not italic
        },
    }

    # Default for unknown types
    DEFAULT = {
        'fill_color': '#FFFFFF',
        'border_color': '#9B3333',
        'border_width': '3.0',
        'shape': 'rectangle',
        'text_color': '#000000',
        'font_family': 'DialogInput',
        'font_size': '24',
        'font_style': 'bold'
    }

    @staticmethod
    def _extract_node_type(node_label: str) -> str:
        """
        Extract node type from label

        Args:
            node_label: Node label (e.g., "US1", "DOC4001", "property800")

        Returns:
            Node type identifier (e.g., "US", "DOC", "property")
        """
        label = node_label.upper().strip()

        # Special handling for property nodes (lowercase prefix)
        if node_label.lower().startswith('property'):
            return 'property'

        # Special handling for Combinar (can be "Combinar" or "COMBINAR")
        if label.startswith('COMBINAR'):
            return 'Combinar'

        # Special handling for Extractor
        if label.startswith('EXTRACTOR'):
            return 'Extractor'

        # Try to match longest prefixes first (4, 3, 2 chars)
        # USVA, USVB, USVC = 4 chars
        # USM, USD, CON, VSF = 3 chars
        # US, SF, TU = 2 chars
        for prefix_len in [4, 3, 2]:
            if len(label) >= prefix_len:
                prefix = label[:prefix_len]
                # Check if this prefix exists in configuration or fallback palette
                if CONFIG_AVAILABLE:
                    config_manager = get_config_manager()
                    if config_manager.get_node_type(prefix):
                        return prefix
                elif prefix in EMPalette.PALETTE:
                    return prefix

        # Default to 'US' if nothing matches
        return 'US'

    @staticmethod
    def get_node_style(node_label: str) -> dict:
        """
        Get complete style dict for a node based on its label
        Uses YAML configuration if available, falls back to hardcoded palette

        Args:
            node_label: Node label (e.g., "US1", "USM12", "USVA102", "DOC4001", "property_foo")

        Returns:
            Dict with keys: fill_color, border_color, border_width, shape,
            text_color, font_family, font_size, font_style
        """
        # Extract node type from label
        node_type = EMPalette._extract_node_type(node_label)

        # Try to get style from configuration manager
        if CONFIG_AVAILABLE:
            try:
                config_manager = get_config_manager()
                visual_config = config_manager.get_visual_style(node_type)

                if visual_config:
                    # Convert configuration format to EMPalette format
                    style = {
                        'fill_color': visual_config.get('fill_color', '#FFFFFF'),
                        'border_color': visual_config.get('border_color', '#000000'),
                        'border_width': str(visual_config.get('border_width', 1.0)),
                        'shape': visual_config.get('shape', 'rectangle'),
                        'text_color': visual_config.get('text_color', '#000000'),
                        'font_family': visual_config.get('font_family', 'DialogInput'),
                        'font_size': str(visual_config.get('font_size', 12)),
                        'font_style': visual_config.get('font_style', 'plain')
                    }
                    return style
            except Exception as e:
                logger.warning(f"Failed to get style from config for {node_type}: {e}")

        # Fallback to hardcoded palette
        label = node_label.upper().strip()

        # Try to match longest prefixes first (9, 8, 4, 3, 2 chars)
        for prefix_len in [9, 8, 4, 3, 2]:
            if len(label) >= prefix_len:
                prefix = label[:prefix_len]
                if prefix in EMPalette.PALETTE:
                    return EMPalette.PALETTE[prefix].copy()

        # Handle lowercase property
        if node_label.lower().startswith('property'):
            if 'PROPERTY' in EMPalette.PALETTE:
                return EMPalette.PALETTE['PROPERTY'].copy()

        # Default style
        return EMPalette.DEFAULT.copy()
