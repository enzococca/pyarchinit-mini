"""GraphML writer — delegates to s3dgraphy.exporter.graphml.GraphMLExporter.

Recon (s3dgraphy 0.1.42):
    from s3dgraphy.exporter.graphml import GraphMLExporter
    GraphMLExporter(graph).export(output_path: str, persist_auxiliary: bool = False)
"""
from pathlib import Path
from typing import Any

from pyarchinit_mini.graphproj.exceptions import GraphMLWriteError


def write_graphml(graph: Any, path: Path, *, persist_auxiliary: bool = False) -> None:
    """Serialize a s3dgraphy.Graph to GraphML at path.

    Creates parent directory if missing. Wraps any underlying error as
    GraphMLWriteError for consistent caller handling.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        from s3dgraphy.exporter.graphml import GraphMLExporter
        exporter = GraphMLExporter(graph)
        exporter.export(str(path), persist_auxiliary=persist_auxiliary)
    except Exception as e:
        raise GraphMLWriteError(path=str(path), msg=str(e)) from e
