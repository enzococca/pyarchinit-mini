"""ParadataStore — per-site filesystem-backed paradata.graphml.

Storage: data/paradata/<site_slug>/paradata.graphml
Atomic write via tmp + os.replace, serialized by per-site flock.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import s3dgraphy

from .filesystem import paradata_dir, paradata_flock, slugify
from .exceptions import ParadataStorageError
from pyarchinit_mini.graphml_io.reader import read_graphml
from pyarchinit_mini.graphml_io.writer import write_graphml


PARADATA_FILENAME = "paradata.graphml"


class ParadataStore:
    def __init__(self, site: str, *, root: Optional[Path] = None) -> None:
        self.site = site
        self._root = Path(root) if root else None
        self._dir = paradata_dir(site, root=root)
        self._path = self._dir / PARADATA_FILENAME

    def load(self) -> "s3dgraphy.Graph":
        """Returns paradata Graph. Empty Graph if file missing."""
        if not self._path.exists():
            return s3dgraphy.Graph(
                graph_id=f"paradata:{slugify(self.site)}",
                name=f"{self.site} paradata",
                description="",
            )
        try:
            return read_graphml(self._path)
        except Exception as e:
            raise ParadataStorageError(
                f"Cannot load paradata: {e}",
                path=str(self._path),
            ) from e

    def atomic_write(self, graph: "s3dgraphy.Graph") -> None:
        """Persist graph atomically via tmp + os.replace under per-site flock."""
        with paradata_flock(self.site, root=self._root):
            self._dir.mkdir(parents=True, exist_ok=True)
            tmp = self._path.with_suffix(self._path.suffix + ".tmp")
            try:
                write_graphml(graph, tmp)
                tmp.replace(self._path)
            except Exception as e:
                if tmp.exists():
                    try:
                        tmp.unlink()
                    except Exception:
                        pass
                raise ParadataStorageError(
                    f"Cannot write paradata: {e}",
                    path=str(self._path),
                ) from e
