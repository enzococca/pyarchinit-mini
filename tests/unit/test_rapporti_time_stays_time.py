"""A temporal relation stays temporal, a physical one stays physical.

`>` / «Posteriore a» are `is_after`, `<` / «Anteriore a» are `is_before`:
they are never turned into `overlies`. «Coperto da» is the reverse of
`overlies`. On writing, `is_after` is `>` (and `<` on the other unit), never
«Coperto da»; `has_same_time` is «Contemporaneo a», never «Uguale a»
(`equals`). Same notation as s3dgraphy >= 1.6.0.dev139 and pyArchInit.
"""
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.graphproj.rapporti_codec import parse_rapporti
from pyarchinit_mini.graphproj.s3d_projector import S3DProjector, ProjectedGraph, Node, Edge
from pyarchinit_mini.graphproj.graph_to_db import write_graph


def _canon(raw):
    return [r.canonical for r in parse_rapporti(raw, current_site="S")]


def test_symbols_are_time():
    assert _canon("[['>', '2'], ['<', '3']]") == ["is_after", "is_before"]


def test_paradata_chain_is_not_a_rapporto():
    assert _canon("[['>>', '2'], ['<<', '3']]") == []


@pytest.mark.parametrize("label,canonical", [
    ("Posteriore a", "is_after"),
    ("Anteriore a", "is_before"),
    ("Later than", "is_after"),
    ("Earlier than", "is_before"),
    ("Contemporaneo a", "has_same_time"),
    ("Uguale a", "equals"),
    ("Same as", "equals"),
    ("Coperto da", "is_overlain_by"),
    ("Covered by", "is_overlain_by"),
])
def test_words(label, canonical):
    assert _canon(f"[['{label}', '2']]") == [canonical]


def _session(rows):
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE site_table (id_sito INTEGER PRIMARY KEY AUTOINCREMENT, sito TEXT UNIQUE)"))
        conn.execute(text("CREATE TABLE period_table (id_period INTEGER PRIMARY KEY, sito TEXT, periodo TEXT, fase TEXT, datazione TEXT)"))
        conn.execute(text("""CREATE TABLE us_table (id_us INTEGER PRIMARY KEY AUTOINCREMENT,
            sito TEXT, area TEXT, us TEXT, unita_tipo TEXT, descrizione TEXT,
            fase_iniziale TEXT, fase_finale TEXT, rapporti TEXT, data_origine TEXT,
            UNIQUE (sito, area, us))"""))
        for us, rapporti in rows:
            conn.execute(text("INSERT INTO us_table (sito, area, us, unita_tipo, rapporti) "
                              "VALUES ('S', 'A', :u, 'US', :r)"), {"u": us, "r": rapporti})
    return sessionmaker(bind=engine)()


def _edges(g):
    by_id = {n.node_id: n.us for n in g.nodes}
    return sorted((e.canonical, by_id[e.source_id], by_id[e.target_id]) for e in g.edges)


@pytest.mark.parametrize("rapporti_1", [
    "[['>', '2']]",
    "[['Posteriore a', '2']]",
])
def test_projector_keeps_later_than_temporal(rapporti_1):
    g = S3DProjector.from_site(_session([("1", rapporti_1), ("2", None)]), "S")
    assert _edges(g) == [("is_after", "1", "2")]


def test_projector_earlier_than_is_turned_round_not_into_overlies():
    g = S3DProjector.from_site(_session([("1", "[['<', '2']]"), ("2", "[['Anteriore a', '3']]"), ("3", None)]), "S")
    assert _edges(g) == [("is_after", "2", "1"), ("is_after", "3", "2")]


def test_projector_reciprocal_pair_is_one_relation():
    g = S3DProjector.from_site(_session([("1", "[['>', '2']]"), ("2", "[['<', '1']]")]), "S")
    assert _edges(g) == [("is_after", "1", "2")]


def test_projector_covered_by_is_physical():
    g = S3DProjector.from_site(_session([("1", "[['Coperto da', '2']]"), ("2", "[['Copre', '1']]")]), "S")
    assert _edges(g) == [("overlies", "2", "1")]


def _two_units(canonical):
    g = ProjectedGraph(site="S", group_by="none")
    g.nodes = [Node(node_id=f"us_{u}", us=u, area="A", sito="S", unit_type="US",
                    description="x", row_id="row_0") for u in ("1", "2")]
    g.edges = [Edge(source_id="us_1", target_id="us_2", canonical=canonical)]
    return g


def _rapporti(session, us):
    raw = session.execute(text("SELECT rapporti FROM us_table WHERE us = :u"), {"u": us}).scalar()
    return eval(raw) if raw else []


def test_writer_is_after_is_a_sign_never_coperto_da():
    s = _session([])
    write_graph(_two_units("is_after"), target_site="S", session=s, source_label="t")
    assert _rapporti(s, "1") == [[">", "2", "A", "S"]]
    assert _rapporti(s, "2") == [["<", "1", "A", "S"]]


def test_writer_has_same_time_is_not_uguale_a():
    s = _session([])
    write_graph(_two_units("has_same_time"), target_site="S", session=s, source_label="t")
    assert _rapporti(s, "1") == [["Contemporaneo a", "2", "A", "S"]]


def test_round_trip_keeps_time_and_space_apart():
    s = _session([])
    write_graph(_two_units("is_after"), target_site="S", session=s, source_label="t")
    assert _edges(S3DProjector.from_site(s, "S")) == [("is_after", "1", "2")]
    s = _session([])
    write_graph(_two_units("overlies"), target_site="S", session=s, source_label="t")
    assert _rapporti(s, "2") == [["Coperto da", "1", "A", "S"]]
    assert _edges(S3DProjector.from_site(s, "S")) == [("overlies", "1", "2")]
