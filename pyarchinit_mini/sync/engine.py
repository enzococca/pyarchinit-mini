import re
from dataclasses import dataclass
from psycopg2.extensions import connection
from . import introspect as I, transform as T, state as S, rowmap as M
from .diff import diff_by_hash
from .policy import select_mode, is_gated, preserve_set_for_table, common_data_columns

@dataclass
class TableResult:
    table: str; mode: str; inserted: int; updated: int; deleted: int
    skipped: bool; error: str | None

_FILL_DEFAULTS = {
    "created_at": "now()", "updated_at": "now()", "version_number": "1",
    "entity_uuid": "gen_random_uuid()::text", "node_uuid": "gen_random_uuid()::text",
}

def _source_hash(src_conn, table, pk, common, src_types, tgt_types, geom):
    hcols = [c for c in common if c != pk]      # pk excluded; identity is the map, not the hash
    cur = src_conn.cursor()
    cur.execute(T.build_pk_hash_select_coerced(table, [pk], hcols, src_types, tgt_types, geom))
    return {str(r[0]): r[1] for r in cur.fetchall()}

def _target_hash(tgt_conn, table, pk, common):
    hcols = [c for c in common if c != pk]
    cur = tgt_conn.cursor()
    cur.execute(f'select "{pk}"::text, {T.row_hash_sql(hcols)} from public."{table}"')
    return {r[0]: r[1] for r in cur.fetchall()}

def _fetch_source_row(src_conn, table, common, pk, v1_pk):
    cur = src_conn.cursor()
    cols = ", ".join(f'"{c}"' for c in common)
    cur.execute(f'select {cols} from public."{table}" where "{pk}"::text=%s', (v1_pk,))
    return cur.fetchone()

def _value_exprs(common, src_types, tgt_types, geom):
    out = []
    for c in common:
        tgt_t = "geometry" if c in geom else tgt_types[c][0]
        out.append(T.cast_expr(src_types[c][0], tgt_t, tgt_types[c][1], ph=f"%({c})s"))
    return out

def _insert_one(tgt_conn, table, common, pk, row, v2_pk, src_types, tgt_types, geom):
    # row is aligned to `common`; force the pk column to the chosen v2_pk
    exprs = _value_exprs(common, src_types, tgt_types, geom)
    fill = {c: v for c, v in _FILL_DEFAULTS.items() if c in tgt_types and c not in common}
    cols = common + list(fill.keys())
    col_sql = ", ".join(f'"{c}"' for c in cols)
    val_sql = ", ".join(exprs + list(fill.values()))
    params = {c: row[i] for i, c in enumerate(common)}
    params[pk] = v2_pk                       # override pk value with the chosen v2_pk
    tgt_conn.cursor().execute(
        f'INSERT INTO public."{table}" ({col_sql}) VALUES ({val_sql})', params)

def _update_one(tgt_conn, table, common, pk, row, v2_pk, src_types, tgt_types, geom):
    set_cols = [c for c in common if c != pk]            # never update the pk
    exprs = _value_exprs(set_cols, src_types, tgt_types, geom)
    assigns = ", ".join(f'"{c}" = {e}' for c, e in zip(set_cols, exprs))
    params = {c: row[common.index(c)] for c in set_cols}
    params["__v2pk"] = v2_pk
    tgt_conn.cursor().execute(
        f'UPDATE public."{table}" SET {assigns} WHERE "{pk}"::text = %(__v2pk)s', params)

def _delete_one(tgt_conn, table, pk, v2_pk):
    tgt_conn.cursor().execute(f'delete from public."{table}" where "{pk}"::text=%s', (v2_pk,))

def _alloc_v2_pk(v1_pk, v2pks, state):
    if v1_pk not in v2pks:
        return v1_pk
    nxt = state["next_high"]
    while str(nxt) in v2pks:
        nxt += 1
    state["next_high"] = nxt + 1
    return str(nxt)

def sync_table(src_conn, tgt_conn, table, cfg, dry_run=True) -> TableResult:
    mode = "unknown"; ins = upd = dele = 0
    try:
        M.ensure_map_table(tgt_conn); S.ensure_state_table(tgt_conn)
        pk_cols = I.primary_key(src_conn, table)
        single_pk = pk_cols[0] if len(pk_cols) == 1 else None
        mode = select_mode(single_pk is not None)
        rc = I.row_count(src_conn, table)
        src_types = I.column_types(src_conn, table)
        tgt_types = I.column_types(tgt_conn, table)
        geom = I.geometry_columns(tgt_conn, table)
        preserve = preserve_set_for_table(cfg.preserve_columns_global,
                                          set(src_types), set(tgt_types), [])
        common = common_data_columns(set(src_types), set(tgt_types), preserve)
        if mode == "additive":
            src_hexpr = T.coerced_row_hash_sql(common, src_types, tgt_types, geom)
            tgt_hexpr = T.row_hash_sql(common)
            scur = src_conn.cursor()
            scur.execute(f'select {src_hexpr}, {", ".join(chr(34)+c+chr(34) for c in common)} '
                         f'from public."{table}"')
            srows = scur.fetchall()
            tcur = tgt_conn.cursor()
            tcur.execute(f'select {tgt_hexpr} from public."{table}"')
            seen = {r[0] for r in tcur.fetchall()}
            exprs = _value_exprs(common, src_types, tgt_types, geom)
            col_sql = ", ".join(f'"{c}"' for c in common)
            sql = f'INSERT INTO public."{table}" ({col_sql}) VALUES ({", ".join(exprs)})'
            icur = tgt_conn.cursor()
            for r in srows:
                h = r[0]
                if h in seen:
                    continue
                seen.add(h)
                row = r[1:]
                params = {c: row[i] for i, c in enumerate(common)}
                icur.execute(sql, params)
                ins += 1
            if dry_run:
                tgt_conn.rollback()
            else:
                S.record_result(tgt_conn, table, I.signature(src_conn, table, pk_cols),
                                mode, ins, 0, 0, None)
                tgt_conn.commit()
            return TableResult(table, mode, ins, 0, 0, False, None)
        if is_gated(rc, cfg.size_threshold_keyset):
            if I.signature(src_conn, table, pk_cols) == S.get_signature(tgt_conn, table):
                tgt_conn.rollback()
                return TableResult(table, mode, 0, 0, 0, True, None)
        if M.map_count(tgt_conn, table) == 0:
            M.bootstrap_table(tgt_conn, src_conn, table, single_pk)
        mp = M.load_map(tgt_conn, table)                       # {v1_pk: v2_pk}
        src = _source_hash(src_conn, table, single_pk, common, src_types, tgt_types, geom)
        tgt_h = _target_hash(tgt_conn, table, single_pk, common)   # {v2_pk: hash}
        target = {v1: tgt_h.get(v2) for v1, v2 in mp.items()}      # {v1_pk: hash-of-its-v2-row}
        d = diff_by_hash(src, target)
        v2pks = M.v2_pk_set(tgt_conn, table, single_pk)
        nums = [int(x) for x in v2pks if re.fullmatch(r"-?\d+", x)]
        state = {"next_high": max([cfg.collision_id_base] + [n + 1 for n in nums])}
        if cfg.delete_enabled and (rc > 0 or cfg.delete_on_empty_source):
            for v1k in d.deletes:
                _delete_one(tgt_conn, table, single_pk, mp[v1k]); M.delete_map(tgt_conn, table, v1k); dele += 1
        for v1k in d.inserts:
            row = _fetch_source_row(src_conn, table, common, single_pk, v1k)
            if row is None:
                continue
            v2k = _alloc_v2_pk(v1k, v2pks, state)
            _insert_one(tgt_conn, table, common, single_pk, row, v2k, src_types, tgt_types, geom)
            M.upsert_map(tgt_conn, table, v1k, v2k); v2pks.add(v2k); ins += 1
        for v1k in d.updates:
            v2k = mp[v1k]
            row = _fetch_source_row(src_conn, table, common, single_pk, v1k)
            if row is None:
                continue
            if v2k in v2pks:
                _update_one(tgt_conn, table, common, single_pk, row, v2k, src_types, tgt_types, geom)
            else:                                   # mapped row deleted in v2 -> re-insert
                v2k = _alloc_v2_pk(v1k, v2pks, state)
                _insert_one(tgt_conn, table, common, single_pk, row, v2k, src_types, tgt_types, geom)
                M.upsert_map(tgt_conn, table, v1k, v2k); v2pks.add(v2k)
            upd += 1
        if dry_run:
            tgt_conn.rollback()
        else:
            S.record_result(tgt_conn, table, I.signature(src_conn, table, pk_cols),
                            mode, ins, upd, dele, None)
            tgt_conn.commit()
        return TableResult(table, mode, ins, upd, dele, False, None)
    except Exception as e:
        tgt_conn.rollback()
        msg = str(e).splitlines()[0]
        try:
            S.ensure_state_table(tgt_conn)
            S.record_result(tgt_conn, table, "", mode, 0, 0, 0, msg); tgt_conn.commit()
        except Exception:
            tgt_conn.rollback()
        return TableResult(table, mode, 0, 0, 0, False, msg)
