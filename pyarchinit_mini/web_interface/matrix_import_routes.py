"""Flask blueprint for the AI Matrix Import flow."""
from __future__ import annotations

import os

from flask import (
    Blueprint, request, render_template, redirect, url_for,
    flash, g, current_app,
)
from sqlalchemy import text

from pyarchinit_mini.ai_matrix.vision_extractor import extract
from pyarchinit_mini.ai_matrix.plan import AIPlan
from pyarchinit_mini.ai_matrix.apply import apply_ai_plan


matrix_import_bp = Blueprint(
    "matrix_import",
    __name__,
    url_prefix="/matrix-import",
)


@matrix_import_bp.route("/")
def upload_form():
    sites = g.db_session.execute(
        text("SELECT sito FROM site_table ORDER BY sito")
    ).fetchall()
    return render_template(
        "matrix_import/upload.html",
        sites=[r[0] for r in sites],
        default_provider=os.environ.get("AI_PROVIDER", "anthropic"),
    )


@matrix_import_bp.post("/upload")
def upload():
    """Stub — full implementation in Task 6."""
    return ("Not implemented yet — coming in Task 6", 501)
