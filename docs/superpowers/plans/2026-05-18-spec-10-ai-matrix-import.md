# Spec 10 — AI Matrix Import Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a `/matrix-import/` web flow that accepts an image of a Harris matrix, sends it to a Vision API (Claude Sonnet 4.7 or GPT-5.5), validates that it really is a matrix, and lets the user review and commit extracted US + relationships into `us_table` and `us_relationships_table`.

**Architecture:** New `pyarchinit_mini/ai_matrix/` package with extractor + apply, new `matrix_import_routes` Flask blueprint with 3 endpoints, 3 Jinja templates, source image stored via existing `MediaService.store_and_register_media`. Plan→preview→apply pattern with hidden JSON field, like the yEd importer (Spec 7).

**Tech Stack:** Python 3.12, Flask 2.x, SQLAlchemy 2.x (raw `text()` queries with named params), Anthropic SDK ≥0.18, OpenAI SDK ≥1.0, pytest. Branch: `feat/spec-10-ai-matrix-import` (already created).

**Reference:** Spec at `docs/superpowers/specs/2026-05-18-spec-10-ai-matrix-import-design.md`.

---

## File map

| Path | Status | Purpose |
|---|---|---|
| `pyarchinit_mini/ai_matrix/__init__.py` | create | package marker |
| `pyarchinit_mini/ai_matrix/plan.py` | create | dataclasses `USRow`, `EdgeRow`, `AIPlan`, `ExtractResult` |
| `pyarchinit_mini/ai_matrix/vision_extractor.py` | create | `extract()` + `_parse_response()` + provider calls |
| `pyarchinit_mini/ai_matrix/apply.py` | create | `apply_ai_plan()` with site auto-create, dedupe, int guard |
| `pyarchinit_mini/web_interface/matrix_import_routes.py` | create | Blueprint with 3 endpoints |
| `pyarchinit_mini/web_interface/templates/matrix_import/upload.html` | create | Upload form |
| `pyarchinit_mini/web_interface/templates/matrix_import/preview.html` | create | Editable preview tables |
| `pyarchinit_mini/web_interface/templates/matrix_import/rejected.html` | create | Rejection page |
| `pyarchinit_mini/web_interface/app.py` | modify | Register blueprint + `csrf.exempt` |
| `pyarchinit_mini/web_interface/templates/base.html` | modify | Add navbar link |
| `pyarchinit_mini/__init__.py` | modify | Version bump 2.6.0 → 2.7.0 |
| `pyproject.toml` | modify | Version bump 2.6.0 → 2.7.0 |
| `CHANGELOG.md` | modify | Add 2.7.0 entry IT+EN |
| `tests/unit/test_ai_matrix_plan_serialization.py` | create | AIPlan.as_dict/from_dict round-trip |
| `tests/unit/test_ai_matrix_extractor_parse.py` | create | `_parse_response` happy + sad paths |
| `tests/unit/test_ai_matrix_extractor_providers.py` | create | Provider routing + error paths |
| `tests/unit/test_ai_matrix_apply.py` | create | `apply_ai_plan` logic |
| `tests/integration/test_matrix_import_upload_route.py` | create | POST /upload with mocked AI |
| `tests/integration/test_matrix_import_rejected_route.py` | create | Rejection rendering |
| `tests/integration/test_matrix_import_apply_route.py` | create | POST /apply → DB commit |
| `tests/integration/test_matrix_import_site_widget.py` | create | Site widget for missing site |

---

## Task 1: AIPlan dataclasses + serialization

**Files:**
- Create: `pyarchinit_mini/ai_matrix/__init__.py`
- Create: `pyarchinit_mini/ai_matrix/plan.py`
- Test: `tests/unit/test_ai_matrix_plan_serialization.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_ai_matrix_plan_serialization.py
"""Round-trip serialization tests for AIPlan dataclasses."""
import pytest

from pyarchinit_mini.ai_matrix.plan import USRow, EdgeRow, AIPlan, ExtractResult


def test_aiplan_round_trip_empty():
    plan = AIPlan(detected_site=None, detected_area=None, us=[], edges=[])
    d = plan.as_dict()
    assert d == {"detected_site": None, "detected_area": None, "us": [], "edges": []}
    assert AIPlan.from_dict(d) == plan


def test_aiplan_round_trip_full():
    plan = AIPlan(
        detected_site="Foro Boario",
        detected_area="Saggio 3",
        us=[USRow(us_num="11a", area="Saggio 3", unit_type="USM",
                  descrizione="Muratura", fase_recente=1, fase_iniziale=1)],
        edges=[EdgeRow(us_from="11a", us_to="12", tipo="copre")],
    )
    d = plan.as_dict()
    assert d["us"][0]["us_num"] == "11a"
    assert d["edges"][0]["tipo"] == "copre"
    assert AIPlan.from_dict(d) == plan


def test_extract_result_rejected_has_no_plan():
    r = ExtractResult(rejected=True, reason="not a matrix", confidence=0.1, plan=None)
    assert r.rejected is True
    assert r.plan is None


def test_extract_result_accepted_has_plan():
    plan = AIPlan(detected_site=None, detected_area=None, us=[], edges=[])
    r = ExtractResult(rejected=False, reason="OK", confidence=0.9, plan=plan)
    assert r.rejected is False
    assert r.plan == plan
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/unit/test_ai_matrix_plan_serialization.py -v`
Expected: `ModuleNotFoundError: No module named 'pyarchinit_mini.ai_matrix'`

- [ ] **Step 3: Create package marker**

```python
# pyarchinit_mini/ai_matrix/__init__.py
"""AI Matrix Import — Vision API based stratigraphic matrix extraction."""
```

- [ ] **Step 4: Implement dataclasses**

```python
# pyarchinit_mini/ai_matrix/plan.py
"""Dataclasses for AI Matrix Import plan + extraction results."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict


@dataclass
class USRow:
    us_num: str
    area: str | None
    unit_type: str
    descrizione: str
    fase_recente: int
    fase_iniziale: int


@dataclass
class EdgeRow:
    us_from: str
    us_to: str
    tipo: str


@dataclass
class AIPlan:
    detected_site: str | None
    detected_area: str | None
    us: list[USRow] = field(default_factory=list)
    edges: list[EdgeRow] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "detected_site": self.detected_site,
            "detected_area": self.detected_area,
            "us": [asdict(u) for u in self.us],
            "edges": [asdict(e) for e in self.edges],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "AIPlan":
        return cls(
            detected_site=d.get("detected_site"),
            detected_area=d.get("detected_area"),
            us=[USRow(**u) for u in d.get("us", [])],
            edges=[EdgeRow(**e) for e in d.get("edges", [])],
        )


@dataclass
class ExtractResult:
    rejected: bool
    reason: str
    confidence: float
    plan: AIPlan | None
```

- [ ] **Step 5: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/unit/test_ai_matrix_plan_serialization.py -v`
Expected: 4 PASSED

- [ ] **Step 6: Commit**

```bash
git add pyarchinit_mini/ai_matrix/__init__.py pyarchinit_mini/ai_matrix/plan.py tests/unit/test_ai_matrix_plan_serialization.py
git commit -m "feat(spec10): ai_matrix.plan dataclasses + round-trip serialization"
```

---

## Task 2: vision_extractor `_parse_response` (validation gate)

**Files:**
- Create: `pyarchinit_mini/ai_matrix/vision_extractor.py`
- Test: `tests/unit/test_ai_matrix_extractor_parse.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_ai_matrix_extractor_parse.py
"""Tests for vision_extractor._parse_response — validation gate + JSON parsing."""
import json
import pytest

from pyarchinit_mini.ai_matrix.vision_extractor import _parse_response


def _ok_payload(**overrides):
    base = {
        "is_harris_matrix": True,
        "confidence": 0.9,
        "reason": "OK",
        "detected_site": "Test",
        "detected_area": None,
        "us": [{"us_num": "1", "area": "A", "unit_type": "US",
                "descrizione": "x", "fase_recente": 1, "fase_iniziale": 1}],
        "edges": [{"us_from": "1", "us_to": "2", "tipo": "copre"}],
    }
    base.update(overrides)
    return json.dumps(base)


def test_parse_valid_json_returns_accepted_result():
    r = _parse_response(_ok_payload())
    assert r.rejected is False
    assert r.confidence == 0.9
    assert r.plan is not None
    assert len(r.plan.us) == 1
    assert r.plan.us[0].us_num == "1"
    assert r.plan.edges[0].tipo == "copre"


def test_parse_rejects_when_not_harris_matrix():
    r = _parse_response(_ok_payload(is_harris_matrix=False, reason="Foto di un muro"))
    assert r.rejected is True
    assert "muro" in r.reason
    assert r.plan is None


def test_parse_rejects_low_confidence():
    r = _parse_response(_ok_payload(confidence=0.5))
    assert r.rejected is True
    assert r.confidence == 0.5
    assert r.plan is None


def test_parse_rejects_invalid_json():
    r = _parse_response("not valid json {{{")
    assert r.rejected is True
    assert "non-JSON" in r.reason or "JSON" in r.reason
    assert r.plan is None


def test_parse_handles_missing_fields_gracefully():
    minimal = json.dumps({"is_harris_matrix": True, "confidence": 0.8})
    r = _parse_response(minimal)
    assert r.rejected is False
    assert r.plan.us == []
    assert r.plan.edges == []
    assert r.plan.detected_site is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/unit/test_ai_matrix_extractor_parse.py -v`
Expected: `ModuleNotFoundError` or `ImportError: cannot import _parse_response`

- [ ] **Step 3: Implement `_parse_response`**

```python
# pyarchinit_mini/ai_matrix/vision_extractor.py
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
            us_from=str(e.get("us_from", "")),
            us_to=str(e.get("us_to", "")),
            tipo=str(e.get("tipo", "")),
        ) for e in data.get("edges", [])],
    )
    return ExtractResult(rejected=False, reason="OK", confidence=confidence, plan=plan)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/unit/test_ai_matrix_extractor_parse.py -v`
Expected: 5 PASSED

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/ai_matrix/vision_extractor.py tests/unit/test_ai_matrix_extractor_parse.py
git commit -m "feat(spec10): vision_extractor._parse_response with validation gate"
```

---

## Task 3: vision_extractor `extract()` + provider routing

**Files:**
- Modify: `pyarchinit_mini/ai_matrix/vision_extractor.py`
- Test: `tests/unit/test_ai_matrix_extractor_providers.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_ai_matrix_extractor_providers.py
"""Tests for vision_extractor.extract() — provider routing and error paths."""
import os
import json
import pytest

from pyarchinit_mini.ai_matrix.vision_extractor import extract


def test_extract_unknown_provider_raises():
    with pytest.raises(ValueError, match="unknown provider"):
        extract(b"fake bytes", None, "gemini")


def test_extract_oversized_image_rejected():
    big = b"x" * (11 * 1024 * 1024)  # 11MB
    r = extract(big, None, "anthropic")
    assert r.rejected is True
    assert "10MB" in r.reason or "troppo grande" in r.reason


def test_extract_anthropic_missing_key_raises(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        extract(b"\x89PNG\r\n\x1a\n" + b"x" * 100, None, "anthropic")


def test_extract_openai_missing_key_raises(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        extract(b"\x89PNG\r\n\x1a\n" + b"x" * 100, None, "openai")


def test_extract_anthropic_call_with_mock(monkeypatch):
    """End-to-end with mocked anthropic client."""
    fake_payload = json.dumps({
        "is_harris_matrix": True,
        "confidence": 0.9,
        "reason": "OK",
        "detected_site": "S1",
        "detected_area": None,
        "us": [{"us_num": "1", "area": "A", "unit_type": "US",
                "descrizione": "test", "fase_recente": 1, "fase_iniziale": 1}],
        "edges": [],
    })

    class FakeContent:
        def __init__(self, text): self.text = text
    class FakeResponse:
        content = [FakeContent(fake_payload)]
    class FakeMessages:
        def create(self, **kw): return FakeResponse()
    class FakeClient:
        def __init__(self, **kw): self.messages = FakeMessages()

    import anthropic
    monkeypatch.setattr(anthropic, "Anthropic", FakeClient)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")

    r = extract(b"\x89PNG\r\n\x1a\n" + b"x" * 100, "context text", "anthropic")
    assert r.rejected is False
    assert r.plan.detected_site == "S1"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/unit/test_ai_matrix_extractor_providers.py -v`
Expected: `ImportError: cannot import name 'extract'`

- [ ] **Step 3: Add extract() + provider calls + media type detection**

Append to `pyarchinit_mini/ai_matrix/vision_extractor.py`:

```python
import base64
import os


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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/unit/test_ai_matrix_extractor_providers.py -v`
Expected: 5 PASSED

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/ai_matrix/vision_extractor.py tests/unit/test_ai_matrix_extractor_providers.py
git commit -m "feat(spec10): vision_extractor.extract() with anthropic+openai routing"
```

---

## Task 4: apply.py — `apply_ai_plan` with site auto-create, dedupe, audit cols

**Files:**
- Create: `pyarchinit_mini/ai_matrix/apply.py`
- Test: `tests/unit/test_ai_matrix_apply.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_ai_matrix_apply.py
"""Tests for ai_matrix.apply.apply_ai_plan."""
from datetime import datetime
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.ai_matrix.plan import AIPlan, USRow, EdgeRow
from pyarchinit_mini.ai_matrix.apply import apply_ai_plan


@pytest.fixture
def db_session(tmp_path):
    """Sqlite session with the minimal schema apply_ai_plan needs."""
    db_path = tmp_path / "test.db"
    engine = create_engine(f"sqlite:///{db_path}")
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE site_table (
                id_sito INTEGER PRIMARY KEY AUTOINCREMENT,
                sito TEXT UNIQUE NOT NULL,
                descrizione TEXT,
                created_at DATETIME,
                updated_at DATETIME
            )
        """))
        conn.execute(text("""
            CREATE TABLE us_table (
                id_us INTEGER PRIMARY KEY AUTOINCREMENT,
                sito TEXT NOT NULL,
                area TEXT NOT NULL,
                us TEXT NOT NULL,
                unita_tipo TEXT,
                d_stratigrafica TEXT,
                fase_recente INTEGER,
                fase_iniziale INTEGER,
                created_at DATETIME,
                updated_at DATETIME
            )
        """))
        conn.execute(text("""
            CREATE TABLE us_relationships_table (
                id_rel INTEGER PRIMARY KEY AUTOINCREMENT,
                sito_from TEXT,
                sito_to TEXT,
                us_from INTEGER,
                us_to INTEGER,
                tipo_relazione TEXT,
                created_at DATETIME,
                updated_at DATETIME
            )
        """))
    Session = sessionmaker(bind=engine)
    s = Session()
    yield s
    s.close()


def _make_plan(us_rows=None, edges=None):
    return AIPlan(
        detected_site=None, detected_area=None,
        us=us_rows or [], edges=edges or [],
    )


def test_apply_creates_site_when_new(db_session):
    plan = _make_plan(us_rows=[USRow("1", "A", "USM", "x", 1, 1)])
    result = apply_ai_plan(plan, "NewSite", db_session)
    assert result.site_created is True
    row = db_session.execute(text("SELECT sito FROM site_table")).fetchone()
    assert row[0] == "NewSite"


def test_apply_does_not_recreate_existing_site(db_session):
    db_session.execute(text(
        "INSERT INTO site_table (sito, created_at, updated_at) VALUES ('S', :n, :n)"
    ), {"n": datetime.utcnow()})
    db_session.commit()
    plan = _make_plan(us_rows=[USRow("1", "A", "USM", "x", 1, 1)])
    result = apply_ai_plan(plan, "S", db_session)
    assert result.site_created is False


def test_apply_imports_us_with_audit_cols(db_session):
    plan = _make_plan(us_rows=[USRow("11a", "Area1", "USM", "Muro", 1, 1)])
    result = apply_ai_plan(plan, "S", db_session)
    assert result.us_imported == 1
    row = db_session.execute(text(
        "SELECT us, area, unita_tipo, created_at FROM us_table WHERE sito = 'S'"
    )).fetchone()
    assert row[0] == "11a"
    assert row[1] == "Area1"
    assert row[2] == "USM"
    assert row[3] is not None  # audit col populated


def test_apply_skips_duplicate_us(db_session):
    plan1 = _make_plan(us_rows=[USRow("1", "A", "USM", "x", 1, 1)])
    apply_ai_plan(plan1, "S", db_session)
    plan2 = _make_plan(us_rows=[USRow("1", "A", "US", "y", 2, 2)])
    result = apply_ai_plan(plan2, "S", db_session)
    assert result.us_imported == 0
    assert result.us_skipped == 1


def test_apply_skips_us_missing_mandatory_fields(db_session):
    plan = _make_plan(us_rows=[
        USRow("", "A", "USM", "x", 1, 1),       # missing us_num
        USRow("1", None, "USM", "x", 1, 1),     # missing area
        USRow("2", "A", "", "x", 1, 1),         # missing unit_type
        USRow("3", "A", "USM", "x", 1, 1),      # valid
    ])
    result = apply_ai_plan(plan, "S", db_session)
    assert result.us_imported == 1
    assert result.us_skipped == 3


def test_apply_coerces_unknown_unit_type_to_us(db_session):
    plan = _make_plan(us_rows=[USRow("1", "A", "XYZ", "x", 1, 1)])
    apply_ai_plan(plan, "S", db_session)
    row = db_session.execute(text("SELECT unita_tipo FROM us_table")).fetchone()
    assert row[0] == "US"


def test_apply_imports_int_edges(db_session):
    plan = _make_plan(edges=[EdgeRow("1", "2", "copre")])
    result = apply_ai_plan(plan, "S", db_session)
    assert result.edges_imported == 1
    row = db_session.execute(text(
        "SELECT us_from, us_to, tipo_relazione FROM us_relationships_table"
    )).fetchone()
    assert row[0] == 1 and row[1] == 2 and row[2] == "copre"


def test_apply_skips_non_numeric_edges(db_session):
    plan = _make_plan(edges=[
        EdgeRow("11a", "12", "copre"),   # us_from non-int
        EdgeRow("1", "abc", "copre"),    # us_to non-int
        EdgeRow("1", "2", "copre"),      # valid
    ])
    result = apply_ai_plan(plan, "S", db_session)
    assert result.edges_imported == 1
    assert result.edges_skipped == 2


def test_apply_skips_unknown_tipo(db_session):
    plan = _make_plan(edges=[
        EdgeRow("1", "2", "invented_relation"),
        EdgeRow("1", "2", "copre"),
    ])
    result = apply_ai_plan(plan, "S", db_session)
    assert result.edges_imported == 1
    assert result.edges_skipped == 1


def test_apply_skips_duplicate_edges(db_session):
    plan1 = _make_plan(edges=[EdgeRow("1", "2", "copre")])
    apply_ai_plan(plan1, "S", db_session)
    plan2 = _make_plan(edges=[EdgeRow("1", "2", "copre")])
    result = apply_ai_plan(plan2, "S", db_session)
    assert result.edges_imported == 0
    assert result.edges_skipped == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/unit/test_ai_matrix_apply.py -v`
Expected: `ImportError: cannot import 'apply_ai_plan'`

- [ ] **Step 3: Implement apply_ai_plan**

```python
# pyarchinit_mini/ai_matrix/apply.py
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
                (sito, area, us, unita_tipo, d_stratigrafica,
                 fase_recente, fase_iniziale, created_at, updated_at)
            VALUES (:sito, :area, :us, :ut, :desc, :fr, :fi, :now, :now)
        """), {
            "sito": sito, "area": u.area, "us": u.us_num, "ut": unit_type,
            "desc": u.descrizione, "fr": u.fase_recente, "fi": u.fase_iniziale,
            "now": now,
        })
        result.us_imported += 1

    # Step 3: us_relationships_table
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
            WHERE sito_from = :s AND sito_to = :s
              AND us_from = :uf AND us_to = :ut AND tipo_relazione = :t
        """), {"s": sito, "uf": us_from, "ut": us_to, "t": e.tipo}).fetchone()
        if existing_rel:
            result.edges_skipped += 1
            continue
        db_session.execute(text("""
            INSERT INTO us_relationships_table
                (sito_from, sito_to, us_from, us_to, tipo_relazione,
                 created_at, updated_at)
            VALUES (:s, :s, :uf, :ut, :t, :now, :now)
        """), {"s": sito, "uf": us_from, "ut": us_to, "t": e.tipo, "now": now})
        result.edges_imported += 1

    db_session.commit()
    return result
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/unit/test_ai_matrix_apply.py -v`
Expected: 10 PASSED

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/ai_matrix/apply.py tests/unit/test_ai_matrix_apply.py
git commit -m "feat(spec10): ai_matrix.apply_ai_plan with site auto-create + dedupe"
```

---

## Task 5: matrix_import_routes blueprint + GET / endpoint

**Files:**
- Create: `pyarchinit_mini/web_interface/matrix_import_routes.py`
- Modify: `pyarchinit_mini/web_interface/app.py`
- Test: `tests/integration/test_matrix_import_upload_route.py` (just the GET part for now)

- [ ] **Step 1: Write the failing test (GET / only — preview tests come in Task 6)**

```python
# tests/integration/test_matrix_import_upload_route.py
"""Integration tests for /matrix-import/ endpoints."""
import io
import json
from pathlib import Path
import pytest

from flask import Flask
from jinja2 import ChoiceLoader, FileSystemLoader

from pyarchinit_mini.web_interface.matrix_import_routes import matrix_import_bp


_APP_TEMPLATES = Path(__file__).parent.parent.parent / "pyarchinit_mini" / "web_interface" / "templates"


@pytest.fixture
def client(tmp_path, monkeypatch):
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    db_path = tmp_path / "mi.db"
    engine = create_engine(f"sqlite:///{db_path}")
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE site_table (
                id_sito INTEGER PRIMARY KEY AUTOINCREMENT,
                sito TEXT UNIQUE NOT NULL,
                descrizione TEXT,
                created_at DATETIME, updated_at DATETIME)
        """))
        conn.execute(text("""
            CREATE TABLE us_table (
                id_us INTEGER PRIMARY KEY AUTOINCREMENT,
                sito TEXT, area TEXT, us TEXT, unita_tipo TEXT,
                d_stratigrafica TEXT, fase_recente INT, fase_iniziale INT,
                created_at DATETIME, updated_at DATETIME)
        """))
        conn.execute(text("""
            CREATE TABLE us_relationships_table (
                id_rel INTEGER PRIMARY KEY AUTOINCREMENT,
                sito_from TEXT, sito_to TEXT, us_from INT, us_to INT,
                tipo_relazione TEXT, created_at DATETIME, updated_at DATETIME)
        """))
        conn.execute(text(
            "INSERT INTO site_table (sito, created_at, updated_at) VALUES ('ExistingSite', :n, :n)"
        ), {"n": "2026-01-01"})
    Session = sessionmaker(bind=engine)

    app = Flask(__name__, template_folder=str(_APP_TEMPLATES))
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test"
    app.jinja_env.globals.setdefault("_", lambda s: s)
    app.jinja_env.globals.setdefault("get_locale", lambda: "it")
    app.jinja_env.globals.setdefault("csrf_token", lambda: "test-csrf")
    app.jinja_env.globals.setdefault("url_for", app.jinja_env.globals.get("url_for", lambda *a, **k: "/"))

    @app.before_request
    def _attach_session():
        from flask import g
        g.db_session = Session()

    app.register_blueprint(matrix_import_bp)
    yield app.test_client()


def test_get_index_renders_with_sites(client):
    r = client.get("/matrix-import/")
    assert r.status_code == 200
    body = r.get_data(as_text=True)
    assert "ExistingSite" in body
    assert "matrix" in body.lower() or "AI" in body
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv/bin/python -m pytest tests/integration/test_matrix_import_upload_route.py::test_get_index_renders_with_sites -v`
Expected: `ImportError: cannot import name 'matrix_import_bp'` or template not found

- [ ] **Step 3: Create blueprint with GET / and upload template**

Create `pyarchinit_mini/web_interface/matrix_import_routes.py`:

```python
"""Flask blueprint for the AI Matrix Import flow."""
from __future__ import annotations

import base64
import json
import os

from flask import (
    Blueprint, request, render_template, redirect, url_for,
    flash, g, current_app,
)
from sqlalchemy import text

from pyarchinit_mini.ai_matrix.vision_extractor import extract
from pyarchinit_mini.ai_matrix.plan import AIPlan
from pyarchinit_mini.ai_matrix.apply import apply_ai_plan


matrix_import_bp = Blueprint(
    "matrix_import",
    __name__,
    url_prefix="/matrix-import",
)


@matrix_import_bp.route("/")
def upload_form():
    sites = g.db_session.execute(
        text("SELECT sito FROM site_table ORDER BY sito")
    ).fetchall()
    return render_template(
        "matrix_import/upload.html",
        sites=[r[0] for r in sites],
        default_provider=os.environ.get("AI_PROVIDER", "anthropic"),
    )
```

Create `pyarchinit_mini/web_interface/templates/matrix_import/upload.html`:

```html
<!DOCTYPE html>
<html lang="{{ get_locale() }}">
<head>
  <meta charset="UTF-8">
  <title>AI Matrix Import</title>
</head>
<body>
  <h1>AI Matrix Import</h1>
  <p>Carica un'immagine di un Harris Matrix e l'AI estrarrà le US e le relazioni stratigrafiche.</p>

  <form method="post" enctype="multipart/form-data" action="{{ url_for('matrix_import.upload') }}">
    <label>Immagine: <input type="file" name="image" accept="image/*" required></label><br>

    <label>Sito esistente:
      <select name="sito" id="sito-select">
        <option value="">-- seleziona o lascia vuoto --</option>
        {% for s in sites %}
          <option value="{{ s }}">{{ s }}</option>
        {% endfor %}
        <option value="__NEW__">+ Nuovo sito</option>
      </select>
    </label><br>

    <label id="sito-new-wrapper" style="display:none">Nome nuovo sito:
      <input type="text" name="sito_new">
    </label><br>

    <label>Area (default per tutte le US):
      <input type="text" name="area" placeholder="es. Saggio 3">
    </label><br>

    <label>Descrizione contesto (opzionale):
      <textarea name="descrizione" rows="3" cols="40"></textarea>
    </label><br>

    <label>Provider:
      <select name="provider">
        <option value="anthropic" {% if default_provider == 'anthropic' %}selected{% endif %}>Anthropic (Claude)</option>
        <option value="openai" {% if default_provider == 'openai' %}selected{% endif %}>OpenAI (GPT)</option>
      </select>
    </label><br>

    <button type="submit">Analizza con AI</button>
  </form>

  <script>
    document.getElementById('sito-select').addEventListener('change', function() {
      document.getElementById('sito-new-wrapper').style.display =
        this.value === '__NEW__' ? 'inline' : 'none';
    });
  </script>
</body>
</html>
```

- [ ] **Step 4: Run test to verify it passes**

Run: `.venv/bin/python -m pytest tests/integration/test_matrix_import_upload_route.py::test_get_index_renders_with_sites -v`
Expected: 1 PASSED

- [ ] **Step 5: Register blueprint in app.py**

Find the section where other blueprints are registered (search for `csrf.exempt(lang_bp)` or `csrf.exempt(yed_import_bp)`) and add immediately after the same group:

```python
# pyarchinit_mini/web_interface/app.py
from pyarchinit_mini.web_interface.matrix_import_routes import matrix_import_bp
# ...
app.register_blueprint(matrix_import_bp)
csrf.exempt(matrix_import_bp)
```

- [ ] **Step 6: Commit**

```bash
git add pyarchinit_mini/web_interface/matrix_import_routes.py \
        pyarchinit_mini/web_interface/templates/matrix_import/upload.html \
        pyarchinit_mini/web_interface/app.py \
        tests/integration/test_matrix_import_upload_route.py
git commit -m "feat(spec10): matrix_import blueprint + GET / upload form"
```

---

## Task 6: POST /upload endpoint + preview.html + rejected.html templates

**Files:**
- Modify: `pyarchinit_mini/web_interface/matrix_import_routes.py`
- Create: `pyarchinit_mini/web_interface/templates/matrix_import/preview.html`
- Create: `pyarchinit_mini/web_interface/templates/matrix_import/rejected.html`
- Modify: `tests/integration/test_matrix_import_upload_route.py`
- Create: `tests/integration/test_matrix_import_rejected_route.py`

- [ ] **Step 1: Add upload + rejected tests**

Append to `tests/integration/test_matrix_import_upload_route.py`:

```python
def test_upload_renders_preview_on_success(client, monkeypatch):
    """Mocked AI returns valid plan → preview rendered."""
    fake_payload = json.dumps({
        "is_harris_matrix": True, "confidence": 0.9, "reason": "OK",
        "detected_site": "FromImage", "detected_area": None,
        "us": [{"us_num": "1", "area": "A", "unit_type": "USM",
                "descrizione": "muro", "fase_recente": 1, "fase_iniziale": 1}],
        "edges": [],
    })
    class FakeContent:
        def __init__(self, t): self.text = t
    class FakeResp:
        content = [FakeContent(fake_payload)]
    class FakeMessages:
        def create(self, **kw): return FakeResp()
    class FakeClient:
        def __init__(self, **kw): self.messages = FakeMessages()
    import anthropic
    monkeypatch.setattr(anthropic, "Anthropic", FakeClient)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")

    r = client.post(
        "/matrix-import/upload",
        data={
            "image": (io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"x" * 100), "matrix.png"),
            "descrizione": "",
            "sito": "",
            "area": "",
            "provider": "anthropic",
        },
        content_type="multipart/form-data",
    )
    assert r.status_code == 200
    body = r.get_data(as_text=True)
    assert "FromImage" in body or "muro" in body
    assert "plan_json" in body


def test_upload_missing_file_redirects(client):
    r = client.post(
        "/matrix-import/upload",
        data={"sito": "", "area": "", "provider": "anthropic"},
        content_type="multipart/form-data",
        follow_redirects=False,
    )
    assert r.status_code in (302, 303)
```

Create new file `tests/integration/test_matrix_import_rejected_route.py`:

```python
"""Test the rejected.html path: AI says is_harris_matrix=false."""
import io
import json
from pathlib import Path
import pytest

from flask import Flask
from pyarchinit_mini.web_interface.matrix_import_routes import matrix_import_bp


_APP_TEMPLATES = Path(__file__).parent.parent.parent / "pyarchinit_mini" / "web_interface" / "templates"


@pytest.fixture
def client(tmp_path, monkeypatch):
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    engine = create_engine(f"sqlite:///{tmp_path}/r.db")
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE site_table (
                id_sito INTEGER PRIMARY KEY AUTOINCREMENT,
                sito TEXT UNIQUE, descrizione TEXT,
                created_at DATETIME, updated_at DATETIME)
        """))
    Session = sessionmaker(bind=engine)
    app = Flask(__name__, template_folder=str(_APP_TEMPLATES))
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test"
    app.jinja_env.globals.setdefault("_", lambda s: s)
    app.jinja_env.globals.setdefault("get_locale", lambda: "it")
    app.jinja_env.globals.setdefault("csrf_token", lambda: "test")
    @app.before_request
    def _s():
        from flask import g
        g.db_session = Session()
    app.register_blueprint(matrix_import_bp)
    yield app.test_client()


def test_rejected_renders_when_ai_says_not_a_matrix(client, monkeypatch):
    fake_payload = json.dumps({
        "is_harris_matrix": False, "confidence": 0.2,
        "reason": "Foto di un muro romano, non un diagramma stratigrafico",
        "detected_site": None, "detected_area": None, "us": [], "edges": [],
    })
    class FakeContent:
        def __init__(self, t): self.text = t
    class FakeResp:
        content = [FakeContent(fake_payload)]
    class FakeMessages:
        def create(self, **kw): return FakeResp()
    class FakeClient:
        def __init__(self, **kw): self.messages = FakeMessages()
    import anthropic
    monkeypatch.setattr(anthropic, "Anthropic", FakeClient)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")

    r = client.post(
        "/matrix-import/upload",
        data={
            "image": (io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"x" * 100), "wall.png"),
            "provider": "anthropic",
        },
        content_type="multipart/form-data",
    )
    assert r.status_code == 200
    body = r.get_data(as_text=True)
    assert "muro romano" in body
    assert "non riconosciuta" in body.lower() or "rejected" in body.lower() or "matrix" in body.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/integration/test_matrix_import_upload_route.py tests/integration/test_matrix_import_rejected_route.py -v`
Expected: 3 FAILED (template not found / endpoint not registered)

- [ ] **Step 3: Add POST /upload to blueprint**

Append to `pyarchinit_mini/web_interface/matrix_import_routes.py`:

```python
@matrix_import_bp.post("/upload")
def upload():
    image_file = request.files.get("image")
    text_hint = request.form.get("descrizione", "").strip()
    sito_form = request.form.get("sito", "").strip()
    sito_new = request.form.get("sito_new", "").strip()
    area_form = request.form.get("area", "").strip()
    provider = request.form.get("provider", "anthropic")

    if not image_file:
        flash("Carica un'immagine", "error")
        return redirect(url_for("matrix_import.upload_form"))
    image_bytes = image_file.read()

    try:
        result = extract(image_bytes, text_hint, provider)
    except Exception as e:
        flash(f"Errore AI: {e}", "error")
        return redirect(url_for("matrix_import.upload_form"))

    if result.rejected:
        return render_template(
            "matrix_import/rejected.html",
            reason=result.reason,
            confidence=result.confidence,
        )

    if sito_form == "__NEW__":
        sito_form = ""
    sito_finale = sito_new or sito_form or (result.plan.detected_site or "")

    return render_template(
        "matrix_import/preview.html",
        plan=result.plan,
        sito=sito_finale,
        area_default=area_form or (result.plan.detected_area or ""),
        sito_needs_input=(sito_finale == ""),
        image_b64=base64.b64encode(image_bytes).decode(),
        plan_json=json.dumps(result.plan.as_dict()),
    )
```

- [ ] **Step 4: Create preview.html**

Create `pyarchinit_mini/web_interface/templates/matrix_import/preview.html`:

```html
<!DOCTYPE html>
<html lang="{{ get_locale() }}">
<head>
  <meta charset="UTF-8">
  <title>Preview AI Matrix Import</title>
</head>
<body>
  <h1>Preview AI Matrix Import</h1>

  {% if sito_needs_input %}
    <div style="background:#ffe; border:1px solid #cc0; padding:10px">
      <strong>⚠️ Nome sito non rilevato.</strong>
      Inseriscilo manualmente per continuare.
    </div>
  {% endif %}

  <form id="apply-form" method="post" action="{{ url_for('matrix_import.apply') }}">
    <input type="hidden" name="plan_json" value='{{ plan_json }}'>
    <input type="hidden" name="image_b64" value="{{ image_b64 }}">

    <label>Sito:
      <input type="text" name="sito" value="{{ sito }}" required>
    </label><br>

    <h3>US estratte ({{ plan.us|length }})</h3>
    <table border="1">
      <thead>
        <tr>
          <th>✓</th><th>US</th><th>Area</th><th>Unità tipo</th>
          <th>Descrizione</th><th>F.rec</th><th>F.ini</th>
        </tr>
      </thead>
      <tbody>
      {% for u in plan.us %}
        <tr>
          <td><input type="checkbox" name="selected_us" value="{{ loop.index0 }}" checked></td>
          <td><input name="us_num_{{ loop.index0 }}" value="{{ u.us_num }}"></td>
          <td><input name="area_{{ loop.index0 }}" value="{{ u.area or area_default }}"></td>
          <td>
            <select name="unit_type_{{ loop.index0 }}">
              <option value="USM" {% if u.unit_type == 'USM' %}selected{% endif %}>USM</option>
              <option value="USR" {% if u.unit_type == 'USR' %}selected{% endif %}>USR</option>
              <option value="US"  {% if u.unit_type == 'US'  %}selected{% endif %}>US</option>
            </select>
          </td>
          <td><input name="desc_{{ loop.index0 }}" value="{{ u.descrizione }}"></td>
          <td><input type="number" name="fr_{{ loop.index0 }}" value="{{ u.fase_recente }}" style="width:50px"></td>
          <td><input type="number" name="fi_{{ loop.index0 }}" value="{{ u.fase_iniziale }}" style="width:50px"></td>
        </tr>
      {% endfor %}
      </tbody>
    </table>

    <h3>Relazioni estratte ({{ plan.edges|length }})</h3>
    <table border="1">
      <thead>
        <tr><th>✓</th><th>US from</th><th>US to</th><th>Tipo</th></tr>
      </thead>
      <tbody>
      {% for e in plan.edges %}
        <tr>
          <td><input type="checkbox" name="selected_edges" value="{{ loop.index0 }}" checked></td>
          <td><input name="ef_{{ loop.index0 }}" value="{{ e.us_from }}"></td>
          <td><input name="et_{{ loop.index0 }}" value="{{ e.us_to }}"></td>
          <td>
            <select name="etipo_{{ loop.index0 }}">
              {% for t in ['copre','coperto da','taglia','tagliato da','riempie','riempito da','si appoggia','gli si appoggia','uguale a'] %}
                <option value="{{ t }}" {% if e.tipo == t %}selected{% endif %}>{{ t }}</option>
              {% endfor %}
            </select>
          </td>
        </tr>
      {% endfor %}
      </tbody>
    </table>

    <br>
    <button type="submit">Importa selezionate</button>
    <a href="{{ url_for('matrix_import.upload_form') }}">Annulla</a>
  </form>
</body>
</html>
```

- [ ] **Step 5: Create rejected.html**

Create `pyarchinit_mini/web_interface/templates/matrix_import/rejected.html`:

```html
<!DOCTYPE html>
<html lang="{{ get_locale() }}">
<head>
  <meta charset="UTF-8">
  <title>Immagine non riconosciuta</title>
</head>
<body>
  <h1>⚠️ Immagine non riconosciuta come Harris Matrix</h1>
  <p><strong>Motivo dall'AI:</strong> {{ reason }}</p>
  <p><strong>Confidence:</strong> {{ "%.0f"|format(confidence * 100) }}%</p>
  <p>L'immagine caricata non è stata riconosciuta come un Harris matrix
     stratigrafico. Niente è stato salvato nel database.</p>
  <a href="{{ url_for('matrix_import.upload_form') }}">← Torna al modulo di upload</a>
</body>
</html>
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/integration/test_matrix_import_upload_route.py tests/integration/test_matrix_import_rejected_route.py -v`
Expected: 4 PASSED

- [ ] **Step 7: Commit**

```bash
git add pyarchinit_mini/web_interface/matrix_import_routes.py \
        pyarchinit_mini/web_interface/templates/matrix_import/preview.html \
        pyarchinit_mini/web_interface/templates/matrix_import/rejected.html \
        tests/integration/test_matrix_import_upload_route.py \
        tests/integration/test_matrix_import_rejected_route.py
git commit -m "feat(spec10): POST /upload + preview.html + rejected.html"
```

---

## Task 7: POST /apply endpoint + form-edits + media save

**Files:**
- Modify: `pyarchinit_mini/web_interface/matrix_import_routes.py`
- Create: `tests/integration/test_matrix_import_apply_route.py`
- Create: `tests/integration/test_matrix_import_site_widget.py`

- [ ] **Step 1: Write failing tests**

Create `tests/integration/test_matrix_import_apply_route.py`:

```python
"""POST /matrix-import/apply commits selected US + edges to DB."""
import json
from pathlib import Path
import pytest

from flask import Flask
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.web_interface.matrix_import_routes import matrix_import_bp


_APP_TEMPLATES = Path(__file__).parent.parent.parent / "pyarchinit_mini" / "web_interface" / "templates"


def _make_app(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path}/a.db")
    with engine.begin() as conn:
        conn.execute(text("""CREATE TABLE site_table (
            id_sito INTEGER PRIMARY KEY AUTOINCREMENT,
            sito TEXT UNIQUE, descrizione TEXT,
            created_at DATETIME, updated_at DATETIME)"""))
        conn.execute(text("""CREATE TABLE us_table (
            id_us INTEGER PRIMARY KEY AUTOINCREMENT,
            sito TEXT, area TEXT, us TEXT, unita_tipo TEXT,
            d_stratigrafica TEXT, fase_recente INT, fase_iniziale INT,
            created_at DATETIME, updated_at DATETIME)"""))
        conn.execute(text("""CREATE TABLE us_relationships_table (
            id_rel INTEGER PRIMARY KEY AUTOINCREMENT,
            sito_from TEXT, sito_to TEXT, us_from INT, us_to INT,
            tipo_relazione TEXT, created_at DATETIME, updated_at DATETIME)"""))
    Session = sessionmaker(bind=engine)
    app = Flask(__name__, template_folder=str(_APP_TEMPLATES))
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "test"
    app.jinja_env.globals.setdefault("_", lambda s: s)
    app.jinja_env.globals.setdefault("get_locale", lambda: "it")
    app.jinja_env.globals.setdefault("csrf_token", lambda: "t")

    @app.before_request
    def _s():
        from flask import g
        g.db_session = Session()

    # Stub the us.list_us endpoint that apply redirects to
    from flask import Blueprint
    us_bp = Blueprint("us", __name__)
    @us_bp.route("/us/list")
    def list_us():
        return "us list page"
    app.register_blueprint(us_bp)

    app.register_blueprint(matrix_import_bp)
    return app, Session


@pytest.fixture
def client_and_session(tmp_path):
    app, Session = _make_app(tmp_path)
    return app.test_client(), Session


def _plan_json(us_rows, edges):
    return json.dumps({
        "detected_site": None, "detected_area": None,
        "us": us_rows, "edges": edges,
    })


def test_apply_commits_us_and_edges(client_and_session):
    client, Session = client_and_session
    plan = _plan_json(
        us_rows=[{"us_num": "1", "area": "A", "unit_type": "USM",
                  "descrizione": "x", "fase_recente": 1, "fase_iniziale": 1}],
        edges=[{"us_from": "1", "us_to": "2", "tipo": "copre"}],
    )
    r = client.post("/matrix-import/apply", data={
        "plan_json": plan,
        "image_b64": "",
        "sito": "TestSite",
        "selected_us": "0",
        "selected_edges": "0",
        "us_num_0": "1", "area_0": "A", "unit_type_0": "USM",
        "desc_0": "x", "fr_0": "1", "fi_0": "1",
        "ef_0": "1", "et_0": "2", "etipo_0": "copre",
    }, follow_redirects=False)
    assert r.status_code in (302, 303)
    s = Session()
    row = s.execute(text("SELECT sito FROM site_table")).fetchone()
    assert row[0] == "TestSite"
    us = s.execute(text("SELECT us, area FROM us_table")).fetchone()
    assert us[0] == "1" and us[1] == "A"
    e = s.execute(text("SELECT us_from, us_to, tipo_relazione FROM us_relationships_table")).fetchone()
    assert e[0] == 1 and e[1] == 2 and e[2] == "copre"


def test_apply_respects_unchecked_rows(client_and_session):
    client, Session = client_and_session
    plan = _plan_json(
        us_rows=[
            {"us_num": "1", "area": "A", "unit_type": "USM",
             "descrizione": "keep", "fase_recente": 1, "fase_iniziale": 1},
            {"us_num": "2", "area": "A", "unit_type": "USM",
             "descrizione": "skip", "fase_recente": 1, "fase_iniziale": 1},
        ],
        edges=[],
    )
    r = client.post("/matrix-import/apply", data={
        "plan_json": plan,
        "sito": "S",
        "selected_us": "0",  # only row 0
        "us_num_0": "1", "area_0": "A", "unit_type_0": "USM",
        "desc_0": "keep", "fr_0": "1", "fi_0": "1",
        "us_num_1": "2", "area_1": "A", "unit_type_1": "USM",
        "desc_1": "skip", "fr_1": "1", "fi_1": "1",
    }, follow_redirects=False)
    assert r.status_code in (302, 303)
    s = Session()
    rows = s.execute(text("SELECT us FROM us_table")).fetchall()
    assert len(rows) == 1
    assert rows[0][0] == "1"


def test_apply_rejects_missing_sito(client_and_session):
    client, _ = client_and_session
    r = client.post("/matrix-import/apply", data={
        "plan_json": _plan_json([], []),
        "sito": "",
    }, follow_redirects=False)
    assert r.status_code in (302, 303)
    # Should redirect back to upload form, not /us/list
    assert "/us/list" not in r.headers.get("Location", "")
```

Create `tests/integration/test_matrix_import_site_widget.py`:

```python
"""When AI doesn't detect a site and form doesn't set one, preview shows widget."""
import io
import json
from pathlib import Path
import pytest

from flask import Flask
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from pyarchinit_mini.web_interface.matrix_import_routes import matrix_import_bp


_APP_TEMPLATES = Path(__file__).parent.parent.parent / "pyarchinit_mini" / "web_interface" / "templates"


@pytest.fixture
def client(tmp_path, monkeypatch):
    engine = create_engine(f"sqlite:///{tmp_path}/w.db")
    with engine.begin() as conn:
        conn.execute(text("""CREATE TABLE site_table (
            id_sito INTEGER PRIMARY KEY AUTOINCREMENT,
            sito TEXT UNIQUE, descrizione TEXT,
            created_at DATETIME, updated_at DATETIME)"""))
    Session = sessionmaker(bind=engine)
    app = Flask(__name__, template_folder=str(_APP_TEMPLATES))
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "t"
    app.jinja_env.globals.setdefault("_", lambda s: s)
    app.jinja_env.globals.setdefault("get_locale", lambda: "it")
    app.jinja_env.globals.setdefault("csrf_token", lambda: "t")
    @app.before_request
    def _s():
        from flask import g
        g.db_session = Session()
    app.register_blueprint(matrix_import_bp)
    yield app.test_client()


def test_preview_shows_site_widget_when_missing(client, monkeypatch):
    """AI returns plan with detected_site=None and form sito='' → widget visible."""
    fake_payload = json.dumps({
        "is_harris_matrix": True, "confidence": 0.9, "reason": "OK",
        "detected_site": None, "detected_area": None,
        "us": [{"us_num": "1", "area": "A", "unit_type": "US",
                "descrizione": "x", "fase_recente": 1, "fase_iniziale": 1}],
        "edges": [],
    })
    class FakeContent:
        def __init__(self, t): self.text = t
    class FakeResp:
        content = [FakeContent(fake_payload)]
    class FakeMessages:
        def create(self, **kw): return FakeResp()
    class FakeClient:
        def __init__(self, **kw): self.messages = FakeMessages()
    import anthropic
    monkeypatch.setattr(anthropic, "Anthropic", FakeClient)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test")

    r = client.post("/matrix-import/upload", data={
        "image": (io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"x" * 100), "m.png"),
        "sito": "", "sito_new": "", "area": "", "provider": "anthropic",
    }, content_type="multipart/form-data")
    assert r.status_code == 200
    body = r.get_data(as_text=True)
    assert "non rilevato" in body.lower() or "widget" in body.lower() or "manualmente" in body.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `.venv/bin/python -m pytest tests/integration/test_matrix_import_apply_route.py tests/integration/test_matrix_import_site_widget.py -v`
Expected: FAILED (apply endpoint missing)

- [ ] **Step 3: Add POST /apply + _apply_form_edits helper**

Append to `pyarchinit_mini/web_interface/matrix_import_routes.py`:

```python
def _apply_form_edits(
    plan: AIPlan,
    form,
    selected_us_idx: set[str],
    selected_edges_idx: set[str],
) -> AIPlan:
    """Build a filtered plan with user-edited values for selected rows only."""
    from pyarchinit_mini.ai_matrix.plan import USRow, EdgeRow
    new_us = []
    for idx, _u in enumerate(plan.us):
        if str(idx) not in selected_us_idx:
            continue
        new_us.append(USRow(
            us_num=form.get(f"us_num_{idx}", "").strip(),
            area=form.get(f"area_{idx}", "").strip() or None,
            unit_type=form.get(f"unit_type_{idx}", "US").strip(),
            descrizione=form.get(f"desc_{idx}", "").strip(),
            fase_recente=int(form.get(f"fr_{idx}", "1") or "1"),
            fase_iniziale=int(form.get(f"fi_{idx}", "1") or "1"),
        ))
    new_edges = []
    for idx, _e in enumerate(plan.edges):
        if str(idx) not in selected_edges_idx:
            continue
        new_edges.append(EdgeRow(
            us_from=form.get(f"ef_{idx}", "").strip(),
            us_to=form.get(f"et_{idx}", "").strip(),
            tipo=form.get(f"etipo_{idx}", "copre").strip(),
        ))
    return AIPlan(
        detected_site=plan.detected_site,
        detected_area=plan.detected_area,
        us=new_us, edges=new_edges,
    )


@matrix_import_bp.post("/apply")
def apply():
    plan_json_str = request.form.get("plan_json", "")
    sito = request.form.get("sito", "").strip()
    image_b64 = request.form.get("image_b64", "")

    if not sito:
        flash("Nome sito obbligatorio", "error")
        return redirect(url_for("matrix_import.upload_form"))
    if not plan_json_str:
        flash("Plan mancante", "error")
        return redirect(url_for("matrix_import.upload_form"))

    selected_us = set(request.form.getlist("selected_us"))
    selected_edges = set(request.form.getlist("selected_edges"))

    plan = AIPlan.from_dict(json.loads(plan_json_str))
    plan = _apply_form_edits(plan, request.form, selected_us, selected_edges)

    result = apply_ai_plan(plan, sito, g.db_session)

    # Save source image as media for the site (best-effort, non-blocking)
    if image_b64:
        try:
            _save_image_for_site(sito, image_b64)
        except Exception as exc:
            current_app.logger.warning("matrix_import media save failed: %s", exc)

    flash(
        f"Importate {result.us_imported} US, {result.edges_imported} relazioni "
        f"({result.us_skipped} US e {result.edges_skipped} relazioni saltate)",
        "success",
    )
    return redirect(url_for("us.list_us", sito=sito))


def _save_image_for_site(sito: str, image_b64: str) -> None:
    """Best-effort: persist the source image as a Media row linked to the site.

    Uses MediaService.store_and_register_media via a temporary file. Looks up
    id_sito by sito name; if MediaService isn't wired into this app context,
    silently no-ops (the import already committed).
    """
    import tempfile
    from sqlalchemy import text as _text

    row = g.db_session.execute(
        _text("SELECT id_sito FROM site_table WHERE sito = :s"), {"s": sito}
    ).fetchone()
    if not row:
        return
    id_sito = int(row[0])

    image_bytes = base64.b64decode(image_b64)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp.write(image_bytes)
        tmp_path = tmp.name

    try:
        from pyarchinit_mini.services.media_service import MediaService
        from pyarchinit_mini.database.database_manager import DatabaseManager
        # If we can't construct these from the app context, just skip.
        # The route caller is expected to have a working MediaService elsewhere.
        media_svc = current_app.extensions.get("media_service")
        if media_svc is None:
            return
        media_svc.store_and_register_media(
            tmp_path,
            entity_type="site",
            entity_id=id_sito,
            description="AI Matrix Import source",
            tags="matrix_source,ai_import",
        )
    finally:
        import os as _os
        try:
            _os.unlink(tmp_path)
        except OSError:
            pass
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `.venv/bin/python -m pytest tests/integration/test_matrix_import_apply_route.py tests/integration/test_matrix_import_site_widget.py -v`
Expected: 4 PASSED

- [ ] **Step 5: Commit**

```bash
git add pyarchinit_mini/web_interface/matrix_import_routes.py \
        tests/integration/test_matrix_import_apply_route.py \
        tests/integration/test_matrix_import_site_widget.py
git commit -m "feat(spec10): POST /apply with form edits + best-effort media save"
```

---

## Task 8: Navbar link

**Files:**
- Modify: `pyarchinit_mini/web_interface/templates/base.html`

- [ ] **Step 1: Locate existing nav items**

Run: `grep -n "url_for.*harris_creator\|url_for.*yed_import\|url_for.*pottery" pyarchinit_mini/web_interface/templates/base.html | head`

This finds the navbar block. Note the surrounding HTML so the new link matches the style.

- [ ] **Step 2: Add the link**

Add a new `<li>` (or anchor matching the surrounding pattern) inside the navbar:

```html
<a href="{{ url_for('matrix_import.upload_form') }}">{{ _('AI Matrix Import') }}</a>
```

Place it adjacent to the existing `harris_creator` or `yed_import` link so it groups with the matrix-related tools.

- [ ] **Step 3: Smoke-check that base.html still renders**

Run: `.venv/bin/python -m pytest tests/integration/ -k "matrix_import" -v`
Expected: all 7+ integration tests still pass (link is in base.html but our integration test fixtures don't extend base.html, so they're unaffected — confirm no template errors anyway).

- [ ] **Step 4: Commit**

```bash
git add pyarchinit_mini/web_interface/templates/base.html
git commit -m "feat(spec10): add AI Matrix Import link to navbar"
```

---

## Task 9: Version bump 2.6.0 → 2.7.0 + CHANGELOG

**Files:**
- Modify: `pyarchinit_mini/__init__.py`
- Modify: `pyproject.toml`
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Bump version in `pyarchinit_mini/__init__.py`**

Find the `__version__` line and change from `2.6.0` to `2.7.0`.

```python
__version__ = "2.7.0"
```

- [ ] **Step 2: Bump version in `pyproject.toml`**

Find the `version = "2.6.0"` line under `[project]` and change to `"2.7.0"`.

```toml
version = "2.7.0"
```

- [ ] **Step 3: Add CHANGELOG entry**

Prepend to `CHANGELOG.md` (under any "Unreleased" header or at the top of versioned entries):

```markdown
## 2.7.0 — 2026-05-18

### Italiano
- **AI Matrix Import** (`/matrix-import/`): nuova feature che usa Vision API
  (Anthropic Claude Sonnet 4.7 o OpenAI GPT-5.5) per estrarre US e relazioni
  stratigrafiche da un'immagine di un Harris matrix. Include validation gate
  (l'AI rifiuta immagini che non sono matrici), preview editabile prima del
  commit, e auto-creazione del sito se nuovo.
- L'immagine sorgente viene salvata come media legato al sito.
- Toggle Anthropic / OpenAI nel form di upload.
- Required env vars: `ANTHROPIC_API_KEY` e/o `OPENAI_API_KEY`, `AI_PROVIDER` opzionale.

### English
- **AI Matrix Import** (`/matrix-import/`): new feature that uses Vision API
  (Anthropic Claude Sonnet 4.7 or OpenAI GPT-5.5) to extract stratigraphic
  units and relationships from an image of a Harris matrix. Includes a
  validation gate (the AI rejects non-matrix images), editable preview
  before commit, and auto-creation of the site if new.
- Source image saved as media linked to the site.
- Anthropic / OpenAI toggle in the upload form.
- Required env vars: `ANTHROPIC_API_KEY` and/or `OPENAI_API_KEY`, optional `AI_PROVIDER`.
```

- [ ] **Step 4: Commit**

```bash
git add pyarchinit_mini/__init__.py pyproject.toml CHANGELOG.md
git commit -m "release: bump to 2.7.0 (Spec 10 AI Matrix Import)"
```

---

## Task 10: Final regression sweep

**Files:** none (verification only)

- [ ] **Step 1: Run unit tests**

Run: `.venv/bin/python -m pytest tests/unit/ -v 2>&1 | tail -10`
Expected: All previously passing tests still pass; new Spec 10 unit tests (~20) pass. `test_delete_site` may fail (pre-existing, unrelated).

- [ ] **Step 2: Run integration tests**

Run: `.venv/bin/python -m pytest tests/integration/ -v --ignore=tests/integration/test_delete_site.py 2>&1 | tail -10`
Expected: All integration tests pass; new Spec 10 integration tests (~7) pass.

- [ ] **Step 3: Run full suite for the canonical count**

Run: `.venv/bin/python -m pytest tests/ --ignore=tests/integration/test_delete_site.py 2>&1 | tail -5`
Expected: ~488 passed (461 + ~27 new), 3 skipped, 3 xfailed.

- [ ] **Step 4: Verify version reachable**

Run: `.venv/bin/python -c "import pyarchinit_mini; print(pyarchinit_mini.__version__)"`
Expected: `2.7.0`

- [ ] **Step 5: No commit — task is verification only**

If any test fails that isn't `test_delete_site`, fix it before declaring the plan complete.
