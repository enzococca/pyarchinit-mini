"""One-shot generator for harris_swimlane test fixtures. Run once; commit outputs."""
import json
import sqlite3
from pathlib import Path

FIX = Path(__file__).parent
DB = FIX / "databases" / "sqlite_volterra_30us_with_periods.db"
JSON_OUT = FIX / "cytoscape_states" / "volterra_loaded.json"

DB.parent.mkdir(parents=True, exist_ok=True)
JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
if DB.exists():
    DB.unlink()

conn = sqlite3.connect(DB)
c = conn.cursor()

c.executescript("""
CREATE TABLE period_table (
    id_period INTEGER PRIMARY KEY AUTOINCREMENT,
    sito TEXT,
    periodo TEXT NOT NULL,
    fase TEXT,
    datazione TEXT,
    descrizione TEXT
);
CREATE TABLE periodizzazione_table (
    id_periodizzazione INTEGER PRIMARY KEY AUTOINCREMENT,
    sito TEXT, area TEXT, us INTEGER,
    periodo_iniziale TEXT, fase_iniziale TEXT,
    periodo_finale TEXT, fase_finale TEXT
);
CREATE TABLE us_table (
    id_us INTEGER PRIMARY KEY AUTOINCREMENT,
    sito TEXT, area TEXT, us INTEGER, unita_tipo TEXT,
    d_stratigrafica TEXT, d_interpretativa TEXT,
    datazione TEXT, file_path TEXT,
    rapporti TEXT, node_uuid TEXT,
    periodo_iniziale TEXT, fase_iniziale TEXT,
    periodo_finale TEXT, fase_finale TEXT
);
""")

# 5 (periodo, fase) rows on the production schema
periods = [
    ("Roman", "a", "-27..100"),
    ("Roman", "b", "100..300"),
    ("Late Antiquity", "a", "300..600"),
    ("Medieval", "a", "600..1200"),
    ("Medieval", "b", "1200..1500"),
]
for p, ph, dz in periods:
    c.execute(
        "INSERT INTO period_table (sito, periodo, fase, datazione) VALUES (?,?,?,?)",
        ("Volterra", p, ph, dz),
    )

# 30 US distributed
us_records = []
for i in range(30):
    period, phase, _ = periods[i % 5]
    rapporti = f"copre {1000 + (i+1) % 30}" if i % 3 == 0 else ""
    us_records.append(
        ("Volterra", "A", 1000 + i, "US",
         f"strat {i}", f"interp {i}",
         f"100..200", None,
         rapporti, f"uuid-{i:03d}",
         period, phase, None, None)
    )
c.executemany(
    "INSERT INTO us_table (sito, area, us, unita_tipo, d_stratigrafica, d_interpretativa, datazione, file_path, rapporti, node_uuid, periodo_iniziale, fase_iniziale, periodo_finale, fase_finale) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
    us_records,
)

conn.commit()
conn.close()
print(f"Wrote {DB} (30 US, 5 periods)")

# Reference shape for SwimlaneState.load test
cytoscape = {
    "rows": [
        {"row_id": "row_late-antiquity_a", "period_name": "Late Antiquity", "phase_name": "a"},
        {"row_id": "row_medieval_a", "period_name": "Medieval", "phase_name": "a"},
        {"row_id": "row_medieval_b", "period_name": "Medieval", "phase_name": "b"},
        {"row_id": "row_roman_a", "period_name": "Roman", "phase_name": "a"},
        {"row_id": "row_roman_b", "period_name": "Roman", "phase_name": "b"},
    ],
    "nodes_count": 30,
    "edges_count_at_least": 5,
}
JSON_OUT.write_text(json.dumps(cytoscape, indent=2))
print(f"Wrote {JSON_OUT}")
