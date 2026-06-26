import json, os
from dataclasses import dataclass, field
from typing import Mapping

DEFAULT_PRESERVE = frozenset({
    "order_layer", "cont_per", "entity_uuid", "node_uuid", "version_number",
    "created_at", "updated_at", "last_modified_timestamp", "last_modified_by",
    "editing_since", "editing_by", "audit_trail", "sync_status",
})
DEFAULT_EXCLUDE = frozenset({"spatial_ref_sys", "raster_columns", "raster_overviews"})

@dataclass
class Config:
    source_dsn: str
    target_dsn: str
    size_threshold_keyset: int = 200_000
    exclude_tables: frozenset = DEFAULT_EXCLUDE
    preserve_columns_global: frozenset = DEFAULT_PRESERVE
    overrides: dict = field(default_factory=dict)
    weekly_full_refresh: bool = True
    delete_enabled: bool = True

def load_config(path: str | None = None, env: Mapping[str, str] = os.environ) -> Config:
    raw = {}
    if path:
        with open(path, encoding="utf-8") as fh:
            raw = json.load(fh)
    src_env = raw.get("source_dsn_env", "PYARCHINIT_CLASSIC_DSN")
    tgt_env = raw.get("target_dsn_env", "DATABASE_URL")
    source_dsn = env[src_env]          # KeyError if missing — intentional
    target_dsn = env[tgt_env]
    preserve = DEFAULT_PRESERVE | frozenset(raw.get("preserve_columns_global", []))
    exclude = DEFAULT_EXCLUDE | frozenset(raw.get("exclude_tables", []))
    return Config(
        source_dsn=source_dsn, target_dsn=target_dsn,
        size_threshold_keyset=int(raw.get("size_threshold_keyset", 200_000)),
        exclude_tables=exclude, preserve_columns_global=preserve,
        overrides=raw.get("overrides", {}),
        weekly_full_refresh=bool(raw.get("weekly_full_refresh", True)),
        delete_enabled=bool(raw.get("delete_enabled", True)),
    )
