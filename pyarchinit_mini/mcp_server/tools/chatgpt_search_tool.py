"""
ChatGPT Search Tool

Implements the 'search' tool required by ChatGPT MCP integration.
Searches archaeological stratigraphic data and returns results in ChatGPT format.
"""

import logging
import json
from typing import Dict, Any, List
from .base_tool import BaseTool, ToolDescription

logger = logging.getLogger(__name__)


class ChatGPTSearchTool(BaseTool):
    """Search tool for ChatGPT integration"""

    def to_tool_description(self) -> ToolDescription:
        return ToolDescription(
            name="search",
            description="Search archaeological stratigraphic data including sites, US (stratigraphic units), and relationships",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for archaeological data"
                    }
                },
                "required": ["query"],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute search and return results in ChatGPT format"""
        try:
            query = arguments.get("query", "")
            if not query:
                return self._format_chatgpt_response([])

            logger.info(f"ChatGPT search: {query}")

            # Search across sites and US
            results = []

            # Search sites
            site_results = self._search_sites(query)
            results.extend(site_results)

            # Search US (stratigraphic units)
            us_results = self._search_us(query)
            results.extend(us_results)

            # Limit to top 10 results
            results = results[:10]

            return self._format_chatgpt_response(results)

        except Exception as e:
            logger.error(f"ChatGPT search error: {str(e)}", exc_info=True)
            return self._format_chatgpt_response([])

    def _search_sites(self, query: str) -> List[Dict[str, str]]:
        """Search sites"""
        from pyarchinit_mini.models.site import Site

        results = []
        try:
            query_lower = query.lower()
            sites = self.db_session.query(Site).filter(
                Site.sito.ilike(f"%{query_lower}%") |
                Site.definizione_sito.ilike(f"%{query_lower}%") |
                Site.descrizione.ilike(f"%{query_lower}%")
            ).limit(5).all()

            for site in sites:
                results.append({
                    "id": f"site-{site.id_sito}",
                    "title": f"Site: {site.sito}",
                    "url": f"pyarchinit://site/{site.id_sito}"
                })
        except Exception as e:
            logger.error(f"Site search error: {e}")

        return results

    def _search_us(self, query: str) -> List[Dict[str, str]]:
        """Search stratigraphic units"""
        from pyarchinit_mini.models.us import US

        results = []
        try:
            query_lower = query.lower()
            units = self.db_session.query(US).filter(
                US.sito.ilike(f"%{query_lower}%") |
                US.us.ilike(f"%{query_lower}%") |
                US.d_stratigrafica.ilike(f"%{query_lower}%") |
                US.unita_tipo.ilike(f"%{query_lower}%")
            ).limit(5).all()

            for unit in units:
                title = f"US {unit.us} ({unit.sito})"
                if unit.unita_tipo:
                    title += f" - {unit.unita_tipo}"

                results.append({
                    "id": f"us-{unit.id_us}",
                    "title": title,
                    "url": f"pyarchinit://us/{unit.id_us}"
                })
        except Exception as e:
            logger.error(f"US search error: {e}")

        return results

    def _format_chatgpt_response(self, results: List[Dict[str, str]]) -> Dict[str, Any]:
        """Format response in ChatGPT MCP format"""
        # ChatGPT expects: {"content": [{"type": "text", "text": "{\"results\":[...]}"}]}
        results_obj = {"results": results}
        results_json = json.dumps(results_obj)

        return {
            "content": [
                {
                    "type": "text",
                    "text": results_json
                }
            ]
        }
