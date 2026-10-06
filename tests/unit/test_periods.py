from sqlalchemy import text

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.graphproj.periods import PeriodRow, load_period_rows, resolve_row_id


def _session(tmp_path):
    conn = DatabaseConnection.sqlite(str(tmp_path / "p.db"))
    conn.create_tables()
    return conn.get_session()


def test_rows_sorted_with_slash_labels(tmp_path):
    with _session(tmp_path) as s:
        s.execute(text("INSERT INTO period_table (sito, periodo, fase, datazione, created_at, updated_at, version_number) VALUES ('S','II','a',NULL,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,1), ('S','I','b','sec. I',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,1)"))
        s.commit()
        rows = load_period_rows(s, "S")
    assert [r.label for r in rows] == ["I/b", "II/a"]
    assert rows[0].row_id == "row_0" and rows[0].datazione == "sec. I" and not rows[0].is_fallback


def test_empty_periodo_rows_are_dropped_and_blank_fase_is_none(tmp_path):
    with _session(tmp_path) as s:
        s.execute(text("INSERT INTO period_table (sito, periodo, fase, created_at, updated_at, version_number) VALUES ('S','','',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,1), ('S','I','',CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,1)"))
        s.commit()
        rows = load_period_rows(s, "S")
    assert [(r.label, r.fase) for r in rows] == [("I", None)]


def test_resolve_matches_fase_then_periodo_then_appends_fallback_once():
    rows = [PeriodRow(row_id="row_0", label="I/a", periodo="I", fase="a")]
    assert resolve_row_id(rows, "a") == "row_0"
    assert resolve_row_id(rows, "I") == "row_0"
    assert resolve_row_id(rows, None) == "row_1"
    assert resolve_row_id(rows, "zzz") == "row_1"
    assert len(rows) == 2 and rows[1].is_fallback and rows[1].label == "Periodo 1"


def test_as_dict_matches_swimlane_row_shape():
    assert PeriodRow(row_id="row_0", label="Periodo 1", is_fallback=True).as_dict() == {
        "row_id": "row_0", "label": "Periodo 1", "periodo": None, "fase": None,
        "datazione": None, "is_fallback": True,
    }


def test_missing_period_table_yields_no_rows(tmp_path, caplog):
    with _session(tmp_path) as s:
        s.execute(text("DROP TABLE period_table")); s.commit()
        assert load_period_rows(s, "S") == []
    assert "period_table unavailable" in caplog.text
