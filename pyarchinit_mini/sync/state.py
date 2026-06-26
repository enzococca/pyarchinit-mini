"""sync_state tracking table — records last sync result per table."""


def ensure_state_table(conn) -> None:
    conn.cursor().execute("""
        CREATE TABLE IF NOT EXISTS public.sync_state (
            table_name text PRIMARY KEY,
            last_signature text,
            last_run_at timestamptz DEFAULT now(),
            last_mode text,
            rows_inserted int DEFAULT 0,
            rows_updated int DEFAULT 0,
            rows_deleted int DEFAULT 0,
            error text
        )""")


def get_signature(conn, table: str) -> str | None:
    cur = conn.cursor()
    cur.execute("select last_signature from public.sync_state where table_name=%s", (table,))
    row = cur.fetchone()
    return row[0] if row else None


def record_result(
    conn,
    table: str,
    signature: str,
    mode: str,
    inserted: int,
    updated: int,
    deleted: int,
    error: str | None,
) -> None:
    conn.cursor().execute("""
        INSERT INTO public.sync_state
          (table_name, last_signature, last_run_at, last_mode, rows_inserted, rows_updated, rows_deleted, error)
        VALUES (%s,%s,now(),%s,%s,%s,%s,%s)
        ON CONFLICT (table_name) DO UPDATE SET
          last_signature=EXCLUDED.last_signature, last_run_at=now(), last_mode=EXCLUDED.last_mode,
          rows_inserted=EXCLUDED.rows_inserted, rows_updated=EXCLUDED.rows_updated,
          rows_deleted=EXCLUDED.rows_deleted, error=EXCLUDED.error
        """, (table, signature, mode, inserted, updated, deleted, error))
