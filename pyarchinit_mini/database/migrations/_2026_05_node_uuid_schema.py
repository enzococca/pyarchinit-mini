"""Schema migration (2026-05-16):
Add `node_uuid TEXT` column + UNIQUE INDEX on us_table, inventario_materiali_table,
periodizzazione_table.

Idempotent: re-running on a DB that already has the column is a no-op.
Supports SQLite and PostgreSQL backends.
"""
import sqlite3
from dataclasses import dataclass, field


@dataclass
class MigrationReport:
    script: str
    db: str
    tables_changed: list = field(default_factory=list)
    tables_skipped: list = field(default_factory=list)
    dry_run: bool = False
    status: str = "ok"


TABLES = ("us_table", "inventario_materiali_table", "periodizzazione_table")


def _table_exists_sqlite(conn, table):
    r = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
    ).fetchone()
    return r is not None


def _has_column_sqlite(conn, table, col):
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(r[1] == col for r in rows)


def _run_sqlite(path: str, dry_run: bool, report: MigrationReport) -> None:
    conn = sqlite3.connect(path)
    try:
        for t in TABLES:
            if not _table_exists_sqlite(conn, t):
                report.tables_skipped.append(f"{t} (missing)")
                continue
            if _has_column_sqlite(conn, t, "node_uuid"):
                report.tables_skipped.append(f"{t} (already has node_uuid)")
                continue
            if not dry_run:
                conn.execute(f"ALTER TABLE {t} ADD COLUMN node_uuid TEXT")
                conn.execute(
                    f"CREATE UNIQUE INDEX IF NOT EXISTS ix_{t}_node_uuid "
                    f"ON {t}(node_uuid)"
                )
            report.tables_changed.append(t)
        if not dry_run:
            conn.commit()
    finally:
        conn.close()


def _run_postgresql(url: str, dry_run: bool, report: MigrationReport) -> None:
    from sqlalchemy import create_engine, text
    eng = create_engine(url)
    with eng.begin() as c:
        for t in TABLES:
            exists = c.execute(
                text("SELECT 1 FROM information_schema.tables WHERE table_name=:t"),
                {"t": t}
            ).first()
            if not exists:
                report.tables_skipped.append(f"{t} (missing)")
                continue
            col = c.execute(
                text(
                    "SELECT 1 FROM information_schema.columns "
                    "WHERE table_name=:t AND column_name='node_uuid'"
                ),
                {"t": t}
            ).first()
            if col:
                report.tables_skipped.append(f"{t} (already has node_uuid)")
                continue
            if not dry_run:
                c.execute(text(f"ALTER TABLE {t} ADD COLUMN node_uuid TEXT"))
                c.execute(
                    text(f"CREATE UNIQUE INDEX IF NOT EXISTS ix_{t}_node_uuid "
                         f"ON {t}(node_uuid)")
                )
            report.tables_changed.append(t)


def run(connection_url: str, *, dry_run: bool = False) -> MigrationReport:
    report = MigrationReport(
        script="2026_05_node_uuid_schema",
        db=connection_url,
        dry_run=dry_run,
    )
    if connection_url.startswith("sqlite"):
        path = connection_url.replace("sqlite:///", "", 1)
        _run_sqlite(path, dry_run, report)
    elif connection_url.startswith("postgresql") or connection_url.startswith("postgres"):
        _run_postgresql(connection_url, dry_run, report)
    else:
        report.status = "unsupported_backend"
    return report
