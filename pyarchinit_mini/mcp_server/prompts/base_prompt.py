"""
Base Prompt Class

Abstract base class for all MCP prompts.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BasePrompt(ABC):
    """Base class for MCP Prompts"""

    def __init__(self, config):
        self.config = config

    @abstractmethod
    def to_prompt_description(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def get(self, arguments: Dict[str, str]) -> Dict[str, Any]:
        pass
