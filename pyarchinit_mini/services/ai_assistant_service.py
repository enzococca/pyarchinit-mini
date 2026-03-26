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

# Default models per provider
DEFAULT_MODELS = {
    "openai": "gpt-4o-mini",
    "anthropic": "claude-sonnet-4-6",
}

SYSTEM_PROMPT = (
    "You are an archaeological data assistant for the PyArchInit system. "
    "You help analyze stratigraphic data, materials, chronology, and site "
    "information. Answer in the same language as the question."
)


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

    def ask(self, question: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Ask the AI assistant a free-form question.

        Args:
            question: The user's question.
            context: Optional dict with keys like ``site_name``, ``us_data``,
                     ``inventory_data``, etc.  Included in the prompt so the
                     model can ground its answer.

        Returns:
            The AI response text, or an error message string on failure.
        """
        system = SYSTEM_PROMPT
        if context:
            system += "\n\nContext data:\n" + json.dumps(context, indent=2, default=str)

        return self._call_llm(system_prompt=system, user_message=question)

    def generate_report_summary(
        self,
        site_data: Dict[str, Any],
        us_list: List[Any],
        inv_list: List[Any],
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

        user_message = (
            "Based on the following archaeological data, write a professional "
            "archaeological summary report for this site. Include sections on: "
            "site overview, stratigraphic sequence, material culture, and "
            "preliminary interpretation. Be thorough but concise.\n\n"
            + "\n".join(context_parts)
        )

        return self._call_llm(system_prompt=SYSTEM_PROMPT, user_message=user_message)

    def analyze_stratigraphy(
        self, site_name: str, relationships: List[Any]
    ) -> str:
        """Ask the AI to analyse a stratigraphic sequence.

        Args:
            site_name: Name of the archaeological site.
            relationships: List of stratigraphic relationships (e.g.
                ``[{"us": 1, "covers": 2}, ...]``).

        Returns:
            Analysis text.
        """
        user_message = (
            f"Analyze the stratigraphic sequence for site '{site_name}'. "
            "Identify the main phases, possible disturbances, and suggest "
            "an interpretation of the depositional history.\n\n"
            "Stratigraphic relationships:\n"
            + json.dumps(relationships[:100], indent=2, default=str)
        )

        return self._call_llm(system_prompt=SYSTEM_PROMPT, user_message=user_message)

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
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.7,
            max_tokens=2048,
        )
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
