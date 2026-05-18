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
