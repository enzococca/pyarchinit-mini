"""Anonymized fixture builder for swimlane regression test.

Connects to Adarte postgres, pulls 100 US from Rimini_RN_2020_21_Museo_Fellini,
renames site to RegressionFixture_v1, preserves US numbers, writes a SQL file
of CREATE/INSERT statements compatible with sqlite (TEXT columns, no
postgres-only types).
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    import psycopg2
except ImportError:
    print("psycopg2 not installed; run on Adarte where pyarchinit_env has it.")
    sys.exit(1)


DSN = "postgresql://admin_pyarchinit:***REMOVED***@10.0.1.6:5432/pyarchinit_v2"
ORIG_SITE = "Rimini_RN_2020_21_Museo_Fellini_Piazza_Malatesta_Lotto_1_3"
NEW_SITE = "RegressionFixture_v1"
LIMIT = 100
OUT_PATH = Path(__file__).parent.parent / "tests" / "fixtures" / "adarte_regression_dump.sql"


def main():
    conn = psycopg2.connect(DSN)
    cur = conn.cursor()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write("-- Auto-generated anonymized fixture for swimlane regression test\n")
        f.write(f"-- Source: {ORIG_SITE} (Adarte production)\n")
        f.write(f"-- Site renamed to: {NEW_SITE}\n")
        f.write("-- DO NOT EDIT BY HAND - re-run scripts/build_regression_fixture.py\n\n")

        # Schema (sqlite-friendly: TEXT, no INDEX-on-NULL postgres quirks)
        f.write("""CREATE TABLE IF NOT EXISTS site_table (
    id_sito INTEGER PRIMARY KEY AUTOINCREMENT, sito TEXT UNIQUE);
""")
        f.write("""CREATE TABLE IF NOT EXISTS period_table (
    id_period INTEGER PRIMARY KEY AUTOINCREMENT, sito TEXT, periodo TEXT,
    fase TEXT, datazione TEXT);
""")
        f.write("""CREATE TABLE IF NOT EXISTS us_table (
    id_us INTEGER PRIMARY KEY AUTOINCREMENT, sito TEXT, area TEXT, us TEXT,
    unita_tipo TEXT, descrizione TEXT, fase_iniziale TEXT, fase_finale TEXT,
    settore TEXT, quadrato TEXT, attivita TEXT, struttura TEXT,
    rapporti TEXT, data_origine TEXT, UNIQUE(sito, area, us));
""")
        f.write(f"INSERT INTO site_table (sito) VALUES ('{NEW_SITE}');\n\n")

        # Periods
        cur.execute("SELECT periodo, fase, datazione FROM period_table WHERE sito = %s", (ORIG_SITE,))
        for periodo, fase, dataz in cur.fetchall():
            f.write(
                "INSERT INTO period_table (sito, periodo, fase, datazione) VALUES "
                f"({_qstr(NEW_SITE)}, {_qstr(periodo or '')}, {_qstr(fase or '')}, {_qstr(dataz or '')});\n"
            )
        f.write("\n")

        # US rows (subset of LIMIT, ordered so we get the high-rapporti ones)
        cur.execute("""SELECT area, us, unita_tipo, descrizione, fase_iniziale, fase_finale, rapporti
                       FROM us_table
                       WHERE sito = %s
                         AND rapporti IS NOT NULL
                         AND rapporti != ''
                         AND rapporti != '[]'
                       ORDER BY LENGTH(rapporti) DESC
                       LIMIT %s""", (ORIG_SITE, LIMIT))
        for area, us, ut, desc, fi, ff, rapp in cur.fetchall():
            # Sanitize rapporti: replace original site name with anonymized one
            rapp_safe = (rapp or "").replace(ORIG_SITE, NEW_SITE)
            f.write(
                "INSERT INTO us_table (sito, area, us, unita_tipo, descrizione, "
                "fase_iniziale, fase_finale, rapporti) VALUES "
                f"({_qstr(NEW_SITE)}, {_qstr(area or '')}, {_qstr(us or '')}, "
                f"{_qstr(ut or 'US')}, {_qstr(desc or '')}, {_qstr(fi or '')}, "
                f"{_qstr(ff or '')}, {_qstr(rapp_safe)});\n"
            )

    conn.close()
    print(f"Fixture written to {OUT_PATH}")


def _qstr(s: str) -> str:
    """Escape single quotes for SQL literal."""
    return "'" + s.replace("'", "''") + "'"


if __name__ == "__main__":
    main()
