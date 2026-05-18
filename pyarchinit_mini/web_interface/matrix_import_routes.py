"""Flask blueprint for the AI Matrix Import flow."""
from __future__ import annotations

import base64
import json
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
    image_file = request.files.get("image")
    text_hint = request.form.get("descrizione", "").strip()
    sito_form = request.form.get("sito", "").strip()
    sito_new = request.form.get("sito_new", "").strip()
    area_form = request.form.get("area", "").strip()
    provider = request.form.get("provider", "anthropic")

    if not image_file:
        flash("Carica un'immagine", "error")
        return redirect(url_for("matrix_import.upload_form"))
    image_bytes = image_file.read()

    try:
        result = extract(image_bytes, text_hint, provider)
    except Exception as e:
        flash(f"Errore AI: {e}", "error")
        return redirect(url_for("matrix_import.upload_form"))

    if result.rejected:
        return render_template(
            "matrix_import/rejected.html",
            reason=result.reason,
            confidence=result.confidence,
        )

    if sito_form == "__NEW__":
        sito_form = ""
    sito_finale = sito_new or sito_form or (result.plan.detected_site or "")

    return render_template(
        "matrix_import/preview.html",
        plan=result.plan,
        sito=sito_finale,
        area_default=area_form or (result.plan.detected_area or ""),
        sito_needs_input=(sito_finale == ""),
        image_b64=base64.b64encode(image_bytes).decode(),
        plan_json=json.dumps(result.plan.as_dict()),
    )


@matrix_import_bp.post("/apply")
def apply():
    """Stub — full implementation in Task 7."""
    return ("Not implemented yet — coming in Task 7", 501)
