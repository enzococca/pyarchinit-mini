def base_tables(conn) -> set:
    cur = conn.cursor()
    cur.execute("select table_name from information_schema.tables "
                "where table_schema='public' and table_type='BASE TABLE'")
    return {r[0] for r in cur.fetchall()}

def column_types(conn, table) -> dict:
    cur = conn.cursor()
    cur.execute("select column_name, data_type, character_maximum_length "
                "from information_schema.columns where table_schema='public' and table_name=%s",
                (table,))
    return {r[0]: (r[1], r[2]) for r in cur.fetchall()}

def primary_key(conn, table) -> list:
    cur = conn.cursor()
    cur.execute("""select a.attname from pg_index i
                   join pg_class c on c.oid=i.indrelid
                   join pg_namespace n on n.oid=c.relnamespace
                   join pg_attribute a on a.attrelid=c.oid and a.attnum=any(i.indkey)
                   where n.nspname='public' and c.relname=%s and i.indisprimary
                   order by a.attnum""", (table,))
    return [r[0] for r in cur.fetchall()]

def geometry_columns(conn, table) -> set:
    cur = conn.cursor()
    cur.execute("select column_name from information_schema.columns "
                "where table_schema='public' and table_name=%s "
                "and udt_name in ('geometry','geography')", (table,))
    return {r[0] for r in cur.fetchall()}

def row_count(conn, table) -> int:
    cur = conn.cursor()
    cur.execute(f'select count(*) from public."{table}"')
    return cur.fetchone()[0]

def signature(conn, table, pk) -> str:
    cur = conn.cursor()
    cur.execute(f'select count(*) from public."{table}"')
    cnt = cur.fetchone()[0]
    maxpk = ""
    if pk:
        cur.execute(f'select max("{pk[0]}") from public."{table}"')
        maxpk = str(cur.fetchone()[0])
    return f"{cnt}:{maxpk}"
