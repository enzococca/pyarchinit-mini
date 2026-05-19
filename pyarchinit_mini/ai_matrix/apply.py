"""Commit an AIPlan to the database: site auto-create, US dedupe, edge int guard."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import text

from pyarchinit_mini.ai_matrix.plan import AIPlan


VALID_UNIT_TYPES = {"USM", "USR", "US"}
VALID_REL_TYPES = {
    "copre", "coperto da",
    "taglia", "tagliato da",
    "riempie", "riempito da",
    "si appoggia", "gli si appoggia",
    "uguale a",
}


@dataclass
class ApplyResult:
    us_imported: int = 0
    us_skipped: int = 0
    edges_imported: int = 0
    edges_skipped: int = 0
    site_created: bool = False


def apply_ai_plan(plan: AIPlan, sito: str, db_session) -> ApplyResult:
    now = datetime.utcnow()
    result = ApplyResult()

    # Step 1: site_table auto-create
    existing = db_session.execute(
        text("SELECT sito FROM site_table WHERE sito = :s"), {"s": sito}
    ).fetchone()
    if not existing:
        db_session.execute(text("""
            INSERT INTO site_table (sito, descrizione, created_at, updated_at)
            VALUES (:sito, :desc, :now, :now)
        """), {"sito": sito, "desc": "Auto-creato da AI Matrix Import", "now": now})
        result.site_created = True

    # Step 2: us_table
    for u in plan.us:
        if not u.us_num or not u.area or not u.unit_type:
            result.us_skipped += 1
            continue
        unit_type = u.unit_type if u.unit_type in VALID_UNIT_TYPES else "US"
        existing_us = db_session.execute(
            text("SELECT us FROM us_table WHERE sito = :s AND us = :u"),
            {"s": sito, "u": u.us_num},
        ).fetchone()
        if existing_us:
            result.us_skipped += 1
            continue
        db_session.execute(text("""
            INSERT INTO us_table
                (sito, area, us, unita_tipo, descrizione,
                 fase_finale, fase_iniziale, created_at, updated_at)
            VALUES (:sito, :area, :us, :ut, :desc, :ffin, :fini, :now, :now)
        """), {
            "sito": sito, "area": u.area, "us": u.us_num, "ut": unit_type,
            "desc": u.descrizione,
            "ffin": str(u.fase_recente) if u.fase_recente is not None else None,
            "fini": str(u.fase_iniziale) if u.fase_iniziale is not None else None,
            "now": now,
        })
        result.us_imported += 1

    # Step 3: us_relationships_table
    # Schema: sito (single), us_from (int), us_to (int), relationship_type, created_at, updated_at
    for e in plan.edges:
        try:
            us_from = int(e.us_from)
            us_to = int(e.us_to)
        except (ValueError, TypeError):
            result.edges_skipped += 1
            continue
        if e.tipo not in VALID_REL_TYPES:
            result.edges_skipped += 1
            continue
        existing_rel = db_session.execute(text("""
            SELECT 1 FROM us_relationships_table
            WHERE sito = :s
              AND us_from = :uf AND us_to = :ut AND relationship_type = :t
        """), {"s": sito, "uf": us_from, "ut": us_to, "t": e.tipo}).fetchone()
        if existing_rel:
            result.edges_skipped += 1
            continue
        db_session.execute(text("""
            INSERT INTO us_relationships_table
                (sito, us_from, us_to, relationship_type,
                 created_at, updated_at)
            VALUES (:s, :uf, :ut, :t, :now, :now)
        """), {"s": sito, "uf": us_from, "ut": us_to, "t": e.tipo, "now": now})
        result.edges_imported += 1

    db_session.commit()
    return result
