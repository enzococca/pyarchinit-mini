"""HTML pages for paradata CRUD — 5 sections (one per node type).

Backed by ParadataStore (JSON sidecar). REST counterparts live in
paradata_routes.py.
"""
from flask import Blueprint, render_template, request, redirect, url_for, abort

from pyarchinit_mini.graphproj.paradata_store import ParadataStore
from pyarchinit_mini.graphproj.exceptions import ParadataConflict, ParadataNotFound

paradata_ui_bp = Blueprint("paradata_ui", __name__, url_prefix="/paradata")


# kind → {list_fn, add_fn, update_fn, delete_fn, columns, fields}
KIND_DEF = {
    "authors": {
        "list_fn": "list_authors", "add_fn": "add_author",
        "update_fn": "update_author", "delete_fn": "delete_author",
        "columns": ["name", "orcid"], "fields": ["name", "orcid"],
    },
    "licenses": {
        "list_fn": "list_licenses", "add_fn": "add_license",
        "update_fn": "update_license", "delete_fn": "delete_license",
        "columns": ["name", "url"], "fields": ["name", "url"],
    },
    "embargoes": {
        "list_fn": "list_embargoes", "add_fn": "add_embargo",
        "update_fn": "update_embargo", "delete_fn": "delete_embargo",
        "columns": ["label", "until"], "fields": ["label", "until"],
    },
    "documents": {
        "list_fn": "list_documents", "add_fn": "add_document",
        "update_fn": "update_document", "delete_fn": "delete_document",
        "columns": ["title", "uri"], "fields": ["title", "uri"],
    },
    "epochs": {
        "list_fn": "list_epochs", "add_fn": "add_epoch",
        "update_fn": "update_epoch", "delete_fn": "delete_epoch",
        "columns": ["name", "start", "end"], "fields": ["name", "start", "end"],
    },
}


def _kind_or_404(kind):
    if kind not in KIND_DEF:
        abort(404)
    return KIND_DEF[kind]


@paradata_ui_bp.get("/<site>/<kind>", endpoint="list")
def list_(site, kind):
    cfg = _kind_or_404(kind)
    store = ParadataStore(site)
    items = getattr(store, cfg["list_fn"])()
    return render_template(
        "paradata/list.html",
        site=site, kind=kind, items=items, columns=cfg["columns"],
    )


@paradata_ui_bp.get("/<site>/<kind>/new", endpoint="new")
def new(site, kind):
    cfg = _kind_or_404(kind)
    return render_template(
        "paradata/edit.html",
        site=site, kind=kind, item=None, fields=cfg["fields"],
        form_action=url_for("paradata_ui.new_post", site=site, kind=kind),
    )


@paradata_ui_bp.post("/<site>/<kind>/new", endpoint="new_post")
def new_post(site, kind):
    cfg = _kind_or_404(kind)
    store = ParadataStore(site)
    kwargs = {f: (request.form.get(f) or None) for f in cfg["fields"]}
    try:
        getattr(store, cfg["add_fn"])(**kwargs)
    except (ParadataConflict, TypeError):
        # Silent on duplicate / missing-required for now; production would
        # re-render with error message
        pass
    return redirect(url_for("paradata_ui.list", site=site, kind=kind))


@paradata_ui_bp.get("/<site>/<kind>/<node_id>/edit", endpoint="edit")
def edit(site, kind, node_id):
    cfg = _kind_or_404(kind)
    store = ParadataStore(site)
    items = getattr(store, cfg["list_fn"])()
    item = next((i for i in items if i["node_id"] == node_id), None)
    if item is None:
        abort(404)
    return render_template(
        "paradata/edit.html",
        site=site, kind=kind, item=item, fields=cfg["fields"],
        form_action=url_for(
            "paradata_ui.edit_post", site=site, kind=kind, node_id=node_id
        ),
    )


@paradata_ui_bp.post("/<site>/<kind>/<node_id>/edit", endpoint="edit_post")
def edit_post(site, kind, node_id):
    cfg = _kind_or_404(kind)
    store = ParadataStore(site)
    kwargs = {f: (request.form.get(f) or None) for f in cfg["fields"]}
    try:
        getattr(store, cfg["update_fn"])(node_id, **kwargs)
    except ParadataNotFound:
        abort(404)
    return redirect(url_for("paradata_ui.list", site=site, kind=kind))


@paradata_ui_bp.post("/<site>/<kind>/<node_id>/delete", endpoint="delete")
def delete(site, kind, node_id):
    cfg = _kind_or_404(kind)
    store = ParadataStore(site)
    try:
        getattr(store, cfg["delete_fn"])(node_id)
    except ParadataNotFound:
        abort(404)
    return redirect(url_for("paradata_ui.list", site=site, kind=kind))
