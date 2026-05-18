"""REST API for paradata CRUD (authors in Task 16; other 4 types in Task 17)."""
from flask import Blueprint, jsonify, request

from pyarchinit_mini.graphproj.paradata_store import ParadataStore
from pyarchinit_mini.graphproj.exceptions import (
    ParadataConflict, ParadataNotFound, ParadataStorageError,
)

paradata_bp = Blueprint("paradata", __name__, url_prefix="/api/v1/paradata")


@paradata_bp.get("/<site>/authors")
def list_authors(site: str):
    store = ParadataStore(site)
    return jsonify(store.list_authors()), 200


@paradata_bp.post("/<site>/authors")
def create_author(site: str):
    payload = request.get_json(silent=True) or {}
    name = payload.get("name")
    if not name:
        return jsonify({"error": "validation", "fields": {"name": "required"}}), 400
    orcid = payload.get("orcid")
    try:
        author = ParadataStore(site).add_author(name=name, orcid=orcid)
    except ParadataConflict as e:
        return jsonify({"error": "duplicate", "existing": e.existing}), 409
    except ParadataStorageError as e:
        return jsonify({"error": "storage", "message": str(e)}), 500
    return jsonify(author), 201


@paradata_bp.put("/<site>/authors/<node_id>")
def update_author(site: str, node_id: str):
    payload = request.get_json(silent=True) or {}
    try:
        updated = ParadataStore(site).update_author(
            node_id,
            name=payload.get("name"),
            orcid=payload.get("orcid"),
        )
    except ParadataNotFound:
        return jsonify({"error": "not_found", "node_id": node_id}), 404
    except ParadataStorageError as e:
        return jsonify({"error": "storage", "message": str(e)}), 500
    return jsonify(updated), 200


@paradata_bp.delete("/<site>/authors/<node_id>")
def delete_author(site: str, node_id: str):
    try:
        ParadataStore(site).delete_author(node_id)
    except ParadataNotFound:
        return jsonify({"error": "not_found", "node_id": node_id}), 404
    return "", 204


# --- generic kind dispatcher (Task 17) ---

# (kind → (list_method, add_method, update_method, delete_method, accepted_fields, required_field))
KIND_METHODS = {
    "licenses": ("list_licenses", "add_license", "update_license", "delete_license",
                 ("name", "url"), "name"),
    "embargoes": ("list_embargoes", "add_embargo", "update_embargo", "delete_embargo",
                  ("label", "until"), "label"),
    "documents": ("list_documents", "add_document", "update_document", "delete_document",
                  ("title", "uri"), "title"),
    "epochs": ("list_epochs", "add_epoch", "update_epoch", "delete_epoch",
               ("name", "start", "end"), "name"),
}


@paradata_bp.get("/<site>/<kind>")
def list_kind(site: str, kind: str):
    if kind == "authors":
        return list_authors(site)
    if kind not in KIND_METHODS:
        return jsonify({"error": "unknown_kind", "kind": kind}), 404
    list_n, *_ = KIND_METHODS[kind]
    fn = getattr(ParadataStore(site), list_n)
    return jsonify(fn()), 200


@paradata_bp.post("/<site>/<kind>")
def create_kind(site: str, kind: str):
    if kind == "authors":
        return create_author(site)
    if kind not in KIND_METHODS:
        return jsonify({"error": "unknown_kind", "kind": kind}), 404
    _, add_n, _, _, fields, required_field = KIND_METHODS[kind]
    payload = request.get_json(silent=True) or {}
    if required_field not in payload or not payload[required_field]:
        return jsonify({
            "error": "validation",
            "fields": {required_field: "required"},
        }), 400
    kwargs = {f: payload.get(f) for f in fields if f in payload}
    try:
        created = getattr(ParadataStore(site), add_n)(**kwargs)
    except ParadataConflict as e:
        return jsonify({"error": "duplicate", "existing": e.existing}), 409
    except ParadataStorageError as e:
        return jsonify({"error": "storage", "message": str(e)}), 500
    return jsonify(created), 201


@paradata_bp.put("/<site>/<kind>/<node_id>")
def update_kind(site: str, kind: str, node_id: str):
    if kind == "authors":
        return update_author(site, node_id)
    if kind not in KIND_METHODS:
        return jsonify({"error": "unknown_kind", "kind": kind}), 404
    _, _, upd_n, _, fields, _ = KIND_METHODS[kind]
    payload = request.get_json(silent=True) or {}
    kwargs = {f: payload[f] for f in fields if f in payload}
    try:
        updated = getattr(ParadataStore(site), upd_n)(node_id, **kwargs)
    except ParadataNotFound:
        return jsonify({"error": "not_found", "node_id": node_id}), 404
    except ParadataStorageError as e:
        return jsonify({"error": "storage", "message": str(e)}), 500
    return jsonify(updated), 200


@paradata_bp.delete("/<site>/<kind>/<node_id>")
def delete_kind(site: str, kind: str, node_id: str):
    if kind == "authors":
        return delete_author(site, node_id)
    if kind not in KIND_METHODS:
        return jsonify({"error": "unknown_kind", "kind": kind}), 404
    _, _, _, del_n, _, _ = KIND_METHODS[kind]
    try:
        getattr(ParadataStore(site), del_n)(node_id)
    except ParadataNotFound:
        return jsonify({"error": "not_found", "node_id": node_id}), 404
    return "", 204
