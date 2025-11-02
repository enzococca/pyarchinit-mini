"""
ChatGPT Fetch Tool

Implements the 'fetch' tool required by ChatGPT MCP integration.
Fetches complete document content for archaeological data.
"""

import logging
import json
from typing import Dict, Any, Optional
from .base_tool import BaseTool, ToolDescription

logger = logging.getLogger(__name__)


class ChatGPTFetchTool(BaseTool):
    """Fetch tool for ChatGPT integration"""

    def to_tool_description(self) -> ToolDescription:
        return ToolDescription(
            name="fetch",
            description="Fetch complete details for a specific archaeological site or stratigraphic unit",
            input_schema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Document ID (e.g., 'site-123' or 'us-456')"
                    }
                },
                "required": ["id"],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute fetch and return document in ChatGPT format"""
        try:
            doc_id = arguments.get("id", "")
            if not doc_id:
                return self._format_error("Document ID is required")

            logger.info(f"ChatGPT fetch: {doc_id}")

            # Parse ID format: "site-123" or "us-456"
            if doc_id.startswith("site-"):
                document = self._fetch_site(doc_id)
            elif doc_id.startswith("us-"):
                document = self._fetch_us(doc_id)
            else:
                return self._format_error(f"Invalid document ID format: {doc_id}")

            if not document:
                return self._format_error(f"Document not found: {doc_id}")

            return self._format_chatgpt_response(document)

        except Exception as e:
            logger.error(f"ChatGPT fetch error: {str(e)}", exc_info=True)
            return self._format_error(str(e))

    def _fetch_site(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Fetch site document"""
        from pyarchinit_mini.models.site import Site

        try:
            site_id = int(doc_id.replace("site-", ""))
            site = self.db_session.query(Site).filter_by(id_sito=site_id).first()

            if not site:
                return None

            # Build full text
            text_parts = [f"Site: {site.sito}"]

            if site.definizione_sito:
                text_parts.append(f"Definition: {site.definizione_sito}")

            if site.descrizione:
                text_parts.append(f"Description: {site.descrizione}")

            if site.nazione:
                text_parts.append(f"Nation: {site.nazione}")

            if site.comune:
                text_parts.append(f"Municipality: {site.comune}")

            if site.provincia:
                text_parts.append(f"Province: {site.provincia}")

            text = "\n\n".join(text_parts)

            return {
                "id": doc_id,
                "title": f"Site: {site.sito}",
                "text": text,
                "url": f"pyarchinit://site/{site.id_sito}",
                "metadata": {
                    "type": "site",
                    "nation": site.nazione or "",
                    "municipality": site.comune or "",
                    "province": site.provincia or ""
                }
            }
        except Exception as e:
            logger.error(f"Fetch site error: {e}")
            return None

    def _fetch_us(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Fetch stratigraphic unit document"""
        from pyarchinit_mini.models.us import US

        try:
            us_id = int(doc_id.replace("us-", ""))
            us = self.db_session.query(US).filter_by(id_us=us_id).first()

            if not us:
                return None

            # Build full text
            text_parts = [f"Stratigraphic Unit: {us.us}"]
            text_parts.append(f"Site: {us.sito}")

            if us.unita_tipo:
                text_parts.append(f"Unit Type: {us.unita_tipo}")

            if us.d_stratigrafica:
                text_parts.append(f"Stratigraphic Description: {us.d_stratigrafica}")

            if us.area:
                text_parts.append(f"Area: {us.area}")

            if us.periodo_iniziale:
                text_parts.append(f"Period: {us.periodo_iniziale}")

            if us.fase_iniziale:
                text_parts.append(f"Phase: {us.fase_iniziale}")

            if us.rapporti:
                text_parts.append(f"Relationships: {us.rapporti}")

            text = "\n\n".join(text_parts)

            return {
                "id": doc_id,
                "title": f"US {us.us} ({us.sito})",
                "text": text,
                "url": f"pyarchinit://us/{us.id_us}",
                "metadata": {
                    "type": "stratigraphic_unit",
                    "site": us.sito,
                    "unit_type": us.unita_tipo or "",
                    "area": us.area or "",
                    "period": us.periodo_iniziale or ""
                }
            }
        except Exception as e:
            logger.error(f"Fetch US error: {e}")
            return None

    def _format_chatgpt_response(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Format response in ChatGPT MCP format"""
        # ChatGPT expects: {"content": [{"type": "text", "text": "{\"id\":\"...\",\"title\":\"...\",\"text\":\"...\",\"url\":\"...\",\"metadata\":{}}"}]}
        doc_json = json.dumps(document)

        return {
            "content": [
                {
                    "type": "text",
                    "text": doc_json
                }
            ]
        }

    def _format_error(self, message: str) -> Dict[str, Any]:
        """Format error response"""
        error_doc = {
            "id": "error",
            "title": "Error",
            "text": message,
            "url": "",
            "metadata": {"error": True}
        }
        return self._format_chatgpt_response(error_doc)
