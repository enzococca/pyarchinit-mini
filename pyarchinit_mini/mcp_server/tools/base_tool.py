"""
Base Tool Class

Abstract base class for all MCP tools.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class ToolDescription:
    """Tool description for MCP protocol"""

    name: str
    description: str
    input_schema: Dict[str, Any]


class BaseTool(ABC):
    """
    Abstract base class for MCP Tools

    Tools execute actions requested by Claude AI.
    Each tool must implement:
    - to_tool_description(): Return ToolDescription
    - execute(arguments): Async method to execute tool action
    """

    def __init__(self, db_session, config):
        """
        Initialize tool

        Args:
            db_session: Database session
            config: MCP configuration
        """
        self.db_session = db_session
        self.config = config

    @abstractmethod
    def to_tool_description(self) -> ToolDescription:
        """
        Return tool description for MCP protocol

        Returns:
            ToolDescription with name, description, input_schema
        """
        pass

    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute tool action

        Args:
            arguments: Tool arguments from Claude

        Returns:
            Dict containing execution results

        Raises:
            ValueError: If arguments are invalid
            RuntimeError: If execution fails
        """
        pass

    def _validate_arguments(
        self, arguments: Dict[str, Any], required_fields: List[str]
    ) -> Dict[str, str]:
        """
        Validate tool arguments

        Args:
            arguments: Arguments to validate
            required_fields: List of required field names

        Returns:
            Dict of errors (empty if valid)
        """
        errors = {}
        for field in required_fields:
            if field not in arguments:
                errors[field] = f"Missing required field: {field}"
        return errors

    def _format_success(
        self, result: Any, message: str = "Success"
    ) -> Dict[str, Any]:
        """
        Format success response

        Args:
            result: Result data
            message: Success message

        Returns:
            Success dict
        """
        return {"success": True, "message": message, "result": result}

    def _format_error(self, error_type: str, message: str) -> Dict[str, Any]:
        """
        Format error response

        Args:
            error_type: Type of error
            message: Error message

        Returns:
            Error dict
        """
        return {"success": False, "error": {"type": error_type, "message": message}}
