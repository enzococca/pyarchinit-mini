"""Generate Harris GraphML from the synthetic DB using the CURRENT em_palette
(pre-Task 9 refactor). The output is the parity baseline that Task 9's
refactored em_palette must match for standard types (US, SU, WSU, USM)."""
import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.dom import minidom

from pyarchinit_mini.graphml_converter.graphml_builder import GraphMLBuilder

DB = Path(__file__).parent / "databases" / "sqlite_fully_migrated.db"
OUT = Path(__file__).parent / "graphml_outputs" / "synthetic_baseline_em_palette.graphml"
OUT.parent.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(DB)
rows = conn.execute("SELECT id_us, sito, us, unita_tipo FROM us_table ORDER BY id_us").fetchall()
conn.close()

builder = GraphMLBuilder()
builder.create_document(title="Synthetic Baseline Harris Matrix")
for id_us, sito, us, unita_tipo in rows:
    # Label format matches what production code uses: type + number
    label = f"{unita_tipo}{us}"
    builder.add_node(node_id=f"{sito}_{us}", label=label)

# Serialize directly via stdlib (builder.to_string has an import-name clash bug)
rough_string = ET.tostring(builder.root, encoding="utf-8")
xml_str = minidom.parseString(rough_string).toprettyxml(indent="  ", encoding="utf-8").decode("utf-8")
OUT.write_text(xml_str, encoding="utf-8")
print(f"Wrote {OUT} ({len(rows)} nodes)")
