"""Vocab alignment migration (2026-05-16):
Remaps legacy stratigraphic unit types in us_table.unita_tipo to the new
EM 1.5.4 vocabulary:
    USVA, USVB → USVs
    USVC       → USVn

Idempotent: subsequent runs find zero rows to update.
"""
import sqlite3
from dataclasses import dataclass, field


@dataclass
class MigrationReport:
    script: str
    db: str
    mappings: dict = field(default_factory=dict)
    dry_run: bool = False
    status: str = "ok"


REMAP = {"USVA": "USVs", "USVB": "USVs", "USVC": "USVn"}


def _run_sqlite(path: str, dry_run: bool, report: MigrationReport) -> None:
    conn = sqlite3.connect(path)
    try:
        for old, new in REMAP.items():
            count = conn.execute(
                "SELECT COUNT(*) FROM us_table WHERE unita_tipo=?", (old,)
            ).fetchone()[0]
            report.mappings[f"{old}→{new}"] = count
            if not dry_run and count > 0:
                conn.execute(
                    "UPDATE us_table SET unita_tipo=? WHERE unita_tipo=?", (new, old)
                )
        if not dry_run:
            conn.commit()
    finally:
        conn.close()


def _run_postgresql(url: str, dry_run: bool, report: MigrationReport) -> None:
    from sqlalchemy import create_engine, text
    eng = create_engine(url)
    with eng.begin() as c:
        for old, new in REMAP.items():
            count = c.execute(
                text("SELECT COUNT(*) FROM us_table WHERE unita_tipo=:o"),
                {"o": old}
            ).scalar()
            report.mappings[f"{old}→{new}"] = count
            if not dry_run and count > 0:
                c.execute(
                    text("UPDATE us_table SET unita_tipo=:n WHERE unita_tipo=:o"),
                    {"n": new, "o": old}
                )


def run(connection_url: str, *, dry_run: bool = False) -> MigrationReport:
    report = MigrationReport(
        script="2026_05_vocab_alignment",
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
