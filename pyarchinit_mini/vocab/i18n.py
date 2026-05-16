import json
from pathlib import Path


class VocabI18n:
    def __init__(self, *, translations_dir: Path) -> None:
        self._dir = Path(translations_dir)
        self._catalogues: dict[str, dict] = {}
        self.missing_translations: set[str] = set()

    def _load(self, lang: str) -> dict:
        if lang in self._catalogues:
            return self._catalogues[lang]
        path = self._dir / f"vocab_{lang}.json"
        if not path.exists():
            return {}
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        self._catalogues[lang] = data
        return data

    def unit_type_label(self, abbreviation: str, lang: str = "en") -> str:
        cat = self._load(lang)
        try:
            return cat["unit_types"][abbreviation]["label"]
        except KeyError:
            pass
        if lang != "en":
            self.missing_translations.add(f"{lang}:{abbreviation}")
            en = self._load("en")
            try:
                return en["unit_types"][abbreviation]["label"]
            except KeyError:
                pass
        return abbreviation

    def unit_type_description(self, abbreviation: str, lang: str = "en") -> str:
        cat = self._load(lang)
        try:
            return cat["unit_types"][abbreviation]["description"]
        except KeyError:
            pass
        if lang != "en":
            en = self._load("en")
            try:
                return en["unit_types"][abbreviation]["description"]
            except KeyError:
                pass
        return ""

    def edge_type_label(self, name: str, lang: str = "en") -> str:
        cat = self._load(lang)
        try:
            return cat["edge_types"][name]["label"]
        except KeyError:
            pass
        if lang != "en":
            self.missing_translations.add(f"{lang}:{name}")
            en = self._load("en")
            try:
                return en["edge_types"][name]["label"]
            except KeyError:
                pass
        return name

    def edge_aliases(self, name: str, lang: str = "it") -> tuple:
        """Return free-form aliases for an edge type in a given language.

        Used by s3d_converter to parse PyArchInit `rapporti` text fields.
        Lives in i18n (not in loader) because aliases are locale-specific
        and NOT present in s3dgraphy JSON pillars.
        """
        cat = self._load(lang)
        aliases = cat.get("edge_type_aliases", {}).get(name, [])
        return tuple(aliases)
