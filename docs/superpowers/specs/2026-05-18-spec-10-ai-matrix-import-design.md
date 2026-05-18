# Spec 10 — AI Matrix Import (Vision API)

> **Status:** Brainstormed, ready for implementation plan
> **Target version:** `pyarchinit-mini` 2.6.0 → 2.7.0
> **Author:** Enzo + Claude Opus 4.7
> **Date:** 2026-05-18

## 1. Goal

Permettere all'utente di caricare un'immagine (foto/scan/schizzo) di un Harris
matrix e farsi estrarre automaticamente le US e le relazioni stratigrafiche
da un modello AI Vision (Claude Sonnet 4.7 o GPT-5.5). Il risultato è
presentato in una **preview editabile** prima del commit in DB, e
l'immagine sorgente viene archiviata come media legato al sito.

Vincolo critico: l'AI deve **prima riconoscere** che l'immagine è un Harris
matrix. Se non lo è, niente viene inserito in DB e l'utente vede un
messaggio di rifiuto con la motivazione.

## 2. Non-goals (YAGNI)

- Async job queue / polling (sync con spinner basta per Adarte single-user).
- PDF-to-image conversion (l'utente carica già un'immagine).
- Crop/rotate UI lato client (l'AI gestisce orientamento).
- Multi-image batch upload.
- OCR di descrizioni lunghe (l'AI legge solo etichette brevi US).
- Active learning / fine-tuning (no salvataggio feedback).
- Auto-applicare senza review (sempre preview, mai bypass).

## 3. Architecture

```
┌────────────────────────────────────────────────────────────┐
│  Browser: GET /matrix-import (upload form)                 │
│  - file (PNG/JPG, max 10MB)                                │
│  - select sito (esistente) o "+ Nuovo sito"                │
│  - area (testo opzionale, default per tutte le US)         │
│  - descrizione contesto (textarea opzionale)               │
│  - select provider (anthropic | openai, default = env)     │
└──────────────────┬─────────────────────────────────────────┘
                   │ POST multipart/form-data /matrix-import/upload
                   ▼
┌────────────────────────────────────────────────────────────┐
│  pyarchinit_mini/ai_matrix/  (new package)                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ vision_extractor.py                                  │  │
│  │   extract(image_bytes, text, provider) → Result     │  │
│  │   - validation gate: is_harris_matrix + confidence  │  │
│  │   - lazy import anthropic/openai                    │  │
│  │   - structured JSON system prompt                   │  │
│  │   - timeout 90s, max image 10MB                     │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ apply.py                                             │  │
│  │   apply_ai_plan(plan, sito, db_session)              │  │
│  │   - site_table auto-create se nuovo                  │  │
│  │   - dedupe (sito, us) esistenti                     │  │
│  │   - skip non-numeric us_from/us_to (Spec 7 pattern)  │  │
│  │   - audit cols created_at/updated_at                 │  │
│  │   - transazione atomica                              │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────┬─────────────────────────────────────────┘
                   │ ExtractResult
                   ▼
        ┌──────────┴──────────┐
        │                     │
   rejected=True         rejected=False
        │                     │
        ▼                     ▼
┌──────────────────┐   ┌─────────────────────────────────────┐
│ rejected.html    │   │  preview.html                       │
│ - motivo AI      │   │  - widget bloccante se sito mancante│
│ - bottone back   │   │  - tabella US editabile + checkbox  │
│ NIENTE in DB     │   │  - tabella edges editabile + check  │
│ Immagine NON     │   │  - hidden plan_json                 │
│ salvata          │   │  - "Importa selezionate"            │
└──────────────────┘   └──────────────┬──────────────────────┘
                                      │ POST /matrix-import/apply
                                      ▼
                       ┌──────────────────────────────────────┐
                       │ apply_ai_plan → DB commit            │
                       │ + MediaService.save(image,           │
                       │     entity_type='site',              │
                       │     entity_id=sito,                  │
                       │     tipo='matrix_source')            │
                       │ Redirect /us/list?sito=X             │
                       └──────────────────────────────────────┘
```

### Confini

- **Nuovo package**: `pyarchinit_mini/ai_matrix/` (extractor + apply).
- **Nuovo blueprint**: `pyarchinit_mini/web_interface/matrix_import_routes.py`
  con 3 endpoints, registrato in `app.py` con `csrf.exempt`.
- **3 nuovi template**: upload.html, preview.html, rejected.html.
- **Niente nuove tabelle DB** — il plan vive in hidden form field tra
  upload e apply.
- **Riusa**: `MediaService`, sessione DB SQLAlchemy, pattern provider di
  `ai_assistant_service.py`.

## 4. Components

### 4.1 `pyarchinit_mini/ai_matrix/vision_extractor.py`

**Dataclasses:**

```python
@dataclass
class USRow:
    us_num: str            # alfanumerico es. "11a"
    area: str | None       # AI's best guess per-row (può essere None)
    unit_type: str         # USM | USR | US (default "US" se ignoto)
    descrizione: str
    fase_recente: int
    fase_iniziale: int

@dataclass
class EdgeRow:
    us_from: str
    us_to: str
    tipo: str              # copre | taglia | riempie | si appoggia | uguale a

@dataclass
class AIPlan:
    detected_site: str | None
    detected_area: str | None
    us: list[USRow]
    edges: list[EdgeRow]

    def as_dict(self) -> dict: ...
    @classmethod
    def from_dict(cls, d: dict) -> "AIPlan": ...

@dataclass
class ExtractResult:
    rejected: bool
    reason: str            # motivo se rejected, "OK" se non
    confidence: float      # 0.0–1.0
    plan: AIPlan | None    # None se rejected
```

**System prompt (costante):**

```
You are an expert in archaeological stratigraphy and Harris matrix diagrams.

Your task: analyze the attached image and determine if it depicts a Harris
matrix (stratigraphic diagram). If yes, extract all stratigraphic units (US/SU)
and their relationships.

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
  "us": [{
    "us_num": str,
    "area": str | null,
    "unit_type": str,
    "descrizione": str,
    "fase_recente": int,
    "fase_iniziale": int
  }],
  "edges": [{
    "us_from": str,
    "us_to": str,
    "tipo": str
  }]
}

If is_harris_matrix is false, return empty us and edges arrays and explain
in 'reason' what you see instead.
```

**Provider routing:**

```python
def extract(image_bytes: bytes, text: str | None, provider: str) -> ExtractResult:
    if len(image_bytes) > 10 * 1024 * 1024:
        return ExtractResult(rejected=True, reason="Immagine > 10MB", confidence=0, plan=None)
    if provider == "anthropic":
        raw = _call_anthropic_vision(image_bytes, text)
    elif provider == "openai":
        raw = _call_openai_vision(image_bytes, text)
    else:
        raise ValueError(f"unknown provider: {provider}")
    return _parse_response(raw)
```

**Confidence threshold:** 0.7 hardcoded — sotto questa soglia, `rejected=True`.

**Anthropic call** (lazy import, riusa pattern `ai_assistant_service`):

```python
def _call_anthropic_vision(image_bytes: bytes, text: str | None) -> str:
    try:
        import anthropic
    except ImportError:
        raise RuntimeError("pip install anthropic")
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY non configurata")
    client = anthropic.Anthropic(api_key=api_key, timeout=90)
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
```

**OpenAI call** (lazy import, simile shape):

```python
def _call_openai_vision(image_bytes: bytes, text: str | None) -> str:
    try:
        import openai
    except ImportError:
        raise RuntimeError("pip install openai")
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY non configurata")
    client = openai.OpenAI(api_key=api_key, timeout=90)
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

**Parsing + validation:**

```python
def _parse_response(raw: str) -> ExtractResult:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        return ExtractResult(rejected=True, reason=f"AI returned non-JSON: {e}", confidence=0, plan=None)
    confidence = float(data.get("confidence", 0))
    if not data.get("is_harris_matrix", False) or confidence < 0.7:
        return ExtractResult(
            rejected=True,
            reason=data.get("reason", "Immagine non riconosciuta come Harris matrix"),
            confidence=confidence,
            plan=None,
        )
    plan = AIPlan(
        detected_site=data.get("detected_site"),
        detected_area=data.get("detected_area"),
        us=[USRow(**u) for u in data.get("us", [])],
        edges=[EdgeRow(**e) for e in data.get("edges", [])],
    )
    return ExtractResult(rejected=False, reason="OK", confidence=confidence, plan=plan)
```

### 4.2 `pyarchinit_mini/ai_matrix/apply.py`

```python
@dataclass
class ApplyResult:
    us_imported: int
    us_skipped: int           # già esistenti in DB
    edges_imported: int
    edges_skipped: int        # non-numeric o duplicate
    site_created: bool        # True se sito_table.sito è stato creato ora

VALID_UNIT_TYPES = {"USM", "USR", "US"}
VALID_REL_TYPES = {
    "copre", "coperto da",
    "taglia", "tagliato da",
    "riempie", "riempito da",
    "si appoggia", "gli si appoggia",
    "uguale a",
}

def apply_ai_plan(
    plan: AIPlan,
    sito: str,
    db_session,
) -> ApplyResult:
    now = datetime.utcnow()
    site_created = False

    # Step 1: site_table auto-create
    existing = db_session.execute(
        text("SELECT sito FROM site_table WHERE sito = :s"), {"s": sito}
    ).fetchone()
    if not existing:
        db_session.execute(text("""
            INSERT INTO site_table (sito, descrizione_sito, created_at, updated_at)
            VALUES (:sito, :desc, :now, :now)
        """), {"sito": sito, "desc": "Auto-creato da AI Matrix Import", "now": now})
        site_created = True

    # Step 2: us_table
    us_imported, us_skipped = 0, 0
    for u in plan.us:
        if not u.us_num or not u.area or not u.unit_type:
            us_skipped += 1
            continue
        unit_type = u.unit_type if u.unit_type in VALID_UNIT_TYPES else "US"
        row = db_session.execute(
            text("SELECT us FROM us_table WHERE sito = :s AND us = :u"),
            {"s": sito, "u": u.us_num},
        ).fetchone()
        if row:
            us_skipped += 1
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
        us_imported += 1

    # Step 3: us_relationships_table (int guard + dedupe)
    edges_imported, edges_skipped = 0, 0
    for e in plan.edges:
        try:
            us_from = int(e.us_from)
            us_to = int(e.us_to)
        except (ValueError, TypeError):
            edges_skipped += 1
            continue
        if e.tipo not in VALID_REL_TYPES:
            edges_skipped += 1
            continue
        # dedupe
        existing_rel = db_session.execute(text("""
            SELECT 1 FROM us_relationships_table
            WHERE sito_from = :s AND sito_to = :s
              AND us_from = :uf AND us_to = :ut AND tipo_relazione = :t
        """), {"s": sito, "uf": us_from, "ut": us_to, "t": e.tipo}).fetchone()
        if existing_rel:
            edges_skipped += 1
            continue
        db_session.execute(text("""
            INSERT INTO us_relationships_table
                (sito_from, sito_to, us_from, us_to, tipo_relazione,
                 created_at, updated_at)
            VALUES (:s, :s, :uf, :ut, :t, :now, :now)
        """), {"s": sito, "uf": us_from, "ut": us_to, "t": e.tipo, "now": now})
        edges_imported += 1

    db_session.commit()
    return ApplyResult(us_imported, us_skipped, edges_imported, edges_skipped, site_created)
```

### 4.3 `pyarchinit_mini/web_interface/matrix_import_routes.py`

```python
from flask import Blueprint, request, render_template, redirect, url_for, flash, g
import json, os
from pyarchinit_mini.ai_matrix.vision_extractor import extract
from pyarchinit_mini.ai_matrix.apply import apply_ai_plan, AIPlan

matrix_import_bp = Blueprint(
    "matrix_import", __name__,
    url_prefix="/matrix-import",
    template_folder="templates",
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

@matrix_import_bp.post("/apply")
def apply():
    plan_json = request.form.get("plan_json", "")
    sito = request.form.get("sito", "").strip()
    image_b64 = request.form.get("image_b64", "")

    if not sito:
        flash("Nome sito obbligatorio", "error")
        return redirect(url_for("matrix_import.upload_form"))

    selected_us = set(request.form.getlist("selected_us"))
    selected_edges = set(request.form.getlist("selected_edges"))

    plan = AIPlan.from_dict(json.loads(plan_json))
    plan = _apply_form_edits(plan, request.form, selected_us, selected_edges)

    result = apply_ai_plan(plan, sito, g.db_session)

    # Save source image as media on the site
    if image_b64:
        try:
            from pyarchinit_mini.services.media_service import save_media_bytes
            save_media_bytes(
                base64.b64decode(image_b64),
                entity_type="site",
                entity_id=sito,
                tipo="matrix_source",
                db_session=g.db_session,
            )
        except Exception:
            pass  # media is bonus, not blocking

    flash(
        f"Importate {result.us_imported} US, {result.edges_imported} relazioni "
        f"({result.us_skipped} US e {result.edges_skipped} relazioni saltate)",
        "success",
    )
    return redirect(url_for("us.list_us", sito=sito))
```

**Helper privati da implementare nel plan:**
- `_apply_form_edits(plan, form, sel_us_idx, sel_edges_idx) -> AIPlan` — costruisce un nuovo `AIPlan` con solo le righe selezionate e i valori editati nel form (us_num_N, area_N, unit_type_N, etc).
- `_detect_media_type(image_bytes) -> str` — guarda i magic bytes; ritorna "image/png", "image/jpeg", o "image/png" come fallback.
- `save_media_bytes(...)` — wrapper su MediaService esistente; se l'API attuale non lo supporta, il plan lo aggiunge come metodo additivo.

### 4.4 Templates

#### `templates/matrix_import/upload.html`

Form HTML semplice con:
- `<input type="file" name="image" accept="image/*" required>`
- `<select name="sito">` con siti esistenti + opzione "+ Nuovo sito"
- JS che se selezionato "+ Nuovo" mostra `<input name="sito_new">`
- `<input name="area">` testo
- `<textarea name="descrizione">` opzionale
- `<select name="provider">` opzioni anthropic/openai
- Bottone submit "Analizza con AI" + spinner CSS

#### `templates/matrix_import/preview.html`

```html
{% if sito_needs_input %}
  <div class="warning-block">
    ⚠️ Nome sito non rilevato — inseriscilo manualmente per continuare:
    <input name="sito" form="apply-form" required>
  </div>
{% endif %}

<form id="apply-form" method="post" action="{{ url_for('matrix_import.apply') }}">
  <input type="hidden" name="plan_json" value='{{ plan_json }}'>
  <input type="hidden" name="image_b64" value="{{ image_b64 }}">
  {% if not sito_needs_input %}
    <input type="hidden" name="sito" value="{{ sito }}">
  {% endif %}

  <h3>US estratte ({{ plan.us|length }})</h3>
  <table>
    <thead>...</thead>
    <tbody>
    {% for u in plan.us %}
      <tr>
        <td><input type="checkbox" name="selected_us" value="{{ loop.index0 }}" checked></td>
        <td><input name="us_num_{{ loop.index0 }}" value="{{ u.us_num }}"></td>
        <td><input name="area_{{ loop.index0 }}" value="{{ u.area or area_default }}"></td>
        <td>
          <select name="unit_type_{{ loop.index0 }}">
            <option {% if u.unit_type=='USM' %}selected{% endif %}>USM</option>
            <option {% if u.unit_type=='USR' %}selected{% endif %}>USR</option>
            <option {% if u.unit_type=='US' %}selected{% endif %}>US</option>
          </select>
        </td>
        <td><input name="desc_{{ loop.index0 }}" value="{{ u.descrizione }}"></td>
        <td><input name="fr_{{ loop.index0 }}" type="number" value="{{ u.fase_recente }}"></td>
        <td><input name="fi_{{ loop.index0 }}" type="number" value="{{ u.fase_iniziale }}"></td>
      </tr>
    {% endfor %}
    </tbody>
  </table>

  <h3>Relazioni estratte ({{ plan.edges|length }})</h3>
  <table>...</table>

  <button type="submit" {% if sito_needs_input %}disabled{% endif %}>
    Importa selezionate
  </button>
</form>
```

#### `templates/matrix_import/rejected.html`

```html
<div class="error-block">
  <h2>⚠️ Immagine non riconosciuta come Harris Matrix</h2>
  <p><strong>Motivo dall'AI:</strong> {{ reason }}</p>
  <p><strong>Confidence:</strong> {{ "%.0f"|format(confidence * 100) }}%</p>
  <a href="{{ url_for('matrix_import.upload_form') }}" class="btn">← Torna a upload</a>
</div>
```

## 5. Data flow

```
1. GET /matrix-import → upload form

2. POST /matrix-import/upload (multipart)
   ├ image_bytes = file.read()  (max 10MB check)
   ├ vision_extractor.extract(image, text, provider)
   │  ├ _call_<provider>_vision(...) → raw JSON string
   │  └ _parse_response(raw) → ExtractResult
   ├ if rejected → render rejected.html (NO image saved, NO DB)
   └ if OK → render preview.html (plan in hidden field)

3. POST /matrix-import/apply
   ├ plan = AIPlan.from_dict(json.loads(form.plan_json))
   ├ apply form edits (us_num, area, unit_type, desc, fasi per riga)
   ├ filter by selected_us / selected_edges checkboxes
   ├ apply_ai_plan(plan, sito, db_session)
   │  ├ INSERT site_table if new
   │  ├ for u in us: INSERT us_table (skip duplicate sito+us)
   │  ├ for e in edges: INSERT us_relationships_table (skip non-int, skip dupe)
   │  └ commit
   ├ MediaService.save_media_bytes(image, site=sito, tipo='matrix_source')
   └ flash + redirect /us/list?sito=X
```

## 6. Error handling

| Caso | Handling |
|---|---|
| Image > 10MB | reject prima della chiamata AI, flash "max 10MB" |
| Image upload mancante | flash, redirect a upload_form |
| Provider package non installato | RuntimeError → flash "pip install <pkg>" |
| API key mancante | RuntimeError → flash "Configura ANTHROPIC_API_KEY" |
| API timeout (>90s) | Exception → flash con messaggio AI |
| AI returns non-JSON | rejected=True, reason="AI returned non-JSON: ..." |
| is_harris_matrix=false | rejected.html, NO data committed |
| confidence < 0.7 | rejected.html con confidence% mostrato |
| us_num/area/unit_type mancanti in riga | apply.py skip riga (us_skipped++) |
| unit_type ignoto | coerce a "US" |
| us_from/us_to non int | skip edge (edges_skipped++) |
| tipo edge non in vocabolario | skip edge |
| Sito già esiste in site_table | salta INSERT site_table (idempotent) |
| (sito, us) già esiste in us_table | salta INSERT us_table (idempotent) |
| Relazione duplicata | salta INSERT (idempotent) |
| MediaService save fail | log warn, ma commit US già fatto (media è bonus) |

## 7. Testing

| Layer | Test file | Coverage |
|---|---|---|
| Unit | `test_ai_matrix_extractor_parse.py` | `_parse_response` happy path, JSON parse fail, missing fields, low confidence (0.5), is_harris_matrix=false |
| Unit | `test_ai_matrix_extractor_providers.py` | Provider routing anthropic/openai/unknown (ValueError) + missing API key error |
| Unit | `test_ai_matrix_apply.py` | site auto-create, dedupe US, dedupe edges, int guard us_from/us_to, unit_type coerce, audit cols populated |
| Unit | `test_ai_matrix_plan_serialization.py` | `AIPlan.as_dict` / `from_dict` round-trip |
| Integration | `test_matrix_import_upload_route.py` | POST /upload con mock anthropic → render preview |
| Integration | `test_matrix_import_rejected_route.py` | mock returns is_harris_matrix=false → render rejected.html |
| Integration | `test_matrix_import_apply_route.py` | POST /apply → US + relazioni create in sqlite test |
| Integration | `test_matrix_import_site_widget.py` | plan senza detected_site, form senza sito → widget bloccante visibile |
| Regression | 461 test esistenti | Restano tutti verdi |

**Mock pattern** (riusa quello di `ai_assistant_service`):

```python
@pytest.fixture
def mock_anthropic_vision(monkeypatch):
    fake_response = json.dumps({
        "is_harris_matrix": True,
        "confidence": 0.9,
        "reason": "OK",
        "detected_site": "Test Site",
        "detected_area": None,
        "us": [{"us_num": "1", "area": "A", "unit_type": "USM",
                "descrizione": "test", "fase_recente": 1, "fase_iniziale": 1}],
        "edges": [],
    })
    class FakeMessages:
        def create(self, **kw):
            return type("R", (), {"content": [type("C", (), {"text": fake_response})()]})()
    monkeypatch.setattr("anthropic.Anthropic",
                        lambda **kw: type("X", (), {"messages": FakeMessages()})())
```

## 8. Definition of Done

### Backend
- [ ] `pyarchinit_mini/ai_matrix/__init__.py` (package empty marker)
- [ ] `pyarchinit_mini/ai_matrix/vision_extractor.py` con `extract()`, dataclasses, anthropic+openai providers, validation gate
- [ ] `pyarchinit_mini/ai_matrix/apply.py` con `apply_ai_plan()`: site auto-create, dedupe, int guard, audit cols
- [ ] `pyarchinit_mini/web_interface/matrix_import_routes.py` con 3 endpoints + blueprint
- [ ] Registrato in `app.py` con `csrf.exempt(matrix_import_bp)`
- [ ] `pyarchinit_mini/services/media_service.py` espone `save_media_bytes()` (o usa metodo esistente compatibile)

### Frontend
- [ ] `templates/matrix_import/upload.html`
- [ ] `templates/matrix_import/preview.html` con widget sito bloccante condizionale
- [ ] `templates/matrix_import/rejected.html`
- [ ] Link "AI Matrix Import" nella navbar principale (in base.html o equivalente)

### Tests
- [ ] 4 file unit (~12 test)
- [ ] 4 file integration (~8 test)
- [ ] Tutti i 461 test esistenti restano verdi

### Release
- [ ] Bump `pyproject.toml` + `__init__.py` da 2.6.0 → 2.7.0
- [ ] CHANGELOG entry IT + EN
- [ ] Dipendenze opzionali in `[ai]` extra: `anthropic>=0.18`, `openai>=1.0` (verificare già presenti)

### Documentazione
- [ ] README sezione "AI Matrix Import": env vars + come usare
- [ ] Nota su `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `AI_PROVIDER`

## 9. Backwards compat

- Pattern provider riusa `ai_assistant_service.py` — nessuna rottura.
- `apply_ai_plan` segue lo stesso shape di `apply_import_plan` (yed_importer):
  audit cols, int guard, dedupe, atomic transaction.
- `MediaService` invariato (se serve nuovo metodo, è additivo).
- Nessun cambiamento ad `us_table`/`site_table`/`us_relationships_table` schema.
- Nessun impatto su Harris Matrix Creator (Spec 9) o pottery (Spec 8).

## 10. Costo stimato per import

Esempio: foto Harris matrix con 50 US, 100 edges:
- Input tokens (image + system prompt + user text): ~3000
- Output tokens (JSON con 50+100 righe): ~3000
- **Claude Sonnet 4.7**: $3/M input + $15/M output = **~$0.054 / import**
- **GPT-5.5**: ~$2.5/M input + $10/M output = **~$0.038 / import**

Per Adarte (uso single-user, ~10 import/giorno):
- ~$0.50/giorno = ~$15/mese (worst case)

## 11. Riferimenti

- Spec 7 — pattern `apply_import_plan` con audit cols + int guard
- Spec 8 — pattern `csrf.exempt(bp)` per blueprint con form upload
- `ai_assistant_service.py` — pattern lazy import + env-driven provider
- Anthropic Vision API docs: https://docs.anthropic.com/claude/docs/vision
- OpenAI Vision API docs: https://platform.openai.com/docs/guides/vision

## 12. Roadmap successiva (oltre Spec 10)

- Async job queue + worker (se gli import diventano molti)
- Salvataggio feedback corrispondenza AI/realtà per dataset di training
- Multi-image batch (cartella → batch import)
- PDF/scan multi-pagina con estrazione per ciascuna pagina
- Integrazione con `harris_swimlane.compute_harris_positions` per visualizzare
  subito il matrix importato nel Creator
