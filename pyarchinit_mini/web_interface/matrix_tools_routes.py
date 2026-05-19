"""Standalone Matrix Tools page: import/export GraphML and Heriverse JSON."""
from __future__ import annotations

import os
from flask import Blueprint, render_template, current_app
from sqlalchemy import text


matrix_tools_bp = Blueprint("matrix_tools", __name__, url_prefix="/matrix-tools")


def _get_session():
    """Mirror the pattern used by other modern blueprints in this app."""
    if hasattr(current_app, "db_manager"):
        return current_app.db_manager.connection.get_session()
    from pyarchinit_mini.database.connection import DatabaseConnection
    db_url = os.getenv("DATABASE_URL", "sqlite:///pyarchinit_mini.db")
    return DatabaseConnection.from_url(db_url).get_session()


@matrix_tools_bp.get("/")
def index():
    with _get_session() as db:
        rows = db.execute(text("SELECT sito FROM site_table ORDER BY sito")).fetchall()
    sites = [r[0] for r in rows]
    return render_template("matrix_tools/index.html", sites=sites)
