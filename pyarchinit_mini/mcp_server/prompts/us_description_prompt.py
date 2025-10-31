"""
US Description Prompt

Template for describing stratigraphic units.
"""

from typing import Dict, Any
from .base_prompt import BasePrompt


class USDescriptionPrompt(BasePrompt):
    """US Description Prompt"""

    def __init__(self, us_service, config):
        super().__init__(config)
        self.us_service = us_service

    def to_prompt_description(self) -> Dict[str, Any]:
        return {
            "name": "us_description",
            "description": "Template for describing stratigraphic units",
        }

    async def get(self, arguments: Dict[str, str]) -> Dict[str, Any]:
        return {"messages": [{"role": "user", "content": "US Description Prompt - Implementation pending"}]}
