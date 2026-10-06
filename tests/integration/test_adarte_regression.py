"""Regression test on anonymized Adarte fixture.

Verifies the new s3dgraphy pipeline (GraphProjector + rapporti_codec bilingual
matching) produces edges on real Italian production data.

Fixture: tests/fixtures/adarte_regression_dump.sql (100 US from Rimini_RN_2020_21,
renamed to RegressionFixture_v1, with the full Italian rapporti vocabulary).
"""
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.graphproj.projector import GraphProjector
from pyarchinit_mini.graphproj.strat_graph import get_swimlane, stratigraphic_edges, stratigraphic_nodes


FIXTURE_SQL = Path(__file__).parent.parent / "fixtures" / "adarte_regression_dump.sql"


@pytest.fixture
def session(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path}/reg.db")
    sql = FIXTURE_SQL.read_text(encoding="utf-8")
    raw = engine.raw_connection()
    raw.executescript(sql)
    raw.commit()
    raw.close()
    return sessionmaker(bind=engine)()


def test_regression_edge_count_meets_baseline(session):
    g = GraphProjector.populate_graph(session, "RegressionFixture_v1", group_by="none")
    # 100 US with dense rapporti → expect at least 50 edges
    assert len(stratigraphic_edges(g)) >= 50, f"Got {len(stratigraphic_edges(g))} edges, expected ≥50"


def test_regression_edge_labels_diverse(session):
    g = GraphProjector.populate_graph(session, "RegressionFixture_v1", group_by="none")
    labels = {e.edge_type for e in stratigraphic_edges(g)}
    # The Italian rapporti vocabulary (Copre/Coperto da/Taglia/Tagliato da/Riempie/...)
    # canonicalizes to ≥4 distinct edge types
    assert len(labels) >= 4, f"Got labels: {labels}"


def test_regression_periods_loaded(session):
    g = GraphProjector.populate_graph(session, "RegressionFixture_v1", group_by="none")
    assert len(get_swimlane(g)["rows"]) >= 1


def test_regression_nodes_loaded(session):
    g = GraphProjector.populate_graph(session, "RegressionFixture_v1", group_by="none")
    assert len(stratigraphic_nodes(g)) >= 30, f"Got {len(stratigraphic_nodes(g))} nodes, expected ≥30"


def test_regression_no_orphan_us_in_edges(session):
    g = GraphProjector.populate_graph(session, "RegressionFixture_v1", group_by="none")
    node_ids = {n.node_id for n in stratigraphic_nodes(g)}
    for e in stratigraphic_edges(g):
        assert e.edge_source in node_ids, f"Edge source {e.edge_source} missing"
        assert e.edge_target in node_ids, f"Edge target {e.edge_target} missing"
