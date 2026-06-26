def cast_expr(src_type: str, tgt_type: str, tgt_maxlen: int | None, ph: str = "%s") -> str:
    t = tgt_type
    if t in ("geometry", "geography"):
        return f"({ph})::{t}"
    if t == "character varying" and tgt_maxlen:
        return f"left(({ph})::text, {tgt_maxlen})"
    if t == "text":
        return f"({ph})::text"
    if t in ("integer", "bigint", "smallint"):
        if src_type in ("character varying", "text"):
            return (f"(CASE WHEN btrim(({ph})::text) ~ '^-?[0-9]+$' "
                    f"THEN btrim(({ph})::text)::{t} ELSE NULL END)")
        return f"({ph})::{t}"
    if t == "boolean":
        if src_type == "boolean":
            return f"({ph})"
        if src_type in ("bigint", "integer", "smallint", "numeric", "double precision"):
            return (f"(CASE WHEN {ph} IS NULL THEN NULL "
                    f"WHEN ({ph})::numeric=0 THEN false ELSE true END)")
        return (f"(CASE WHEN btrim(({ph})::text) IN ('1','true','t','yes','si','y') THEN true "
                f"WHEN btrim(({ph})::text) IN ('0','false','f','no','n','') THEN false ELSE NULL END)")
    if t == "date":
        if src_type == "date":
            return f"({ph})"
        return ("(CASE "
                f"WHEN btrim(({ph})::text) ~ '^[0-9]{{4}}-[0-9]{{2}}-[0-9]{{2}}' THEN substr(btrim(({ph})::text),1,10)::date "
                f"WHEN btrim(({ph})::text) ~ '^[0-9]{{1,2}}/[0-9]{{1,2}}/[0-9]{{4}}$' THEN to_date(btrim(({ph})::text),'DD/MM/YYYY') "
                f"WHEN btrim(({ph})::text) ~ '^[0-9]{{1,2}}-[0-9]{{1,2}}-[0-9]{{4}}$' THEN to_date(btrim(({ph})::text),'DD-MM-YYYY') "
                "ELSE NULL END)")
    if t == "timestamp with time zone":
        return f"({ph})::timestamptz"
    if t == "timestamp without time zone":
        return f"({ph})::timestamp"
    if t == "double precision":
        return f"({ph})::double precision"
    if t == "numeric":
        return f"({ph})::numeric"
    return f"({ph})"   # matching/other types: pass the value through

def row_hash_sql(columns: list[str]) -> str:
    parts = "||'|'||".join(f"coalesce(\"{c}\"::text,'')" for c in columns)
    return f"md5({parts})" if columns else "md5('')"

def build_pk_hash_select(table: str, pk: list[str], hash_cols: list[str]) -> str:
    pk_sql = ", ".join(f'"{c}"' for c in pk)
    return f'SELECT {pk_sql}, {row_hash_sql(hash_cols)} FROM public."{table}"'

def coerced_row_hash_sql(columns: list[str], src_types: dict, tgt_types: dict, geom: set) -> str:
    if not columns:
        return "md5('')"
    parts = []
    for c in columns:
        tgt_t = "geometry" if c in geom else tgt_types[c][0]
        expr = cast_expr(src_types[c][0], tgt_t, tgt_types[c][1], ph=f'"{c}"')
        parts.append(f"coalesce(({expr})::text,'')")
    return "md5(" + "||'|'||".join(parts) + ")"

def build_pk_hash_select_coerced(table: str, pk: list[str], columns: list[str],
                                 src_types: dict, tgt_types: dict, geom: set) -> str:
    pk_sql = ", ".join(f'"{c}"' for c in pk)
    return (f'SELECT {pk_sql}, '
            f'{coerced_row_hash_sql(columns, src_types, tgt_types, geom)} FROM public."{table}"')

def build_insert(table: str, cols: list[str], value_exprs: list[str], fill: dict[str, str]) -> str:
    all_cols = cols + list(fill.keys())
    col_sql = ", ".join(f'"{c}"' for c in all_cols)
    val_sql = ", ".join(value_exprs + list(fill.values()))
    return f'INSERT INTO public."{table}" ({col_sql}) VALUES ({val_sql})'

def build_update(table: str, set_cols: list[str], set_exprs: list[str], pk: list[str]) -> str:
    # pk uses NAMED placeholders so the whole statement is named-param (set_exprs
    # carry named %(col)s placeholders from cast_expr; mixing named+positional is illegal).
    assigns = ", ".join(f'"{c}" = {e}' for c, e in zip(set_cols, set_exprs))
    where = " AND ".join(f'"{c}" = %(__pk_{c})s' for c in pk)
    return f'UPDATE public."{table}" SET {assigns} WHERE {where}'
