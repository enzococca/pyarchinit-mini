"""ParadataStore — per-site filesystem-backed paradata.graphml + paradata.json.

Storage:
  data/paradata/<site_slug>/paradata.graphml  — stratigraphic graph (s3dgraphy)
  data/paradata/<site_slug>/paradata.json     — paradata entities (authors, …)

The s3dgraphy GraphMLExporter does not persist standalone AuthorNode instances
to GraphML (they are emitted only as image-copies inside ParadataNodeGroups).
Paradata entities are therefore stored in a JSON sidecar so they survive full
read/write cycles while still being constructed as native s3dgraphy node
objects for any in-memory use that requires the typed API.

Atomic write via tmp + os.replace, serialized by per-site flock.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

import s3dgraphy

from .filesystem import paradata_dir, paradata_flock, slugify
from .exceptions import ParadataConflict, ParadataNotFound, ParadataStorageError
from pyarchinit_mini.graphml_io.reader import read_graphml
from pyarchinit_mini.graphml_io.writer import write_graphml


PARADATA_FILENAME = "paradata.graphml"
PARADATA_JSON = "paradata.json"


class ParadataStore:
    def __init__(self, site: str, *, root: Optional[Path] = None) -> None:
        self.site = site
        self._root = Path(root) if root else None
        self._dir = paradata_dir(site, root=root)
        self._path = self._dir / PARADATA_FILENAME
        self._json_path = self._dir / PARADATA_JSON

    # ------------------------------------------------------------------
    # GraphML graph persistence (stratigraphic layer)
    # ------------------------------------------------------------------

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

    # ------------------------------------------------------------------
    # JSON sidecar helpers (paradata entities)
    # ------------------------------------------------------------------

    def _load_json(self) -> dict:
        """Load the JSON sidecar; return empty structure if missing."""
        if not self._json_path.exists():
            return {"authors": {}}
        try:
            return json.loads(self._json_path.read_text(encoding="utf-8"))
        except Exception as e:
            raise ParadataStorageError(
                f"Cannot load paradata JSON: {e}",
                path=str(self._json_path),
            ) from e

    def _write_json(self, data: dict) -> None:
        """Atomically persist the JSON sidecar."""
        self._dir.mkdir(parents=True, exist_ok=True)
        tmp = self._json_path.with_suffix(self._json_path.suffix + ".tmp")
        try:
            tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            tmp.replace(self._json_path)
        except Exception as e:
            if tmp.exists():
                try:
                    tmp.unlink()
                except Exception:
                    pass
            raise ParadataStorageError(
                f"Cannot write paradata JSON: {e}",
                path=str(self._json_path),
            ) from e

    # ------------------------------------------------------------------
    # Author CRUD
    # ------------------------------------------------------------------

    AUTHOR_PREFIX = "author:"

    def _next_author_id(self, existing_ids: set) -> str:
        n = 1
        while f"{self.AUTHOR_PREFIX}{n}" in existing_ids:
            n += 1
        return f"{self.AUTHOR_PREFIX}{n}"

    def list_authors(self) -> list[dict]:
        """Return all stored authors as a list of dicts."""
        data = self._load_json()
        return list(data.get("authors", {}).values())

    def add_author(self, *, name: str, orcid: str | None = None) -> dict:
        """Create a new author entry.

        Raises ParadataConflict if an author with the same name (case-insensitive)
        already exists.
        """
        from s3dgraphy.nodes.author_node import AuthorNode  # native class

        with paradata_flock(self.site, root=self._root):
            data = self._load_json()
            authors: dict = data.setdefault("authors", {})

            # Deduplicate by name (case-insensitive)
            for entry in authors.values():
                if entry["name"].lower() == name.lower():
                    raise ParadataConflict(
                        node_id=entry["node_id"],
                        existing=entry,
                    )

            node_id = self._next_author_id(set(authors.keys()))

            # Construct via native class so any future callers get a typed object
            node = AuthorNode(node_id, name=name)
            if orcid is not None:
                node.data["orcid"] = orcid

            entry = {
                "node_id": node_id,
                "name": node.name,
                "orcid": node.data.get("orcid"),
            }
            authors[node_id] = entry
            self._write_json(data)
            return dict(entry)

    def update_author(
        self,
        node_id: str,
        *,
        name: str | None = None,
        orcid: str | None = None,
    ) -> dict:
        """Update fields on an existing author.

        Raises ParadataNotFound if node_id is not found.
        """
        with paradata_flock(self.site, root=self._root):
            data = self._load_json()
            authors: dict = data.setdefault("authors", {})

            if node_id not in authors:
                raise ParadataNotFound(node_id=node_id)

            entry = authors[node_id]
            if name is not None:
                entry["name"] = name
            if orcid is not None:
                entry["orcid"] = orcid

            self._write_json(data)
            return dict(entry)

    def delete_author(self, node_id: str) -> None:
        """Delete an author by node_id.

        Raises ParadataNotFound if node_id is not found.
        """
        with paradata_flock(self.site, root=self._root):
            data = self._load_json()
            authors: dict = data.setdefault("authors", {})

            if node_id not in authors:
                raise ParadataNotFound(node_id=node_id)

            del authors[node_id]
            self._write_json(data)

    # ------------------------------------------------------------------
    # Generic list-based helpers (licenses, embargoes, documents, epochs)
    # ------------------------------------------------------------------

    LICENSE_KEY = "licenses"
    EMBARGO_KEY = "embargoes"
    DOCUMENT_KEY = "documents"
    EPOCH_KEY = "epochs"

    LICENSE_PREFIX = "license:"
    EMBARGO_PREFIX = "embargo:"
    DOCUMENT_PREFIX = "document:"
    EPOCH_PREFIX = "epoch:"

    def _generic_next_id(self, data: dict, key: str, prefix: str) -> str:
        existing = {item["node_id"] for item in data.get(key, [])}
        n = 1
        while f"{prefix}{n}" in existing:
            n += 1
        return f"{prefix}{n}"

    def _generic_add(self, key: str, prefix: str, **fields) -> dict:
        with paradata_flock(self.site, root=self._root):
            data = self._load_json()
            data.setdefault(key, [])
            node_id = self._generic_next_id(data, key, prefix)
            entry = {"node_id": node_id, **{k: v for k, v in fields.items() if v is not None}}
            data[key].append(entry)
            self._write_json(data)
            return entry

    def _generic_list(self, key: str) -> list[dict]:
        data = self._load_json()
        return list(data.get(key, []))

    def _generic_update(self, key: str, node_id: str, **fields) -> dict:
        with paradata_flock(self.site, root=self._root):
            data = self._load_json()
            items = data.get(key, [])
            target = next((i for i in items if i["node_id"] == node_id), None)
            if target is None:
                raise ParadataNotFound(node_id=node_id)
            for k, v in fields.items():
                if v is not None:
                    target[k] = v
            self._write_json(data)
            return target

    def _generic_delete(self, key: str, node_id: str) -> None:
        with paradata_flock(self.site, root=self._root):
            data = self._load_json()
            items = data.get(key, [])
            target = next((i for i in items if i["node_id"] == node_id), None)
            if target is None:
                raise ParadataNotFound(node_id=node_id)
            data[key] = [i for i in items if i["node_id"] != node_id]
            self._write_json(data)

    # --- licenses ---

    def list_licenses(self) -> list[dict]:
        return self._generic_list(self.LICENSE_KEY)

    def add_license(self, *, name: str, url: str | None = None) -> dict:
        return self._generic_add(self.LICENSE_KEY, self.LICENSE_PREFIX, name=name, url=url)

    def update_license(self, node_id: str, **fields) -> dict:
        return self._generic_update(self.LICENSE_KEY, node_id, **fields)

    def delete_license(self, node_id: str) -> None:
        self._generic_delete(self.LICENSE_KEY, node_id)

    # --- embargoes ---

    def list_embargoes(self) -> list[dict]:
        return self._generic_list(self.EMBARGO_KEY)

    def add_embargo(self, *, label: str, until: str | None = None) -> dict:
        return self._generic_add(self.EMBARGO_KEY, self.EMBARGO_PREFIX, label=label, until=until)

    def update_embargo(self, node_id: str, **fields) -> dict:
        return self._generic_update(self.EMBARGO_KEY, node_id, **fields)

    def delete_embargo(self, node_id: str) -> None:
        self._generic_delete(self.EMBARGO_KEY, node_id)

    # --- documents ---

    def list_documents(self) -> list[dict]:
        return self._generic_list(self.DOCUMENT_KEY)

    def add_document(self, *, title: str, uri: str | None = None) -> dict:
        return self._generic_add(self.DOCUMENT_KEY, self.DOCUMENT_PREFIX, title=title, uri=uri)

    def update_document(self, node_id: str, **fields) -> dict:
        return self._generic_update(self.DOCUMENT_KEY, node_id, **fields)

    def delete_document(self, node_id: str) -> None:
        self._generic_delete(self.DOCUMENT_KEY, node_id)

    # --- epochs ---

    def list_epochs(self) -> list[dict]:
        return self._generic_list(self.EPOCH_KEY)

    def add_epoch(self, *, name: str, start: Any = None, end: Any = None) -> dict:
        return self._generic_add(self.EPOCH_KEY, self.EPOCH_PREFIX, name=name, start=start, end=end)

    def update_epoch(self, node_id: str, **fields) -> dict:
        return self._generic_update(self.EPOCH_KEY, node_id, **fields)

    def delete_epoch(self, node_id: str) -> None:
        self._generic_delete(self.EPOCH_KEY, node_id)
