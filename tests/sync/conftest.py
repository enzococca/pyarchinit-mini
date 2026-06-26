import os, pytest, psycopg2
SRC = os.getenv("TEST_SYNC_SRC_DSN"); TGT = os.getenv("TEST_SYNC_TGT_DSN")
pytestmark = pytest.mark.skipif(not (SRC and TGT), reason="set TEST_SYNC_SRC_DSN/TEST_SYNC_TGT_DSN")

@pytest.fixture
def src_conn():
    c = psycopg2.connect(SRC); c.autocommit = True     # source is read-only
    yield c; c.close()

@pytest.fixture
def tgt_conn():
    c = psycopg2.connect(TGT); c.autocommit = False    # engine controls the transaction
    yield c; c.close()

@pytest.fixture
def make_table():
    created = []  # (conn, name)
    def _make(conn, name, ddl, rows=()):
        cur = conn.cursor()
        cur.execute(f'DROP TABLE IF EXISTS public."{name}" CASCADE')
        cur.execute(ddl)
        created.append((conn, name))
        for r in rows:
            ph = ",".join(["%s"] * len(r))
            cur.execute(f'INSERT INTO public."{name}" VALUES ({ph})', r)
        conn.commit()      # no-op under autocommit; required for the transactional target
        return name
    yield _make
    for conn, name in created:
        conn.cursor().execute(f'DROP TABLE IF EXISTS public."{name}" CASCADE')
        conn.commit()
