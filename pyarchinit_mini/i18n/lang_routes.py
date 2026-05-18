"""Blueprint for language switching — POST + redirect to referrer.

Preserves the current URL query string by relying on the browser's Referer
header. Compatible with the existing get_locale() resolution chain
(session > URL > Accept-Language > default).
"""
from flask import Blueprint, session, redirect, request, url_for

lang_bp = Blueprint("lang", __name__)

_VALID_LANGS = frozenset({"it", "en"})


@lang_bp.post("/set-language/<lang>")
def set_language(lang: str):
    """Save chosen language in session, redirect back to referrer (or /)."""
    if lang in _VALID_LANGS:
        session["lang"] = lang
        session.permanent = True
    target = request.referrer or url_for("index")
    return redirect(target)
