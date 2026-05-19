"""Canonical rapporti reader/writer.

Reader accepts both legacy 2-tuple `[rel, us]` and new 4-tuple
`[rel, us, area, sito]`. Writer always emits 4-tuple list. Inverse pairs
for non-symmetric directional edges are declared here as a single source
of truth, used by both the s3dgraphy projector (deduplication on read)
and graph_to_db (write inverses on the OTHER US row during import).
"""
from __future__ import annotations

import ast
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

# Inverse canonicals that must be converted to their forward counterpart by
# swapping source and target.  Only directional (non-symmetric) inverses.
REVERSE_TO_FORWARD: Dict[str, str] = {
    "is_after": "overlies",
    "is_cut_by": "cuts",
    "is_filled_by": "fills",
    "is_abutted_by": "abuts",
}


logger = logging.getLogger(__name__)


# Symmetric edges: A↔B is the same as B↔A; one entry per pair.
SYMMETRIC = frozenset({"has_same_time", "is_bonded_to"})

# Directional pairs: relation → its inverse.
INVERSE_PAIRS: Dict[str, str] = {
    "overlies": "is_after",
    "is_after": "overlies",
    "cuts": "is_cut_by",
    "is_cut_by": "cuts",
    "fills": "is_filled_by",
    "is_filled_by": "fills",
    "abuts": "is_abutted_by",
    "is_abutted_by": "abuts",
    "is_before": "is_after",
}

# Italian aliases that are NOT in vocab_it.json (observed in live Adarte data
# on Rimini_RN_2020_21_Museo_Fellini).
_IT_EXTRAS: Dict[str, str] = {
    # Inverse directional aliases (will be swapped to forward by REVERSE_TO_FORWARD)
    "riempito da": "is_filled_by",   # was wrongly "is_after" — fixed
    "tagliato da": "is_cut_by",      # was missing
    "coperto da": "is_after",        # explicit fallback in case EdgeRegistry misses it
    # Symmetric / other
    "si lega a": "is_bonded_to",
    "si lega_a": "is_bonded_to",
    "connesso a": "is_bonded_to",
    "connesso_a": "is_bonded_to",
    "anteriore a": "is_before",
    "posteriore a": "is_after",
    "gli si appoggia": "is_abutted_by",  # was "is_before" — fixed to proper inverse
}

# Canonical → italian display label (for swimlane web + GraphML edge labels).
CANONICAL_TO_ITALIAN: Dict[str, str] = {
    "overlies": "Copre",
    "is_after": "Coperto da",
    "cuts": "Taglia",
    "is_cut_by": "Tagliato da",
    "fills": "Riempie",
    "is_filled_by": "Riempito da",
    "abuts": "Si appoggia a",
    "is_abutted_by": "Gli si appoggia",
    "has_same_time": "Uguale a",
    "is_bonded_to": "Si lega a",
    "is_before": "Anteriore a",
}

# Canonical → english display label.
CANONICAL_TO_ENGLISH: Dict[str, str] = {
    "overlies": "Covers",
    "is_after": "Covered by",
    "cuts": "Cuts",
    "is_cut_by": "Cut by",
    "fills": "Fills",
    "is_filled_by": "Filled by",
    "abuts": "Leans on",
    "is_abutted_by": "Leant on by",
    "has_same_time": "Same as",
    "is_bonded_to": "Bonded to",
    "is_before": "Before",
}


def display_label(canonical: str, locale: str = "it") -> str:
    """Return the localized display label for a canonical relation name."""
    if locale.lower().startswith("en"):
        return CANONICAL_TO_ENGLISH.get(canonical, canonical)
    return CANONICAL_TO_ITALIAN.get(canonical, canonical)


# English fallbacks (Al-Khutm-style data).
_EN_TO_CANONICAL: Dict[str, str] = {
    "covers": "overlies",
    "cuts": "cuts",
    "fills": "fills",
    "leans on": "abuts",
    "leans_on": "abuts",
    "equal to": "has_same_time",
    "equal_to": "has_same_time",
    "same as": "has_same_time",
    "continuity": "has_same_time",
    "bonds to": "is_bonded_to",
    "bonds_to": "is_bonded_to",
    "connected to": "is_bonded_to",
    "connected_to": "is_bonded_to",
    "covered by": "is_after",
    "covered_by": "is_after",
    "cut by": "is_cut_by",
    "cut_by": "is_cut_by",
}


@dataclass(frozen=True)
class Rapporto:
    canonical: str
    target_us: str
    target_area: Optional[str]
    target_sito: str

    @property
    def dedup_key(self) -> tuple:
        return (self.canonical, self.target_us, self.target_area or "", self.target_sito)


_REG = None


def _registry_singleton():
    global _REG
    if _REG is None:
        try:
            from pyarchinit_mini.graphproj.edge_registry import EdgeRegistry
            _REG = EdgeRegistry()
        except Exception as exc:
            logger.debug("EdgeRegistry unavailable: %s", exc)
            _REG = False  # mark as unavailable
    return _REG if _REG else None


def _resolve_canonical(label: str) -> Optional[str]:
    low = label.strip().lower()
    if not low:
        return None
    reg = _registry_singleton()
    if reg is not None:
        try:
            canon = reg.resolve_italian_alias(low)
            if canon:
                return canon
        except Exception as exc:
            logger.debug("resolve_italian_alias failed for %r: %s", low, exc)
    return _IT_EXTRAS.get(low) or _EN_TO_CANONICAL.get(low)


def parse_rapporti(raw: Optional[str], *, current_site: str) -> List[Rapporto]:
    """Parse the rapporti field. Accepts 2-tuple or 4-tuple list-of-lists."""
    if not raw or not raw.strip():
        return []
    try:
        parsed = ast.literal_eval(raw)
    except (SyntaxError, ValueError):
        logger.warning("rapporti malformed (literal_eval failed): %r", raw[:80])
        return []
    if not isinstance(parsed, (list, tuple)):
        return []
    out: List[Rapporto] = []
    for item in parsed:
        if not isinstance(item, (list, tuple)) or len(item) < 2:
            continue
        rel = str(item[0]).strip()
        target_us = str(item[1]).strip()
        target_area = (
            str(item[2]).strip()
            if len(item) >= 3 and item[2] not in (None, "")
            else None
        )
        target_sito = (
            str(item[3]).strip()
            if len(item) >= 4 and item[3] not in (None, "")
            else current_site
        )
        canonical = _resolve_canonical(rel)
        if not canonical or not target_us:
            continue
        out.append(Rapporto(canonical, target_us, target_area, target_sito))
    return out


def serialize_rapporti(
    items: List[Rapporto], *, italian_labels: Dict[str, str],
) -> str:
    """Serialize a list of Rapporto as a 4-tuple list-of-lists string.

    italian_labels maps canonical → italian display string.
    Dedups by (canonical, target_us, target_area, target_sito).
    """
    seen = set()
    rows: List[List[str]] = []
    for r in items:
        key = r.dedup_key
        if key in seen:
            continue
        seen.add(key)
        label = italian_labels.get(r.canonical, r.canonical)
        rows.append([label, r.target_us, r.target_area or "", r.target_sito])
    return repr(rows)
