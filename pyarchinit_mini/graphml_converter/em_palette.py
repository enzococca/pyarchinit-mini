"""
Extended Matrix Palette — now backed by VocabProvider.

Legacy `EMPalette.PALETTE` dict access is retained as a deprecated proxy for
backward compatibility; emits DeprecationWarning on read.
"""
import warnings
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Import VocabProvider for the new path
try:
    from pyarchinit_mini.vocab.provider import VocabProvider
    from pyarchinit_mini.vocab.types import VisualStyle
    VOCAB_AVAILABLE = True
except ImportError:
    VOCAB_AVAILABLE = False

# Legacy config manager (kept as second-level fallback for now)
try:
    from pyarchinit_mini.config.em_node_config_manager import get_config_manager
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False


# Legacy hardcoded palette — kept verbatim for last-resort fallback.
# Do NOT use this directly outside this module; call EMPalette.get_node_style().
_PALETTE_LEGACY = {
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

_DEFAULT = {
    'fill_color': '#CCCCCC',
    'border_color': '#000000',
    'border_width': '3.0',
    'shape': 'rectangle',
    'text_color': '#000000',
    'font_family': 'DialogInput',
    'font_size': '24',
    'font_style': 'bold'
}


def _vocab_style_to_legacy_dict(vs: "VisualStyle") -> Dict[str, Any]:
    """Convert VocabProvider VisualStyle dataclass to the legacy dict shape."""
    return {
        "fill_color": vs.fill_color,
        "border_color": vs.border_color,
        "border_width": str(vs.border_width),
        "shape": vs.shape,
        "text_color": vs.text_color,
        "font_family": vs.font_family,
        "font_size": str(vs.font_size),
        "font_style": vs.font_style,
    }


class _PaletteProxy:
    """Backward-compat dict-like access for `EMPalette.PALETTE['US']`.

    Emits DeprecationWarning on every read-access; the public API is
    `EMPalette.get_node_style(label)`.
    """

    def __init__(self, legacy_dict: dict) -> None:
        self._legacy = legacy_dict

    def _warn(self) -> None:
        warnings.warn(
            "EMPalette.PALETTE is deprecated; use EMPalette.get_node_style(label) instead",
            DeprecationWarning,
            stacklevel=3,
        )

    def __getitem__(self, key: str) -> dict:
        self._warn()
        return self._legacy[key]

    def __contains__(self, key: object) -> bool:
        return key in self._legacy

    def get(self, key: str, default: Any = None) -> Any:
        self._warn()
        return self._legacy.get(key, default)

    def keys(self):
        self._warn()
        return self._legacy.keys()

    def items(self):
        self._warn()
        return self._legacy.items()

    def values(self):
        self._warn()
        return self._legacy.values()


class EMPalette:
    """Extended Matrix visual styling for nodes — VocabProvider-backed since Spec 1."""

    PALETTE = _PaletteProxy(_PALETTE_LEGACY)
    DEFAULT = _DEFAULT

    @staticmethod
    def _extract_node_type(node_label: str) -> str:
        """Extract node type from label, preserving case for vocab keys.

        Tries vocab keys (case-sensitive) first by matching them as prefixes
        of the input label. Falls back to uppercase prefix matching against
        the legacy palette.

        Args:
            node_label: Node label (e.g., "US1", "USVs42", "DOC4001", "property800")

        Returns:
            Node type identifier (e.g., "US", "USVs", "DOC", "property")
        """
        # Special handling for property nodes (lowercase prefix)
        if node_label.lower().startswith('property'):
            return 'property'

        label_upper = node_label.upper().strip()

        # Special handling for Combinar (can be "Combinar" or "COMBINAR")
        if label_upper.startswith('COMBINAR'):
            return 'Combinar'

        # Special handling for Extractor
        if label_upper.startswith('EXTRACTOR'):
            return 'Extractor'

        # Path 1: try vocab keys as case-sensitive prefixes (longest first)
        if VOCAB_AVAILABLE:
            try:
                vp = VocabProvider.instance()
                vocab_keys = sorted(vp._visual_by_type.keys(), key=len, reverse=True)
                for key in vocab_keys:
                    if node_label.startswith(key):
                        return key
            except Exception:
                pass

        # Path 2: legacy uppercase prefix matching (4, 3, 2 chars)
        for prefix_len in [4, 3, 2]:
            if len(label_upper) >= prefix_len:
                prefix = label_upper[:prefix_len]
                if prefix in _PALETTE_LEGACY:
                    return prefix

        # No match found — return the label as-is so get_node_style can fall
        # through to the neutral _DEFAULT rather than mapping to 'US'.
        return node_label

    @staticmethod
    def get_node_style(node_label: str) -> dict:
        """Get complete style dict for a node based on its label.

        Lookup order:
          1. VocabProvider (canonical since Spec 1)
          2. Legacy YAML config manager (second-level fallback)
          3. Hardcoded _PALETTE_LEGACY (last resort for known types)
          4. _DEFAULT (grey rectangle for truly unknown types)

        Args:
            node_label: Node label (e.g., "US1", "USVs42", "DOC4001", "property_foo")

        Returns:
            Dict with keys: fill_color, border_color, border_width, shape,
            text_color, font_family, font_size, font_style
        """
        node_type = EMPalette._extract_node_type(node_label)

        # Path 1: VocabProvider (canonical source since Spec 1)
        if VOCAB_AVAILABLE:
            try:
                vp = VocabProvider.instance()
                vs = vp.get_visual_style(node_type)
                is_fallback = (vs == VisualStyle.fallback())
                if is_fallback and node_type in _PALETTE_LEGACY:
                    # VocabProvider returned generic fallback for a type the legacy
                    # palette explicitly knows — prefer the legacy entry so known
                    # types like WSU, USVA/B/C, DOC, PROPERTY don't lose their style.
                    return _PALETTE_LEGACY[node_type].copy()
                return _vocab_style_to_legacy_dict(vs)
            except Exception as e:
                logger.warning("VocabProvider lookup failed for %s: %s", node_type, e)

        # Path 2: legacy YAML config manager
        if CONFIG_AVAILABLE:
            try:
                config_manager = get_config_manager()
                visual_config = config_manager.get_visual_style(node_type)
                if visual_config:
                    return {
                        'fill_color': visual_config.get('fill_color', '#FFFFFF'),
                        'border_color': visual_config.get('border_color', '#000000'),
                        'border_width': str(visual_config.get('border_width', 1.0)),
                        'shape': visual_config.get('shape', 'rectangle'),
                        'text_color': visual_config.get('text_color', '#000000'),
                        'font_family': visual_config.get('font_family', 'DialogInput'),
                        'font_size': str(visual_config.get('font_size', 12)),
                        'font_style': visual_config.get('font_style', 'plain'),
                    }
            except Exception as e:
                logger.warning("Config manager lookup failed for %s: %s", node_type, e)

        # Path 3: legacy hardcoded palette (prefix scan, longest first)
        label_upper = node_label.upper().strip()
        for prefix_len in [9, 8, 4, 3, 2]:
            if len(label_upper) >= prefix_len:
                prefix = label_upper[:prefix_len]
                if prefix in _PALETTE_LEGACY:
                    return _PALETTE_LEGACY[prefix].copy()

        if node_label.lower().startswith('property'):
            if 'PROPERTY' in _PALETTE_LEGACY:
                return _PALETTE_LEGACY['PROPERTY'].copy()

        # Path 4: neutral fallback
        return _DEFAULT.copy()
