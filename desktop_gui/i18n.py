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


# Export for external use
__all__ = ['DesktopI18n', 'get_i18n', '_']
