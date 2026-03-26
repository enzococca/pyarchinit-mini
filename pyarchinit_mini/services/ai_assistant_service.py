"""
AI Archaeological Assistant Service

Provides AI-powered analysis of archaeological data using configurable
LLM providers (OpenAI GPT or Anthropic Claude).
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Default models per provider (latest as of March 2026)
# OpenAI: gpt-5.4-mini (fast+cheap), gpt-5.4 (best), o4-mini (reasoning)
# Anthropic: claude-haiku-4-5 (cheapest), claude-sonnet-4-6 (fast), claude-opus-4-6 (best)
DEFAULT_MODELS = {
    "openai": "gpt-5.4-mini",
    "anthropic": "claude-sonnet-4-6",
}
# All supported models for UI selection
AVAILABLE_MODELS = {
    "openai": ["gpt-5.4-mini", "gpt-5.4", "gpt-4.1-mini", "gpt-4.1", "o4-mini"],
    "anthropic": ["claude-haiku-4-5", "claude-sonnet-4-6", "claude-opus-4-6"],
}
# Models that use max_completion_tokens instead of max_tokens
_NEW_TOKEN_PARAM_MODELS = {"gpt-5.4", "gpt-5.4-mini", "o4-mini", "o3", "o3-mini", "o1", "o1-mini"}

SYSTEM_PROMPT_IT = """Sei un assistente archeologico esperto per il sistema PyArchInit.
Aiuti ad analizzare dati stratigrafici, materiali, cronologia e informazioni sui siti.

REGOLE DI FORMATTAZIONE (OBBLIGATORIE):
- Rispondi SEMPRE in HTML ben formattato (non markdown).
- Usa <h4> per i titoli di sezione, <h5> per i sottotitoli.
- Usa <p> per i paragrafi, <ul>/<li> per le liste.
- Per le tabelle usa <table class="table table-sm table-striped"><thead>...<tbody>...
- Per i dati importanti usa <strong> o <span class="badge bg-info">.
- Quando menzioni una US, crea un link: <a href="/us?sito=NOME_SITO&us_number=NUMERO">US NUMERO</a>
- Quando menzioni un materiale, crea un link: <a href="/inventario">Inv. NUMERO</a>
- NON usare markdown (no #, no **, no ```). Solo HTML pulito.
- Struttura la risposta con sezioni chiare, titoli e paragrafi.
"""

SYSTEM_PROMPT_EN = """You are an expert archaeological assistant for the PyArchInit system.
You help analyze stratigraphic data, materials, chronology, and site information.

FORMATTING RULES (MANDATORY):
- ALWAYS respond in well-formatted HTML (not markdown).
- Use <h4> for section titles, <h5> for subtitles.
- Use <p> for paragraphs, <ul>/<li> for lists.
- For tables use <table class="table table-sm table-striped"><thead>...<tbody>...
- For important data use <strong> or <span class="badge bg-info">.
- When mentioning a US, create a link: <a href="/us?sito=SITE_NAME&us_number=NUMBER">US NUMBER</a>
- When mentioning a material, create a link: <a href="/inventario">Inv. NUMBER</a>
- Do NOT use markdown (no #, no **, no ```). Only clean HTML.
- Structure the response with clear sections, titles, and paragraphs.
"""

def _get_system_prompt(lang='it'):
    return SYSTEM_PROMPT_IT if lang == 'it' else SYSTEM_PROMPT_EN


class AIAssistantService:
    """Service for AI-powered archaeological analysis.

    Configuration via environment variables:
        AI_PROVIDER  - 'openai' or 'anthropic' (default: 'openai')
        AI_API_KEY   - API key for the chosen provider
        AI_MODEL     - Model name override (optional)
    """

    def __init__(self):
        self.provider: str = os.environ.get("AI_PROVIDER", "openai").lower()
        self.api_key: str = os.environ.get("AI_API_KEY", "")
        self.model: str = os.environ.get(
            "AI_MODEL", DEFAULT_MODELS.get(self.provider, "gpt-4o-mini")
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def ask(self, question: str, context: Optional[Dict[str, Any]] = None, lang: str = 'it') -> str:
        """Ask the AI assistant a free-form question.

        Args:
            question: The user's question.
            context: Optional dict with site/US/material data for grounding.
            lang: 'it' or 'en' for response language.

        Returns:
            HTML-formatted AI response, or an error message string.
        """
        system = _get_system_prompt(lang)
        if context:
            # Add site name for link generation
            site_name = context.get('site', {}).get('sito', '') if isinstance(context.get('site'), dict) else ''
            if site_name:
                system += f"\n\nSite name for links: {site_name}"
            system += "\n\nContext data:\n" + json.dumps(context, indent=2, default=str)[:8000]

        return self._call_llm(system_prompt=system, user_message=question)

    def generate_report_summary(
        self,
        site_data: Dict[str, Any],
        us_list: List[Any],
        inv_list: List[Any],
        lang: str = 'it',
    ) -> str:
        """Generate a professional archaeological summary report.

        Args:
            site_data: Dictionary with site metadata.
            us_list: List of stratigraphic-unit records (dicts or objects).
            inv_list: List of inventory/material records.

        Returns:
            A formatted summary string.
        """
        context_parts = [
            "Site information:",
            json.dumps(site_data, indent=2, default=str),
            f"\nNumber of stratigraphic units: {len(us_list)}",
        ]
        if us_list:
            context_parts.append("Stratigraphic units data:")
            context_parts.append(json.dumps(us_list[:50], indent=2, default=str))
        context_parts.append(f"\nNumber of inventory items: {len(inv_list)}")
        if inv_list:
            context_parts.append("Inventory data:")
            context_parts.append(json.dumps(inv_list[:50], indent=2, default=str))

        site_name = site_data.get('sito', '')
        if lang == 'it':
            user_message = (
                f"Basandoti sui seguenti dati archeologici del sito '{site_name}', "
                "scrivi un report archeologico professionale in HTML. Includi sezioni su: "
                "panoramica del sito, sequenza stratigrafica, cultura materiale, "
                "interpretazione preliminare. Crea link alle US menzionate. "
                "Usa tabelle HTML per i dati tabulari.\n\n"
                + "\n".join(context_parts)
            )
        else:
            user_message = (
                f"Based on the following archaeological data for site '{site_name}', "
                "write a professional archaeological summary report in HTML. Include sections on: "
                "site overview, stratigraphic sequence, material culture, and "
                "preliminary interpretation. Create links to mentioned US. "
                "Use HTML tables for tabular data.\n\n"
                + "\n".join(context_parts)
            )

        return self._call_llm(system_prompt=_get_system_prompt(lang), user_message=user_message)

    def analyze_stratigraphy(
        self, site_name: str, relationships: List[Any], lang: str = 'it'
    ) -> str:
        if lang == 'it':
            user_message = (
                f"Analizza la sequenza stratigrafica del sito '{site_name}'. "
                "Identifica le fasi principali, possibili disturbi, e suggerisci "
                "un'interpretazione della storia deposizionale. "
                "Crea link alle US menzionate nel formato HTML. Usa tabelle se utile.\n\n"
                "Relazioni stratigrafiche:\n"
                + json.dumps(relationships[:100], indent=2, default=str)
            )
        else:
            user_message = (
                f"Analyze the stratigraphic sequence for site '{site_name}'. "
                "Identify the main phases, possible disturbances, and suggest "
                "an interpretation of the depositional history. "
                "Create links to mentioned US in HTML format. Use tables if helpful.\n\n"
                "Stratigraphic relationships:\n"
                + json.dumps(relationships[:100], indent=2, default=str)
            )

        return self._call_llm(system_prompt=_get_system_prompt(lang), user_message=user_message)

    # ------------------------------------------------------------------
    # Provider helpers (lazy imports)
    # ------------------------------------------------------------------

    def _call_llm(self, system_prompt: str, user_message: str) -> str:
        """Route the request to the configured provider."""
        if not self.api_key:
            return (
                "Error: AI_API_KEY environment variable is not set. "
                "Please configure it with your API key."
            )

        try:
            if self.provider == "anthropic":
                return self._call_anthropic(system_prompt, user_message)
            else:
                return self._call_openai(system_prompt, user_message)
        except Exception as exc:  # noqa: BLE001
            logger.exception("AI assistant call failed")
            return f"Error communicating with AI provider: {exc}"

    def _call_openai(self, system_prompt: str, user_message: str) -> str:
        """Call the OpenAI chat completions API."""
        try:
            import openai  # lazy import
        except ImportError:
            return (
                "Error: the 'openai' package is not installed. "
                "Run: pip install openai"
            )

        client = openai.OpenAI(api_key=self.api_key)
        params = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.1,
        }
        # GPT-5.4, o-series use max_completion_tokens; older models use max_tokens
        if self.model in _NEW_TOKEN_PARAM_MODELS:
            params["max_completion_tokens"] = 4096
        else:
            params["max_tokens"] = 4096
        response = client.chat.completions.create(**params)
        return response.choices[0].message.content

    def _call_anthropic(self, system_prompt: str, user_message: str) -> str:
        """Call the Anthropic messages API."""
        try:
            import anthropic  # lazy import
        except ImportError:
            return (
                "Error: the 'anthropic' package is not installed. "
                "Run: pip install anthropic"
            )

        client = anthropic.Anthropic(api_key=self.api_key)
        response = client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_message},
            ],
        )
        return response.content[0].text
