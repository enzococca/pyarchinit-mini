from pyarchinit_mini.sync.transform import (
    cast_expr, row_hash_sql, build_pk_hash_select, build_insert, build_update)

def test_cast_varchar_to_integer_guards_non_numeric():
    e = cast_expr("character varying", "integer", None)
    assert "~ '^-?[0-9]+$'" in e and "::integer" in e and "%s" in e

def test_cast_bigint_to_boolean():
    e = cast_expr("bigint", "boolean", None)
    assert "false" in e and "true" in e and "%s" in e

def test_cast_varchar_to_date_handles_eu_formats():
    e = cast_expr("character varying", "date", None)
    assert "DD/MM/YYYY" in e and "DD-MM-YYYY" in e

def test_cast_text_to_varchar_truncates():
    e = cast_expr("text", "character varying", 100)
    assert "left(" in e and "100" in e

def test_cast_geometry_uses_geometry_cast():
    assert cast_expr("geometry", "geometry", None) == "(%s)::geometry"

def test_row_hash_uses_pipe_operator_not_concat_ws():
    h = row_hash_sql(["a", "b"])
    assert h.startswith("md5(") and "||'|'||" in h and "concat_ws" not in h

def test_build_pk_hash_select():
    s = build_pk_hash_select("us_table", ["id_us"], ["sito", "us"])
    assert s.lower().startswith("select")
    assert '"id_us"' in s and 'from public."us_table"' in s.lower()

def test_build_insert_includes_fill_and_value_exprs():
    sql = build_insert("us_table", ["sito"], ["(%s)::text"], {"created_at": "now()", "version_number": "1"})
    assert 'insert into public."us_table"' in sql.lower()
    assert '"sito"' in sql and '"created_at"' in sql and "now()" in sql and "(%s)::text" in sql

def test_build_update_sets_and_pk_where():
    sql = build_update("site_table", ["descrizione"], ["(%(descrizione)s)::text"], ["id_sito"])
    assert 'update public."site_table" set "descrizione" = (%(descrizione)s)::text' in sql.lower()
    assert 'where "id_sito" = %(__pk_id_sito)s' in sql.lower()
