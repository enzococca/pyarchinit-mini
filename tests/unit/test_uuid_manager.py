"""Test UUID manager functionality."""
import re
from pyarchinit_mini.stratigraph.uuid_manager import (
    generate_uuid, validate_uuid, ensure_uuid, build_uri,
    get_entity_type_for_table, TABLE_ENTITY_TYPE_MAP
)


def test_generate_uuid_format():
    uid = generate_uuid()
    assert re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$', uid)


def test_validate_uuid_valid():
    uid = generate_uuid()
    assert validate_uuid(uid) is True


def test_validate_uuid_invalid():
    assert validate_uuid("not-a-uuid") is False
    assert validate_uuid(None) is False
    assert validate_uuid(123) is False


def test_ensure_uuid_generates_when_missing():
    class FakeRecord:
        entity_uuid = None
    r = FakeRecord()
    result = ensure_uuid(r)
    assert validate_uuid(result)
    assert r.entity_uuid == result


def test_ensure_uuid_keeps_existing():
    class FakeRecord:
        entity_uuid = None
    r = FakeRecord()
    r.entity_uuid = generate_uuid()
    original = r.entity_uuid
    result = ensure_uuid(r)
    assert result == original


def test_build_uri_with_table_name():
    uid = generate_uuid()
    uri = build_uri('us_table', uid)
    assert uri == f"http://pyarchinit.org/ontology/stratigraphic-unit/{uid}"


def test_build_uri_with_slug():
    uid = generate_uuid()
    uri = build_uri('site', uid)
    assert uri == f"http://pyarchinit.org/ontology/site/{uid}"


def test_table_entity_type_map_has_all_tables():
    assert 'us_table' in TABLE_ENTITY_TYPE_MAP
    assert 'site_table' in TABLE_ENTITY_TYPE_MAP
    assert 'inventario_materiali_table' in TABLE_ENTITY_TYPE_MAP
