"""Blueprint for /import-graphml/ — upload + preview + apply yEd Extended Matrix."""
from __future__ import annotations

import os
import uuid
from pathlib import Path

from flask import (
    Blueprint, current_app, request, render_template, jsonify,
    session as flask_session, redirect, url_for,
)

from pyarchinit_mini.graphml_io.yed_importer import (
    parse_extended_matrix, build_import_plan, apply_import_plan,
)
from pyarchinit_mini.harris_swimlane.exceptions import (
    YEDImporterError, YEDImportValidationError,
)


yed_import_bp = Blueprint(
    "yed_import", __name__, url_prefix="/import-graphml",
    template_folder="templates",
)

_PLAN_CACHE: dict[str, dict] = {}


def _get_session():
    if hasattr(current_app, "db_manager"):
        return current_app.db_manager.connection.get_session()
    from pyarchinit_mini.database.connection import DatabaseConnection
    db_url = os.getenv("DATABASE_URL", "sqlite:///pyarchinit_mini.db")
    return DatabaseConnection.from_url(db_url).get_session()


@yed_import_bp.get("/")
def index():
    return render_template("yed_import/index.html")


@yed_import_bp.post("/preview")
def preview():
    f = request.files.get("file")
    if not f or not f.filename:
        return jsonify({"error": "missing_file"}), 400
    tmpdir = Path("/tmp/yed_import")
    tmpdir.mkdir(parents=True, exist_ok=True)
    upload_path = tmpdir / f"{uuid.uuid4().hex}.graphml"
    f.save(str(upload_path))

    try:
        with _get_session() as session:
            parsed = parse_extended_matrix(upload_path)
            plan = build_import_plan(parsed, session)
    except (YEDImporterError, YEDImportValidationError) as e:
        return jsonify({"error": "import", "message": str(e)}), 400
    finally:
        try: upload_path.unlink()
        except Exception: pass

    plan_id = uuid.uuid4().hex
    _PLAN_CACHE[plan_id] = {
        "sites": plan.sites,
        "periodizations": plan.periodizations,
        "us_records": plan.us_records,
        "relationships": plan.relationships,
        "warnings": plan.warnings,
        "conflicts": plan.conflicts,
    }
    return render_template("yed_import/preview.html", plan_id=plan_id, plan=plan)


@yed_import_bp.post("/apply")
def apply():
    plan_id = request.form.get("plan_id", "")
    raw = _PLAN_CACHE.pop(plan_id, None)
    if not raw:
        return jsonify({"error": "plan_expired"}), 400
    from pyarchinit_mini.graphml_io.yed_importer import ImportPlan
    plan = ImportPlan(**raw)
    with _get_session() as session:
        result = apply_import_plan(plan, session)
    return render_template("yed_import/result.html", result=result)
