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

## Cron (Adarte) — INSTALLED & LIVE since 2026-06-27

Nightly at **03:00** via a wrapper script (keeps DSNs/secrets out of the crontab line).

Crontab entry (`crontab -l` on ganesh@10.0.1.13):
```
0 3 * * * /home/ganesh/run_pyarchinit_sync.sh
```

Wrapper `/home/ganesh/run_pyarchinit_sync.sh` (lives on the server only, not in this repo):
```bash
#!/usr/bin/env bash
export PYARCHINIT_CLASSIC_DSN="postgresql://admin_pyarchinit:<pw>@10.0.1.6:5432/pyarchinit"
export DATABASE_URL="postgresql://admin_pyarchinit:<pw>@10.0.1.6:5432/pyarchinit_v2"
LOGDIR=/home/ganesh/logs; mkdir -p "$LOGDIR"; LOG="$LOGDIR/pyarchinit_sync.log"
echo "===== sync run $(date -Is) =====" >> "$LOG"
/home/ganesh/pyarchinit_env/bin/python -m pyarchinit_mini.sync --apply --log "$LOG" >> "$LOG" 2>&1
echo "----- exit $? @ $(date -Is) -----" >> "$LOG"
```

Monitor / verify:
```
ssh ganesh@10.0.1.13 'tail -30 /home/ganesh/logs/pyarchinit_sync.log'   # each run: TOTAL tables=127 +N ~M -K, exit 0
ssh ganesh@10.0.1.13 'crontab -l | grep run_pyarchinit_sync'            # cron present
ssh ganesh@10.0.1.13 'systemctl is-active cron'                         # daemon active
```
Healthy steady-state on a quiet night = `+0 ~0 -0 exit 0`. Non-zero `~`/`+`/`-` means real v1 deltas propagated.

Reinstall the cron idempotently (no duplicate):
```
( crontab -l 2>/dev/null | grep -v run_pyarchinit_sync.sh ; echo '0 3 * * * /home/ganesh/run_pyarchinit_sync.sh' ) | crontab -
```

Notes:
- weekly full refresh of keyset tables is handled by the engine's signature gate;
  force a deep pass if needed by clearing `sync_state` for those tables.
- First production apply (2026-06-27) was `+0 ~57 -0` (thesaurus_sigle only); `sync_row_map` bootstrapped to ~933k rows; backup at `/home/ganesh/pyarchinit_v2_pre_sync_20260627.dump` (399 MB).

## Rollback
pg_restore --clean --no-owner -d "$DATABASE_URL" ~/pyarchinit_v2_pre_sync_<date>.dump

## Native-preserving model (since 2026-06-27)
- Identity is the map `public.sync_row_map (table_name, v1_pk, v2_pk)`; a row is synced from v1 iff it is mapped.
- v2-native rows (inserted directly in v2, not mapped) are NEVER updated or deleted.
- DELETE happens only for mapped rows whose v1_pk disappeared from v1.
- Id collisions (a new v1 row whose id is taken by a native row) get a v2 id from `collision_id_base` (default 1e9); the map records v1_pk->v2_pk. Relationships are by name (sito/us), so the reassigned surrogate id is harmless.
- No-PK tables (e.g. shape_finali_polygon) are additive-only (insert new v1 content; no update/delete).
- First run bootstraps the map from the current overlap (v1 ids also present in v2); it will not re-delete natives.
- To force a deep refresh of a large gated table, delete its row from public.sync_state.
