"""Flask blueprint exposing VocabProvider over REST.

Endpoints (all read-only):
  GET /api/v1/vocab/unit-types               — list (filterable by lang, family)
  GET /api/v1/vocab/unit-types/<abbr>        — single
  GET /api/v1/vocab/edge-types               — list (filterable by lang)
  GET /api/v1/vocab/visual-style/<unit_type> — visual style dict
  GET /api/v1/vocab/diagnostics              — admin (gate applied in Task 12)
"""
import hashlib
import json
from dataclasses import asdict
from flask import Blueprint, jsonify, make_response, request
from flask_login import current_user

from pyarchinit_mini.vocab.provider import VocabProvider

vocab_bp = Blueprint("vocab", __name__, url_prefix="/api/v1/vocab")


def _serialize_unit_type(ut) -> dict:
    d = asdict(ut)
    d["visual_style"] = asdict(ut.visual_style)
    return d


def _etag_for(payload) -> str:
    body = json.dumps(payload, default=str, sort_keys=True).encode("utf-8")
    return hashlib.sha256(body).hexdigest()[:16]


def _make_response(payload):
    body = json.dumps(payload, default=str)
    resp = make_response(body, 200)
    resp.headers["Content-Type"] = "application/json"
    resp.headers["ETag"] = _etag_for(payload)
    resp.headers["Cache-Control"] = "private, max-age=3600"
    resp.headers["X-Vocab-Status"] = "ok"
    return resp


@vocab_bp.get("/unit-types")
def get_unit_types():
    lang = request.args.get("lang", "en")
    family = request.args.get("family")
    types = VocabProvider.instance().get_unit_types(lang=lang)
    if family:
        if family not in {"real", "virtual"}:
            return jsonify({"error": "invalid_family", "valid": ["real", "virtual"]}), 400
        types = [t for t in types if t.family == family]
    return _make_response([_serialize_unit_type(t) for t in types])


@vocab_bp.get("/unit-types/<abbr>")
def get_unit_type(abbr: str):
    lang = request.args.get("lang", "en")
    t = VocabProvider.instance().get_unit_type(abbr, lang=lang)
    if t is None:
        all_types = VocabProvider.instance().get_unit_types(lang=lang)
        suggestions = [x.abbreviation for x in all_types
                       if abbr.upper() in x.abbreviation.upper()][:5]
        return jsonify({"error": "unknown_unit_type", "unit_type": abbr, "suggestions": suggestions}), 404
    return _make_response(_serialize_unit_type(t))


@vocab_bp.get("/edge-types")
def get_edge_types():
    lang = request.args.get("lang", "en")
    edges = VocabProvider.instance().get_edge_types(lang=lang)
    return _make_response([asdict(e) for e in edges])


@vocab_bp.get("/visual-style/<unit_type>")
def get_visual_style(unit_type: str):
    style = VocabProvider.instance().get_visual_style(unit_type)
    return _make_response(asdict(style))


@vocab_bp.get("/diagnostics")
def diagnostics():
    if not getattr(current_user, "is_authenticated", False):
        return jsonify({"error": "forbidden"}), 403
    role = getattr(current_user, "role", None)
    role_value = getattr(role, "value", role) if role else None
    if role_value not in ("ADMIN", "admin"):
        return jsonify({"error": "forbidden"}), 403
    return jsonify(VocabProvider.instance().diagnostics()), 200
