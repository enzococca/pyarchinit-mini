import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.graphproj.s3d_projector import ProjectedGraph, Row, Node, Edge
from pyarchinit_mini.graphproj.graph_to_db import write_graph


@pytest.fixture
def session(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path}/g.db")
    with engine.begin() as conn:
        conn.execute(text("""CREATE TABLE site_table (
            id_sito INTEGER PRIMARY KEY AUTOINCREMENT, sito TEXT UNIQUE)"""))
        conn.execute(text("""CREATE TABLE us_table (
            id_us INTEGER PRIMARY KEY AUTOINCREMENT,
            sito TEXT, area TEXT, us TEXT, unita_tipo TEXT,
            descrizione TEXT, fase_iniziale TEXT, fase_finale TEXT,
            rapporti TEXT, data_origine TEXT,
            UNIQUE (sito, area, us))"""))
    return sessionmaker(bind=engine)()


def _graph_2_us_1_edge():
    g = ProjectedGraph(site="S", group_by="none")
    g.nodes = [
        Node(node_id="us_1", us="1", area="A", sito="S", unit_type="USM",
             description="x", row_id="row_0"),
        Node(node_id="us_2", us="2", area="A", sito="S", unit_type="USV",
             description="y", row_id="row_0"),
    ]
    g.edges = [Edge(source_id="us_1", target_id="us_2", canonical="overlies")]
    return g


def test_write_graph_inserts_us_rows(session):
    res = write_graph(_graph_2_us_1_edge(), target_site="S", session=session, source_label="test")
    assert res.imported_us == 2
    rows = session.execute(text("SELECT us, area, unita_tipo FROM us_table ORDER BY us")).fetchall()
    assert rows == [("1", "A", "USM"), ("2", "A", "USV")]


def test_write_graph_writes_rapporti_4tuple_both_sides(session):
    write_graph(_graph_2_us_1_edge(), target_site="S", session=session, source_label="test")
    r1 = session.execute(text("SELECT rapporti FROM us_table WHERE us='1'")).scalar()
    r2 = session.execute(text("SELECT rapporti FROM us_table WHERE us='2'")).scalar()
    items1 = eval(r1)
    items2 = eval(r2)
    assert items1 == [["Copre", "2", "A", "S"]]
    assert items2 == [["Coperto da", "1", "A", "S"]]


def test_write_graph_upsert_does_not_duplicate(session):
    write_graph(_graph_2_us_1_edge(), target_site="S", session=session, source_label="test")
    write_graph(_graph_2_us_1_edge(), target_site="S", session=session, source_label="test")
    count = session.execute(text("SELECT COUNT(*) FROM us_table")).scalar()
    assert count == 2
    r1 = session.execute(text("SELECT rapporti FROM us_table WHERE us='1'")).scalar()
    items1 = eval(r1)
    # Dedup: still 1 entry, not 2
    assert len(items1) == 1


def test_write_graph_symmetric_edge_no_inverse(session):
    g = ProjectedGraph(site="S", group_by="none")
    g.nodes = [
        Node(node_id="us_1", us="1", area="A", sito="S", unit_type="USM",
             description="x", row_id="row_0"),
        Node(node_id="us_2", us="2", area="A", sito="S", unit_type="USM",
             description="y", row_id="row_0"),
    ]
    g.edges = [Edge(source_id="us_1", target_id="us_2", canonical="has_same_time")]
    res = write_graph(g, target_site="S", session=session, source_label="test")
    assert res.imported_edges == 1
    assert res.inverses_written == 0  # symmetric → no inverse
    r1 = session.execute(text("SELECT rapporti FROM us_table WHERE us='1'")).scalar()
    r2 = session.execute(text("SELECT rapporti FROM us_table WHERE us='2'")).scalar()
    items1 = eval(r1) if r1 else []
    items2 = eval(r2) if r2 else []
    # forward written on 1; nothing on 2
    assert len(items1) == 1
    assert items1[0][0] == "Uguale a"
    assert items2 == []


def test_write_graph_stub_counted(session):
    g = ProjectedGraph(site="S", group_by="none")
    g.nodes = [
        Node(node_id="us_99", us="99", area="A", sito="S", unit_type="US",
             description="Imported placeholder", row_id="row_0"),
    ]
    g.edges = []
    res = write_graph(g, target_site="S", session=session, source_label="test")
    assert res.imported_us == 1
    assert res.stubs_created == 1


def test_write_graph_unknown_inverse_skipped(session):
    """An edge with an unmapped inverse logs to inverses_skipped, writes forward only."""
    g = ProjectedGraph(site="S", group_by="none")
    g.nodes = [
        Node(node_id="us_1", us="1", area="A", sito="S", unit_type="USM",
             description="x", row_id="row_0"),
        Node(node_id="us_2", us="2", area="A", sito="S", unit_type="USM",
             description="y", row_id="row_0"),
    ]
    g.edges = [Edge(source_id="us_1", target_id="us_2", canonical="partially_covers")]
    res = write_graph(g, target_site="S", session=session, source_label="test")
    assert res.imported_edges == 1
    assert res.inverses_written == 0
    assert "partially_covers" in res.inverses_skipped


def test_write_graph_writes_data_origine(session):
    write_graph(_graph_2_us_1_edge(), target_site="S", session=session, source_label="graphml")
    origin = session.execute(text("SELECT data_origine FROM us_table WHERE us='1'")).scalar()
    assert origin and origin.startswith("graphml_")
