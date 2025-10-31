"""
Stratigraphic Model Prompt

Template for generating stratigraphic 3D models.
"""

from typing import Dict, Any
from .base_prompt import BasePrompt


class StratigraphicModelPrompt(BasePrompt):
    """Stratigraphic Model Prompt"""

    def __init__(self, db_session, config):
        super().__init__(config)
        self.db_session = db_session

    def to_prompt_description(self) -> Dict[str, Any]:
        return {
            "name": "stratigraphic_model",
            "description": "Template for generating stratigraphic 3D models",
        }

    async def get(self, arguments: Dict[str, str]) -> Dict[str, Any]:
        return {"messages": [{"role": "user", "content": "Stratigraphic Model Prompt - Implementation pending"}]}
