"""Graph routes — view, download (Task 19); import-preview/apply (Task 20)."""
import uuid
from pathlib import Path
from flask import Blueprint, abort, g, render_template, request, send_file, session as flask_session

from pyarchinit_mini.graphproj.filesystem import paradata_dir, slugify
from pyarchinit_mini.graphproj.exceptions import GraphMLReadError, IngestStaleError
from pyarchinit_mini.graphml_io.reader import read_graphml
from pyarchinit_mini.graphproj.ingestor import GraphIngestor

graph_bp = Blueprint("graph", __name__, url_prefix="/sites")

STRATIGRAPHY_FILENAME = "stratigraphy.graphml"


def _stratigraphy_path(site: str) -> Path:
    return paradata_dir(site) / STRATIGRAPHY_FILENAME


@graph_bp.get("/<site>/graph/download")
def download(site: str):
    path = _stratigraphy_path(site).resolve()
    if not path.exists():
        abort(404)
    return send_file(
        path,
        as_attachment=True,
        download_name=f"{slugify(site)}_stratigraphy.graphml",
        mimetype="application/xml",
    )


@graph_bp.get("/<site>/graph/view")
def view(site: str):
    path = _stratigraphy_path(site)
    if not path.exists():
        abort(404)
    content = path.read_text(encoding="utf-8")
    return content, 200, {"Content-Type": "application/xml; charset=utf-8"}


@graph_bp.post("/<site>/graph/import-preview")
def import_preview(site: str):
    upload = request.files.get("file")
    if upload is None:
        return ("No file uploaded", 400)

    imports_dir = paradata_dir(site) / "imports"
    imports_dir.mkdir(parents=True, exist_ok=True)
    upload_id = uuid.uuid4().hex
    saved_path = imports_dir / f"{upload_id}.graphml"
    upload.save(saved_path)

    try:
        graph = read_graphml(saved_path)
    except GraphMLReadError as e:
        return f"Invalid GraphML: {e}", 400

    db_session = getattr(g, "db_session", None)
    if db_session is None:
        return "No DB session bound", 500
    ingestor = GraphIngestor(db_session, site)
    plan = ingestor.preview(graph)

    # Persist plan in Flask session for the apply step
    flask_session[f"import_plan:{site}:{upload_id}"] = {
        "snapshot_revision": plan.snapshot_revision,
        "inserts": [e.__dict__ for e in plan.inserts],
        "updates": [e.__dict__ for e in plan.updates],
        "skips_local_newer": [e.__dict__ for e in plan.skips_local_newer],
        "skips_locked": [e.__dict__ for e in plan.skips_locked],
    }

    return render_template(
        "graph_import_preview.html",
        site=site, plan=plan, upload_id=upload_id,
    )


@graph_bp.post("/<site>/graph/import-apply")
def import_apply(site: str):
    upload_id = request.form.get("upload_id")
    if not upload_id:
        return "Missing upload_id", 400

    stored = flask_session.get(f"import_plan:{site}:{upload_id}")
    if stored is None:
        return ("Plan not found in session", 404)

    from pyarchinit_mini.graphproj.ingest_plan import IngestPlan, NodePlanEntry

    def _r(entries):
        return tuple(NodePlanEntry(**e) for e in entries)

    plan = IngestPlan(
        site=site,
        snapshot_revision=stored["snapshot_revision"],
        inserts=_r(stored["inserts"]),
        updates=_r(stored["updates"]),
        skips_local_newer=_r(stored["skips_local_newer"]),
        skips_locked=_r(stored["skips_locked"]),
    )

    db_session = getattr(g, "db_session", None)
    if db_session is None:
        return "No DB session bound", 500
    ingestor = GraphIngestor(db_session, site)
    try:
        result = ingestor.apply(plan)
    except IngestStaleError as e:
        return (
            f"Plan stale (expected={e.expected}, actual={e.actual}). Re-upload to retry.",
            409,
        )

    # Cleanup
    flask_session.pop(f"import_plan:{site}:{upload_id}", None)
    upload_file = paradata_dir(site) / "imports" / f"{upload_id}.graphml"
    if upload_file.exists():
        try:
            upload_file.unlink()
        except Exception:
            pass

    return render_template(
        "graph_import_result.html",
        site=site, result=result,
    )
