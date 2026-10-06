import pytest
from s3dgraphy.importer.pyarchinit_importer import PyArchInitImporter
from sqlalchemy import text

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.graphproj.enrich import VALID_GROUP_BY, attach_pyarchinit_attributes, load_us_rows
from pyarchinit_mini.graphproj.periods import PeriodRow
from pyarchinit_mini.graphproj.strat_graph import pyarchinit_attrs, stratigraphic_nodes


@pytest.fixture
def db(tmp_path):
    path = tmp_path / "e.db"
    conn = DatabaseConnection.sqlite(str(path)); conn.create_tables()
    with conn.get_session() as s:
        s.execute(text("INSERT INTO site_table (sito, created_at, updated_at, version_number) VALUES ('S', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1)"))
        s.execute(text("INSERT INTO us_table (sito, area, settore, us, unita_tipo, descrizione, fase_iniziale, periodo_iniziale, struttura, node_uuid, rapporti, created_at, updated_at, version_number) VALUES "
                       "('S','A','Nord','1','US','d1','a','I','Edificio_A','0192aaaa-0000-7000-8000-000000000001',\"[['Copre', '2', 'A', 'S']]\", CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1),"
                       "('S','A','Nord','2','USM','d2',NULL,NULL,NULL,NULL,NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1)"))
        s.commit()
    return conn, path


def _graph(path):
    imp = PyArchInitImporter(connection_url=f"sqlite:///{path}", mapping_name="pyarchinit_us_mapping", filters={"sito": "S"})
    return imp, imp.parse()


def test_load_rows_reads_description_phase_group_and_rapporti(db):
    conn, _ = db
    with conn.get_session() as s:
        rows = load_us_rows(s, "S", group_by="strutture")
    r = {x.us: x for x in rows}
    assert r["1"].description == "d1" and r["1"].phase == "a" and r["1"].periodo == "I"
    assert r["1"].sub_group == "Edificio_A" and r["2"].sub_group is None
    assert r["1"].rapporti.startswith("[[") and r["2"].unit_type == "USM"


def test_load_rows_rejects_unknown_group_by(db):
    conn, _ = db
    with conn.get_session() as s, pytest.raises(ValueError):
        load_us_rows(s, "S", group_by="banana")
    assert "strutture" in VALID_GROUP_BY


def test_attach_matches_row_by_uuid(db):
    conn, path = db
    imp, g = _graph(path)
    with conn.get_session() as s:
        rows = load_us_rows(s, "S")
    period_rows = [PeriodRow(row_id="row_0", label="I/a", periodo="I", fase="a")]
    mapping = attach_pyarchinit_attributes(g, imp, rows, period_rows=period_rows)
    node = next(n for n in stratigraphic_nodes(g) if n.node_id == "0192aaaa-0000-7000-8000-000000000001")
    a = pyarchinit_attrs(node)
    assert a["us"] == "1" and a["area"] == "A" and a["row_id"] == "row_0" and a["description"] == "d1"
    assert node.attributes["EMid"] == "0192aaaa-0000-7000-8000-000000000001"
    assert mapping[a["id_us"]] == node.node_id


def test_attach_matches_row_without_uuid_by_importer_name(db):
    conn, path = db
    imp, g = _graph(path)
    with conn.get_session() as s:
        rows = load_us_rows(s, "S")
    period_rows = [PeriodRow(row_id="row_0", label="I/a", periodo="I", fase="a")]
    attach_pyarchinit_attributes(g, imp, rows, period_rows=period_rows)
    usm = next(n for n in stratigraphic_nodes(g) if n.name == "A.Nord.USM2")
    assert pyarchinit_attrs(usm)["us"] == "2"
    assert pyarchinit_attrs(usm)["row_id"] == "row_1"        # fallback row appended
    assert period_rows[1].is_fallback


def test_attach_skips_rows_without_node_and_reports_them(db, caplog):
    conn, path = db
    imp, g = _graph(path)
    with conn.get_session() as s:
        rows = load_us_rows(s, "S")
    for n in list(stratigraphic_nodes(g)):
        if n.name == "A.Nord.USM2":
            g.remove_node(n.node_id)
    mapping = attach_pyarchinit_attributes(g, imp, rows, period_rows=[])
    assert len(mapping) == 1 and "A.Nord.USM2" in caplog.text
