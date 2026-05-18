"""Tests for vision_extractor._parse_response — validation gate + JSON parsing."""
import json
import pytest

from pyarchinit_mini.ai_matrix.vision_extractor import _parse_response


def _ok_payload(**overrides):
    base = {
        "is_harris_matrix": True,
        "confidence": 0.9,
        "reason": "OK",
        "detected_site": "Test",
        "detected_area": None,
        "us": [{"us_num": "1", "area": "A", "unit_type": "US",
                "descrizione": "x", "fase_recente": 1, "fase_iniziale": 1}],
        "edges": [{"us_from": "1", "us_to": "2", "tipo": "copre"}],
    }
    base.update(overrides)
    return json.dumps(base)


def test_parse_valid_json_returns_accepted_result():
    r = _parse_response(_ok_payload())
    assert r.rejected is False
    assert r.confidence == 0.9
    assert r.plan is not None
    assert len(r.plan.us) == 1
    assert r.plan.us[0].us_num == "1"
    assert r.plan.edges[0].tipo == "copre"


def test_parse_rejects_when_not_harris_matrix():
    r = _parse_response(_ok_payload(is_harris_matrix=False, reason="Foto di un muro"))
    assert r.rejected is True
    assert "muro" in r.reason
    assert r.plan is None


def test_parse_rejects_low_confidence():
    r = _parse_response(_ok_payload(confidence=0.5))
    assert r.rejected is True
    assert r.confidence == 0.5
    assert r.plan is None


def test_parse_rejects_invalid_json():
    r = _parse_response("not valid json {{{")
    assert r.rejected is True
    assert "non-JSON" in r.reason or "JSON" in r.reason
    assert r.plan is None


def test_parse_handles_missing_fields_gracefully():
    minimal = json.dumps({"is_harris_matrix": True, "confidence": 0.8})
    r = _parse_response(minimal)
    assert r.rejected is False
    assert r.plan.us == []
    assert r.plan.edges == []
    assert r.plan.detected_site is None
