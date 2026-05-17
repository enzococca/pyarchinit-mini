import json
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path
from typing import Optional

from .exceptions import VocabBootstrapError, VocabSchemaError


@dataclass
class NodeDatamodel:
    version: str
    raw: dict
    stratigraphic_subtypes: dict = field(default_factory=dict)


@dataclass
class ConnectionsDatamodel:
    version: str
    raw: dict
    edge_types: dict = field(default_factory=dict)


@dataclass
class VisualRulesDatamodel:
    version: str
    raw: dict
    node_styles: dict = field(default_factory=dict)


def _default_dir() -> Path:
    """Locate s3dgraphy JSON_config via importlib.resources."""
    # TODO(Spec-2): honour PYARCHINIT_VOCAB_STRICT=0 env var → downgrade VocabBootstrapError
    # to runtime VocabUnavailableError per Spec §7
    try:
        with resources.as_file(resources.files("s3dgraphy") / "JSON_config") as p:
            return Path(p)
    except (ModuleNotFoundError, FileNotFoundError) as e:
        raise VocabBootstrapError(
            "s3dgraphy is not installed",
            hint="pip install s3dgraphy>=0.1.42",
        ) from e


def _load_json(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as e:
        raise VocabBootstrapError(
            f"JSON file not found: {path}",
            hint="ensure s3dgraphy is properly installed",
        ) from e
    except PermissionError as e:
        raise VocabBootstrapError(
            f"permission denied reading: {path}",
            hint="check file permissions on the s3dgraphy install directory",
        ) from e
    except UnicodeDecodeError as e:
        raise VocabBootstrapError(
            f"file is not valid UTF-8: {path}",
            hint="JSON pillar files must be UTF-8; check for corruption",
        ) from e
    except json.JSONDecodeError as e:
        raise VocabSchemaError(path=str(path), line=e.lineno, column=e.colno, msg=e.msg) from e


def _resolve_node_datamodel_file(d: Path) -> Path:
    for name in ("s3Dgraphy_node_datamodel.json", "s3Dgraphy_node_datamodel .json"):
        p = d / name
        if p.exists():
            return p
    raise VocabBootstrapError(
        f"s3Dgraphy_node_datamodel.json not found in {d}",
        hint="upgrade s3dgraphy: pip install --upgrade s3dgraphy>=0.1.42",
    )


def _resolve_connections_file(d: Path, *, allow_legacy: bool) -> Path:
    canonical = d / "s3Dgraphy_connections_datamodel.json"
    if canonical.exists():
        return canonical
    legacy = d / "em_connection_rules.json"
    if legacy.exists():
        if not allow_legacy:
            raise VocabBootstrapError(
                f"Only legacy {legacy.name} found (s3dgraphy version too old)",
                hint="upgrade: pip install --upgrade s3dgraphy>=0.1.42",
            )
        return legacy
    raise VocabBootstrapError(
        "no connections datamodel file found",
        hint="upgrade s3dgraphy",
    )


def load_node_datamodel(*, json_config_dir: Optional[Path] = None) -> NodeDatamodel:
    d = Path(json_config_dir) if json_config_dir else _default_dir()
    if not d.exists():
        raise VocabBootstrapError(f"JSON_config directory not found: {d}")
    path = _resolve_node_datamodel_file(d)
    raw = _load_json(path)
    subtypes = {}
    strat = raw.get("stratigraphic_nodes", {}).get("StratigraphicNode", {})
    subtypes.update(strat.get("subtypes", {}))
    return NodeDatamodel(
        version=raw.get("s3Dgraphy_data_model_version", "unknown"),
        raw=raw,
        stratigraphic_subtypes=subtypes,
    )


def load_connections_datamodel(*, json_config_dir: Optional[Path] = None, allow_legacy: bool = False) -> ConnectionsDatamodel:
    d = Path(json_config_dir) if json_config_dir else _default_dir()
    if not d.exists():
        raise VocabBootstrapError(f"JSON_config directory not found: {d}")
    path = _resolve_connections_file(d, allow_legacy=allow_legacy)
    raw = _load_json(path)
    edge_types = raw.get("edge_types") or raw.get("connection_types") or {}
    return ConnectionsDatamodel(
        version=raw.get("version", "unknown"),
        raw=raw,
        edge_types=edge_types,
    )


def load_visual_rules(*, json_config_dir: Optional[Path] = None) -> VisualRulesDatamodel:
    d = Path(json_config_dir) if json_config_dir else _default_dir()
    if not d.exists():
        raise VocabBootstrapError(f"JSON_config directory not found: {d}")
    path = d / "em_visual_rules.json"
    if not path.exists():
        raise VocabBootstrapError(f"em_visual_rules.json not found in {d}")
    raw = _load_json(path)
    return VisualRulesDatamodel(
        version=raw.get("version", "unknown"),
        raw=raw,
        node_styles=raw.get("node_styles", {}),
    )
