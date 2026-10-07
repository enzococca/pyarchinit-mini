"""Shared guard: the generic write tools (insert_data, batch_insert) must
never write the media tables.

A media row created without going through manage_media is a record with no
file behind it. When a generic insert tool answers "required_field_missing",
an AI client retries with '' / 0 and the husk row lands in the database
(pyarchinit-mini#4: 129 such rows). Refusing up-front, before any schema
is reflected or reported back, is the only reliable stop.
"""

MEDIA_TABLES = ("media_table", "media_thumb_table", "media_to_entity_table")


def media_table_guard(table: str):
    """Return the refusal response if `table` is a media table, else None."""
    if table not in MEDIA_TABLES:
        return None
    return {
        "success": False,
        "error": "use_manage_media_tool",
        "message": (
            f"❌ Direct insert into '{table}' is not allowed. "
            f"Media files must be uploaded using the 'manage_media' tool "
            f"to ensure proper file storage and path management. "
            f"\n\n📋 How to use manage_media:\n"
            f"1. Upload file with operation='upload'\n"
            f"2. Provide entity_type (one of: us, inventario, pottery, struttura, tomba, tma, ut, site)\n"
            f"3. Provide entity_id (the entity's integer primary key, e.g. id_sito, id_us, id_invmat)\n"
            f"4. Either provide file_path on server OR file_content_base64\n"
            f"5. The tool stores the file in the configured media storage, creates the "
            f"media_table record and links it in media_to_entity_table\n\n"
            f"Example:\n"
            f"{{\n"
            f"  'operation': 'upload',\n"
            f"  'entity_type': 'site',\n"
            f"  'entity_id': 12,\n"
            f"  'file_content_base64': '<base64-encoded-content>',\n"
            f"  'filename': 'site_photo.jpg',\n"
            f"  'description': 'Site overview'\n"
            f"}}\n\n"
            f"This ensures files are stored permanently in the correct location, "
            f"not in temporary directories like /tmp/ where they will be lost."
        ),
        "correct_tool": "manage_media",
        "tool_operations": ["upload", "get", "list", "update", "delete"],
    }
