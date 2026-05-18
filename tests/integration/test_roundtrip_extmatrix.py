"""End-to-end round-trip: DB → export → re-import → DB unchanged."""
from pathlib import Path
import sqlite3
import pytest

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.harris_swimlane.swimlane_state import SwimlaneState
from pyarchinit_mini.graphml_io.yed_writer import write_extended_matrix_graphml
from pyarchinit_mini.graphml_io.yed_importer import (
    parse_extended_matrix, build_import_plan, apply_import_plan,
)

FIX_DB = Path(__file__).parent.parent / "fixtures" / "databases" / "sqlite_volterra_30us_with_periods.db"


def _ensure_tables(session):
    """The synthetic Volterra fixture doesn't ship us_relationships_table or
    site_table; both are required by apply_import_plan + the snapshot query.
    """
    session.execute(text("""
        CREATE TABLE IF NOT EXISTS us_relationships_table (
          id_relationship INTEGER PRIMARY KEY,
          sito TEXT, us_from TEXT, us_to TEXT, relationship_type TEXT
        )
    """))
    session.execute(text("""
        CREATE TABLE IF NOT EXISTS site_table (
          id_sito INTEGER PRIMARY KEY, sito TEXT
        )
    """))
    session.commit()


def _snapshot(session):
    return {
        "us": session.execute(text(
            "SELECT us, unita_tipo, periodo_iniziale, fase_iniziale, node_uuid "
            "FROM us_table WHERE sito='Volterra' ORDER BY us"
        )).fetchall(),
        "rels": session.execute(text(
            "SELECT us_from, us_to, relationship_type "
            "FROM us_relationships_table WHERE sito='Volterra' ORDER BY us_from, us_to"
        )).fetchall(),
    }


def test_roundtrip_export_then_reimport_idempotent(tmp_path):
    # 1. Open source DB, ensure tables, snapshot
    eng_src = create_engine(f"sqlite:///{FIX_DB}")
    s_src = sessionmaker(bind=eng_src)()
    _ensure_tables(s_src)
    before = _snapshot(s_src)

    # 2. Export
    state = SwimlaneState.load(s_src, "Volterra")
    out = tmp_path / "roundtrip.graphml"
    write_extended_matrix_graphml(state, site_meta={"sito": "Volterra"}, epochs=[], out=out)
    s_src.close()

    # 3. Copy source DB to target (so we test idempotency of re-importing into
    # an already-populated DB rather than into an empty one).
    import shutil
    target = tmp_path / "target.db"
    shutil.copyfile(FIX_DB, target)
    eng_dst = create_engine(f"sqlite:///{target}")
    s_dst = sessionmaker(bind=eng_dst)()
    _ensure_tables(s_dst)

    # 4. Re-import
    parsed = parse_extended_matrix(out)
    plan = build_import_plan(parsed, s_dst)
    apply_import_plan(plan, s_dst)

    # 5. Snapshot after
    after = _snapshot(s_dst)
    s_dst.close()

    # All US present (counts equal)
    assert {r[0] for r in before["us"]} == {r[0] for r in after["us"]}
