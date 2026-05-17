"""Backfill migration (2026-05-16):
Populates `node_uuid` column with UUID v7 values on us_table,
inventario_materiali_table, periodizzazione_table. Batched at 1000 rows.

Idempotent: only updates rows WHERE node_uuid IS NULL.
"""
import sqlite3
from dataclasses import dataclass, field

from pyarchinit_mini.database.utils import generate_node_uuid


@dataclass
class MigrationReport:
    script: str
    db: str
    rows_updated: dict = field(default_factory=dict)
    dry_run: bool = False
    status: str = "ok"


TABLES = ("us_table", "inventario_materiali_table", "periodizzazione_table")
BATCH = 1000


def _backfill_sqlite(db_path: str, dry_run: bool) -> dict:
    conn = sqlite3.connect(db_path)
    out = {}
    try:
        for t in TABLES:
            # Determine PK column. For test fixtures it's "id"; for real
            # pyarchinit_mini.models.us.US it's "id_us". Inspect the table.
            cols = conn.execute(f"PRAGMA table_info({t})").fetchall()
            pk_col = next((c[1] for c in cols if c[5]), None)
            if pk_col is None:
                out[t] = 0
                continue
            col_names = {c[1] for c in cols}
            if "node_uuid" not in col_names:
                # Column not yet added (e.g. schema migration was dry-run)
                out[t] = 0
                continue
            rows = conn.execute(
                f"SELECT {pk_col} FROM {t} WHERE node_uuid IS NULL"
            ).fetchall()
            count = len(rows)
            if count == 0 or dry_run:
                out[t] = count
                continue
            for offset in range(0, count, BATCH):
                batch = rows[offset:offset + BATCH]
                for (row_id,) in batch:
                    conn.execute(
                        f"UPDATE {t} SET node_uuid=? WHERE {pk_col}=?",
                        (generate_node_uuid(), row_id)
                    )
                conn.commit()
            out[t] = count
    finally:
        conn.close()
    return out


def _backfill_postgresql(url: str, dry_run: bool) -> dict:
    from sqlalchemy import create_engine, text, inspect
    eng = create_engine(url)
    out = {}
    inspector = inspect(eng)
    with eng.begin() as c:
        for t in TABLES:
            if t not in inspector.get_table_names():
                out[t] = 0
                continue
            pk_cols = inspector.get_pk_constraint(t).get("constrained_columns", [])
            if not pk_cols:
                out[t] = 0
                continue
            pk_col = pk_cols[0]
            rows = c.execute(text(f"SELECT {pk_col} FROM {t} WHERE node_uuid IS NULL")).fetchall()
            count = len(rows)
            if not dry_run and count > 0:
                for (row_id,) in rows:
                    c.execute(
                        text(f"UPDATE {t} SET node_uuid=:u WHERE {pk_col}=:i"),
                        {"u": generate_node_uuid(), "i": row_id}
                    )
            out[t] = count
    return out


def run(connection_url: str, *, dry_run: bool = False) -> MigrationReport:
    report = MigrationReport(
        script="2026_05_node_uuid_backfill",
        db=connection_url,
        dry_run=dry_run,
    )
    if connection_url.startswith("sqlite"):
        path = connection_url.replace("sqlite:///", "", 1)
        report.rows_updated = _backfill_sqlite(path, dry_run)
    elif connection_url.startswith("postgresql") or connection_url.startswith("postgres"):
        report.rows_updated = _backfill_postgresql(connection_url, dry_run)
    else:
        report.status = "unsupported_backend"
    return report
