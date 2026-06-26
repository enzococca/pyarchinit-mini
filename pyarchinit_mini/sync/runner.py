import logging, psycopg2
from psycopg2.extensions import connection
from . import introspect as I
from .config import Config
from .engine import sync_table, TableResult

def discover_tables(src_conn: connection, tgt_conn: connection, cfg: Config) -> list[str]:
    mirrored = I.base_tables(src_conn) & I.base_tables(tgt_conn)
    return sorted(mirrored - set(cfg.exclude_tables))

def run(cfg: Config, tables: list[str] | None = None, dry_run: bool = True, logger=None, _conns: tuple | None = None) -> list[TableResult]:
    logger = logger or logging.getLogger("sync")
    src, tgt = _conns or (psycopg2.connect(cfg.source_dsn), psycopg2.connect(cfg.target_dsn))
    src.autocommit = True              # source: read-only
    owns = _conns is None
    try:
        names = tables if tables else discover_tables(src, tgt, cfg)
        results = []
        ti = tu = td = 0
        for name in names:
            r = sync_table(src, tgt, name, cfg, dry_run=dry_run)
            results.append(r)
            ti += r.inserted; tu += r.updated; td += r.deleted
            tag = "DRY" if dry_run else "APPLY"
            state = "SKIP" if r.skipped else ("ERR:" + r.error if r.error else "ok")
            logger.info("[%s] %-40s mode=%-7s +%d ~%d -%d %s",
                        tag, name, r.mode, r.inserted, r.updated, r.deleted, state)
        logger.info("[%s] TOTAL tables=%d +%d ~%d -%d",
                    "DRY" if dry_run else "APPLY", len(results), ti, tu, td)
        return results
    finally:
        if owns:
            src.close(); tgt.close()
