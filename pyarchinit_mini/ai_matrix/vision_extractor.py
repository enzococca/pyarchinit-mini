"""Vision API extractor for Harris matrix images."""
from __future__ import annotations

import base64
import json
import os

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


MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10MB
API_TIMEOUT_S = 90


SYSTEM_PROMPT = """You are an expert in archaeological stratigraphy and Harris matrix diagrams.

Your task: analyze the attached image and determine if it depicts a Harris matrix (stratigraphic diagram). If yes, extract all stratigraphic units (US/SU) and their relationships.

A Harris matrix is a diagram with:
- Numbered rectangles/boxes (= stratigraphic units, US)
- Lines/arrows connecting them (= temporal relationships)
- Hierarchical layout: recent units on top, older on bottom

Vocabulary for unit_type:
- USM = muratura (masonry/wall)
- USR = revestimento (covering/coating)
- US  = stratigraphic deposit (default if ambiguous)

Vocabulary for edge tipo (Italian stratigraphic vocabulary):
- "copre"        = covers
- "taglia"       = cuts
- "riempie"      = fills
- "si appoggia"  = leans on
- "uguale a"     = same as

OUTPUT: strict JSON only, no markdown, no commentary. Schema:
{
  "is_harris_matrix": bool,
  "confidence": float 0..1,
  "reason": str,
  "detected_site": str | null,
  "detected_area": str | null,
  "us": [{"us_num": str, "area": str | null, "unit_type": str,
          "descrizione": str, "fase_recente": int, "fase_iniziale": int}],
  "edges": [{"us_from": str, "us_to": str, "tipo": str}]
}

If is_harris_matrix is false, return empty us and edges arrays and explain in 'reason' what you see instead."""


def _detect_media_type(image_bytes: bytes) -> str:
    """Return MIME type based on magic bytes. Defaults to PNG."""
    if image_bytes[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if image_bytes[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if image_bytes[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if image_bytes[:4] == b"RIFF" and image_bytes[8:12] == b"WEBP":
        return "image/webp"
    return "image/png"


def extract(image_bytes: bytes, text: str | None, provider: str) -> ExtractResult:
    """Send image to Vision API and return parsed ExtractResult.

    Args:
        image_bytes: raw image content (<=10MB)
        text: optional user-provided context
        provider: 'anthropic' or 'openai'
    """
    if len(image_bytes) > MAX_IMAGE_BYTES:
        return ExtractResult(
            rejected=True,
            reason="Immagine troppo grande (max 10MB)",
            confidence=0.0,
            plan=None,
        )
    if provider == "anthropic":
        raw = _call_anthropic_vision(image_bytes, text)
    elif provider == "openai":
        raw = _call_openai_vision(image_bytes, text)
    else:
        raise ValueError(f"unknown provider: {provider}")
    return _parse_response(raw)


def _call_anthropic_vision(image_bytes: bytes, text: str | None) -> str:
    try:
        import anthropic
    except ImportError:
        raise RuntimeError("Il package 'anthropic' non è installato. pip install anthropic")
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY non configurata")
    client = anthropic.Anthropic(api_key=api_key, timeout=API_TIMEOUT_S)
    response = client.messages.create(
        model="claude-sonnet-4-7",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {
                    "type": "base64",
                    "media_type": _detect_media_type(image_bytes),
                    "data": base64.b64encode(image_bytes).decode(),
                }},
                {"type": "text", "text": text or "Analyze the matrix."},
            ],
        }],
    )
    return response.content[0].text


def _call_openai_vision(image_bytes: bytes, text: str | None) -> str:
    try:
        import openai
    except ImportError:
        raise RuntimeError("Il package 'openai' non è installato. pip install openai")
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY non configurata")
    client = openai.OpenAI(api_key=api_key, timeout=API_TIMEOUT_S)
    media_type = _detect_media_type(image_bytes)
    response = client.chat.completions.create(
        model="gpt-5.5",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": [
                {"type": "image_url", "image_url": {
                    "url": f"data:{media_type};base64,{base64.b64encode(image_bytes).decode()}"
                }},
                {"type": "text", "text": text or "Analyze the matrix."},
            ]},
        ],
    )
    return response.choices[0].message.content
