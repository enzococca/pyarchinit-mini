"""Schema migration (2026-05-18):
Add the pyarchinit-compatible columns to ``period_table``.

The SQLAlchemy ``Period`` model historically declared (``period_name``,
``phase_name``, ``start_date``, ``end_date``, ``description``, ``chronology``).
The real pyarchinit schema (used by QGIS plugin and PG ``pyarchinit_v2``)
is (``periodo``, ``fase``, ``datazione``, ``descrizione``, ``sito``). Spec
3-bis queries the latter, so existing SQLite/PostgreSQL DBs created via
``Base.metadata.create_all()`` need the new columns aliased over.

Idempotent: re-running on a DB that already has the new columns is a
no-op. Backfills ``periodo`` from ``period_name`` / ``fase`` from
``phase_name`` when both exist.

Supports SQLite and PostgreSQL backends.
"""
import sqlite3
from dataclasses import dataclass, field
from urllib.parse import urlparse


@dataclass
class MigrationReport:
    script: str
    db: str
    tables_changed: list = field(default_factory=list)
    tables_skipped: list = field(default_factory=list)
    dry_run: bool = False
    status: str = "ok"


TABLE = "period_table"
NEW_COLUMNS = [
    ("periodo", "TEXT"),
    ("fase", "TEXT"),
    ("datazione", "TEXT"),
    ("descrizione", "TEXT"),
    ("sito", "TEXT"),
]


def _table_exists_sqlite(conn, table):
    return conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
    ).fetchone() is not None


def _has_column_sqlite(conn, table, col):
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(r[1] == col for r in rows)


def _run_sqlite(path: str, dry_run: bool, report: MigrationReport) -> None:
    conn = sqlite3.connect(path)
    try:
        if not _table_exists_sqlite(conn, TABLE):
            report.tables_skipped.append(f"{TABLE} (missing)")
            return
        existing = {r[1] for r in conn.execute(f"PRAGMA table_info({TABLE})").fetchall()}
        added = []
        for col, ctype in NEW_COLUMNS:
            if col in existing:
                continue
            if not dry_run:
                conn.execute(f"ALTER TABLE {TABLE} ADD COLUMN {col} {ctype}")
            added.append(col)
        # Backfill: periodo ← period_name, fase ← phase_name (only if legacy cols exist)
        if not dry_run and added:
            if "period_name" in existing and "periodo" in added:
                conn.execute(
                    f"UPDATE {TABLE} SET periodo = period_name WHERE periodo IS NULL"
                )
            if "phase_name" in existing and "fase" in added:
                conn.execute(
                    f"UPDATE {TABLE} SET fase = phase_name WHERE fase IS NULL"
                )
            conn.commit()
        if added:
            report.tables_changed.append(f"{TABLE} (+{','.join(added)})")
        else:
            report.tables_skipped.append(f"{TABLE} (already aligned)")
    finally:
        conn.close()


def _run_postgresql(url: str, dry_run: bool, report: MigrationReport) -> None:
    import psycopg2
    p = urlparse(url)
    conn = psycopg2.connect(
        host=p.hostname, port=p.port or 5432,
        user=p.username, password=p.password,
        dbname=p.path.lstrip("/"),
    )
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT to_regclass(%s)", (f"public.{TABLE}",)
        )
        if cur.fetchone()[0] is None:
            report.tables_skipped.append(f"{TABLE} (missing)")
            return
        cur.execute(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_schema='public' AND table_name=%s", (TABLE,)
        )
        existing = {r[0] for r in cur.fetchall()}
        added = []
        for col, ctype in NEW_COLUMNS:
            if col in existing:
                continue
            if not dry_run:
                cur.execute(f"ALTER TABLE {TABLE} ADD COLUMN {col} {ctype}")
            added.append(col)
        if not dry_run and added:
            if "period_name" in existing and "periodo" in added:
                cur.execute(
                    f"UPDATE {TABLE} SET periodo = period_name WHERE periodo IS NULL"
                )
            if "phase_name" in existing and "fase" in added:
                cur.execute(
                    f"UPDATE {TABLE} SET fase = phase_name WHERE fase IS NULL"
                )
            conn.commit()
        if added:
            report.tables_changed.append(f"{TABLE} (+{','.join(added)})")
        else:
            report.tables_skipped.append(f"{TABLE} (already aligned)")
    finally:
        conn.close()


def run(url: str, dry_run: bool = False) -> MigrationReport:
    report = MigrationReport(
        script=__name__, db=url, dry_run=dry_run,
    )
    try:
        if url.startswith("sqlite"):
            path = url.replace("sqlite:///", "", 1)
            _run_sqlite(path, dry_run, report)
        elif url.startswith("postgresql") or url.startswith("postgres"):
            _run_postgresql(url, dry_run, report)
        else:
            report.status = "unsupported"
    except Exception as e:
        report.status = f"error: {e}"
    return report
