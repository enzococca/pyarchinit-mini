"""Vision API extractor for Harris matrix images."""
from __future__ import annotations

import json

from pyarchinit_mini.ai_matrix.plan import AIPlan, USRow, EdgeRow, ExtractResult


CONFIDENCE_THRESHOLD = 0.7


def _parse_response(raw: str) -> ExtractResult:
    """Parse the AI's JSON response into an ExtractResult.

    Applies the validation gate: rejects non-matrix images and low-confidence
    results before constructing an AIPlan.
    """
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        return ExtractResult(
            rejected=True,
            reason=f"AI returned non-JSON response: {e}",
            confidence=0.0,
            plan=None,
        )

    try:
        confidence = float(data.get("confidence", 0.0))
        is_matrix = bool(data.get("is_harris_matrix", False))

        if not is_matrix or confidence < CONFIDENCE_THRESHOLD:
            return ExtractResult(
                rejected=True,
                reason=data.get("reason", "Immagine non riconosciuta come Harris matrix"),
                confidence=confidence,
                plan=None,
            )

        plan = AIPlan(
            detected_site=data.get("detected_site"),
            detected_area=data.get("detected_area"),
            us=[USRow(
                us_num=str(u.get("us_num", "")),
                area=u.get("area"),
                unit_type=str(u.get("unit_type", "US")),
                descrizione=str(u.get("descrizione", "")),
                fase_recente=int(u.get("fase_recente", 1)),
                fase_iniziale=int(u.get("fase_iniziale", 1)),
            ) for u in data.get("us", [])],
            edges=[EdgeRow(
                us_from=str(edge_e.get("us_from", "")),
                us_to=str(edge_e.get("us_to", "")),
                tipo=str(edge_e.get("tipo", "")),
            ) for edge_e in data.get("edges", [])],
        )
        return ExtractResult(rejected=False, reason="OK", confidence=confidence, plan=plan)
    except (ValueError, TypeError) as e:
        return ExtractResult(
            rejected=True,
            reason=f"AI returned malformed values: {e}",
            confidence=0.0,
            plan=None,
        )
