from psycopg2.extensions import connection
from psycopg2.extras import execute_values


def ensure_map_table(conn: connection) -> None:
    conn.cursor().execute("""
        CREATE TABLE IF NOT EXISTS public.sync_row_map (
            table_name text NOT NULL,
            v1_pk text NOT NULL,
            v2_pk text NOT NULL,
            last_run_at timestamptz DEFAULT now(),
            PRIMARY KEY (table_name, v1_pk),
            UNIQUE (table_name, v2_pk)
        )""")


def map_count(conn: connection, table: str) -> int:
    cur = conn.cursor()
    cur.execute("select count(*) from public.sync_row_map where table_name=%s", (table,))
    return cur.fetchone()[0]


def load_map(conn: connection, table: str) -> dict[str, str]:
    cur = conn.cursor()
    cur.execute("select v1_pk, v2_pk from public.sync_row_map where table_name=%s", (table,))
    return {r[0]: r[1] for r in cur.fetchall()}


def v2_pk_set(conn: connection, table: str, pk: str) -> set[str]:
    cur = conn.cursor()
    cur.execute(f'select "{pk}"::text from public."{table}"')
    return {r[0] for r in cur.fetchall()}


def bootstrap_table(tgt_conn: connection, src_conn: connection, table: str, pk: str) -> int:
    if map_count(tgt_conn, table) > 0:      # only bootstrap an empty map
        return 0
    scur = src_conn.cursor()
    scur.execute(f'select "{pk}"::text from public."{table}"')
    v1 = {r[0] for r in scur.fetchall()}
    v2 = v2_pk_set(tgt_conn, table, pk)
    overlap = sorted(v1 & v2)
    if not overlap:
        return 0
    tcur = tgt_conn.cursor()
    execute_values(tcur,
        "INSERT INTO public.sync_row_map (table_name, v1_pk, v2_pk) VALUES %s "
        "ON CONFLICT (table_name, v1_pk) DO NOTHING",
        [(table, k, k) for k in overlap])
    return len(overlap)


def upsert_map(conn: connection, table: str, v1_pk: str, v2_pk: str) -> None:
    conn.cursor().execute(
        "INSERT INTO public.sync_row_map (table_name, v1_pk, v2_pk) VALUES (%s,%s,%s) "
        "ON CONFLICT (table_name, v1_pk) DO UPDATE SET v2_pk=EXCLUDED.v2_pk, last_run_at=now()",
        (table, v1_pk, v2_pk))


def delete_map(conn: connection, table: str, v1_pk: str) -> None:
    conn.cursor().execute(
        "delete from public.sync_row_map where table_name=%s and v1_pk=%s", (table, v1_pk))
