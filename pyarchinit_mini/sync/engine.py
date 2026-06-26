from dataclasses import dataclass
from . import introspect as I, transform as T, state as S
from .diff import diff_by_hash, diff_by_keyset
from .policy import select_mode, preserve_set_for_table, common_data_columns

@dataclass
class TableResult:
    table: str; mode: str; inserted: int; updated: int; deleted: int
    skipped: bool; error: str | None

_FILL_DEFAULTS = {
    "created_at": "now()", "updated_at": "now()", "version_number": "1",
    "entity_uuid": "gen_random_uuid()::text", "node_uuid": "gen_random_uuid()::text",
}

def _fetch_keyed_hash(conn, table, pk, hash_cols):
    cur = conn.cursor()
    cur.execute(T.build_pk_hash_select(table, pk, hash_cols))
    return {tuple(r[:len(pk)]): r[len(pk)] for r in cur.fetchall()}

def _pk_set(conn, table, pk):
    cur = conn.cursor()
    cur.execute(f'select {", ".join(chr(34)+c+chr(34) for c in pk)} from public."{table}"')
    return {tuple(r) for r in cur.fetchall()}

def _fetch_source_rows(src_conn, table, common, pk, keys=None, all_rows=False):
    """Return rows as tuples ordered (common..., pk...)."""
    cur = src_conn.cursor()
    sel = ", ".join(f'"{c}"' for c in common + pk)
    if all_rows:
        cur.execute(f'select {sel} from public."{table}"')
        return cur.fetchall()
    rows = []
    where = " AND ".join(f'"{c}"=%s' for c in pk)
    for key in (keys or []):
        cur.execute(f'select {sel} from public."{table}" where {where}', list(key))
        r = cur.fetchone()
        if r is not None:
            rows.append(r)
    return rows

def _value_exprs(common, src_types, tgt_types, geom):
    # Named placeholder per column: cast_expr may emit the placeholder N times
    # (varchar->int = 2, varchar->date = 6); a named %(col)s binds them all to one value.
    out = []
    for c in common:
        tgt_t = "geometry" if c in geom else tgt_types[c][0]
        out.append(T.cast_expr(src_types[c][0], tgt_t, tgt_types[c][1], ph=f"%({c})s"))
    return out

def _insert_rows(tgt_conn, table, common, rows, src_types, tgt_types, geom):
    if not rows:
        return 0
    exprs = _value_exprs(common, src_types, tgt_types, geom)
    fill = {c: v for c, v in _FILL_DEFAULTS.items() if c in tgt_types and c not in common}
    sql = T.build_insert(table, common, exprs, fill)
    cur = tgt_conn.cursor(); total = 0
    for r in rows:
        params = {c: r[i] for i, c in enumerate(common)}    # dict (named params)
        cur.execute(sql, params)
        total += cur.rowcount
    return total

def _update_rows(tgt_conn, table, common, pk, rows, src_types, tgt_types, geom):
    if not rows:
        return 0
    exprs = _value_exprs(common, src_types, tgt_types, geom)
    sql = T.build_update(table, common, exprs, pk)
    cur = tgt_conn.cursor(); total = 0
    for r in rows:
        params = {c: r[i] for i, c in enumerate(common)}
        for j, p in enumerate(pk):
            params[f"__pk_{p}"] = r[len(common) + j]
        cur.execute(sql, params)
        total += cur.rowcount
    return total

def _delete_rows(tgt_conn, table, pk, keys, cfg):
    if not keys or not cfg.delete_enabled:
        return 0
    cur = tgt_conn.cursor(); total = 0
    where = " AND ".join(f'"{c}"=%s' for c in pk)
    for key in keys:
        cur.execute(f'delete from public."{table}" where {where}', list(key))
        total += cur.rowcount
    return total

def sync_table(src_conn, tgt_conn, table, cfg, dry_run=True) -> TableResult:
    mode = "unknown"          # so the except handler can reference it on early failure
    ins = upd = dele = 0
    try:
        S.ensure_state_table(tgt_conn)   # idempotent; MUST precede get_signature
        pk = I.primary_key(src_conn, table)
        override = cfg.overrides.get(table) or {}
        rc = I.row_count(src_conn, table)
        mode = select_mode(rc, bool(pk), cfg.size_threshold_keyset, override.get("mode"))
        src_types = I.column_types(src_conn, table)
        tgt_types = I.column_types(tgt_conn, table)
        geom = I.geometry_columns(tgt_conn, table)
        preserve = preserve_set_for_table(cfg.preserve_columns_global, set(src_types), set(tgt_types),
                                          override.get("extra_preserve", []))
        common = common_data_columns(set(src_types), set(tgt_types), preserve)
        if mode in ("keyset", "replace"):
            if I.signature(src_conn, table, pk) == S.get_signature(tgt_conn, table):
                tgt_conn.rollback()      # close the open transaction; nothing to persist
                return TableResult(table, mode, 0, 0, 0, True, None)
        if mode == "replace":
            tgt_conn.cursor().execute(f'TRUNCATE public."{table}"')
            rows = _fetch_source_rows(src_conn, table, common, pk, all_rows=True)
            ins = _insert_rows(tgt_conn, table, common, rows, src_types, tgt_types, geom)
        elif mode == "keyset":
            d = diff_by_keyset(_pk_set(src_conn, table, pk), _pk_set(tgt_conn, table, pk))
            rows = _fetch_source_rows(src_conn, table, common, pk, keys=d.inserts)
            ins = _insert_rows(tgt_conn, table, common, rows, src_types, tgt_types, geom)
            dele = _delete_rows(tgt_conn, table, pk, d.deletes, cfg)
        else:  # full
            d = diff_by_hash(_fetch_keyed_hash(src_conn, table, pk, common),
                             _fetch_keyed_hash(tgt_conn, table, pk, common))
            ins = _insert_rows(tgt_conn, table, common,
                               _fetch_source_rows(src_conn, table, common, pk, keys=d.inserts),
                               src_types, tgt_types, geom)
            upd = _update_rows(tgt_conn, table, common, pk,
                               _fetch_source_rows(src_conn, table, common, pk, keys=d.updates),
                               src_types, tgt_types, geom)
            dele = _delete_rows(tgt_conn, table, pk, d.deletes, cfg)
        if dry_run:
            tgt_conn.rollback()
        else:
            S.record_result(tgt_conn, table, I.signature(src_conn, table, pk), mode, ins, upd, dele, None)
            tgt_conn.commit()
        return TableResult(table, mode, ins, upd, dele, False, None)
    except Exception as e:
        tgt_conn.rollback()
        return TableResult(table, mode, 0, 0, 0, False, str(e).splitlines()[0])
