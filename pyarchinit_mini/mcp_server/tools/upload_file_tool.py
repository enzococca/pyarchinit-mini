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
                "Upload a file to temporary storage. Returns a file_id for use in other tools. "
                "Use this BEFORE import_excel to avoid passing large base64 data directly."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "Filename"
                    },
                    "content_base64": {
                        "type": "string",
                        "description": "Base64-encoded file content"
                    },
                },
                "required": ["filename", "content_base64"],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file upload"""
        try:
            filename = arguments.get("filename")
            content_base64 = arguments.get("content_base64")

            if not filename or not content_base64:
                return self._format_error("Missing required parameters")

            # Decode base64
            try:
                file_data = base64.b64decode(content_base64)
            except Exception as e:
                return self._format_error(f"Failed to decode file: {str(e)}")

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

            logger.info(f"File uploaded: {filename} → {file_id} ({len(file_data)} bytes)")

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
