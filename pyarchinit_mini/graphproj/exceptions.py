from typing import Optional


class GraphProjError(Exception):
    """Base for graphproj errors."""


class ProjectionError(GraphProjError):
    def __init__(self, msg: str, *, site: Optional[str] = None) -> None:
        super().__init__(msg)
        self.site = site


class IngestError(GraphProjError):
    pass


class IngestStaleError(IngestError):
    def __init__(self, *, expected: str, actual: str) -> None:
        super().__init__(f"Plan stale: expected snapshot {expected}, found {actual}")
        self.expected = expected
        self.actual = actual


class ParadataConflict(GraphProjError):
    def __init__(self, *, node_id: str, existing: dict) -> None:
        super().__init__(f"Paradata node {node_id} already exists")
        self.node_id = node_id
        self.existing = existing


class ParadataNotFound(GraphProjError):
    def __init__(self, *, node_id: str) -> None:
        super().__init__(f"Paradata node {node_id} not found")
        self.node_id = node_id


class ParadataStorageError(GraphProjError):
    def __init__(self, msg: str, *, path: Optional[str] = None) -> None:
        super().__init__(msg)
        self.path = path


class GraphMLReadError(GraphProjError):
    def __init__(self, *, path: str, msg: str) -> None:
        super().__init__(f"{msg} reading {path}")
        self.path = path


class GraphMLWriteError(GraphProjError):
    def __init__(self, *, path: str, msg: str) -> None:
        super().__init__(f"{msg} writing {path}")
        self.path = path
