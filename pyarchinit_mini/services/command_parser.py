"""
Command Parser for 3D Builder Chat

Parses natural language commands and converts them to MCP tool calls.
Simple pattern-based parser - can be enhanced with Claude API later.
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger(__name__)


class CommandParser:
    """
    Parses user commands and converts to MCP tool calls

    Examples:
        "Crea US 1,2,3" -> build_3d(us_ids=[1,2,3])
        "Mostra solo periodo Romano" -> filter(period="Romano")
        "Nascondi US 5" -> filter(hide_us=[5])
    """

    # Command patterns
    PATTERNS = {
        # Build 3D
        r"(?:crea|genera|costruisci|build).*?us\s+([\d,\s]+)": "build_us",
        r"(?:crea|genera|costruisci|build).*?(?:tutto|all|completo|everything)": "build_all",
        r"(?:crea|genera|costruisci|build).*?graphml": "build_from_graphml",

        # Filter
        r"(?:filtra|mostra solo|show only).*?periodo\s+(\w+)": "filter_period",
        r"(?:nascondi|hide).*?us\s+([\d,\s]+)": "hide_us",
        r"(?:mostra|show).*?us\s+([\d,\s]+)": "show_us",

        # Export
        r"(?:esporta|export).*?(\.blend|\.glb|\.obj)": "export",

        # Material/Color
        r"(?:colora|color).*?us\s+(\d+).*?(#[\da-fA-F]{6}|\w+)": "color_us",
        r"(?:trasparenza|transparency).*?(\d+)": "set_transparency",
    }

    def parse(self, command: str) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Parse command and return list of tool calls

        Args:
            command: User command in natural language

        Returns:
            List of (tool_name, arguments) tuples
        """
        command = command.lower().strip()
        tool_calls = []

        for pattern, action in self.PATTERNS.items():
            match = re.search(pattern, command, re.IGNORECASE)
            if match:
                tool_call = self._action_to_tool_call(action, match)
                if tool_call:
                    tool_calls.append(tool_call)
                    logger.info(f"Matched pattern: {action}")

        if not tool_calls:
            logger.warning(f"No pattern matched for command: {command}")

        return tool_calls

    def _action_to_tool_call(
        self,
        action: str,
        match: re.Match
    ) -> Optional[Tuple[str, Dict[str, Any]]]:
        """Convert action to tool call"""

        # Build actions
        if action == "build_us":
            us_ids = self._parse_us_list(match.group(1))
            return ("build_3d", {"us_ids": us_ids, "mode": "selected"})

        elif action == "build_all":
            return ("build_3d", {"mode": "all"})

        elif action == "build_from_graphml":
            return ("build_3d", {"mode": "graphml"})

        # Filter actions
        elif action == "filter_period":
            period = match.group(1).strip()
            return ("filter", {"filter_type": "period", "period": period})

        elif action == "hide_us":
            us_ids = self._parse_us_list(match.group(1))
            return ("filter", {"filter_type": "hide_us", "us_ids": us_ids})

        elif action == "show_us":
            us_ids = self._parse_us_list(match.group(1))
            return ("filter", {"filter_type": "show_us", "us_ids": us_ids})

        # Export actions
        elif action == "export":
            format_ext = match.group(1)
            export_format = format_ext.replace(".", "")
            return ("export", {"format": export_format})

        # Material actions
        elif action == "color_us":
            us_id = int(match.group(1))
            color = match.group(2)
            return ("material", {
                "us_id": us_id,
                "material_type": "color",
                "color": color
            })

        elif action == "set_transparency":
            transparency = int(match.group(1)) / 100.0  # Convert to 0-1
            return ("filter", {
                "filter_type": "transparency",
                "value": transparency
            })

        return None

    def _parse_us_list(self, us_str: str) -> List[int]:
        """Parse comma-separated US list"""
        us_ids = []
        for part in us_str.split(","):
            part = part.strip()
            if part.isdigit():
                us_ids.append(int(part))
        return us_ids

    def get_help(self) -> str:
        """Get help text with command examples"""
        return """
        Comandi Disponibili:

        **Costruzione 3D:**
        - "Crea US 1,2,3" - Crea proxy per US specifiche
        - "Costruisci tutto" - Crea tutte le US
        - "Genera dal GraphML" - Usa il GraphML per costruire

        **Filtri:**
        - "Mostra solo periodo Romano" - Filtra per periodo
        - "Nascondi US 5,6" - Nascondi US specifiche
        - "Mostra US 1,2,3" - Mostra solo queste US
        - "Trasparenza 50" - Imposta trasparenza al 50%

        **Export:**
        - "Esporta come .blend" - Esporta modello Blender
        - "Export .glb" - Esporta come glTF

        **Materiali:**
        - "Colora US 3 rosso" - Colora una US
        - "Color US 5 #FF0000" - Usa colore HEX
        """
