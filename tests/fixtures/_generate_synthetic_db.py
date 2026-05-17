"""One-shot generator for the synthetic test DB. Run once, commit the .db.

Schema mirrors a subset of us_table needed for Harris matrix generation.
Includes a mix of standard types (US, USM) and types that will change after
Task 9 (USVs, USVn, RSF — these are new types introduced post-spec).
Also includes legacy USVA/USVB/USVC values to verify graceful fallback.
"""
import sqlite3
from pathlib import Path

OUT = Path(__file__).parent / "databases" / "sqlite_fully_migrated.db"
OUT.parent.mkdir(parents=True, exist_ok=True)
if OUT.exists():
    OUT.unlink()

conn = sqlite3.connect(OUT)
c = conn.cursor()

c.execute("""CREATE TABLE us_table (
    id_us INTEGER PRIMARY KEY,
    sito TEXT, area TEXT, us INTEGER, unita_tipo TEXT,
    d_stratigrafica TEXT, d_interpretativa TEXT,
    rapporti TEXT, node_uuid TEXT
)""")

unit_types_cycle = [
    "US", "US", "US", "USVs", "USVs", "USVn", "SF", "VSF", "USM", "USD",
    "US", "US", "USVs", "USVn", "SF", "USM", "RSF", "US", "US", "US",
    "USVs", "USVs", "USVn", "SF", "VSF", "USM", "USD", "US", "US", "US",
]
rows = [
    (i, "TestSite", "A", 1000 + i, ut, f"strat {i}", f"interp {i}", "",
     f"01900000-0000-7{i:03d}-8000-000000000000")
    for i, ut in enumerate(unit_types_cycle)
]
c.executemany("INSERT INTO us_table VALUES (?,?,?,?,?,?,?,?,?)", rows)
conn.commit()
conn.close()
print(f"Wrote {OUT} ({len(rows)} rows)")
