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


def test_get_pottery_by_id(pottery_service):
    p = pottery_service.create_pottery({"sito": "X", "form": "Olla"})
    fetched = pottery_service.get_pottery_by_id(p.id_rep)
    assert fetched is not None
    assert fetched.id_rep == p.id_rep


def test_get_pottery_by_id_missing(pottery_service):
    assert pottery_service.get_pottery_by_id(99999) is None


def test_get_pottery_dto_by_id(pottery_service):
    p = pottery_service.create_pottery({"sito": "X", "form": "Olla", "qty": 2})
    dto = pottery_service.get_pottery_dto_by_id(p.id_rep)
    assert dto is not None
    assert dto.sito == "X"
    assert dto.qty == 2


def test_update_pottery(pottery_service):
    p = pottery_service.create_pottery({"sito": "X", "form": "Olla"})
    u = pottery_service.update_pottery(p.id_rep, {"form": "Ciotola", "qty": 5})
    assert u.form == "Ciotola"
    assert u.qty == 5


def test_update_pottery_missing_raises(pottery_service):
    with pytest.raises(ValueError, match="not found"):
        pottery_service.update_pottery(99999, {"form": "X"})


def test_update_does_not_break_unique_constraint(pottery_service):
    a = pottery_service.create_pottery({"sito": "X", "id_number": 1})
    b = pottery_service.create_pottery({"sito": "X", "id_number": 2})
    with pytest.raises(ValueError, match="already exists"):
        pottery_service.update_pottery(b.id_rep, {"id_number": 1})


def test_delete_pottery(pottery_service):
    p = pottery_service.create_pottery({"sito": "X", "form": "Olla"})
    assert pottery_service.delete_pottery(p.id_rep) is True
    assert pottery_service.get_pottery_by_id(p.id_rep) is None


def test_delete_pottery_missing_returns_false(pottery_service):
    assert pottery_service.delete_pottery(99999) is False
