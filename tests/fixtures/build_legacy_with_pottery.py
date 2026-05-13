"""
Build a minimal legacy PyArchInit-QGIS SQLite DB that contains the
pottery_table with the original QGIS schema (no sync columns).
Used by integration tests for upgrade_legacy_schema and migrate-database.
"""
from pathlib import Path
import sqlite3

FIXTURE = Path(__file__).parent / "legacy_with_pottery.sqlite"

def build():
    if FIXTURE.exists():
        FIXTURE.unlink()
    conn = sqlite3.connect(FIXTURE)
    cur = conn.cursor()
    # Minimal site_table and us_table so the upgrade pass can run
    cur.execute("""
        CREATE TABLE site_table (
            id_sito INTEGER PRIMARY KEY,
            sito TEXT NOT NULL,
            nazione TEXT,
            regione TEXT,
            comune TEXT,
            descrizione TEXT,
            find_check INTEGER
        )
    """)
    cur.execute("INSERT INTO site_table VALUES (1, 'Castelseprio', 'IT', 'Lombardia', 'CS', 'desc', 0)")

    cur.execute("""
        CREATE TABLE us_table (
            id_us INTEGER PRIMARY KEY,
            sito TEXT,
            area TEXT,
            us INTEGER,
            d_stratigrafica TEXT
        )
    """)
    cur.execute("INSERT INTO us_table VALUES (1, 'Castelseprio', 'A', 1, 'strato')")

    # QGIS pottery_table EXACT schema (no sync cols)
    cur.execute("""
        CREATE TABLE pottery_table (
            id_rep INTEGER PRIMARY KEY,
            id_number INTEGER,
            sito TEXT,
            area TEXT,
            us INTEGER,
            box INTEGER,
            photo TEXT,
            drawing TEXT,
            anno INTEGER,
            fabric TEXT,
            percent TEXT,
            material TEXT,
            form TEXT,
            specific_form TEXT,
            ware TEXT,
            munsell TEXT,
            surf_trat TEXT,
            exdeco TEXT,
            intdeco TEXT,
            wheel_made TEXT,
            descrip_ex_deco TEXT,
            descrip_in_deco TEXT,
            note TEXT,
            diametro_max NUMERIC(7,3),
            qty INTEGER,
            diametro_rim NUMERIC(7,3),
            diametro_bottom NUMERIC(7,3),
            diametro_height NUMERIC(7,3),
            diametro_preserved NUMERIC(7,3),
            specific_shape TEXT,
            bag INTEGER,
            sector TEXT,
            UNIQUE (sito, id_number)
        )
    """)
    cur.executemany(
        "INSERT INTO pottery_table VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        [
            (1, 101, 'Castelseprio', 'A', 1, 5, '/leg/p1.jpg', '/leg/d1.png',
             2023, 'Coarse', '80%', 'Ceramica', 'Olla', 'Olla A', 'African RS',
             '7.5YR 5/6', 'lisciata', 'liscia', 'liscia', 'Yes',
             'esterno liscio', 'interno liscio', 'integra',
             14.5, 1, 12.0, 6.0, 18.0, 100.0, 'A1', 3, 'NE'),
            (2, 102, 'Castelseprio', 'A', 1, 5, None, None,
             2023, 'Fine', '20%', 'Ceramica', 'Ciotola', None, 'TS',
             '5YR 6/8', 'depurata', None, None, 'Indeterminate',
             None, None, 'frammento di orlo',
             8.0, 2, 8.0, None, None, 30.0, 'B2', 4, 'NE'),
        ],
    )
    conn.commit()
    conn.close()
    print(f"Built fixture: {FIXTURE}")

if __name__ == "__main__":
    build()
