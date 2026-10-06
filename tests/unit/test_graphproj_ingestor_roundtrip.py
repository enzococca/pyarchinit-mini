"""Export -> import round trip through s3dgraphy GraphML must be a no-op plan:
existing US are recognised by their exported node id (EMid does not survive
the round trip) and non-stratigraphic nodes are not proposed as US."""
from sqlalchemy import text

from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.graphml_io.reader import read_graphml
from pyarchinit_mini.graphml_io.writer import write_graphml
from pyarchinit_mini.graphproj.ingestor import GraphIngestor
from pyarchinit_mini.graphproj.projector import GraphProjector

UUIDS = {n: "0192bbbb-0000-7000-8000-%012d" % n for n in (11, 12, 13)}


def test_export_import_roundtrip_proposes_only_updates(tmp_path):
    conn = DatabaseConnection.sqlite(str(tmp_path / "rt.db")); conn.create_tables()
    with conn.get_session() as s:
        s.execute(text("INSERT INTO site_table (sito, created_at, updated_at, version_number) "
                       "VALUES ('S', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1)"))
        for us, uuid in UUIDS.items():
            s.execute(text("INSERT INTO us_table (sito, area, us, unita_tipo, node_uuid, created_at, updated_at, "
                           "version_number) VALUES ('S','A',:us,'US',:uuid,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP,1)"),
                      {"us": str(us), "uuid": uuid})
        s.commit()
        graph = GraphProjector.populate_graph(s, "S")
        out = tmp_path / "g.graphml"
        write_graphml(graph, out)
        plan = GraphIngestor(s, "S").preview(read_graphml(out))

    assert plan.inserts == ()
    assert len(plan.updates) == 3
    assert {e.node_uuid for e in plan.updates} == set(UUIDS.values())
    assert all(int(e.after["us"]) in UUIDS for e in plan.updates + plan.inserts)
