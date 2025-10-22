"""
Locale manager for non-Flask contexts (Desktop GUI, CLI, API)
"""

import gettext
import os
from pathlib import Path
from typing import Optional


class LocaleManager:
    """Manage translations for non-Flask contexts"""

    def __init__(self, default_locale: str = 'it'):
        """Initialize locale manager

        Args:
            default_locale: Default language code ('it' or 'en')
        """
        self.current_locale = default_locale
        self.localedir = self._get_translations_dir()
        self._translator: Optional[gettext.GNUTranslations] = None
        self.load_locale()

    def _get_translations_dir(self) -> Path:
        """Get path to translations directory

        Returns:
            Path to pyarchinit_mini/translations
        """
        return Path(__file__).parent.parent / 'translations'

    def load_locale(self, lang: Optional[str] = None):
        """Load translations for specified language

        Args:
            lang: Language code ('it' or 'en'), or None to use current_locale
        """
        if lang:
            self.current_locale = lang

        try:
            self._translator = gettext.translation(
                'messages',
                localedir=str(self.localedir),
                languages=[self.current_locale],
                fallback=True
            )
            print(f"[i18n] Loaded translations for: {self.current_locale}")
        except Exception as e:
            print(f"[i18n] Translation loading error: {e}")
            print(f"[i18n] Using fallback (no translations)")
            self._translator = gettext.NullTranslations()

    def gettext(self, message: str) -> str:
        """Translate message to current locale

        Args:
            message: English message to translate

        Returns:
            Translated message
        """
        if self._translator:
            return self._translator.gettext(message)
        return message

    def ngettext(self, singular: str, plural: str, n: int) -> str:
        """Translate plural message

        Args:
            singular: Singular form
            plural: Plural form
            n: Count

        Returns:
            Translated message (singular or plural)
        """
        if self._translator:
            return self._translator.ngettext(singular, plural, n)
        return singular if n == 1 else plural

    def switch_language(self, lang: str):
        """Switch interface language

        Args:
            lang: Language code ('it' or 'en')
        """
        if lang in ['it', 'en']:
            self.load_locale(lang)
        else:
            print(f"[i18n] Unsupported language: {lang}")

    def get_current_locale(self) -> str:
        """Get current locale

        Returns:
            Current language code
        """
        return self.current_locale

    def get_available_locales(self) -> list:
        """Get list of available locales

        Returns:
            List of language codes
        """
        available = []
        if self.localedir.exists():
            for item in self.localedir.iterdir():
                if item.is_dir() and (item / 'LC_MESSAGES').exists():
                    available.append(item.name)
        return available or ['it', 'en']


# Global instance for non-Flask usage
_default_manager: Optional[LocaleManager] = None


def get_locale_manager() -> LocaleManager:
    """Get global LocaleManager instance

    Returns:
        LocaleManager singleton
    """
    global _default_manager
    if _default_manager is None:
        _default_manager = LocaleManager()
    return _default_manager


# Convenience function for quick translation
def _(message: str) -> str:
    """Translate message using global locale manager

    Args:
        message: Message to translate

    Returns:
        Translated message
    """
    return get_locale_manager().gettext(message)
