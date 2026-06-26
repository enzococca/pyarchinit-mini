# Runbook — sync classic pyarchinit -> pyarchinit_v2

## DSNs (env)
- PYARCHINIT_CLASSIC_DSN = postgresql://admin_pyarchinit:<pw>@10.0.1.6:5432/pyarchinit
- DATABASE_URL           = postgresql://admin_pyarchinit:<pw>@10.0.1.6:5432/pyarchinit_v2

## Local test DBs (for the integration tests)
createdb sync_test_src ; createdb sync_test_tgt
export TEST_SYNC_SRC_DSN=postgresql://localhost/sync_test_src
export TEST_SYNC_TGT_DSN=postgresql://localhost/sync_test_tgt
python -m pytest tests/sync -v

## First run (the re-sync)
1. Dry-run (no writes):
   PYARCHINIT_CLASSIC_DSN=... DATABASE_URL=... python -m pyarchinit_mini.sync
2. Backup target:
   pg_dump "$DATABASE_URL" -Fc -f ~/pyarchinit_v2_pre_sync_$(date +%Y%m%d).dump
3. Apply (start narrow, then full):
   ... python -m pyarchinit_mini.sync --apply --tables site_table,us_table,inventario_materiali_table
   ... python -m pyarchinit_mini.sync --apply
4. Verify: re-run dry-run -> expect all tables +0 ~0 -0 (or SKIP).

## Cron (Adarte)
0 1 * * *  PYARCHINIT_CLASSIC_DSN=... DATABASE_URL=... /home/ganesh/pyarchinit_env/bin/python -m pyarchinit_mini.sync --apply --log /home/ganesh/sync_classic_to_v2.log
# weekly full refresh of keyset tables is handled by the engine's signature gate;
# force a deep pass if needed by clearing sync_state for those tables.

## Rollback
pg_restore --clean --no-owner -d "$DATABASE_URL" ~/pyarchinit_v2_pre_sync_<date>.dump
