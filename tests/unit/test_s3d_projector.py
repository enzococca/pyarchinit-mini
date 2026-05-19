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


# ---------------------------------------------------------------------------
# Task 6 — sub-grouping tests
# ---------------------------------------------------------------------------

@pytest.fixture
def session_factory_full(tmp_path):
    """us_table schema with sub-grouping columns."""
    engine = create_engine(f"sqlite:///{tmp_path}/full.db")
    with engine.begin() as conn:
        conn.execute(text("""CREATE TABLE site_table (id_sito INTEGER PRIMARY KEY, sito TEXT)"""))
        conn.execute(text("""CREATE TABLE period_table (
            id_period INTEGER PRIMARY KEY,
            sito TEXT, periodo TEXT, fase TEXT, datazione TEXT)"""))
        conn.execute(text("""CREATE TABLE us_table (
            id_us INTEGER PRIMARY KEY AUTOINCREMENT,
            sito TEXT, area TEXT, us TEXT, unita_tipo TEXT,
            descrizione TEXT, fase_iniziale TEXT,
            settore TEXT, quadrato TEXT, attivita TEXT, struttura TEXT,
            rapporti TEXT)"""))
    return sessionmaker(bind=engine)


def test_sub_group_by_area(session_factory_full):
    s = session_factory_full()
    s.execute(text("INSERT INTO us_table (sito, area, us, unita_tipo) VALUES ('S','A1','1','USM')"))
    s.execute(text("INSERT INTO us_table (sito, area, us, unita_tipo) VALUES ('S','A2','2','USM')"))
    s.commit()
    g = S3DProjector.from_site(s, "S", group_by="area")
    by_us = {n.us: n for n in g.nodes}
    assert by_us["1"].sub_group == "A1"
    assert by_us["2"].sub_group == "A2"


def test_sub_group_by_settore(session_factory_full):
    s = session_factory_full()
    s.execute(text("INSERT INTO us_table (sito, area, us, unita_tipo, settore) "
                   "VALUES ('S','A','1','USM','Nord')"))
    s.commit()
    g = S3DProjector.from_site(s, "S", group_by="settore")
    assert g.nodes[0].sub_group == "Nord"


def test_sub_group_by_strutture_uses_struttura_column(session_factory_full):
    s = session_factory_full()
    s.execute(text("INSERT INTO us_table (sito, area, us, unita_tipo, struttura) "
                   "VALUES ('S','A','1','USM','Edificio_A')"))
    s.commit()
    g = S3DProjector.from_site(s, "S", group_by="strutture")
    assert g.nodes[0].sub_group == "Edificio_A"


def test_sub_group_none_returns_none(session_factory_full):
    s = session_factory_full()
    s.execute(text("INSERT INTO us_table (sito, area, us, unita_tipo, settore) "
                   "VALUES ('S','A','1','USM','Nord')"))
    s.commit()
    g = S3DProjector.from_site(s, "S", group_by="none")
    assert g.nodes[0].sub_group is None


def test_sub_group_graceful_when_column_missing(tmp_path):
    """If us_table lacks the requested sub-grouping column, fall back to None."""
    engine = create_engine(f"sqlite:///{tmp_path}/legacy.db")
    with engine.begin() as conn:
        # NO settore/quadrato/attivita/struttura columns
        conn.execute(text("""CREATE TABLE site_table (id_sito INTEGER PRIMARY KEY, sito TEXT)"""))
        conn.execute(text("""CREATE TABLE period_table (id_period INTEGER PRIMARY KEY,
            sito TEXT, periodo TEXT, fase TEXT, datazione TEXT)"""))
        conn.execute(text("""CREATE TABLE us_table (
            id_us INTEGER PRIMARY KEY AUTOINCREMENT, sito TEXT, area TEXT, us TEXT,
            unita_tipo TEXT, descrizione TEXT, fase_iniziale TEXT, rapporti TEXT)"""))
        conn.execute(text("INSERT INTO us_table (sito,area,us,unita_tipo) VALUES ('S','A','1','USM')"))
    s = sessionmaker(bind=engine)()
    g = S3DProjector.from_site(s, "S", group_by="settore")
    # No crash; sub_group falls back to None
    assert g.nodes[0].sub_group is None


# ---------------------------------------------------------------------------
# Fix A — inverse-to-forward direction normalization
# ---------------------------------------------------------------------------

def _make_inverse_session(tmp_path, rapporti_str):
    """Helper: two-US DB where US 1 carries the given rapporti string."""
    engine = create_engine(f"sqlite:///{tmp_path}/inv.db")
    with engine.begin() as conn:
        conn.execute(text("""CREATE TABLE site_table (id_sito INTEGER PRIMARY KEY, sito TEXT)"""))
        conn.execute(text("""CREATE TABLE period_table (
            id_period INTEGER PRIMARY KEY, sito TEXT, periodo TEXT, fase TEXT, datazione TEXT)"""))
        conn.execute(text("""CREATE TABLE us_table (
            id_us INTEGER PRIMARY KEY AUTOINCREMENT,
            sito TEXT, area TEXT, us TEXT, unita_tipo TEXT,
            descrizione TEXT, fase_iniziale TEXT, fase_finale TEXT, rapporti TEXT)"""))
        conn.execute(text(
            "INSERT INTO us_table (sito, area, us, unita_tipo, rapporti) "
            f"VALUES ('S','A','1','USM','{rapporti_str}')"
        ))
        conn.execute(text(
            "INSERT INTO us_table (sito, area, us, unita_tipo) VALUES ('S','A','2','USM')"
        ))
    return sessionmaker(bind=engine)()


def test_normalize_inverse_coperto_da(tmp_path):
    """'Coperto da' (is_after) on US 1 → emits Edge(2→1, 'overlies') not Edge(1→2, 'is_after')."""
    s = _make_inverse_session(tmp_path, '[[\"Coperto da\", \"2\"]]')
    g = S3DProjector.from_site(s, "S")
    assert len(g.edges) == 1
    e = g.edges[0]
    by_us = {n.us: n.node_id for n in g.nodes}
    assert e.canonical == "overlies", f"Expected 'overlies', got {e.canonical!r}"
    assert e.source_id == by_us["2"], "source should be US 2 (the overlying one)"
    assert e.target_id == by_us["1"], "target should be US 1 (the covered one)"


def test_normalize_inverse_tagliato_da(tmp_path):
    """'Tagliato da' (is_cut_by) on US 1 → emits Edge(2→1, 'cuts')."""
    s = _make_inverse_session(tmp_path, '[[\"Tagliato da\", \"2\"]]')
    g = S3DProjector.from_site(s, "S")
    assert len(g.edges) == 1
    e = g.edges[0]
    by_us = {n.us: n.node_id for n in g.nodes}
    assert e.canonical == "cuts"
    assert e.source_id == by_us["2"]
    assert e.target_id == by_us["1"]


def test_normalize_inverse_riempito_da(tmp_path):
    """'Riempito da' (is_filled_by) on US 1 → emits Edge(2→1, 'fills')."""
    s = _make_inverse_session(tmp_path, '[[\"Riempito da\", \"2\"]]')
    g = S3DProjector.from_site(s, "S")
    assert len(g.edges) == 1
    e = g.edges[0]
    by_us = {n.us: n.node_id for n in g.nodes}
    assert e.canonical == "fills"
    assert e.source_id == by_us["2"]
    assert e.target_id == by_us["1"]


def test_no_inverse_canonicals_in_graph(tmp_path):
    """After normalization, no inverse canonical names appear in graph.edges."""
    from pyarchinit_mini.graphproj.rapporti_codec import REVERSE_TO_FORWARD
    # Give both US a mix of inverse rapporti
    engine = create_engine(f"sqlite:///{tmp_path}/mix.db")
    with engine.begin() as conn:
        conn.execute(text("""CREATE TABLE site_table (id_sito INTEGER PRIMARY KEY, sito TEXT)"""))
        conn.execute(text("""CREATE TABLE period_table (
            id_period INTEGER PRIMARY KEY, sito TEXT, periodo TEXT, fase TEXT, datazione TEXT)"""))
        conn.execute(text("""CREATE TABLE us_table (
            id_us INTEGER PRIMARY KEY AUTOINCREMENT,
            sito TEXT, area TEXT, us TEXT, unita_tipo TEXT,
            descrizione TEXT, fase_iniziale TEXT, fase_finale TEXT, rapporti TEXT)"""))
        conn.execute(text(
            "INSERT INTO us_table (sito, area, us, unita_tipo, rapporti) "
            "VALUES ('S','A','1','USM','[[\"Coperto da\",\"2\"],[\"Tagliato da\",\"3\"]]')"
        ))
        conn.execute(text(
            "INSERT INTO us_table (sito, area, us, unita_tipo) VALUES ('S','A','2','USM')"
        ))
        conn.execute(text(
            "INSERT INTO us_table (sito, area, us, unita_tipo) VALUES ('S','A','3','USM')"
        ))
    s = sessionmaker(bind=engine)()
    g = S3DProjector.from_site(s, "S")
    inverse_found = [e.canonical for e in g.edges if e.canonical in REVERSE_TO_FORWARD]
    assert inverse_found == [], f"Inverse canonicals still present: {inverse_found}"
