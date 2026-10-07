"""The generic MCP write tools (insert_data / batch_insert) must refuse every
media table.

A media row written there without going through manage_media is a record
with no file behind it. pyarchinit-mini#4 found 129 such husk rows
(NOT NULL columns minimally filled with '' / 0, everything else NULL), the
exact shape an AI client produces when a generic insert tool answers
"required_field_missing" and it retries with empty values. insert_data has
blocked media_table/media_thumb_table since 1.9.25; batch_insert never did,
and neither covered media_to_entity_table.
"""
import pytest
from sqlalchemy import create_engine, text

from pyarchinit_mini.models.base import Base
import pyarchinit_mini.models  # noqa: F401  (registers every model on Base)
from pyarchinit_mini.mcp_server.tools.batch_insert_tool import batch_insert
from pyarchinit_mini.mcp_server.tools.insert_data_tool import insert_data

MEDIA_TABLES = ["media_table", "media_thumb_table", "media_to_entity_table"]

# A minimal, schema-valid row per table: what the tool would happily insert
# if the guard were missing.
ROW = {
    "media_table": {"filename": "x.jpg"},
    "media_thumb_table": {"id_media": 1},
    "media_to_entity_table": {
        "id_entity": 1, "entity_type": "US", "table_name": "us_table", "id_media": 1,
    },
}


@pytest.fixture
def db_url(tmp_path, monkeypatch):
    url = f"sqlite:///{tmp_path / 'guard.db'}"
    Base.metadata.create_all(create_engine(url))
    monkeypatch.setenv("DATABASE_URL", url)
    return url


def _count(url, table):
    with create_engine(url).connect() as c:
        return c.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()


@pytest.mark.parametrize("table", MEDIA_TABLES)
def test_batch_insert_refuses_media_tables(db_url, table):
    result = batch_insert(table=table, records=[ROW[table]])

    assert result["success"] is False
    assert result["error"] == "use_manage_media_tool"
    assert result["correct_tool"] == "manage_media"
    assert _count(db_url, table) == 0


def test_batch_insert_refuses_media_tables_even_in_validate_only(db_url):
    """The guard must sit before validation: validate_only=True must not leak
    schema details that teach the client how to fill the row."""
    result = batch_insert(table="media_table", records=[ROW["media_table"]], validate_only=True)

    assert result["success"] is False
    assert result["error"] == "use_manage_media_tool"


@pytest.mark.parametrize("table", MEDIA_TABLES)
def test_insert_data_refuses_media_tables(db_url, table):
    result = insert_data(table=table, data=ROW[table])

    assert result["success"] is False
    assert result["error"] == "use_manage_media_tool"
    assert result["correct_tool"] == "manage_media"
    assert _count(db_url, table) == 0
