"""yEd GraphML importer for pyarchinit Extended Matrix files.

Pipeline:
  1. parse_extended_matrix(path) -> ParsedGraphML (raw extraction)
  2. build_import_plan(parsed, session) -> ImportPlan (DB diff)
  3. apply_import_plan(plan, session) -> ImportResult (commit)
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from lxml import etree

from pyarchinit_mini.harris_swimlane.exceptions import (
    YEDImporterError, YEDImportValidationError,
)
from pyarchinit_mini.graphml_io.yed_keys import KEY_BY_ATTR_NAME, US_NODE_FIELDS


@dataclass
class ParsedGraphML:
    epochs: list[dict] = field(default_factory=list)
    nodes: list[dict] = field(default_factory=list)
    edges: list[dict] = field(default_factory=list)


NS = {
    "g": "http://graphml.graphdrawing.org/xmlns",
    "y": "http://www.yworks.com/xml/graphml",
}


def parse_extended_matrix(path: Path) -> ParsedGraphML:
    """Parse a pyarchinit Extended Matrix yEd GraphML file.

    Raises YEDImporterError if the file is malformed or not pyarchinit-shaped.
    """
    path = Path(path)
    try:
        tree = etree.parse(str(path))
    except etree.XMLSyntaxError as e:
        raise YEDImporterError(f"malformed XML: {e}") from e

    root = tree.getroot()
    # Build attr_name -> key_id map by reading <key> elements.
    key_attr_to_id: dict[str, str] = {}
    key_id_to_attr: dict[str, str] = {}
    for k in root.findall("g:key", NS):
        kid = k.get("id")
        attr = k.get("attr.name")
        if kid and attr:
            key_attr_to_id[attr] = kid
            key_id_to_attr[kid] = attr

    # Validate: must have at least pyarchinit.us key declared.
    if "pyarchinit.us" not in key_attr_to_id:
        raise YEDImporterError("not a pyarchinit Extended Matrix file (no pyarchinit.us key)")

    parsed = ParsedGraphML()

    # Graph-level data (epochs_meta).
    graphs = root.findall(".//g:graph", NS)
    for g in graphs:
        for d in g.findall("g:data", NS):
            if d.get("key") == key_attr_to_id.get("pyarchinit.epochs_meta"):
                txt = (d.text or "").strip()
                if txt:
                    try:
                        parsed.epochs = json.loads(txt)
                    except json.JSONDecodeError:
                        pass  # warning will surface in build_import_plan
                break

    # Node-level data -- index node_id -> us_number for later edge mapping.
    node_id_to_us: dict[str, str] = {}
    for n in root.findall(".//g:node", NS):
        node_id = n.get("id", "")
        rec: dict = {"_node_id": node_id}
        for d in n.findall("g:data", NS):
            kid = d.get("key", "")
            attr = key_id_to_attr.get(kid)
            if not attr:
                continue
            if attr.startswith("pyarchinit."):
                short = attr.split("pyarchinit.", 1)[1]
                rec[short] = (d.text or "").strip()
            elif attr == "EMID":
                rec.setdefault("node_uuid", (d.text or "").strip())
        # Only nodes with pyarchinit.us are stratigraphic US records.
        if rec.get("us"):
            parsed.nodes.append(rec)
            node_id_to_us[node_id] = rec["us"]

    # Edges -- only those connecting recognised US nodes.
    for e in root.findall(".//g:edge", NS):
        src = e.get("source", "")
        tgt = e.get("target", "")
        us_from = node_id_to_us.get(src)
        us_to = node_id_to_us.get(tgt)
        if not us_from or not us_to:
            continue
        rel = ""
        for d in e.findall("g:data", NS):
            kid = d.get("key", "")
            attr = key_id_to_attr.get(kid, "")
            if attr == "description":
                rel = (d.text or "").strip()
                break
        parsed.edges.append({
            "us_from": us_from, "us_to": us_to, "type": rel,
        })

    return parsed
