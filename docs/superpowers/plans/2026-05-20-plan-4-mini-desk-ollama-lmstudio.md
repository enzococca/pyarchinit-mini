# Mini-desk Ollama + LM Studio LLM Providers Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend mini-desk's AI service from 2 cloud providers (openai, anthropic) to 4 (+ ollama, + lmstudio) with async local model discovery, mirroring the QGIS plugin's `LLMProvider` pattern. Admin UI dropdown extended. 4 integration tests added.

**Architecture:** Refactor `pyarchinit_mini/services/ai_assistant_service.py` to introduce `LLMProvider` enum + `PROVIDER_DEFAULTS` dict (matching the plugin shape). New `pyarchinit_mini/services/local_llm_discovery.py` does HTTP probes against `http://localhost:11434/v1/models` (Ollama) and `http://localhost:1234/v1/models` (LM Studio). UI dropdown re-rendered per provider.

**Tech Stack:** Python 3.11+, FastAPI, httpx (async HTTP), pytest, pytest-httpx for discovery mocks.

**Independent of bridge work** — mergeable as own tag `2.10.0-llm-locals` or folded into `3.0.0-bridge-migration`.

**Spec reference:** [`docs/superpowers/specs/2026-05-20-s3dgraphy-bridge-design.md`](../specs/2026-05-20-s3dgraphy-bridge-design.md) Appendix 1.

---

## Pre-flight

- [ ] Branch off `master`: `git checkout -b plan-4-mini-desk-ollama-lmstudio`.
- [ ] Verify baseline tests pass: `cd /Users/enzo/pyarchinit-mini-desk && pytest tests/integration/test_admin_ai_settings_routes.py -v` → all green.
- [ ] Ensure `pytest-httpx` installed: `pip show pytest-httpx || pip install pytest-httpx>=0.30`.
- [ ] Add `httpx>=0.27` and `pytest-httpx>=0.30` to `requirements.txt` and `requirements-dev.txt` respectively if missing.

Expected output:
```
$ pytest tests/integration/test_admin_ai_settings_routes.py -v
============ N passed in X.XXs ============
```

---

## Task 1 — Introduce `LLMProvider` enum + `PROVIDER_DEFAULTS` scaffolding

**Why:** Match the plugin shape (`modules/utility/llm_providers.py`) so the bridge migration in Plan 2 has a symmetric API to refer to.

- [ ] Write failing test `tests/unit/test_llm_provider_enum.py`:

```python
import pytest
from pyarchinit_mini.services.ai_assistant_service import LLMProvider, PROVIDER_DEFAULTS

def test_enum_has_four_members():
    assert {m.value for m in LLMProvider} == {"openai", "anthropic", "ollama", "lmstudio"}

def test_provider_defaults_keys():
    for p in LLMProvider:
        d = PROVIDER_DEFAULTS[p]
        assert "base_url" in d
        assert "needs_api_key" in d
        assert "is_local" in d
        assert "default_models" in d
```

- [ ] Run: `pytest tests/unit/test_llm_provider_enum.py -v` → must fail with ImportError.

- [ ] Edit `pyarchinit_mini/services/ai_assistant_service.py` — add at top after imports, before `DEFAULT_MODELS`:

```python
from enum import Enum

class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    LMSTUDIO = "lmstudio"

PROVIDER_DEFAULTS: dict = {}  # populated in Tasks 2 + 3
```

- [ ] Re-run unit test — `test_enum_has_four_members` passes, `test_provider_defaults_keys` still fails (empty dict). Defer second assertion to Task 3.

- [ ] Run full suite once: `pytest tests/ -x` — must remain green (no regressions). Commit.

---

## Task 2 — Populate `PROVIDER_DEFAULTS[OPENAI]` and `PROVIDER_DEFAULTS[ANTHROPIC]`

**Why:** Move the existing `DEFAULT_MODELS` + `AVAILABLE_MODELS` literals into the new dict so there is a single source of truth. Keep the old names as aliases for backwards compatibility until Task 7 stops reading them.

- [ ] Edit `ai_assistant_service.py`:

```python
PROVIDER_DEFAULTS = {
    LLMProvider.OPENAI: {
        "base_url": "https://api.openai.com/v1",
        "needs_api_key": True,
        "is_local": False,
        "default_model": "gpt-5.5-mini",
        "default_models": [
            "gpt-5.5", "gpt-5.5-mini", "gpt-5.4", "gpt-5.4-mini",
            "gpt-4.1", "gpt-4.1-mini", "o4-mini",
        ],
    },
    LLMProvider.ANTHROPIC: {
        "base_url": "https://api.anthropic.com",
        "needs_api_key": True,
        "is_local": False,
        "default_model": "claude-sonnet-4-7",
        "default_models": [
            "claude-opus-4-7", "claude-sonnet-4-7", "claude-haiku-4-5",
            "claude-opus-4-6", "claude-sonnet-4-6",
        ],
    },
}

# Back-compat aliases (deprecated, removed once UI fully migrated in Task 7)
DEFAULT_MODELS = {p.value: PROVIDER_DEFAULTS[p]["default_model"]
                  for p in (LLMProvider.OPENAI, LLMProvider.ANTHROPIC)}
AVAILABLE_MODELS = {p.value: PROVIDER_DEFAULTS[p]["default_models"]
                    for p in (LLMProvider.OPENAI, LLMProvider.ANTHROPIC)}
```

- [ ] Run full suite — must stay green. Commit.

---

## Task 3 — Add `OLLAMA` + `LMSTUDIO` entries

- [ ] Extend `PROVIDER_DEFAULTS`:

```python
PROVIDER_DEFAULTS[LLMProvider.OLLAMA] = {
    "base_url": "http://localhost:11434/v1",
    "needs_api_key": False,
    "is_local": True,
    "default_model": "",
    "default_models": [],
}
PROVIDER_DEFAULTS[LLMProvider.LMSTUDIO] = {
    "base_url": "http://localhost:1234/v1",
    "needs_api_key": False,
    "is_local": True,
    "default_model": "",
    "default_models": [],
}
```

- [ ] Re-run `tests/unit/test_llm_provider_enum.py` — both tests pass.

- [ ] Add one more unit case:

```python
def test_local_providers_no_api_key():
    assert PROVIDER_DEFAULTS[LLMProvider.OLLAMA]["needs_api_key"] is False
    assert PROVIDER_DEFAULTS[LLMProvider.LMSTUDIO]["needs_api_key"] is False
    assert PROVIDER_DEFAULTS[LLMProvider.OLLAMA]["base_url"].endswith(":11434/v1")
    assert PROVIDER_DEFAULTS[LLMProvider.LMSTUDIO]["base_url"].endswith(":1234/v1")
```

- [ ] Run, verify green. Commit.

---

## Task 4 — New module `local_llm_discovery.py` (async HTTP probe)

**Why:** Ollama exposes `/v1/models` (OpenAI-compat) and a richer `/api/tags` (native). LM Studio exposes only `/v1/models`. Probe both via the OpenAI-compat endpoint so a single code path works.

- [ ] Write failing test `tests/unit/test_local_llm_discovery.py`:

```python
import pytest
from pyarchinit_mini.services.local_llm_discovery import discover_models
from pyarchinit_mini.services.ai_assistant_service import LLMProvider

OPENAI_COMPAT_PAYLOAD = {
    "object": "list",
    "data": [
        {"id": "llama3.2:3b", "object": "model"},
        {"id": "qwen2.5:7b", "object": "model"},
    ],
}

@pytest.mark.asyncio
async def test_discover_ollama_returns_models(httpx_mock):
    httpx_mock.add_response(
        url="http://localhost:11434/v1/models",
        json=OPENAI_COMPAT_PAYLOAD,
    )
    models = await discover_models(LLMProvider.OLLAMA, timeout=2.0)
    assert models == ["llama3.2:3b", "qwen2.5:7b"]

@pytest.mark.asyncio
async def test_discover_lmstudio_returns_models(httpx_mock):
    httpx_mock.add_response(
        url="http://localhost:1234/v1/models",
        json={"object": "list", "data": [{"id": "mistral-7b-instruct"}]},
    )
    models = await discover_models(LLMProvider.LMSTUDIO, timeout=2.0)
    assert models == ["mistral-7b-instruct"]

@pytest.mark.asyncio
async def test_discover_server_down_returns_empty(httpx_mock):
    import httpx
    httpx_mock.add_exception(httpx.ConnectError("connection refused"))
    models = await discover_models(LLMProvider.OLLAMA, timeout=0.5)
    assert models == []

@pytest.mark.asyncio
async def test_discover_cloud_provider_raises():
    with pytest.raises(ValueError, match="not a local provider"):
        await discover_models(LLMProvider.OPENAI)
```

- [ ] Run: `pytest tests/unit/test_local_llm_discovery.py -v` → ImportError (module missing).

- [ ] Create `pyarchinit_mini/services/local_llm_discovery.py`:

```python
"""Async discovery of locally-installed LLM models (Ollama, LM Studio).

Both servers expose an OpenAI-compatible `/v1/models` endpoint, so a single
HTTP GET handles them. Cloud providers (OpenAI, Anthropic) are rejected —
their model lists are static and live in ``PROVIDER_DEFAULTS``.
"""
from __future__ import annotations

import logging
from typing import List

import httpx

from pyarchinit_mini.services.ai_assistant_service import (
    LLMProvider,
    PROVIDER_DEFAULTS,
)

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT_SECONDS = 3.0


async def discover_models(
    provider: LLMProvider,
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> List[str]:
    """Return the list of model ids the local provider currently serves.

    Returns ``[]`` (never raises) when the server is unreachable, so the
    admin UI can render a "no models found" state.

    Raises ``ValueError`` if called with a cloud provider — caller bug.
    """
    cfg = PROVIDER_DEFAULTS[provider]
    if not cfg.get("is_local"):
        raise ValueError(f"{provider.value} is not a local provider")

    url = f"{cfg['base_url'].rstrip('/')}/models"
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            payload = resp.json()
    except (httpx.HTTPError, ValueError) as exc:
        logger.info("discover_models(%s) failed: %s", provider.value, exc)
        return []

    data = payload.get("data", []) if isinstance(payload, dict) else []
    return [item["id"] for item in data if isinstance(item, dict) and "id" in item]
```

- [ ] Add `pytest-asyncio` config in `pyproject.toml` if not already present:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

- [ ] Run: `pytest tests/unit/test_local_llm_discovery.py -v` → all 4 pass.

- [ ] Commit.

---

## Task 5 — Wire discovery into `LLMProviderManager`

**Why:** Single import surface for callers (admin route in Task 7, future bridge consumers).

- [ ] Check whether `LLMProviderManager` already exists in `ai_assistant_service.py`:

```bash
grep -n "class LLMProviderManager" pyarchinit_mini/services/ai_assistant_service.py
```

If not present, create the minimal class:

- [ ] Append to `ai_assistant_service.py`:

```python
class LLMProviderManager:
    """Thin facade exposing provider metadata + async discovery."""

    @staticmethod
    def list_providers() -> list[LLMProvider]:
        return list(LLMProvider)

    @staticmethod
    def defaults_for(provider: LLMProvider) -> dict:
        return PROVIDER_DEFAULTS[provider]

    @staticmethod
    async def discover_models(provider: LLMProvider, timeout: float = 3.0) -> list[str]:
        from pyarchinit_mini.services.local_llm_discovery import discover_models
        return await discover_models(provider, timeout=timeout)

    @staticmethod
    def available_models(provider: LLMProvider) -> list[str]:
        """Sync helper returning cached static list (cloud) or empty for local
        (caller must use ``discover_models`` for live local data)."""
        return list(PROVIDER_DEFAULTS[provider]["default_models"])
```

- [ ] Add test `tests/unit/test_llm_provider_manager.py`:

```python
import pytest
from pyarchinit_mini.services.ai_assistant_service import (
    LLMProvider, LLMProviderManager,
)

def test_list_providers():
    assert len(LLMProviderManager.list_providers()) == 4

def test_available_models_cloud():
    assert "gpt-5.5-mini" in LLMProviderManager.available_models(LLMProvider.OPENAI)
    assert "claude-sonnet-4-7" in LLMProviderManager.available_models(LLMProvider.ANTHROPIC)

def test_available_models_local_empty():
    assert LLMProviderManager.available_models(LLMProvider.OLLAMA) == []
    assert LLMProviderManager.available_models(LLMProvider.LMSTUDIO) == []

@pytest.mark.asyncio
async def test_manager_discover_models_delegates(httpx_mock):
    httpx_mock.add_response(
        url="http://localhost:11434/v1/models",
        json={"data": [{"id": "llama3.2:3b"}]},
    )
    out = await LLMProviderManager.discover_models(LLMProvider.OLLAMA)
    assert out == ["llama3.2:3b"]
```

- [ ] Run: `pytest tests/unit/test_llm_provider_manager.py -v` → all pass. Commit.

---

## Task 6 — Verify `max_completion_tokens` routing still applies (cloud only)

**Why:** GPT-5 family + o-series require `max_completion_tokens`. Local OpenAI-compat servers expect plain `max_tokens`. Mistake routing breaks both.

- [ ] Confirm current set in `ai_assistant_service.py`:

```python
_NEW_TOKEN_PARAM_MODELS = {
    "gpt-5.5", "gpt-5.5-mini", "gpt-5.4", "gpt-5.4-mini",
    "o4-mini", "o3", "o3-mini", "o1", "o1-mini",
}
```

- [ ] Add helper if not present:

```python
def _token_param_name(provider: LLMProvider, model: str) -> str:
    """Return 'max_completion_tokens' for cloud OpenAI GPT-5/o-series,
    'max_tokens' otherwise (including local OpenAI-compat servers)."""
    if provider is LLMProvider.OPENAI and model in _NEW_TOKEN_PARAM_MODELS:
        return "max_completion_tokens"
    return "max_tokens"
```

- [ ] Add test `tests/unit/test_token_param_routing.py`:

```python
from pyarchinit_mini.services.ai_assistant_service import (
    LLMProvider, _token_param_name,
)

def test_gpt5_uses_max_completion_tokens():
    assert _token_param_name(LLMProvider.OPENAI, "gpt-5.5") == "max_completion_tokens"
    assert _token_param_name(LLMProvider.OPENAI, "o4-mini") == "max_completion_tokens"

def test_gpt4_uses_max_tokens():
    assert _token_param_name(LLMProvider.OPENAI, "gpt-4.1") == "max_tokens"

def test_anthropic_always_max_tokens():
    assert _token_param_name(LLMProvider.ANTHROPIC, "claude-opus-4-7") == "max_tokens"

def test_ollama_always_max_tokens_even_for_gpt5_named_model():
    # Local OpenAI-compat servers expect max_tokens regardless of model id
    assert _token_param_name(LLMProvider.OLLAMA, "gpt-5.5") == "max_tokens"

def test_lmstudio_always_max_tokens():
    assert _token_param_name(LLMProvider.LMSTUDIO, "mistral-7b") == "max_tokens"
```

- [ ] Run, verify all 5 pass. If existing call sites in `ai_assistant_service.py` build request payloads directly with the literal `"max_tokens"` / `"max_completion_tokens"` key, refactor them to use `_token_param_name(provider, model)`. Re-run full suite.

- [ ] Commit.

---

## Task 7 — Admin UI: extend dropdown to 4 providers + "Refresh models" button

**Why:** Without UI exposure the new providers are invisible to users.

- [ ] Locate the AI settings template and route:

```bash
grep -rn "admin/settings/ai" pyarchinit_mini/ --include="*.py"
grep -rn "DEFAULT_MODELS\|AVAILABLE_MODELS" pyarchinit_mini/web_interface/templates/
```

Expected discovery: `pyarchinit_mini/api/admin_ai_settings.py` (or equivalent route file) and a Jinja template under `pyarchinit_mini/web_interface/templates/admin/ai_settings.html` (exact name to be confirmed by the grep above — adjust references below accordingly).

- [ ] Edit the template — replace the existing 2-option `<select name="provider">` with:

```html
<label for="provider">{{ _("LLM Provider") }}</label>
<select name="provider" id="provider"
        onchange="onProviderChange(this.value)">
  {% for p in providers %}
    <option value="{{ p.value }}"
            {% if p.value == current_provider %}selected{% endif %}>
      {{ p.value | capitalize }}
    </option>
  {% endfor %}
</select>

<div id="local-fields" style="display:{{ 'block' if is_local else 'none' }}">
  <label for="base_url">{{ _("Base URL") }}</label>
  <input type="text" name="base_url" id="base_url"
         value="{{ current_base_url }}">
  <button type="button" onclick="refreshModels()">
    {{ _("Refresh models") }}
  </button>
  <span id="discovery-status"></span>
</div>

<label for="model">{{ _("Model") }}</label>
<select name="model" id="model">
  {% for m in available_models %}
    <option value="{{ m }}"
            {% if m == current_model %}selected{% endif %}>{{ m }}</option>
  {% endfor %}
</select>

<div id="api-key-field" style="display:{{ 'none' if is_local else 'block' }}">
  <label for="api_key">{{ _("API Key") }}</label>
  <input type="password" name="api_key" id="api_key"
         placeholder="{{ masked_api_key }}">
</div>

<script>
const LOCAL_PROVIDERS = ["ollama", "lmstudio"];
function onProviderChange(p) {
  const isLocal = LOCAL_PROVIDERS.includes(p);
  document.getElementById("local-fields").style.display = isLocal ? "block" : "none";
  document.getElementById("api-key-field").style.display = isLocal ? "none" : "block";
}
async function refreshModels() {
  const p = document.getElementById("provider").value;
  const status = document.getElementById("discovery-status");
  status.textContent = "{{ _('Discovering…') }}";
  const resp = await fetch(`/admin/settings/ai/discover?provider=${p}`);
  const j = await resp.json();
  const sel = document.getElementById("model");
  sel.innerHTML = "";
  for (const m of (j.models || [])) {
    const opt = document.createElement("option");
    opt.value = m; opt.textContent = m;
    sel.appendChild(opt);
  }
  status.textContent = j.models?.length
    ? `{{ _('Found') }} ${j.models.length}`
    : "{{ _('No models found — is the server running?') }}";
}
</script>
```

- [ ] Edit the route handler in `pyarchinit_mini/api/admin_ai_settings.py` (or the actual location found via grep):

```python
from flask import Blueprint, jsonify, render_template, request
import asyncio

from pyarchinit_mini.services.ai_assistant_service import (
    LLMProvider, LLMProviderManager, PROVIDER_DEFAULTS,
)

bp = Blueprint("admin_ai_settings", __name__, url_prefix="/admin/settings/ai")


@bp.route("/", methods=["GET", "POST"])
def settings_page():
    # ... existing POST save logic untouched ...
    current_provider = _load_setting("ai_provider", "openai")
    current_model = _load_setting("ai_model", "")
    current_base_url = _load_setting(
        "ai_base_url",
        PROVIDER_DEFAULTS[LLMProvider(current_provider)]["base_url"],
    )
    provider_enum = LLMProvider(current_provider)
    is_local = PROVIDER_DEFAULTS[provider_enum]["is_local"]

    return render_template(
        "admin/ai_settings.html",
        providers=list(LLMProvider),
        current_provider=current_provider,
        current_model=current_model,
        current_base_url=current_base_url,
        is_local=is_local,
        available_models=LLMProviderManager.available_models(provider_enum),
        masked_api_key=_mask(_load_setting("ai_api_key", "")),
    )


@bp.route("/discover", methods=["GET"])
def discover():
    """Async-discover models for a local provider; returns JSON ``{models: [...]}``."""
    try:
        provider = LLMProvider(request.args.get("provider", ""))
    except ValueError:
        return jsonify({"error": "unknown provider", "models": []}), 400
    if not PROVIDER_DEFAULTS[provider]["is_local"]:
        # Cloud — return static list from defaults.
        return jsonify({"models": PROVIDER_DEFAULTS[provider]["default_models"]})
    models = asyncio.run(LLMProviderManager.discover_models(provider, timeout=3.0))
    return jsonify({"models": models})
```

- [ ] Manual smoke (optional but recommended):

```bash
cd /Users/enzo/pyarchinit-mini-desk
flask --app pyarchinit_mini.web_interface run --port 5050 &
curl http://localhost:5050/admin/settings/ai/discover?provider=ollama
# Expected on a machine without Ollama: {"models": []}
```

- [ ] Commit.

---

## Task 8 — Integration test: switch provider OpenAI → Ollama

- [ ] Add to `tests/integration/test_admin_ai_settings_routes.py`:

```python
def test_switch_provider_openai_to_ollama(db_manager, tmp_path, monkeypatch):
    app = _make_app(db_manager, tmp_path, monkeypatch)
    client = app.test_client()

    # Start with openai saved
    client.post("/admin/settings/ai", data={
        "provider": "openai", "model": "gpt-5.5-mini",
        "api_key": "sk-test", "csrf_token": "test-csrf-token",
    })

    # Switch to ollama with custom base_url
    resp = client.post("/admin/settings/ai", data={
        "provider": "ollama", "model": "",
        "base_url": "http://localhost:11434/v1",
        "csrf_token": "test-csrf-token",
    })
    assert resp.status_code in (200, 302)

    from pyarchinit_mini.services.app_setting_service import AppSettingService
    svc = AppSettingService(db_manager)
    assert svc.get("ai_provider") == "ollama"
    assert svc.get("ai_base_url") == "http://localhost:11434/v1"
```

- [ ] Run: `pytest tests/integration/test_admin_ai_settings_routes.py::test_switch_provider_openai_to_ollama -v` → pass. Commit.

---

## Task 9 — Integration test: discovery returns empty (server down)

- [ ] Add:

```python
def test_discover_endpoint_server_down_returns_empty(
    db_manager, tmp_path, monkeypatch, httpx_mock,
):
    import httpx as _httpx
    httpx_mock.add_exception(_httpx.ConnectError("refused"))

    app = _make_app(db_manager, tmp_path, monkeypatch)
    client = app.test_client()
    resp = client.get("/admin/settings/ai/discover?provider=ollama")
    assert resp.status_code == 200
    assert resp.get_json() == {"models": []}
```

- [ ] Run, verify pass. Commit.

---

## Task 10 — Integration test: model not loaded → graceful fallback

- [ ] Add:

```python
def test_model_not_loaded_falls_back_to_empty_select(
    db_manager, tmp_path, monkeypatch, httpx_mock,
):
    httpx_mock.add_response(
        url="http://localhost:11434/v1/models",
        json={"object": "list", "data": []},
    )
    app = _make_app(db_manager, tmp_path, monkeypatch)
    client = app.test_client()

    # Save a model that does not exist on the server
    client.post("/admin/settings/ai", data={
        "provider": "ollama", "model": "nonexistent:latest",
        "base_url": "http://localhost:11434/v1",
        "csrf_token": "test-csrf-token",
    })

    resp = client.get("/admin/settings/ai/discover?provider=ollama")
    assert resp.get_json() == {"models": []}

    # Settings page renders without 500 even though saved model isn't in list
    page = client.get("/admin/settings/ai")
    assert page.status_code == 200
    assert b"nonexistent:latest" in page.data  # preserved as <option>
```

- [ ] Run, verify pass. Commit.

---

## Task 11 — Integration test: model loaded → selection saved + persisted

- [ ] Add:

```python
def test_model_loaded_selection_persisted(
    db_manager, tmp_path, monkeypatch, httpx_mock,
):
    httpx_mock.add_response(
        url="http://localhost:11434/v1/models",
        json={"data": [{"id": "llama3.2:3b"}, {"id": "qwen2.5:7b"}]},
    )
    app = _make_app(db_manager, tmp_path, monkeypatch)
    client = app.test_client()

    resp = client.get("/admin/settings/ai/discover?provider=ollama")
    assert resp.get_json() == {"models": ["llama3.2:3b", "qwen2.5:7b"]}

    client.post("/admin/settings/ai", data={
        "provider": "ollama", "model": "llama3.2:3b",
        "base_url": "http://localhost:11434/v1",
        "csrf_token": "test-csrf-token",
    })

    from pyarchinit_mini.services.app_setting_service import AppSettingService
    svc = AppSettingService(db_manager)
    assert svc.get("ai_provider") == "ollama"
    assert svc.get("ai_model") == "llama3.2:3b"
    assert svc.get("ai_base_url") == "http://localhost:11434/v1"

    # Reload page renders saved selection
    page = client.get("/admin/settings/ai")
    assert b'value="llama3.2:3b"' in page.data
```

- [ ] Run all 4 new integration tests:

```bash
pytest tests/integration/test_admin_ai_settings_routes.py -v -k "switch_provider or discover_endpoint or model_not_loaded or model_loaded"
```

Expected: 4 passed.

- [ ] Run full suite: `pytest tests/ -x` — all green. Commit.

---

## Task 12 — CHANGELOG entry + version bump

- [ ] Open `CHANGELOG.md` (mini-desk). Insert a new section above the most recent entry:

```markdown
## [2.10.0-llm-locals] — 2026-05-XX

### IT
- **Aggiunto supporto provider LLM locali**: il pannello `/admin/settings/ai`
  ora elenca 4 provider (OpenAI, Anthropic, Ollama, LM Studio). Per i due
  provider locali viene mostrato il campo Base URL e il pulsante
  "Aggiorna modelli" che esegue il discovery asincrono dei modelli
  installati (`http://localhost:11434/v1/models` per Ollama,
  `http://localhost:1234/v1/models` per LM Studio).
- **API**: nuovo enum `LLMProvider` e dizionario `PROVIDER_DEFAULTS` in
  `pyarchinit_mini/services/ai_assistant_service.py`, allineati al plugin
  QGIS `modules/utility/llm_providers.py`.
- **Nuovo modulo**: `pyarchinit_mini/services/local_llm_discovery.py`
  espone `async def discover_models(provider, timeout)`.
- **Routing token**: confermato che `max_completion_tokens` resta
  riservato a OpenAI GPT-5 / o-series; tutti gli altri (Anthropic, Ollama,
  LM Studio) usano `max_tokens`.
- **Test**: 4 nuovi test di integrazione in
  `tests/integration/test_admin_ai_settings_routes.py` + 3 file di test
  unitari.

### EN
- **Added local LLM provider support**: `/admin/settings/ai` panel now
  lists 4 providers (OpenAI, Anthropic, Ollama, LM Studio). Local providers
  expose a Base URL field and a "Refresh models" button performing async
  discovery against `http://localhost:11434/v1/models` (Ollama) and
  `http://localhost:1234/v1/models` (LM Studio).
- **API**: new `LLMProvider` enum and `PROVIDER_DEFAULTS` dict in
  `pyarchinit_mini/services/ai_assistant_service.py`, mirroring the QGIS
  plugin's `modules/utility/llm_providers.py`.
- **New module**: `pyarchinit_mini/services/local_llm_discovery.py`
  exposes `async def discover_models(provider, timeout)`.
- **Token routing**: `max_completion_tokens` confirmed reserved for OpenAI
  GPT-5 / o-series; all others (Anthropic, Ollama, LM Studio) use
  `max_tokens`.
- **Tests**: 4 new integration tests in
  `tests/integration/test_admin_ai_settings_routes.py` + 3 unit-test files.
```

- [ ] Bump version. If mini-desk uses `pyarchinit_mini/__init__.py:__version__`:

```python
__version__ = "2.10.0-llm-locals"
```

If a `pyproject.toml` `[project]` table holds the version, update it there too.

- [ ] Tag suggestion (do NOT push without user confirmation):

```bash
git tag -a 2.10.0-llm-locals -m "LLM locals: Ollama + LM Studio providers"
```

Alternative: fold the bump into the upcoming `3.0.0-bridge-migration` tag — defer the bump and only land the CHANGELOG section if the bridge ships in the same release window.

- [ ] Commit (CHANGELOG + version bump).

---

## Self-Review Checklist

Run this after the last commit, before requesting code review:

- [ ] `pytest tests/ -v` → all green, including:
  - `tests/unit/test_llm_provider_enum.py` (3 tests)
  - `tests/unit/test_local_llm_discovery.py` (4 tests)
  - `tests/unit/test_llm_provider_manager.py` (4 tests)
  - `tests/unit/test_token_param_routing.py` (5 tests)
  - `tests/integration/test_admin_ai_settings_routes.py` (existing + 4 new)
- [ ] `python -c "from pyarchinit_mini.services.ai_assistant_service import LLMProvider, PROVIDER_DEFAULTS, LLMProviderManager; print(len(LLMProvider))"` → prints `4`.
- [ ] `python -c "import asyncio; from pyarchinit_mini.services.local_llm_discovery import discover_models; from pyarchinit_mini.services.ai_assistant_service import LLMProvider; print(asyncio.run(discover_models(LLMProvider.OLLAMA, timeout=1.0)))"` → prints `[]` (when no Ollama running) or a list of model ids (when running).
- [ ] Open `/admin/settings/ai` in browser:
  - Dropdown shows 4 options.
  - Selecting "Ollama" or "LM Studio" reveals Base URL field + "Refresh models" button and hides API key field.
  - Selecting "OpenAI" or "Anthropic" hides Base URL + shows API key field.
  - "Refresh models" button updates the model `<select>` without page reload.
- [ ] `_token_param_name(LLMProvider.OPENAI, "gpt-5.5")` returns `"max_completion_tokens"`; same call with `LLMProvider.OLLAMA` returns `"max_tokens"`.
- [ ] `grep -n "DEFAULT_MODELS\|AVAILABLE_MODELS" pyarchinit_mini/` — no production callers besides the back-compat aliases at the top of `ai_assistant_service.py`. (Aliases can be deleted in a follow-up if no one else imports them.)
- [ ] CHANGELOG entry present in both IT and EN.
- [ ] Version bump applied OR explicit note in PR description that bump is deferred to bridge release.

If every box is ticked, the plan is complete and ready for `requesting-code-review`.