"""
MCP Prompts

Prompts provide pre-defined templates for common tasks:
- stratigraphic_model: Template for generating stratigraphic 3D models
- period_visualization: Template for period-based visualization
- us_description: Template for describing stratigraphic units
"""

from .stratigraphic_model_prompt import StratigraphicModelPrompt
from .period_visualization_prompt import PeriodVisualizationPrompt
from .us_description_prompt import USDescriptionPrompt

__all__ = [
    "StratigraphicModelPrompt",
    "PeriodVisualizationPrompt",
    "USDescriptionPrompt",
]
