# Spec 8 — Pottery features (preview img, filtri id/anno, lang switch fix, scheda gallery)

> **Status:** Brainstormed, ready for implementation plan
> **Target version:** `pyarchinit-mini` 2.5.0 → 2.5.1
> **Author:** Enzo + Claude Opus 4.7
> **Date:** 2026-05-18

## 1. Goal

Quattro richieste utente sul modulo Pottery, indipendenti tra loro ma tutte
all'interno della stessa area UI (`pottery_routes.py` + `templates/pottery/`):

1. **Preview image nella lista** — thumbnail della prima media accanto a ogni
   record, con mini-carousel scroll-snap se la pottery ha più foto.
2. **Filtri id_number + anno** nel form di ricerca, match esatto.
3. **Bug: cambio lingua azzera filtri** — sostituito con `POST /set-language/<lang>`
   + redirect a referrer (preserva la query string).
4. **Immagini nella scheda detail** — grid thumb 120×120 + GLightbox, tutte
   le foto del reperto inline (no go-to-edit/media manager).

## 2. Non-goals (YAGNI)

- Filtri range id_number/anno (>, <, between).
- Carousel paginato per >10 media in lista (improbabile per pottery).
- Upload media inline nella scheda (esiste già `/pottery/<id>/media`).
- Spec 9 (Harris Matrix edges ortogonali) — separato.

## 3. Architecture

```
                              Browser
              ┌──────────────────────────────────────┐
              │  /pottery/                           │
              │  ┌─────────────────────────────────┐ │
              │  │ Filtri: sito|area|us|form|     │ │
              │  │  fabric|q + id_number + anno   │ │
              │  ├─────────────────────────────────┤ │
              │  │ Lista: thumb 48×48 mini-       │ │
              │  │  carousel scroll-snap CSS-only │ │
              │  ├─────────────────────────────────┤ │
              │  │ Lang switch [IT][EN] →         │ │
              │  │  POST /set-language/<lang>     │ │
              │  └─────────────────────────────────┘ │
              │  /pottery/<id>  (detail)             │
              │  ┌─────────────────────────────────┐ │
              │  │ Gallery thumb 120×120 + GLight-│ │
              │  │ box (all media inline)         │ │
              │  ├─────────────────────────────────┤ │
              │  │ Form fields (sito, area, US..) │ │
              │  └─────────────────────────────────┘ │
              └────┬──────────────────────────┬──────┘
                  │                          │
          GET /pottery/?sito=X&id_number=N    POST /set-language/<lang>
          GET /pottery/<id>                      ↓
                  ↓                       session['lang'] = lang
                  ↓                       redirect(referrer)
         ┌──────────────────┐
         │ pottery_routes.py│
         │   (mod)          │ ────────→ ┌──────────────────────┐
         │                  │           │ pyarchinit_mini/     │
         │                  │           │  i18n/lang_routes.py │
         │                  │           │  (NEW: blueprint)    │
         └──┬───────────────┘           └──────────────────────┘
            │
            ▼
       ┌─────────────────┐
       │ pottery_service │
       │ filter + media  │
       │ thumbnail URL   │
       └─────────────────┘
            │
            ▼
   us_table + pottery_table + media_table (existing)
```

### Confini

- **Frontend templates** — 2 file modificati + 1 modificato:
  - `templates/pottery/list.html` — colonna thumb-carousel + 2 input filtri
  - `templates/pottery/detail.html` — `<div id="pottery-media-grid">` con thumb 120×120 GLightbox
  - `templates/components/language_switcher.html` — `<a>` sostituito con `<form method="post">`
- **Backend** — nuovo blueprint `lang_routes.py` con `POST /set-language/<lang>`.
- **pottery_routes.py** — estende `FILTER_KEYS` con `id_number`, `anno`.
- **pottery_service** — aggiunge supporto WHERE `id_number`/`anno`.
- **Pre-load media batch** — `media_for_pottery_ids(ids)` evita N+1.
- **Niente migration DB** — campi `id_number`/`anno` già presenti nel modello Pottery.
- **Niente nuove tabelle** — `media_table` consumata via `/api/media/by-entity/pottery/<id>`.

## 4. Components

### 4.1 `pyarchinit_mini/i18n/lang_routes.py` (new blueprint)

```python
"""Blueprint for language switching — POST + redirect to referrer."""
from flask import Blueprint, session, redirect, request, url_for

lang_bp = Blueprint("lang", __name__)

_VALID_LANGS = frozenset({"it", "en"})


@lang_bp.post("/set-language/<lang>")
def set_language(lang: str):
    """Save chosen language in session, redirect back to referrer (or /)."""
    if lang in _VALID_LANGS:
        session["lang"] = lang
        session.permanent = True
    target = request.referrer or url_for("index")
    return redirect(target)
```

- Registrato in `app.py` come `app.register_blueprint(lang_bp)`
- CSRF: pattern già usato per paradata_ui_bp/yed_import_bp — `csrf.exempt(lang_bp)`.
  Lingua non è dato sensibile e non altera DB.

### 4.2 `pyarchinit_mini/web_interface/pottery_routes.py` (modify)

Estendi le `FILTER_KEYS` in **5 punti** (list, export pdf, export csv,
export single pdf, api stats):

```python
FILTER_KEYS = ("sito", "area", "us", "form", "fabric", "q",
               "id_number", "anno")
filters = {k: request.args.get(k) for k in FILTER_KEYS if request.args.get(k)}
```

In `pottery_list`, pre-carica i media batch:

```python
@app.route("/pottery/")
def pottery_list():
    page = int(request.args.get("page", 1))
    size = int(request.args.get("size", 25))
    filters = {k: request.args.get(k) for k in FILTER_KEYS if request.args.get(k)}
    items, total = service.list(filters, page=page, size=size)
    ids = [p.id_rep for p in items]
    media_by_pottery = service.media_for_pottery_ids(ids)
    # {id_rep: [{"thumb_url": "...", "filename": "...", "url": "..."}], ...}
    return render_template(
        "pottery/list.html",
        items=items, filters=filters, total=total, page=page, size=size,
        media_by_pottery=media_by_pottery,
    )
```

### 4.3 `pottery_service` (or pottery_routes inline) — filtri + media batch

```python
def list(filters, *, page=1, size=25):
    q = session.query(Pottery)
    if filters.get("sito"): q = q.filter(Pottery.sito.ilike(f"%{filters['sito']}%"))
    if filters.get("area"): q = q.filter(Pottery.area.ilike(f"%{filters['area']}%"))
    if filters.get("us"): q = q.filter(Pottery.us == filters["us"])
    if filters.get("form"): q = q.filter(Pottery.form.ilike(f"%{filters['form']}%"))
    if filters.get("fabric"): q = q.filter(Pottery.fabric.ilike(f"%{filters['fabric']}%"))
    if filters.get("q"):
        kw = f"%{filters['q']}%"
        q = q.filter(or_(Pottery.descrizione.ilike(kw), Pottery.note.ilike(kw)))
    if filters.get("id_number"):
        try: q = q.filter(Pottery.id_number == int(filters["id_number"]))
        except ValueError: pass  # ignore non-numeric input
    if filters.get("anno"):
        try: q = q.filter(Pottery.anno == int(filters["anno"]))
        except ValueError: pass
    total = q.count()
    items = q.offset((page - 1) * size).limit(size).all()
    return items, total


def media_for_pottery_ids(ids: list[int]) -> dict[int, list[dict]]:
    if not ids:
        return {}
    rows = session.execute(text(
        "SELECT m.entity_id, m.file_path, m.filename "
        "FROM media_table m WHERE m.entity_type='pottery' AND m.entity_id = ANY(:ids) "
        "ORDER BY m.entity_id, m.id_media"
    ), {"ids": ids}).fetchall()
    out: dict[int, list[dict]] = {}
    for r in rows:
        out.setdefault(r[0], []).append({
            "url": f"/media/{r[1]}",
            "thumb_url": f"/media/{r[1]}",  # full file; lazy-load handles size
            "filename": r[2],
        })
    return out
```

Adatta la query alla tua effettiva schema `media_table` (entity_type/entity_id
o per-tabella `pottery_media_table`). Verifica il SELECT prima di committare.

### 4.4 `templates/pottery/list.html` — filtri estesi

```html
<form method="get" class="row g-2 mb-3">
  <div class="col-md-2"><input class="form-control form-control-sm" type="text"   name="sito"      value="{{ filters.sito or '' }}" placeholder="Sito"></div>
  <div class="col-md-1"><input class="form-control form-control-sm" type="text"   name="area"      value="{{ filters.area or '' }}" placeholder="Area"></div>
  <div class="col-md-1"><input class="form-control form-control-sm" type="number" name="us"        value="{{ filters.us or '' }}" placeholder="US"></div>
  <div class="col-md-1"><input class="form-control form-control-sm" type="number" name="id_number" value="{{ filters.id_number or '' }}" placeholder="ID num" min="0"></div>
  <div class="col-md-1"><input class="form-control form-control-sm" type="number" name="anno"      value="{{ filters.anno or '' }}" placeholder="Anno" min="1900" max="2099"></div>
  <div class="col-md-2"><input class="form-control form-control-sm" type="text"   name="form"      value="{{ filters.form or '' }}" placeholder="Forma" list="dl-forms"></div>
  <div class="col-md-1"><input class="form-control form-control-sm" type="text"   name="fabric"    value="{{ filters.fabric or '' }}" placeholder="Impasto" list="dl-fabrics"></div>
  <div class="col-md-2"><input class="form-control form-control-sm" type="text"   name="q"         value="{{ filters.q or '' }}" placeholder="Ricerca"></div>
  <div class="col-md-1"><button class="btn btn-sm btn-secondary">Filtra</button></div>
</form>
```

### 4.5 `templates/pottery/list.html` — colonna mini-carousel

Sostituisco il badge "Sì/No" nella cella Media:

```html
<td>
  {% set media_list = media_by_pottery.get(p.id_rep, []) %}
  {% if media_list %}
    <div class="pottery-mini-carousel" role="list">
      {% for m in media_list %}
        <a class="glightbox" data-gallery="pot-{{ p.id_rep }}"
           href="{{ m.url }}" data-title="{{ m.filename }}" role="listitem">
          <img src="{{ m.thumb_url or m.url }}" alt="" loading="lazy"
               width="48" height="48"
               style="object-fit:cover;border-radius:3px"/>
        </a>
      {% endfor %}
    </div>
  {% else %}
    <span class="badge bg-secondary">No</span>
  {% endif %}
</td>
```

CSS (inline in `{% block extra_css %}` di list.html oppure in `style.css`):

```css
.pottery-mini-carousel {
  display: flex; gap: 4px; max-width: 200px;
  overflow-x: auto; scroll-snap-type: x mandatory;
  padding: 2px;
}
.pottery-mini-carousel > a { scroll-snap-align: start; flex: 0 0 auto; }
.pottery-mini-carousel::-webkit-scrollbar { height: 4px; }
.pottery-mini-carousel::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 2px; }
```

CSS-only — niente JS aggiuntivo. GLightbox è già incluso da `base.html`.

### 4.6 `templates/pottery/detail.html` — gallery grid

Aggiungo una sezione `<div id="pottery-media-grid">` PRIMA del form fields:

```html
<div id="pottery-media-grid" class="mb-4">
  <h5><i class="fas fa-images"></i> {{ _('Media') }}</h5>
  <div class="d-flex flex-wrap gap-2" id="pottery-thumbs"></div>
</div>

<script>
fetch("/api/media/by-entity/pottery/{{ pottery.id_rep }}")
  .then(r => r.ok ? r.json() : {items: []})
  .then(data => {
    const container = document.getElementById('pottery-thumbs');
    const items = data.items || data || [];
    if (!items.length) {
      container.innerHTML = '<p class="text-muted">{{ _("No media") }}</p>';
      return;
    }
    container.innerHTML = items.map(m => `
      <a class="glightbox" data-gallery="pot-detail" href="${m.url}" data-title="${m.filename || ''}">
        <img src="${m.thumb_url || m.url}" alt=""
             width="120" height="120" loading="lazy"
             style="object-fit:cover;border-radius:4px;border:1px solid var(--border-color)"/>
      </a>
    `).join('');
    if (window.GLightbox) {
      GLightbox({ selector: '.glightbox' });
    }
  });
</script>
```

### 4.7 `templates/components/language_switcher.html` — POST form

```html
<div class="language-switcher ms-3">
  <div class="btn-group" role="group" aria-label="Language selector">
    {% set current_lang = get_locale() %}
    <form method="post" action="{{ url_for('lang.set_language', lang='it') }}" class="d-inline">
      <button type="submit"
              class="btn btn-sm {% if current_lang == 'it' %}btn-primary{% else %}btn-outline-secondary{% endif %}"
              title="Italiano">🇮🇹 IT</button>
    </form>
    <form method="post" action="{{ url_for('lang.set_language', lang='en') }}" class="d-inline">
      <button type="submit"
              class="btn btn-sm {% if current_lang == 'en' %}btn-primary{% else %}btn-outline-secondary{% endif %}"
              title="English">🇬🇧 EN</button>
    </form>
  </div>
</div>
```

I form POST mantengono il browser su `request.referrer` (settato automaticamente
dal `Referer` header). L'endpoint `/set-language/<lang>` salva session + redirect.
La query string corrente (`?sito=test&q=ware`) viene preservata.

## 5. Data flows

### Flow A — Pottery list + filtri + thumb-carousel

```
Browser: GET /pottery/?sito=Volterra&id_number=42&anno=2024&page=1
    ↓
pottery_list(filters={sito, id_number, anno})
    ↓
service.list(filters, page, size) → items, total
service.media_for_pottery_ids([item.id_rep for item in items]) → media_by_pottery
    ↓
render list.html(items, total, filters, media_by_pottery)
    ↓
Browser: thumb-carousel + filtri compilati + GLightbox bind on .glightbox
```

### Flow B — Detail con gallery

```
Browser: GET /pottery/<id>
    ↓
pottery_detail(id) → render detail.html(pottery)
    ↓
Browser: fetch /api/media/by-entity/pottery/<id>
    ↓
Render grid thumb 120×120 + GLightbox bind
```

### Flow C — Lang switch

```
Browser: POST /set-language/it  (form submit from switcher button)
   Referer: /pottery/?sito=Volterra&id_number=42
    ↓
lang.set_language('it')
   session['lang'] = 'it'
   session.permanent = True
    ↓
redirect(request.referrer)  → /pottery/?sito=Volterra&id_number=42 (URL preservata)
    ↓
Browser ricarica con lang IT applicato (templates _ usano session)
```

## 6. Error handling

| Categoria | Sorgente | Trattamento |
|---|---|---|
| Filtro `id_number=abc` (non numerico) | User input | `try/except ValueError` in service → ignora filtro (no SQL error) |
| Filtro `anno=abcd` | User input | Stesso |
| `/api/media/by-entity/pottery/<id>` torna 500 | Backend bug | JS catch → mostra "Errore caricamento media" inline |
| `request.referrer` None (utente entrato direttamente) | Edge case | Fallback a `url_for("index")` nell'endpoint set_language |
| Pottery senza media | DB | `media_by_pottery.get(id) → []` → fallback badge "No" |
| Lang non valido (POST `/set-language/zh`) | URL tamper | Validation `if lang in _VALID_LANGS` → redirect senza salvare |

## 7. Testing

| Layer | Test | Strategia |
|---|---|---|
| Unit | `set_language` view | Mock session, POST `/set-language/it`, assert session['lang']=='it' + 302 to referrer |
| Unit | `set_language` rejection | POST `/set-language/zh` → no session change, redirect |
| Integration | Pottery filter `id_number` | GET `/pottery/?id_number=42` → only matching pottery |
| Integration | Pottery filter `anno` | GET `/pottery/?anno=2024` → only 2024 records |
| Integration | Pottery filter non-numerico ignorato | GET `/pottery/?id_number=abc` → 200 + tutti i record |
| Integration | `media_by_pottery` passato al template | Verify context dict |
| Integration | Language switch preserva URL | POST `/set-language/en` con `Referer: /pottery/?q=test` → Location `/pottery/?q=test` |
| Frontend manual smoke | Thumb-carousel scroll-snap | Browser test: pottery con 5 media → carousel scrolla |
| Frontend manual smoke | Detail GLightbox | Click thumb 120 → lightbox apre |
| Regression | 447 esistenti | Must pass |

## 8. Definition of Done

### Backend
- [ ] `lang_bp` blueprint nuovo, registrato in `app.py`, CSRF-esente
- [ ] `pottery_routes.py` `FILTER_KEYS` estesa con `id_number`, `anno`
- [ ] Service onora i 2 nuovi filtri (cast int + ignore on `ValueError`)
- [ ] Pre-load media batch (`media_for_pottery_ids`) per evitare N+1

### Frontend
- [ ] `pottery/list.html` — 2 input nuovi + mini-carousel CSS scroll-snap + GLightbox bind
- [ ] `pottery/detail.html` — `#pottery-media-grid` con thumb 120×120 + GLightbox
- [ ] `components/language_switcher.html` — POST form via `/set-language/<lang>`

### Test
- [ ] 7+ test (2 lang, 4 filtri pottery, 1 media batch)
- [ ] 447 esistenti restano verdi (no regression)

### Release
- [ ] Bump 2.5.0 → 2.5.1 (patch — UI fix + new filters, no breaking API)
- [ ] CHANGELOG entry IT+EN

## 9. Backwards compat

- URL `/pottery/?lang=it` continua a funzionare: `get_locale()` legge
  ancora `request.args.get('lang')` come prima opzione.
- Vecchi link al detail/list senza nuovi filtri funzionano (Optional).
- Niente API breaking.

## 10. Riferimenti

- Spec 2 (paradata_ui_bp, pattern blueprint CSRF-esente)
- Spec 3-bis (harris_creator_bp, pattern session in form)
- Spec 7 (yed_import_bp + CSRF exemption + `app.register_blueprint`)
- Esistente `i18n/flask_babel_config.py:get_locale()` — priorità URL > session > cookie > Accept-Language > default 'it'
- Esistente `components/language_switcher.html` — link `<a>` (sostituito)
- Modello `Pottery` — `id_number INTEGER`, `anno INTEGER` (già presenti)
- `media_table` o `pottery_media_table` — schema da verificare a implementazione
