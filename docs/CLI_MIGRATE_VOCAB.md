# pyarchinit-mini-migrate-vocab

CLI for the Spec 1 Foundation migrations. Runs 3 sub-migrations in sequence:
1. `node_uuid_schema` — `ALTER TABLE ADD COLUMN node_uuid TEXT` on `us_table`,
   `inventario_materiali_table`, `periodizzazione_table` (+ unique index).
2. `node_uuid_backfill` — `UPDATE … SET node_uuid = uuid7()` on rows where
   `node_uuid IS NULL`, batched at 1000 rows.
3. `vocab_alignment` — `USVA`/`USVB` → `USVs`, `USVC` → `USVn` on
   `us_table.unita_tipo`.

All 3 are **idempotent** — re-running is a no-op once a DB is fully aligned.

## Quick start

```bash
# Preview what will change (no mutation)
pyarchinit-mini-migrate-vocab --dry-run

# Apply (auto-backup before mutating)
pyarchinit-mini-migrate-vocab --apply --yes

# List recorded backups
pyarchinit-mini-migrate-vocab --list-backups
```

## Flags

| Flag | Description |
|---|---|
| `--dry-run` | Compute what would change; do not mutate. Mutually exclusive with `--apply` / `--rollback` / `--list-backups`. |
| `--apply` | Backup each discovered DB, then run the 3 migrations in sequence. |
| `--rollback` | Print restore instructions (manual: SQLite cp / PG pg_restore). |
| `--list-backups` | Read `<backups-dir>/_index.json` and list known backups. |
| `--database <url>` | Override discovery; target only this DB. Format: `sqlite:///path/to.db` or `postgresql://user:pw@host/db`. |
| `--script <name>` | Run a single migration script: `node_uuid_schema`, `node_uuid_backfill`, or `vocab_alignment`. Advanced; default runs all 3. |
| `--only-default` | Skip `data/connections.json` discovery (only `DATABASE_URL` or `--database`). |
| `--backups-dir <path>` | Where backups live. Default: `data/backups`. |
| `--yes` | Skip confirmation prompts (for scripted runs). |

## DB discovery

When `--database` is NOT given, the CLI looks at:

1. `$DATABASE_URL` (the default app DB)
2. `data/connections.json` (saved web connections, unless `--only-default`)

All discovered DBs are migrated in turn.

## Backup mechanics

- **SQLite**: file copy via `shutil.copy2` → `<backups-dir>/<dbname>.pre_vocab_alignment_<YYYYMMDD_HHMMSS>.db`
- **PostgreSQL**: `pg_dump -Fc -d <url> -f <dump>` → `<backups-dir>/<dbname>.pre_vocab_alignment_<...>.dump`
- SHA-256 checksum recorded in `<backups-dir>/_index.json` alongside path/size/timestamp.

Restore is manual: copy the SQLite file back, or `pg_restore` the dump.

## Troubleshooting

### "SQLite 3.35+ required for DROP COLUMN" (only relevant to manual rollback)
The schema migration uses `ALTER TABLE … ADD COLUMN` which is supported on
SQLite ≥ 3.2. Reversing it via `DROP COLUMN` requires SQLite ≥ 3.35 (2021).
If your SQLite is older, manually restore from the backup file instead.

### "pg_dump: command not found"
The PostgreSQL backup path shells out to `pg_dump`. Install PostgreSQL
client tools (e.g. `brew install libpq` on macOS, `apt install
postgresql-client` on Debian/Ubuntu).

### Idempotency
All 3 scripts are safe to re-run. The schema script skips columns that
already exist; the backfill skips rows with non-NULL `node_uuid`; the
vocab alignment skips rows whose `unita_tipo` is already a canonical value.

### Concurrent runs
A file lock at `data/.migration_lock` prevents concurrent `--apply`
invocations. If a previous run was killed mid-flight, you can remove
the lock manually after verifying no other process is running.
