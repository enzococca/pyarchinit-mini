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
        current_app.logger.exception("matrix_import: extract() raised")
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


def _apply_form_edits(
    plan: AIPlan,
    form,
    selected_us_idx: set,
    selected_edges_idx: set,
) -> AIPlan:
    """Build a filtered plan with user-edited values for selected rows only."""
    from pyarchinit_mini.ai_matrix.plan import USRow, EdgeRow
    new_us = []
    for idx, _u in enumerate(plan.us):
        if str(idx) not in selected_us_idx:
            continue
        new_us.append(USRow(
            us_num=form.get(f"us_num_{idx}", "").strip(),
            area=form.get(f"area_{idx}", "").strip() or None,
            unit_type=form.get(f"unit_type_{idx}", "US").strip(),
            descrizione=form.get(f"desc_{idx}", "").strip(),
            fase_recente=int(form.get(f"fr_{idx}", "1") or "1"),
            fase_iniziale=int(form.get(f"fi_{idx}", "1") or "1"),
        ))
    new_edges = []
    for idx, _e in enumerate(plan.edges):
        if str(idx) not in selected_edges_idx:
            continue
        new_edges.append(EdgeRow(
            us_from=form.get(f"ef_{idx}", "").strip(),
            us_to=form.get(f"et_{idx}", "").strip(),
            tipo=form.get(f"etipo_{idx}", "copre").strip(),
        ))
    return AIPlan(
        detected_site=plan.detected_site,
        detected_area=plan.detected_area,
        us=new_us, edges=new_edges,
    )


@matrix_import_bp.post("/apply")
def apply():
    plan_json_str = request.form.get("plan_json", "")
    sito = request.form.get("sito", "").strip()
    image_b64 = request.form.get("image_b64", "")

    if not sito:
        flash("Nome sito obbligatorio", "error")
        return redirect(url_for("matrix_import.upload_form"))
    if not plan_json_str:
        flash("Plan mancante", "error")
        return redirect(url_for("matrix_import.upload_form"))

    selected_us = set(request.form.getlist("selected_us"))
    selected_edges = set(request.form.getlist("selected_edges"))

    try:
        plan = AIPlan.from_dict(json.loads(plan_json_str))
    except (json.JSONDecodeError, TypeError) as e:
        current_app.logger.warning("matrix_import: malformed plan_json: %s", e)
        flash("Plan malformato — riprova l'analisi", "error")
        return redirect(url_for("matrix_import.upload_form"))
    plan = _apply_form_edits(plan, request.form, selected_us, selected_edges)

    if not plan.us and not plan.edges:
        flash("Nessuna riga selezionata — controlla almeno una US o relazione", "error")
        return redirect(url_for("matrix_import.upload_form"))

    result = apply_ai_plan(plan, sito, g.db_session)

    # Save source image as media for the site (best-effort, non-blocking)
    if image_b64:
        try:
            _save_image_for_site(sito, image_b64)
        except Exception as exc:
            current_app.logger.warning("matrix_import media save failed: %s", exc)

    flash(
        f"Importate {result.us_imported} US, {result.edges_imported} relazioni "
        f"({result.us_skipped} US e {result.edges_skipped} relazioni saltate)",
        "success",
    )
    return redirect(url_for("us.list_us", sito=sito))


def _save_image_for_site(sito: str, image_b64: str) -> None:
    """Best-effort: persist the source image as a Media row linked to the site.

    Uses MediaService.store_and_register_media via a temporary file. Looks up
    id_sito by sito name; if MediaService isn't wired into this app context,
    silently no-ops (the import already committed).
    """
    import tempfile
    from sqlalchemy import text as _text

    row = g.db_session.execute(
        _text("SELECT id_sito FROM site_table WHERE sito = :s"), {"s": sito}
    ).fetchone()
    if not row:
        return
    id_sito = int(row[0])

    image_bytes = base64.b64decode(image_b64)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp.write(image_bytes)
        tmp_path = tmp.name

    try:
        media_svc = current_app.extensions.get("media_service")
        if media_svc is None:
            return
        media_svc.store_and_register_media(
            tmp_path,
            entity_type="site",
            entity_id=id_sito,
            description="AI Matrix Import source",
            tags="matrix_source,ai_import",
        )
    finally:
        import os as _os
        try:
            _os.unlink(tmp_path)
        except OSError:
            pass
