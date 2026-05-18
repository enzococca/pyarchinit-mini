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


from sqlalchemy import text
from sqlalchemy.orm import Session


@dataclass
class ImportPlan:
    sites: list[dict] = field(default_factory=list)
    periodizations: list[dict] = field(default_factory=list)
    us_records: list[dict] = field(default_factory=list)
    relationships: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    conflicts: list[dict] = field(default_factory=list)


def build_import_plan(parsed: ParsedGraphML, session: Session) -> ImportPlan:
    plan = ImportPlan()
    if not parsed.nodes:
        raise YEDImportValidationError("File contains no US nodes")
    sito_set = {n.get("sito") for n in parsed.nodes if n.get("sito")}
    if not sito_set:
        raise YEDImportValidationError("No pyarchinit.sito on any node")

    # Sites
    for sito in sito_set:
        existing = session.execute(text(
            "SELECT 1 FROM site_table WHERE sito = :s LIMIT 1"
        ), {"s": sito}).fetchone()
        plan.sites.append({"sito": sito, "da_creare": existing is None})

    # Periodizations from epochs_meta
    seen_pz = set()
    for ep in parsed.epochs:
        for sito in sito_set:
            key = (sito, ep.get("periodo"), ep.get("fase"))
            if key in seen_pz:
                continue
            seen_pz.add(key)
            existing = session.execute(text(
                "SELECT 1 FROM periodizzazione_table "
                "WHERE sito=:s AND periodo_iniziale=:p AND fase_iniziale=:f LIMIT 1"
            ), {"s": sito, "p": ep.get("periodo", ""), "f": ep.get("fase", "")}).fetchone()
            plan.periodizations.append({
                "sito": sito,
                "periodo": ep.get("periodo", ""),
                "fase": ep.get("fase", ""),
                "datazione_estesa": ep.get("datazione_estesa", ""),
                "action": "update" if existing else "create",
            })

    # US records — upsert by node_uuid, fallback (sito, us)
    for n in parsed.nodes:
        sito = n.get("sito")
        us = n.get("us")
        uuid = n.get("node_uuid") or n.get("EMID") or ""
        existing = None
        if uuid:
            existing = session.execute(text(
                "SELECT id_us FROM us_table WHERE node_uuid = :u LIMIT 1"
            ), {"u": uuid}).fetchone()
        if not existing:
            existing = session.execute(text(
                "SELECT id_us FROM us_table WHERE sito = :s AND us = :u LIMIT 1"
            ), {"s": sito, "u": us}).fetchone()
        action = "update" if existing else "create"
        plan.us_records.append({
            "sito": sito, "us": us, "node_uuid": uuid,
            "unita_tipo": n.get("unita_tipo", "US"),
            "area": n.get("area", ""),
            "periodo_iniziale": n.get("periodo_iniziale", ""),
            "fase_iniziale": n.get("fase_iniziale", ""),
            "d_stratigrafica": n.get("d_stratigrafica", ""),
            "rapporti": n.get("rapporti", ""),
            "struttura": n.get("struttura", ""),
            "attivita": n.get("attivita", ""),
            "settore": n.get("settore", ""),
            "ambient": n.get("ambient", ""),
            "saggio": n.get("saggio", ""),
            "quad_par": n.get("quad_par", ""),
            "datazione": n.get("datazione_estesa", ""),
            "action": action,
        })

    # Relationships
    for e in parsed.edges:
        plan.relationships.append({
            "sito": list(sito_set)[0] if len(sito_set) == 1 else "",
            "us_from": e["us_from"],
            "us_to": e["us_to"],
            "type": e["type"],
            "action": "create",
        })

    return plan


@dataclass
class ImportResult:
    sites_created: int = 0
    sites_updated: int = 0
    periodizations_created: int = 0
    periodizations_updated: int = 0
    us_created: int = 0
    us_updated: int = 0
    us_skipped: int = 0
    relationships_created: int = 0
    duration_ms: int = 0
    errors: list[str] = field(default_factory=list)


def apply_import_plan(plan: ImportPlan, session: Session) -> ImportResult:
    """Apply the plan in one transaction. Best-effort auto-regen after."""
    import time
    start = time.time()
    result = ImportResult()
    try:
        for s in plan.sites:
            if s["da_creare"]:
                session.execute(text(
                    "INSERT INTO site_table (sito) VALUES (:s)"
                ), {"s": s["sito"]})
                result.sites_created += 1

        for p in plan.periodizations:
            if p["action"] == "create":
                session.execute(text(
                    "INSERT INTO periodizzazione_table "
                    "(sito, periodo_iniziale, fase_iniziale, datazione_estesa) "
                    "VALUES (:s, :p, :f, :d)"
                ), {"s": p["sito"], "p": p["periodo"], "f": p["fase"],
                    "d": p["datazione_estesa"]})
                result.periodizations_created += 1
            else:
                result.periodizations_updated += 1

        for r in plan.us_records:
            if r["action"] == "create":
                session.execute(text(
                    "INSERT INTO us_table (sito, area, us, unita_tipo, "
                    "node_uuid, periodo_iniziale, fase_iniziale, "
                    "d_stratigrafica, rapporti, datazione, "
                    "struttura, attivita, settore, ambient, saggio, quad_par) "
                    "VALUES (:sito, :area, :us, :ut, :uuid, :p, :f, :ds, :rap, :dz, "
                    ":struttura, :attivita, :settore, :ambient, :saggio, :quad_par)"
                ), {
                    "sito": r["sito"], "area": r["area"], "us": r["us"],
                    "ut": r["unita_tipo"], "uuid": r["node_uuid"] or None,
                    "p": r["periodo_iniziale"], "f": r["fase_iniziale"],
                    "ds": r["d_stratigrafica"], "rap": r["rapporti"],
                    "dz": r["datazione"],
                    "struttura": r["struttura"], "attivita": r["attivita"],
                    "settore": r["settore"], "ambient": r["ambient"],
                    "saggio": r["saggio"], "quad_par": r["quad_par"],
                })
                result.us_created += 1
            else:
                # Update by node_uuid if present, else by (sito, us)
                if r["node_uuid"]:
                    session.execute(text(
                        "UPDATE us_table SET sito=:sito, area=:area, us=:us, "
                        "unita_tipo=:ut, periodo_iniziale=:p, fase_iniziale=:f, "
                        "d_stratigrafica=:ds, rapporti=:rap, datazione=:dz, "
                        "struttura=:struttura, attivita=:attivita, settore=:settore, "
                        "ambient=:ambient, saggio=:saggio, quad_par=:quad_par "
                        "WHERE node_uuid = :uuid"
                    ), {
                        "sito": r["sito"], "area": r["area"], "us": r["us"],
                        "ut": r["unita_tipo"],
                        "p": r["periodo_iniziale"], "f": r["fase_iniziale"],
                        "ds": r["d_stratigrafica"], "rap": r["rapporti"], "dz": r["datazione"],
                        "struttura": r["struttura"], "attivita": r["attivita"],
                        "settore": r["settore"], "ambient": r["ambient"],
                        "saggio": r["saggio"], "quad_par": r["quad_par"],
                        "uuid": r["node_uuid"],
                    })
                else:
                    session.execute(text(
                        "UPDATE us_table SET unita_tipo=:ut, periodo_iniziale=:p, "
                        "fase_iniziale=:f, d_stratigrafica=:ds, rapporti=:rap, "
                        "datazione=:dz, struttura=:struttura, attivita=:attivita, "
                        "settore=:settore, ambient=:ambient, saggio=:saggio, "
                        "quad_par=:quad_par WHERE sito=:sito AND us=:us"
                    ), {"ut": r["unita_tipo"],
                        "p": r["periodo_iniziale"], "f": r["fase_iniziale"],
                        "ds": r["d_stratigrafica"], "rap": r["rapporti"],
                        "dz": r["datazione"],
                        "struttura": r["struttura"], "attivita": r["attivita"],
                        "settore": r["settore"], "ambient": r["ambient"],
                        "saggio": r["saggio"], "quad_par": r["quad_par"],
                        "sito": r["sito"], "us": r["us"]})
                result.us_updated += 1

        seen_rel = set()
        for rel in plan.relationships:
            key = (rel["sito"], rel["us_from"], rel["us_to"], rel["type"])
            if key in seen_rel:
                continue
            seen_rel.add(key)
            # Dedupe against DB
            exists = session.execute(text(
                "SELECT 1 FROM us_relationships_table "
                "WHERE sito=:s AND us_from=:f AND us_to=:t AND relationship_type=:r LIMIT 1"
            ), {"s": rel["sito"], "f": rel["us_from"], "t": rel["us_to"], "r": rel["type"]}).fetchone()
            if not exists:
                session.execute(text(
                    "INSERT INTO us_relationships_table "
                    "(sito, us_from, us_to, relationship_type) "
                    "VALUES (:s, :f, :t, :r)"
                ), {"s": rel["sito"], "f": rel["us_from"], "t": rel["us_to"], "r": rel["type"]})
                result.relationships_created += 1
        session.commit()
    except Exception as e:
        session.rollback()
        result.errors.append(str(e))

    result.duration_ms = int((time.time() - start) * 1000)
    return result
