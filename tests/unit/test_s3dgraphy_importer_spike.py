"""Canary for the s3dgraphy importer API this project builds on (issue #2).

If this file goes red after a s3dgraphy upgrade, the library changed under us;
fix graphproj/* before touching anything else.
"""
import sqlite3

import pytest
from s3dgraphy.importer.pyarchinit_importer import PyArchInitImporter
from s3dgraphy.nodes.stratigraphic_node import StratigraphicNode


@pytest.fixture
def mini_db(tmp_path):
    path = tmp_path / "mini.sqlite"
    c = sqlite3.connect(path)
    c.executescript("""
    CREATE TABLE us_table (id_us INTEGER PRIMARY KEY, sito TEXT, area TEXT, settore TEXT,
      us TEXT, unita_tipo TEXT, d_stratigrafica TEXT, descrizione TEXT, rapporti TEXT,
      node_uuid TEXT, periodo_iniziale TEXT, fase_iniziale TEXT, quota_abs REAL, schedatore TEXT);
    CREATE TABLE periodizzazione_table (id_periodizzazione INTEGER PRIMARY KEY, sito TEXT,
      periodo_iniziale TEXT, fase_iniziale TEXT, datazione_estesa TEXT);
    INSERT INTO us_table VALUES (1,'S','A','Nord','1','US','strato','d1',
      "[['Copre', '2', 'A', 'S']]",'0192aaaa-0000-7000-8000-000000000001','I','a',12.5,'Mario');
    INSERT INTO us_table VALUES (2,'S','A','Nord','2','USM','muro','d2',NULL,NULL,'I','a',NULL,'Mario');
    INSERT INTO us_table VALUES (3,'OTHER','A','','9','US','altro',NULL,NULL,NULL,NULL,NULL,NULL,NULL);
    """)
    c.commit(); c.close()
    return path


def test_importer_reads_only_the_filtered_site_and_keys_nodes_by_uuid(mini_db):
    imp = PyArchInitImporter(connection_url=f"sqlite:///{mini_db}",
                             mapping_name="pyarchinit_us_mapping", filters={"sito": "S"})
    graph = imp.parse()
    strat = [n for n in graph.nodes if isinstance(n, StratigraphicNode)]
    assert sorted(n.name for n in strat) == ["A.Nord.US1", "A.Nord.USM2"]
    by_name = {n.name: n for n in strat}
    assert by_name["A.Nord.US1"].node_id == "0192aaaa-0000-7000-8000-000000000001"
    assert by_name["A.Nord.USM2"].node_id != ""          # minted uuid4 for the NULL row
    assert isinstance(graph.attributes, dict)             # we store swimlane rows here


def test_importer_does_not_create_stratigraphic_edges(mini_db):
    imp = PyArchInitImporter(connection_url=f"sqlite:///{mini_db}",
                             mapping_name="pyarchinit_us_mapping", filters={"sito": "S"})
    graph = imp.parse()
    strat_ids = {n.node_id for n in graph.nodes if isinstance(n, StratigraphicNode)}
    assert not [e for e in graph.edges if e.edge_source in strat_ids and e.edge_target in strat_ids]


def test_importer_degrades_when_periodizzazione_has_mini_columns(mini_db):
    imp = PyArchInitImporter(connection_url=f"sqlite:///{mini_db}",
                             mapping_name="pyarchinit_us_mapping", filters={"sito": "S"})
    imp.parse()
    assert any("periodization table" in w for w in imp.warnings)


def test_name_resolution_helper_collapses_empty_parts(mini_db):
    imp = PyArchInitImporter(connection_url=f"sqlite:///{mini_db}",
                             mapping_name="pyarchinit_us_mapping", filters={"sito": "S"})
    assert imp._resolve_node_name({"area": "A", "settore": "", "unita_tipo": "US", "us": "7"}, "us") == "A.US7"
    assert imp._resolve_node_name({"area": None, "settore": None, "unita_tipo": "USVs", "us": "3"}, "us") == "USVs3"
