"""
Base Resource Class

Abstract base class for all MCP resources.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class ResourceDescription:
    """Resource description for MCP protocol"""

    uri: str
    name: str
    description: str
    mime_type: str = "application/json"


class BaseResource(ABC):
    """
    Abstract base class for MCP Resources

    Resources provide context data to Claude AI.
    Each resource must implement:
    - to_resource_description(): Return ResourceDescription
    - read(resource_id): Async method to read resource data
    """

    def __init__(self, config: Any):
        """
        Initialize resource

        Args:
            config: MCP configuration
        """
        self.config = config

    @abstractmethod
    def to_resource_description(self) -> ResourceDescription:
        """
        Return resource description for MCP protocol

        Returns:
            ResourceDescription with URI, name, description, mime_type
        """
        pass

    @abstractmethod
    async def read(self, resource_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Read resource data

        Args:
            resource_id: Optional resource identifier

        Returns:
            Dict containing resource data

        Raises:
            ValueError: If resource_id is invalid
            NotFoundError: If resource not found
        """
        pass

    def _format_error(self, error_type: str, message: str) -> Dict[str, Any]:
        """
        Format error response

        Args:
            error_type: Type of error (e.g., "NotFound", "ValidationError")
            message: Error message

        Returns:
            Error dict
        """
        return {"error": {"type": error_type, "message": message}}
