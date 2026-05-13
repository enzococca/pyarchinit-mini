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


@pytest.fixture
def populated(pottery_service):
    pottery_service.create_pottery({"sito": "X", "area": "A", "us": 1, "form": "Olla", "fabric": "Coarse", "qty": 5})
    pottery_service.create_pottery({"sito": "X", "area": "A", "us": 2, "form": "Ciotola", "fabric": "Fine", "qty": 1})
    pottery_service.create_pottery({"sito": "Y", "area": "B", "us": 1, "form": "Olla", "fabric": "Coarse", "qty": 2})
    return pottery_service


def test_get_all_pottery_paginated(populated):
    items, total = populated.get_all_pottery(page=1, size=2)
    assert total == 3
    assert len(items) == 2


def test_get_all_pottery_filter_by_sito(populated):
    items, total = populated.get_all_pottery(filters={"sito": "X"})
    assert total == 2
    assert all(i.sito == "X" for i in items)


def test_get_all_pottery_filter_combined(populated):
    items, total = populated.get_all_pottery(filters={"sito": "X", "form": "Olla"})
    assert total == 1


def test_count_pottery(populated):
    assert populated.count_pottery() == 3
    assert populated.count_pottery({"form": "Olla"}) == 2


def test_search_pottery_text(populated):
    items = populated.search_pottery("Cias")  # case-insensitive substring, no matches
    assert items == []
    items = populated.search_pottery("Olla")
    assert len(items) == 2


def test_get_pottery_by_site(populated):
    items = populated.get_pottery_by_site("Y")
    assert len(items) == 1
    assert items[0].sito == "Y"


def test_get_pottery_by_us(populated):
    items = populated.get_pottery_by_us("X", "A", 1)
    assert len(items) == 1


def test_get_pottery_by_form(populated):
    items = populated.get_pottery_by_form("Olla")
    assert len(items) == 2


def test_form_distribution(populated):
    dist = populated.get_form_distribution()
    assert dist["Olla"] == 2
    assert dist["Ciotola"] == 1


def test_fabric_distribution_scoped_by_site(populated):
    dist = populated.get_fabric_distribution(sito="X")
    assert dist["Coarse"] == 1
    assert dist["Fine"] == 1


def test_count_by_site(populated):
    rows = populated.count_by_site()
    by_site = {r["sito"]: r["count"] for r in rows}
    assert by_site["X"] == 2
    assert by_site["Y"] == 1


def test_calculate_mni(populated):
    mni = populated.calculate_mni(sito="X")
    # (Olla, Coarse, None) qty=5 and (Ciotola, Fine, None) qty=1
    assert mni["total"] == 6
    assert len(mni["groups"]) == 2
