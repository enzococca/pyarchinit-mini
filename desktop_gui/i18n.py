"""
Internationalization (i18n) module for PyArchInit-Mini Desktop GUI
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pyarchinit_mini.i18n.locale_manager import LocaleManager


class DesktopI18n:
    """Desktop GUI internationalization manager"""

    def __init__(self, default_locale: str = 'it'):
        """Initialize desktop i18n

        Args:
            default_locale: Default language code ('it' or 'en')
        """
        self.locale_manager = LocaleManager(default_locale)

    def _(self, message: str) -> str:
        """Translate message to current locale

        Args:
            message: English message to translate

        Returns:
            Translated message
        """
        return self.locale_manager.gettext(message)

    def ngettext(self, singular: str, plural: str, n: int) -> str:
        """Translate plural message

        Args:
            singular: Singular form
            plural: Plural form
            n: Count

        Returns:
            Translated message
        """
        return self.locale_manager.ngettext(singular, plural, n)

    def switch_language(self, lang: str):
        """Switch interface language

        Args:
            lang: Language code ('it' or 'en')
        """
        self.locale_manager.switch_language(lang)

    def get_current_locale(self) -> str:
        """Get current locale

        Returns:
            Language code
        """
        return self.locale_manager.get_current_locale()

    def get_available_locales(self) -> list:
        """Get available locales

        Returns:
            List of language codes
        """
        return self.locale_manager.get_available_locales()


# Global instance for desktop GUI
_desktop_i18n = None


def get_i18n() -> DesktopI18n:
    """Get global DesktopI18n instance

    Returns:
        DesktopI18n singleton
    """
    global _desktop_i18n
    if _desktop_i18n is None:
        # Load language preference from config.json
        import json
        default_locale = 'it'  # Default to Italian
        config_file = os.path.join(os.path.dirname(__file__), '..', 'config.json')

        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    default_locale = config.get('language', 'it')
            except (json.JSONDecodeError, IOError):
                # If config is invalid, use default
                pass

        _desktop_i18n = DesktopI18n(default_locale)
    return _desktop_i18n


# Convenience function for translations
def _(message: str) -> str:
    """Translate message

    Args:
        message: Message to translate

    Returns:
        Translated message
    """
    return get_i18n()._(message)


def get_unit_types() -> list:
    """Get translated unit types for Extended Matrix

    Returns:
        List of translated unit type strings
    """
    i18n = get_i18n()
    return [
        i18n._("US"),
        i18n._("USM"),
        i18n._("VSF"),
        i18n._("SF"),
        i18n._("CON"),
        i18n._("USD"),
        i18n._("USVA"),
        i18n._("USVB"),
        i18n._("USVC"),
        i18n._("DOC"),
        i18n._("TU"),
        i18n._("property"),
        i18n._("Combiner"),
        i18n._("Extractor")
    ]


def get_unit_type_original_values() -> list:
    """Get original (untranslated) unit type values

    Returns:
        List of original unit type strings (for database storage)
    """
    return [
        "US", "USM", "VSF", "SF", "CON", "USD",
        "USVA", "USVB", "USVC", "DOC", "TU",
        "property", "Combiner", "Extractor"
    ]


def translate_unit_type_to_original(translated_value: str) -> str:
    """Convert translated unit type back to original value

    Args:
        translated_value: Translated unit type (e.g., "SU" in English)

    Returns:
        Original value (e.g., "US")
    """
    i18n = get_i18n()
    originals = get_unit_type_original_values()

    for original in originals:
        if i18n._(original) == translated_value:
            return original

    # If not found, return as-is
    return translated_value


def translate_unit_type_from_original(original_value: str) -> str:
    """Convert original unit type to translated value

    Args:
        original_value: Original unit type (e.g., "US")

    Returns:
        Translated value (e.g., "SU" in English, "US" in Italian)
    """
    i18n = get_i18n()
    return i18n._(original_value)


# Export for external use
__all__ = ['DesktopI18n', 'get_i18n', '_', 'get_unit_types',
           'get_unit_type_original_values', 'translate_unit_type_to_original',
           'translate_unit_type_from_original']
