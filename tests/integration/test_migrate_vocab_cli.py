import sqlite3
import subprocess
import sys
from pathlib import Path
import pytest


@pytest.fixture
def legacy_db(tmp_path):
    """A small DB with: legacy vocab values + tables needing node_uuid backfill."""
    db = tmp_path / "test.db"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE us_table (id_us INTEGER PRIMARY KEY, unita_tipo TEXT)")
    conn.execute("CREATE TABLE inventario_materiali_table (id INTEGER PRIMARY KEY)")
    conn.execute("CREATE TABLE periodizzazione_table (id INTEGER PRIMARY KEY)")
    conn.execute("INSERT INTO us_table VALUES (1, 'USVA')")
    conn.execute("INSERT INTO us_table VALUES (2, 'US')")
    conn.execute("INSERT INTO inventario_materiali_table(id) VALUES (1)")
    conn.execute("INSERT INTO periodizzazione_table(id) VALUES (1)")
    conn.commit()
    conn.close()
    return db


def _run_cli(args):
    """Invoke the CLI as a subprocess for E2E-ish coverage."""
    return subprocess.run(
        [sys.executable, "-m", "pyarchinit_mini.cli.migrate_vocab"] + args,
        capture_output=True, text=True
    )


def test_dry_run_does_not_mutate(legacy_db, tmp_path):
    result = _run_cli([
        "--dry-run",
        "--database", f"sqlite:///{legacy_db}",
        "--backups-dir", str(tmp_path / "b"),
        "--yes",
    ])
    assert result.returncode == 0, f"stderr: {result.stderr}\nstdout: {result.stdout}"
    conn = sqlite3.connect(legacy_db)
    val = conn.execute("SELECT unita_tipo FROM us_table WHERE id_us=1").fetchone()[0]
    conn.close()
    assert val == "USVA"  # NOT migrated


def test_apply_runs_all_three_migrations(legacy_db, tmp_path):
    result = _run_cli([
        "--apply",
        "--database", f"sqlite:///{legacy_db}",
        "--backups-dir", str(tmp_path / "b"),
        "--yes",
    ])
    assert result.returncode == 0, f"stderr: {result.stderr}\nstdout: {result.stdout}"
    # Vocab aligned
    conn = sqlite3.connect(legacy_db)
    val = conn.execute("SELECT unita_tipo FROM us_table WHERE id_us=1").fetchone()[0]
    assert val == "USVs", f"vocab not aligned: {val}"
    # node_uuid backfilled on us_table
    nulls = conn.execute("SELECT COUNT(*) FROM us_table WHERE node_uuid IS NULL").fetchone()[0]
    assert nulls == 0, f"us_table still has {nulls} NULL node_uuid"
    conn.close()
    # Backup file exists
    assert any((tmp_path / "b").glob("*.db")), "backup file not created"


def test_list_backups_after_apply(legacy_db, tmp_path):
    _run_cli([
        "--apply",
        "--database", f"sqlite:///{legacy_db}",
        "--backups-dir", str(tmp_path / "b"),
        "--yes",
    ])
    result = _run_cli([
        "--list-backups",
        "--backups-dir", str(tmp_path / "b"),
    ])
    assert result.returncode == 0
    assert "test.db" in result.stdout


def test_missing_database_arg_with_no_env_exits_nonzero(tmp_path, monkeypatch):
    # Clear env so discovery yields nothing
    monkeypatch.delenv("DATABASE_URL", raising=False)
    result = _run_cli([
        "--dry-run",
        "--backups-dir", str(tmp_path / "b"),
        "--only-default",
        "--yes",
    ])
    # When no DB discovered, exit code != 0
    assert result.returncode != 0
