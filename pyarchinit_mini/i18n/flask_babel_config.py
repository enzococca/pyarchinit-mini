"""
Flask-Babel configuration for PyArchInit-Mini web interface
"""

from flask import request, session
from flask_babel import Babel, gettext, lazy_gettext
from typing import Optional
import os


# Global Babel instance
babel: Optional[Babel] = None


def get_locale():
    """Determine user's preferred language

    Priority order:
    1. URL parameter (?lang=en or ?lang=it)
    2. Session variable
    3. Cookie
    4. Browser Accept-Language header
    5. Default to Italian

    Returns:
        Language code ('it' or 'en')
    """
    # 1. Check URL parameter
    lang_param = request.args.get('lang')
    if lang_param and lang_param in ['it', 'en']:
        session['lang'] = lang_param
        return lang_param

    # 2. Check session
    if 'lang' in session and session['lang'] in ['it', 'en']:
        return session['lang']

    # 3. Check browser Accept-Language header
    browser_lang = request.accept_languages.best_match(['it', 'en'])
    if browser_lang:
        return browser_lang

    # 4. Default to Italian
    return 'it'


def init_babel(app):
    """Initialize Flask-Babel for the application

    Args:
        app: Flask application instance

    Returns:
        Configured Babel instance
    """
    global babel

    # Configure Babel
    app.config['BABEL_DEFAULT_LOCALE'] = 'it'
    app.config['BABEL_SUPPORTED_LOCALES'] = ['it', 'en']

    # Translation directories
    # Look for translations in pyarchinit_mini/translations
    translations_dir = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'translations'
    )
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = translations_dir

    # Initialize Babel with locale_selector (Flask-Babel 3.x and 4.x compatible)
    babel = Babel(app, locale_selector=get_locale)

    print(f"[i18n] Flask-Babel initialized")
    print(f"[i18n] Default locale: {app.config['BABEL_DEFAULT_LOCALE']}")
    print(f"[i18n] Translations directory: {translations_dir}")
    print(f"[i18n] Supported locales: {app.config['BABEL_SUPPORTED_LOCALES']}")

    return babel


def get_translations():
    """Get current Babel translations instance

    Returns:
        Translations instance or None
    """
    if babel:
        return babel.instance.translations
    return None


# Convenience exports for template usage
_ = gettext
_l = lazy_gettext
