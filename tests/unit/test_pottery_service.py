"""Unit tests for PotteryService."""

import pytest


def test_create_pottery_minimal(pottery_service):
    p = pottery_service.create_pottery({"sito": "X", "form": "Olla"})
    assert p.id_rep is not None
    assert p.sito == "X"
    assert p.form == "Olla"


def test_create_pottery_requires_sito(pottery_service):
    with pytest.raises(ValueError, match="sito"):
        pottery_service.create_pottery({"form": "Olla"})


def test_create_pottery_qty_must_be_positive(pottery_service):
    with pytest.raises(ValueError, match="qty"):
        pottery_service.create_pottery({"sito": "X", "qty": 0})
    with pytest.raises(ValueError, match="qty"):
        pottery_service.create_pottery({"sito": "X", "qty": -1})


def test_create_pottery_rejects_duplicate_sito_id_number(pottery_service):
    pottery_service.create_pottery({"sito": "X", "id_number": 1})
    with pytest.raises(ValueError, match="already exists"):
        pottery_service.create_pottery({"sito": "X", "id_number": 1})
