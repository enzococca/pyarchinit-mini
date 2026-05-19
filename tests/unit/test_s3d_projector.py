import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.graphproj.s3d_projector import S3DProjector


@pytest.fixture
def session_factory(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path}/p.db")
    with engine.begin() as conn:
        conn.execute(text("""CREATE TABLE site_table (
            id_sito INTEGER PRIMARY KEY AUTOINCREMENT,
            sito TEXT UNIQUE, descrizione TEXT)"""))
        conn.execute(text("""CREATE TABLE period_table (
            id_period INTEGER PRIMARY KEY AUTOINCREMENT,
            sito TEXT, periodo TEXT, fase TEXT, datazione TEXT,
            descrizione TEXT)"""))
        conn.execute(text("""CREATE TABLE us_table (
            id_us INTEGER PRIMARY KEY AUTOINCREMENT,
            sito TEXT, area TEXT, us TEXT, unita_tipo TEXT,
            descrizione TEXT,
            fase_iniziale TEXT, fase_finale TEXT,
            rapporti TEXT)"""))
        conn.execute(text("INSERT INTO site_table (sito) VALUES ('S1')"))
    return sessionmaker(bind=engine)


def test_period_fallback_when_table_empty(session_factory):
    s = session_factory()
    s.execute(text("INSERT INTO us_table (sito, area, us, unita_tipo) VALUES ('S1','A','1','USM')"))
    s.commit()
    g = S3DProjector.from_site(s, "S1")
    assert len(g.rows) == 1
    assert g.rows[0].label == "Periodo 1"
    assert g.rows[0].is_fallback is True


def test_periods_loaded_from_table(session_factory):
    s = session_factory()
    s.execute(text("INSERT INTO period_table (sito, periodo, fase, datazione) VALUES ('S1','II','a','XII sec')"))
    s.execute(text("INSERT INTO period_table (sito, periodo, fase, datazione) VALUES ('S1','I','b','X sec')"))
    s.commit()
    g = S3DProjector.from_site(s, "S1")
    # sorted alphabetically by (periodo, fase)
    assert [r.label for r in g.rows] == ["I/b", "II/a"]
    assert all(r.is_fallback is False for r in g.rows)


def test_us_without_period_goes_to_fallback_row(session_factory):
    s = session_factory()
    s.execute(text("INSERT INTO period_table (sito, periodo, fase) VALUES ('S1','I','a')"))
    s.execute(text("INSERT INTO us_table (sito, area, us, unita_tipo, fase_iniziale) VALUES ('S1','A','1','USM','a')"))
    s.execute(text("INSERT INTO us_table (sito, area, us, unita_tipo, fase_iniziale) VALUES ('S1','A','2','USM', NULL)"))
    s.commit()
    g = S3DProjector.from_site(s, "S1")
    by_label = {r.label: r for r in g.rows}
    assert "I/a" in by_label
    assert "Periodo 1" in by_label
    us1 = next(n for n in g.nodes if n.us == "1")
    us2 = next(n for n in g.nodes if n.us == "2")
    assert us1.row_id == by_label["I/a"].row_id
    assert us2.row_id == by_label["Periodo 1"].row_id


def test_edges_built_from_rapporti(session_factory):
    s = session_factory()
    s.execute(text("INSERT INTO us_table (sito, area, us, unita_tipo, rapporti) "
                   "VALUES ('S1','A','1','USM','[[\"Copre\", \"2\"]]')"))
    s.execute(text("INSERT INTO us_table (sito, area, us, unita_tipo) VALUES ('S1','A','2','USM')"))
    s.commit()
    g = S3DProjector.from_site(s, "S1")
    assert len(g.edges) == 1
    e = g.edges[0]
    assert e.canonical == "overlies"
    # source = us_1's node_id, target = us_2's node_id
    by_us = {n.us: n.node_id for n in g.nodes}
    assert e.source_id == by_us["1"]
    assert e.target_id == by_us["2"]


def test_edges_dedup_symmetric():
    """has_same_time edges deduplicated on sorted (src, tgt)."""
    # Use plain sqlite, two US with reciprocal "Uguale a"
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(text("""CREATE TABLE site_table (id_sito INTEGER PRIMARY KEY AUTOINCREMENT, sito TEXT UNIQUE)"""))
        conn.execute(text("""CREATE TABLE period_table (id_period INTEGER PRIMARY KEY, sito TEXT, periodo TEXT, fase TEXT, datazione TEXT)"""))
        conn.execute(text("""CREATE TABLE us_table (id_us INTEGER PRIMARY KEY AUTOINCREMENT,
            sito TEXT, area TEXT, us TEXT, unita_tipo TEXT, descrizione TEXT,
            fase_iniziale TEXT, fase_finale TEXT, rapporti TEXT)"""))
        conn.execute(text("INSERT INTO us_table (sito,area,us,unita_tipo,rapporti) "
                          "VALUES ('S','A','1','USM','[[\"Uguale a\",\"2\"]]')"))
        conn.execute(text("INSERT INTO us_table (sito,area,us,unita_tipo,rapporti) "
                          "VALUES ('S','A','2','USM','[[\"Uguale a\",\"1\"]]')"))
    s = sessionmaker(bind=engine)()
    g = S3DProjector.from_site(s, "S")
    # Only one symmetric edge, not two
    assert len(g.edges) == 1
    assert g.edges[0].canonical == "has_same_time"
