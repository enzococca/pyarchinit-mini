"""Graph routes — view, download (Task 19); import-preview/apply (Task 20)."""
from pathlib import Path
from flask import Blueprint, abort, send_file

from pyarchinit_mini.graphproj.filesystem import paradata_dir, slugify

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
