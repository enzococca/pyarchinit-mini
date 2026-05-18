"""GraphML reader — delegates to s3dgraphy.importer.import_graphml.GraphMLImporter.

Recon (s3dgraphy 0.1.42):
    from s3dgraphy.importer.import_graphml import GraphMLImporter
    importer = GraphMLImporter(filepath: str, graph=None)
    importer.parse()  # mutates graph; if graph=None, creates a fresh one
"""
from pathlib import Path
from typing import Any

from pyarchinit_mini.graphproj.exceptions import GraphMLReadError


def read_graphml(path: Path) -> Any:
    """Read a GraphML file into a s3dgraphy.Graph.

    Returns the populated Graph. Raises GraphMLReadError on missing file,
    malformed XML, or any underlying importer error.
    """
    path = Path(path)
    if not path.exists():
        raise GraphMLReadError(path=str(path), msg="file not found")
    try:
        import s3dgraphy
        from s3dgraphy.importer.import_graphml import GraphMLImporter
        # Create a fresh graph; importer will populate it during parse()
        graph = s3dgraphy.Graph(
            graph_id=f"imported:{path.stem}",
            name=path.stem,
            description=f"Imported from {path}",
        )
        importer = GraphMLImporter(str(path), graph)
        importer.parse()
        return graph
    except GraphMLReadError:
        raise
    except Exception as e:
        raise GraphMLReadError(path=str(path), msg=str(e)) from e
