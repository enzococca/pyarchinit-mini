import threading
from pathlib import Path
from typing import Any, Optional

from .i18n import VocabI18n
from .loader import load_connections_datamodel, load_node_datamodel, load_visual_rules
from .types import EdgeType, UnitType, VisualStyle


def _build_visual_style(entry: dict) -> VisualStyle:
    style = entry.get("style", {})
    mat = style.get("material", {}).get("color")
    rgba = (mat["r"], mat["g"], mat["b"], mat.get("a", 1.0)) if mat else None
    return VisualStyle(
        shape=style.get("shape", "rectangle"),
        fill_color=style.get("fill_color", "#FFFFFF"),
        border_color=style.get("border_color", "#000000"),
        border_style=style.get("border_style", "solid"),
        file_2d_raster=entry.get("file_2d") or entry.get("2d_file_rast"),
        file_2d_vector=entry.get("2d_file_vect"),
        file_3d=entry.get("file_3d") or entry.get("3d_file"),
        material_rgba=rgba,
        label_position=entry.get("label_position", "over"),
    )


class VocabProvider:
    _instance: Optional["VocabProvider"] = None
    _lock = threading.Lock()

    def __init__(self, *, json_config_dir: Optional[Path] = None,
                 translations_dir: Optional[Path] = None) -> None:
        self._node = load_node_datamodel(json_config_dir=json_config_dir)
        self._conn = load_connections_datamodel(
            json_config_dir=json_config_dir,
            allow_legacy=True,
        )
        self._visual = load_visual_rules(json_config_dir=json_config_dir)
        self._i18n = VocabI18n(
            translations_dir=translations_dir
            or Path(__file__).parent / "translations"
        )
        self._unit_types_raw: dict[str, dict] = self._node.stratigraphic_subtypes
        self._visual_by_type: dict[str, VisualStyle] = {
            abbr: _build_visual_style(entry)
            for abbr, entry in self._visual.node_styles.items()
        }

    @classmethod
    def instance(cls, **kwargs) -> "VocabProvider":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls(**kwargs)
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        # TODO(Spec-2): emit warning if called outside test context (per Spec §4.1)
        with cls._lock:
            cls._instance = None

    def _build_unit_type(self, abbr: str, raw: dict, lang: str) -> UnitType:
        return UnitType(
            abbreviation=abbr,
            class_name=raw.get("class", "Node"),
            parent=raw.get("parent"),
            label=self._i18n.unit_type_label(abbr, lang=lang),
            description=self._i18n.unit_type_description(abbr, lang=lang) or raw.get("description", ""),
            symbol=raw.get("symbol", ""),
            family=raw.get("family"),
            is_series=bool(raw.get("is_series", False)),
            cidoc_mapping=raw.get("mapping", {}).get("cidoc"),
            properties=raw.get("properties", {}),
            visual_style=self.get_visual_style(abbr),
        )

    def get_unit_types(self, lang: str = "en") -> list[UnitType]:
        return [self._build_unit_type(a, r, lang) for a, r in self._unit_types_raw.items()]

    def get_unit_type(self, abbreviation: str, lang: str = "en") -> Optional[UnitType]:
        raw = self._unit_types_raw.get(abbreviation)
        if raw is None:
            return None
        return self._build_unit_type(abbreviation, raw, lang)

    def get_edge_types(self, lang: str = "en") -> list[EdgeType]:
        out = []
        for name, raw in self._conn.edge_types.items():
            out.append(EdgeType(
                name=name,
                label=self._i18n.edge_type_label(name, lang=lang),
                italian_aliases=self._i18n.edge_aliases(name, lang="it"),
                symmetric=bool(raw.get("symmetric", False)),
                legal_pairs=tuple(tuple(p) for p in raw.get("legal_pairs", ())),
            ))
        return out

    def get_legal_edges(self, source_type: str, target_type: str) -> list[EdgeType]:
        all_edges = self.get_edge_types()
        return [e for e in all_edges if (source_type, target_type) in e.legal_pairs]

    def get_visual_style(self, unit_type: str) -> VisualStyle:
        return self._visual_by_type.get(unit_type, VisualStyle.fallback())

    def get_cidoc_mapping(self, unit_type: str) -> Optional[str]:
        ut = self.get_unit_type(unit_type)
        return ut.cidoc_mapping if ut else None

    def s3dgraphy_version(self) -> str:
        try:
            import s3dgraphy
            return getattr(s3dgraphy, "__version__", "unknown")
        except ImportError:
            return "not installed"

    def data_model_versions(self) -> dict[str, str]:
        return {
            "node": self._node.version,
            "connections": self._conn.version,
            "visual": self._visual.version,
        }

    def diagnostics(self) -> dict[str, Any]:
        return {
            "s3dgraphy_version": self.s3dgraphy_version(),
            "data_model_versions": self.data_model_versions(),
            "counts": {
                "unit_types": len(self._unit_types_raw),
                "edge_types": len(self._conn.edge_types),
                "visual_styles": len(self._visual_by_type),
            },
            "missing_translations": sorted(self._i18n.missing_translations),
        }
