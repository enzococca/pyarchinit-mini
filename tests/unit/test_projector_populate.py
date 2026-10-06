import pytest
from sqlalchemy import text

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.graphproj.exceptions import ProjectionError
from pyarchinit_mini.graphproj.projector import GraphProjector
from pyarchinit_mini.graphproj.strat_graph import (
    get_swimlane, pyarchinit_attrs, stratigraphic_edges, stratigraphic_nodes,
)


@pytest.fixture
def db(tmp_path):
    path = tmp_path / "proj.db"
    conn = DatabaseConnection.sqlite(str(path)); conn.create_tables()
    with conn.get_session() as s:
        s.execute(text("INSERT INTO site_table (sito, created_at, updated_at, version_number) VALUES ('S', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1)"))
        s.execute(text("INSERT INTO period_table (sito, periodo, fase, created_at, updated_at, version_number) VALUES ('S','I','a', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1)"))
        s.execute(text(
            "INSERT INTO us_table (sito, area, settore, us, unita_tipo, descrizione, fase_iniziale, periodo_iniziale, node_uuid, rapporti, created_at, updated_at, version_number) VALUES "
            "('S','A','Nord','1','US','d1','a','I','0192aaaa-0000-7000-8000-000000000001',\"[['Copre', '2', 'A', 'S']]\", CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1),"
            "('S','A','Nord','2','USM','d2','a','I',NULL,NULL, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1),"
            "('S','A',NULL,'3','USVs',NULL,NULL,NULL,'0192aaaa-0000-7000-8000-000000000003',\"[['Taglia', '1', 'A', 'S']]\", CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1)"))
        s.commit()
    return conn, path


def test_populate_builds_contract_graph(db):
    conn, _ = db
    with conn.get_session() as s:
        g = GraphProjector.populate_graph(s, "S", group_by="area")
    assert g.graph_id == "strat:S"
    nodes = {pyarchinit_attrs(n)["us"]: n for n in stratigraphic_nodes(g)}
    assert set(nodes) == {"1", "2", "3"}
    assert nodes["1"].node_id == "0192aaaa-0000-7000-8000-000000000001"
    assert {(e.edge_source, e.edge_type, e.edge_target) for e in stratigraphic_edges(g)} == {
        (nodes["1"].node_id, "overlies", nodes["2"].node_id),
        (nodes["3"].node_id, "cuts", nodes["1"].node_id),
    }
    sw = get_swimlane(g)
    assert sw["group_by"] == "area" and sw["rows"][0]["label"] == "I/a"
    assert pyarchinit_attrs(nodes["1"])["sub_group"] == "A"


def test_populate_is_stable_for_rows_with_uuid(db):
    conn, _ = db
    with conn.get_session() as s:
        a = GraphProjector.populate_graph(s, "S"); b = GraphProjector.populate_graph(s, "S")
    ids = lambda g: {n.node_id for n in stratigraphic_nodes(g) if pyarchinit_attrs(n)["node_uuid"].startswith("0192")}
    assert ids(a) == ids(b)


def test_populate_area_filter_and_unknown_site(db):
    conn, _ = db
    with conn.get_session() as s:
        assert len(stratigraphic_nodes(GraphProjector.populate_graph(s, "S", area="B"))) == 0
        assert len(stratigraphic_nodes(GraphProjector.populate_graph(s, "NOPE"))) == 0


def test_populate_rejects_bad_group_by(db):
    conn, _ = db
    with conn.get_session() as s, pytest.raises(ValueError):
        GraphProjector.populate_graph(s, "S", group_by="banana")


def test_free_text_rapporti_yield_edges(db):
    conn, _ = db
    with conn.get_session() as s:
        s.execute(text("UPDATE us_table SET rapporti = 'copre 2' WHERE us = '1'")); s.commit()
        g = GraphProjector.populate_graph(s, "S")
    nodes = {pyarchinit_attrs(n)["us"]: n.node_id for n in stratigraphic_nodes(g)}
    overlies = [(e.edge_source, e.edge_target) for e in stratigraphic_edges(g) if e.edge_type == "overlies"]
    assert overlies == [(nodes["1"], nodes["2"])]


def test_populate_graph_wraps_importer_failure(db):
    conn, _ = db
    with conn.get_session() as s:
        s.execute(text("DROP TABLE us_table")); s.commit()
        with pytest.raises(ProjectionError):
            GraphProjector.populate_graph(s, "S")


def test_populate_without_period_table_uses_fallback_row(db):
    conn, _ = db
    with conn.get_session() as s:
        s.execute(text("DROP TABLE period_table")); s.commit()
        g = GraphProjector.populate_graph(s, "S")
    assert get_swimlane(g)["rows"][0]["is_fallback"] is True
    assert len(stratigraphic_nodes(g)) == 3
