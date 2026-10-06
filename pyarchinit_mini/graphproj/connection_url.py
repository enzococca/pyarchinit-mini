"""Translate mini's SQLAlchemy session into the connection URL s3dgraphy's
PyArchInitImporter accepts (``sqlite:///<abs path>`` or ``postgresql://…``)."""
from __future__ import annotations

import os

from .exceptions import ProjectionError


def connection_url_from_session(session) -> str:
    url = session.get_bind().url
    backend = url.get_backend_name()
    if backend == "sqlite":
        if not url.database or url.database == ":memory:":
            raise ProjectionError(
                "s3dgraphy projection needs a file-backed SQLite database "
                "(in-memory databases cannot be shared with the importer)"
            )
        return "sqlite:///" + os.path.abspath(url.database)
    if backend in ("postgresql", "postgres"):
        return url.render_as_string(hide_password=False)
    raise ProjectionError(f"Unsupported database backend for s3dgraphy projection: {backend}")
