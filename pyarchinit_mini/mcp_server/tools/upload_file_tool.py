"""
Upload File Tool

Uploads a file to a temporary location and returns a file_id for later use.
This avoids passing large base64 data in tool parameters.
"""

import os
import tempfile
import base64
import uuid
import logging
from typing import Dict, Any
from .base_tool import BaseTool, ToolDescription

logger = logging.getLogger(__name__)

# Global storage for uploaded files (in-memory for now)
_uploaded_files: Dict[str, str] = {}


class UploadFileTool(BaseTool):
    """Upload File Tool - Uploads files for later use"""

    def to_tool_description(self) -> ToolDescription:
        return ToolDescription(
            name="upload_file",
            description=(
                "🔴 STEP 1 OF 2: Upload Excel file. "
                "ALWAYS use this FIRST when importing Excel files. "
                "Returns file_id (36 chars) to use in STEP 2 (import_excel). "
                "⚡ FASTEST: Use 'file_path' parameter with absolute path to Excel file. "
                "Alternative: Use 'content_base64' parameter (slower). "
                "Workflow: upload_file → get file_id → import_excel with file_id."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Excel filename (e.g., 'data.xlsx'). Optional if file_path is provided."
                    },
                    "file_path": {
                        "type": "string",
                        "description": "⚡ FASTEST: Absolute path to Excel file on filesystem (e.g., '/Users/name/Downloads/data.xlsx')"
                    },
                    "content_base64": {
                        "type": "string",
                        "description": "Base64-encoded Excel file content (alternative to file_path, slower)"
                    },
                },
                "required": [],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file upload"""
        try:
            filename = arguments.get("filename")
            file_path = arguments.get("file_path")
            content_base64 = arguments.get("content_base64")

            # Require at least one input method
            if not file_path and not content_base64:
                return self._format_error("Must provide either 'file_path' or 'content_base64'")

            # Option 1: Direct file path (FASTEST)
            if file_path:
                # Security validation
                file_path = os.path.abspath(file_path)

                # Check file exists
                if not os.path.exists(file_path):
                    return self._format_error(f"File not found: {file_path}")

                # Check it's a file, not a directory
                if not os.path.isfile(file_path):
                    return self._format_error(f"Path is not a file: {file_path}")

                # Extract filename if not provided
                if not filename:
                    filename = os.path.basename(file_path)

                # Read file directly
                try:
                    with open(file_path, 'rb') as f:
                        file_data = f.read()
                except Exception as e:
                    return self._format_error(f"Failed to read file: {str(e)}")

                logger.info(f"⚡ File uploaded via path: {filename} ({len(file_data)} bytes)")

            # Option 2: Base64 encoded content (SLOWER, fallback)
            else:
                if not filename:
                    return self._format_error("filename is required when using content_base64")

                # Decode base64
                try:
                    file_data = base64.b64decode(content_base64)
                except Exception as e:
                    return self._format_error(f"Failed to decode file: {str(e)}")

                logger.info(f"File uploaded via base64: {filename} ({len(file_data)} bytes)")

            # Generate unique file_id
            file_id = str(uuid.uuid4())

            # Create temp directory if it doesn't exist
            temp_dir = os.path.join(tempfile.gettempdir(), 'pyarchinit_uploads')
            os.makedirs(temp_dir, exist_ok=True)

            # Save file
            file_ext = os.path.splitext(filename)[1]
            filepath = os.path.join(temp_dir, f"{file_id}{file_ext}")

            with open(filepath, 'wb') as f:
                f.write(file_data)

            # Store in global registry
            _uploaded_files[file_id] = filepath

            return self._format_success(
                {
                    "file_id": file_id,
                    "filename": filename,
                    "size": len(file_data),
                    "path": filepath
                },
                f"File uploaded: {filename} ({len(file_data)} bytes) → file_id: {file_id}"
            )

        except Exception as e:
            logger.error(f"Upload failed: {str(e)}", exc_info=True)
            return self._format_error(f"Upload failed: {str(e)}")


def get_uploaded_file_path(file_id: str) -> str:
    """Get file path from file_id"""
    return _uploaded_files.get(file_id)


def cleanup_uploaded_file(file_id: str):
    """Remove uploaded file"""
    filepath = _uploaded_files.pop(file_id, None)
    if filepath and os.path.exists(filepath):
        try:
            os.remove(filepath)
        except:
            pass
