"""CLI: pyarchinit-mini-migrate-vocab

Wraps the 3 Spec 1 Foundation migrations (node_uuid schema → backfill →
vocab alignment USVA/USVB→USVs USVC→USVn) and the backup module.

Discovery order for target DBs:
  1. --database <url>  (CLI flag, wins outright)
  2. $DATABASE_URL     (default app DB)
  3. data/connections.json  (saved web connections; skip with --only-default)

Usage examples:
  pyarchinit-mini-migrate-vocab --dry-run
  pyarchinit-mini-migrate-vocab --apply --yes
  pyarchinit-mini-migrate-vocab --rollback --yes
  pyarchinit-mini-migrate-vocab --list-backups
  pyarchinit-mini-migrate-vocab --apply --script vocab_alignment --database sqlite:///x.db --yes
"""
from __future__ import annotations

import argparse
import importlib
import json
import os
import sys
from pathlib import Path

# Use importlib to avoid name collisions with the legacy DatabaseMigrations
# class exported from pyarchinit_mini.database.migrations.__init__.
_pkg = "pyarchinit_mini.database.migrations"
schema_m = importlib.import_module(f"{_pkg}._2026_05_node_uuid_schema")
backfill_m = importlib.import_module(f"{_pkg}._2026_05_node_uuid_backfill")
align_m = importlib.import_module(f"{_pkg}._2026_05_vocab_alignment")

from pyarchinit_mini.database.migrations.backup import backup_database  # noqa: E402


SCRIPTS = {
    "node_uuid_schema": schema_m,
    "node_uuid_backfill": backfill_m,
    "vocab_alignment": align_m,
}
ORDER = ["node_uuid_schema", "node_uuid_backfill", "vocab_alignment"]


def _discover_dbs(args) -> list[str]:
    if args.database:
        return [args.database]
    dbs: list[str] = []
    env = os.environ.get("DATABASE_URL")
    if env:
        dbs.append(env)
    if not args.only_default:
        conns = Path("data/connections.json")
        if conns.exists():
            try:
                data = json.loads(conns.read_text(encoding="utf-8"))
                for entry in data.get("connections", []):
                    url = entry.get("url")
                    if url and url not in dbs:
                        dbs.append(url)
            except json.JSONDecodeError:
                print(f"warning: could not parse {conns}", file=sys.stderr)
    return dbs


def _confirm(prompt: str, yes: bool) -> bool:
    if yes:
        return True
    try:
        ans = input(f"{prompt} [y/N] ").strip().lower()
    except EOFError:
        return False
    return ans == "y"


def _list_backups(backups_dir: Path) -> int:
    idx = backups_dir / "_index.json"
    if not idx.exists():
        print("No backups found.")
        return 0
    for r in json.loads(idx.read_text(encoding="utf-8")):
        print(f"{r['timestamp']}  {r['backup_path']}  ({r['size_bytes']} bytes)")
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        prog="pyarchinit-mini-migrate-vocab",
        description="Foundation migrations: node_uuid schema + backfill + vocab alignment.",
    )
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Report changes without mutating")
    mode.add_argument("--apply", action="store_true", help="Backup then apply migrations")
    mode.add_argument("--rollback", action="store_true", help="(Manual) restore from backup")
    mode.add_argument("--list-backups", action="store_true", help="List recorded backups")
    p.add_argument("--database", type=str, help="Target a specific DB URL")
    p.add_argument("--script", type=str, choices=list(SCRIPTS.keys()),
                   help="Run a single script (advanced)")
    p.add_argument("--only-default", action="store_true",
                   help="Skip data/connections.json discovery")
    p.add_argument("--backups-dir", type=Path, default=Path("data/backups"))
    p.add_argument("--yes", action="store_true", help="Skip confirmation prompts")
    args = p.parse_args(argv)

    if args.list_backups:
        return _list_backups(args.backups_dir)

    if args.rollback:
        # TODO(Spec-2): implement actual rollback (read _index.json → restore latest backup
        # SQLite via cp / PG via pg_restore). Currently prints manual instructions only.
        print("Rollback requires manual restore. Use --list-backups to see what's available,")
        print("then copy/restore the backup file manually (SQLite) or pg_restore (PostgreSQL).")
        return 0

    dbs = _discover_dbs(args)
    if not dbs:
        print("No databases discovered. Use --database <url> or set DATABASE_URL.",
              file=sys.stderr)
        return 2

    scripts_to_run = (
        [SCRIPTS[args.script]] if args.script
        else [SCRIPTS[k] for k in ORDER]
    )

    # TODO(Spec-2): acquire data/.migration_lock (PID + timestamp) to reject concurrent
    # --apply invocations per Spec §6.3
    overall_status = 0
    for db in dbs:
        print(f"== DB: {db} ==")
        if args.apply:
            if not _confirm(f"Backup and migrate {db}?", args.yes):
                print("  skipped (no confirmation)")
                continue
            try:
                rec = backup_database(db, backups_dir=args.backups_dir)
                print(f"  backup: {rec.backup_path}")
            except Exception as e:
                print(f"  backup failed: {e}", file=sys.stderr)
                overall_status = 1
                continue
        for script in scripts_to_run:
            try:
                report = script.run(db, dry_run=args.dry_run)
                print(f"  {report.script}: status={report.status}")
                if hasattr(report, "tables_changed") and report.tables_changed:
                    print(f"    tables_changed: {report.tables_changed}")
                if hasattr(report, "tables_skipped") and report.tables_skipped:
                    print(f"    tables_skipped: {report.tables_skipped}")
                if hasattr(report, "rows_updated"):
                    print(f"    rows_updated: {report.rows_updated}")
                if hasattr(report, "mappings"):
                    print(f"    mappings: {report.mappings}")
            except Exception as e:
                print(f"  {script.__name__} FAILED: {e}", file=sys.stderr)
                overall_status = 1

    # TODO(Spec-2): append per-script JSON-line entry to data/migration.log per Spec §6.4
    # (ts, script, db, rows_updated/mappings/tables_*, duration_ms, status)
    return overall_status


if __name__ == "__main__":
    sys.exit(main())
