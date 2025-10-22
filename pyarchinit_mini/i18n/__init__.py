"""
Internationalization (i18n) module for PyArchInit-Mini
Provides Flask-Babel configuration and locale utilities
"""

from .flask_babel_config import init_babel, get_locale, get_translations, _
from .locale_manager import LocaleManager

__all__ = [
    'init_babel',
    'get_locale',
    'get_translations',
    '_',
    'LocaleManager'
]
