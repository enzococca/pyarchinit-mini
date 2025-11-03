"""
Media Management Tool

Provides comprehensive media file management for archaeological entities:
- Upload and store media files (images, documents, videos, 3D models)
- Associate media with entities (site, us, inventario)
- Get, update, and delete media records
- Manage media metadata and thumbnails
- Get media statistics and summaries
"""

import logging
import os
import base64
import tempfile
from typing import Dict, Any, Optional, List
from pathlib import Path
from .base_tool import BaseTool, ToolDescription
from ...services.media_service import MediaService
from ...media_manager.media_handler import MediaHandler

logger = logging.getLogger(__name__)


class MediaManagementTool(BaseTool):
    """Comprehensive media file management for archaeological entities"""

    def to_tool_description(self) -> ToolDescription:
        return ToolDescription(
            name="manage_media",
            description=(
                "⚠️ REQUIRED FOR ALL MEDIA OPERATIONS - This is the ONLY correct way to upload media files. "
                "DO NOT use 'insert_data' tool for media_table - it will fail. "
                "\n\n"
                "Comprehensive media file management tool: "
                "Upload, retrieve, update, and delete media files (images, documents, videos, 3D models). "
                "Associate media with entities: site, us, inventario. "
                "Supports base64-encoded content or file paths. "
                "Automatically handles: "
                "1) File storage in permanent location (~/.pyarchinit_mini/media/) "
                "2) Unique filename generation with hash "
                "3) Database record creation with correct relative paths "
                "4) Thumbnail generation for images "
                "\n\n"
                "Files are stored permanently, NOT in /tmp/ where they would be lost on reboot."
            ),
            input_schema={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["upload", "get", "list", "update", "delete", "statistics", "set_primary"],
                        "description": (
                            "'upload' = Store new media file, "
                            "'get' = Get media by ID, "
                            "'list' = List media for entity, "
                            "'update' = Update media metadata, "
                            "'delete' = Delete media file and record, "
                            "'statistics' = Get media statistics, "
                            "'set_primary' = Set media as primary for entity"
                        )
                    },
                    "media_id": {
                        "type": "integer",
                        "description": "Media ID (for get, update, delete, set_primary operations)"
                    },
                    "entity_type": {
                        "type": "string",
                        "enum": ["site", "us", "inventario"],
                        "description": "Type of entity: site, us, or inventario"
                    },
                    "entity_id": {
                        "type": ["string", "integer"],
                        "description": "Entity ID (site name, US number, or inventario ID)"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Path to media file on server (for upload)"
                    },
                    "file_content_base64": {
                        "type": "string",
                        "description": "Base64-encoded file content (alternative to file_path)"
                    },
                    "filename": {
                        "type": "string",
                        "description": "Filename for uploaded content (required with file_content_base64)"
                    },
                    "media_type": {
                        "type": "string",
                        "enum": ["image", "document", "video", "audio", "3d_model"],
                        "description": "Type of media file"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of media file"
                    },
                    "tags": {
                        "type": "string",
                        "description": "Comma-separated tags"
                    },
                    "author": {
                        "type": "string",
                        "description": "Author/creator name"
                    },
                    "is_primary": {
                        "type": "boolean",
                        "description": "Set as primary media for entity",
                        "default": False
                    },
                    "is_public": {
                        "type": "boolean",
                        "description": "Make media publicly accessible",
                        "default": True
                    },
                    "delete_file": {
                        "type": "boolean",
                        "description": "Delete physical file (for delete operation)",
                        "default": True
                    },
                    "page": {
                        "type": "integer",
                        "description": "Page number for pagination",
                        "default": 1
                    },
                    "size": {
                        "type": "integer",
                        "description": "Results per page",
                        "default": 10
                    }
                },
                "required": ["operation"],
            },
        )

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute media management operation"""
        try:
            operation = arguments.get("operation")

            # Create DatabaseManager from db_session
            from ...database.connection import DatabaseConnection
            from ...database.manager import DatabaseManager

            # Get engine from session
            engine = self.db_session.bind
            db_connection = DatabaseConnection(engine.url.render_as_string(hide_password=False))
            db_connection._engine = engine  # Reuse existing engine
            db_manager = DatabaseManager(db_connection)

            # Initialize media service
            media_handler = MediaHandler()
            media_service = MediaService(db_manager, media_handler)

            logger.info(f"Executing media operation: {operation}")

            if operation == "upload":
                return await self._handle_upload(media_service, arguments)
            elif operation == "get":
                return await self._handle_get(media_service, arguments)
            elif operation == "list":
                return await self._handle_list(media_service, arguments)
            elif operation == "update":
                return await self._handle_update(media_service, arguments)
            elif operation == "delete":
                return await self._handle_delete(media_service, arguments)
            elif operation == "statistics":
                return await self._handle_statistics(media_service, arguments)
            elif operation == "set_primary":
                return await self._handle_set_primary(media_service, arguments)
            else:
                return self._format_error(f"Unknown operation: {operation}")

        except Exception as e:
            logger.error(f"Media management error: {str(e)}", exc_info=True)
            return self._format_error(f"Media management failed: {str(e)}")

    async def _handle_upload(
        self,
        media_service: MediaService,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle media upload operation"""
        entity_type = arguments.get("entity_type")
        entity_id = arguments.get("entity_id")
        file_path = arguments.get("file_path")
        file_content_base64 = arguments.get("file_content_base64")
        filename = arguments.get("filename")
        description = arguments.get("description", "")
        tags = arguments.get("tags", "")
        author = arguments.get("author", "")
        is_primary = arguments.get("is_primary", False)

        if not entity_type or not entity_id:
            return self._format_error("entity_type and entity_id are required for upload")

        # Handle base64 content
        temp_file = None
        try:
            if file_content_base64:
                if not filename:
                    return self._format_error("filename is required when using file_content_base64")

                # Decode base64 and save to temp file
                file_content = base64.b64decode(file_content_base64)
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=Path(filename).suffix
                )
                temp_file.write(file_content)
                temp_file.close()
                file_path = temp_file.name

            elif not file_path:
                return self._format_error("Either file_path or file_content_base64 is required")

            # Check file exists
            if not os.path.exists(file_path):
                return self._format_error(f"File not found: {file_path}")

            # Store and register media
            media = media_service.store_and_register_media(
                file_path=file_path,
                entity_type=entity_type,
                entity_id=str(entity_id),
                description=description,
                tags=tags,
                author=author,
                is_primary=is_primary
            )

            return self._format_success(
                result={
                    "media_id": media.id_media,
                    "media_name": media.media_name,
                    "media_type": media.media_type,
                    "media_path": media.media_path,
                    "file_size": media.file_size,
                    "entity_type": media.entity_type,
                    "entity_id": media.entity_id,
                    "is_primary": media.is_primary
                },
                message=f"Media uploaded successfully: {media.media_name}"
            )

        finally:
            # Clean up temp file
            if temp_file and os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                except:
                    pass

    async def _handle_get(
        self,
        media_service: MediaService,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle get media by ID operation"""
        media_id = arguments.get("media_id")

        if not media_id:
            return self._format_error("media_id is required for get operation")

        media = media_service.get_media_by_id(media_id)

        if not media:
            return self._format_error(f"Media not found: {media_id}")

        return self._format_success(
            result={
                "media_id": media.id_media,
                "media_name": media.media_name,
                "media_filename": media.media_filename,
                "media_type": media.media_type,
                "media_path": media.media_path,
                "file_size": media.file_size,
                "entity_type": media.entity_type,
                "entity_id": media.entity_id,
                "description": media.description,
                "tags": media.tags,
                "author": media.author,
                "is_primary": media.is_primary,
                "is_public": media.is_public
            },
            message=f"Media retrieved: {media.media_name}"
        )

    async def _handle_list(
        self,
        media_service: MediaService,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle list media for entity operation"""
        entity_type = arguments.get("entity_type")
        entity_id = arguments.get("entity_id")
        page = arguments.get("page", 1)
        size = arguments.get("size", 10)

        if not entity_type or not entity_id:
            return self._format_error("entity_type and entity_id are required for list operation")

        media_list = media_service.get_media_by_entity(
            entity_type=entity_type,
            entity_id=str(entity_id),
            page=page,
            size=size
        )

        # Get total count
        total_count = media_service.count_media({
            "entity_type": entity_type,
            "entity_id": str(entity_id)
        })

        # Get primary media
        primary_media = media_service.get_primary_media(entity_type, str(entity_id))

        result = {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "total_count": total_count,
            "page": page,
            "size": size,
            "primary_media_id": primary_media.id_media if primary_media else None,
            "media_items": [
                {
                    "media_id": media.id_media,
                    "media_name": media.media_name,
                    "media_type": media.media_type,
                    "media_path": media.media_path,
                    "file_size": media.file_size,
                    "description": media.description,
                    "tags": media.tags,
                    "author": media.author,
                    "is_primary": media.is_primary
                }
                for media in media_list
            ]
        }

        return self._format_success(
            result=result,
            message=f"Found {total_count} media items for {entity_type} {entity_id}"
        )

    async def _handle_update(
        self,
        media_service: MediaService,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle update media metadata operation"""
        media_id = arguments.get("media_id")

        if not media_id:
            return self._format_error("media_id is required for update operation")

        # Build update data
        update_data = {}
        if "description" in arguments:
            update_data["description"] = arguments["description"]
        if "tags" in arguments:
            update_data["tags"] = arguments["tags"]
        if "author" in arguments:
            update_data["author"] = arguments["author"]
        if "is_public" in arguments:
            update_data["is_public"] = arguments["is_public"]

        if not update_data:
            return self._format_error("No update data provided")

        media = media_service.update_media(media_id, update_data)

        return self._format_success(
            result={
                "media_id": media.id_media,
                "media_name": media.media_name,
                "updated_fields": list(update_data.keys())
            },
            message=f"Media updated: {media.media_name}"
        )

    async def _handle_delete(
        self,
        media_service: MediaService,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle delete media operation"""
        media_id = arguments.get("media_id")
        delete_file = arguments.get("delete_file", True)

        if not media_id:
            return self._format_error("media_id is required for delete operation")

        # Get media info before deletion
        media = media_service.get_media_by_id(media_id)
        if not media:
            return self._format_error(f"Media not found: {media_id}")

        media_name = media.media_name
        success = media_service.delete_media(media_id, delete_file=delete_file)

        if success:
            return self._format_success(
                result={
                    "media_id": media_id,
                    "media_name": media_name,
                    "deleted_file": delete_file
                },
                message=f"Media deleted: {media_name}"
            )
        else:
            return self._format_error(f"Failed to delete media: {media_id}")

    async def _handle_statistics(
        self,
        media_service: MediaService,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle get media statistics operation"""
        entity_type = arguments.get("entity_type")
        entity_id = arguments.get("entity_id")

        if entity_type and entity_id:
            # Get statistics for specific entity
            # Count media for this entity
            total_count = media_service.count_media({
                "entity_type": entity_type,
                "entity_id": str(entity_id)
            })

            # Get media list to analyze
            media_list = media_service.get_media_by_entity(
                entity_type=entity_type,
                entity_id=str(entity_id),
                size=1000  # Get all
            )

            # Analyze media
            type_counts = {}
            total_size = 0
            authors = set()

            for media in media_list:
                media_type = media.media_type or 'unknown'
                type_counts[media_type] = type_counts.get(media_type, 0) + 1
                total_size += media.file_size or 0
                if media.author:
                    authors.add(media.author)

            result = {
                "entity_type": entity_type,
                "entity_id": entity_id,
                "total_media": total_count,
                "type_distribution": type_counts,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "unique_authors": len(authors)
            }
        else:
            # Get global statistics
            result = media_service.get_media_statistics()

        return self._format_success(
            result=result,
            message="Media statistics retrieved"
        )

    async def _handle_set_primary(
        self,
        media_service: MediaService,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle set primary media operation"""
        media_id = arguments.get("media_id")
        entity_type = arguments.get("entity_type")
        entity_id = arguments.get("entity_id")

        if not media_id or not entity_type or not entity_id:
            return self._format_error(
                "media_id, entity_type, and entity_id are required for set_primary operation"
            )

        success = media_service.set_primary_media(
            media_id=media_id,
            entity_type=entity_type,
            entity_id=str(entity_id)
        )

        if success:
            return self._format_success(
                result={"media_id": media_id, "is_primary": True},
                message=f"Media {media_id} set as primary for {entity_type} {entity_id}"
            )
        else:
            return self._format_error("Failed to set primary media")
