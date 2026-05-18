"""yEd GraphML key definitions for pyarchinit Extended Matrix files.

The 38 keys d0..d37 are the canonical schema used by pyarchinit QGIS plugin.
Both yed_writer (emission) and yed_importer (parsing) share this mapping.

Each KEY entry: (key_id, attr_name, attr_type, for_target, yfiles_type)
"""
from typing import NamedTuple, Optional


class KeyDef(NamedTuple):
    key_id: str           # "d0" .. "d37"
    attr_name: Optional[str]
    attr_type: Optional[str]
    for_target: str       # "graph" | "node" | "edge" | "port" | "graphml"
    yfiles_type: Optional[str] = None


KEYS: tuple[KeyDef, ...] = (
    KeyDef("d0", "pyarchinit.epochs_meta", "string", "graph"),
    KeyDef("d1", None, None, "port", "portgraphics"),
    KeyDef("d2", None, None, "port", "portgeometry"),
    KeyDef("d3", None, None, "port", "portuserdata"),
    KeyDef("d4", "EMID", "string", "node"),
    KeyDef("d5", "URI", "string", "node"),
    KeyDef("d6", "pyarchinit.us", "string", "node"),
    KeyDef("d7", "pyarchinit.area", "string", "node"),
    KeyDef("d8", "pyarchinit.sito", "string", "node"),
    KeyDef("d9", "pyarchinit.unita_tipo", "string", "node"),
    KeyDef("d10", "pyarchinit.periodo_iniziale", "string", "node"),
    KeyDef("d11", "pyarchinit.fase_iniziale", "string", "node"),
    KeyDef("d12", "pyarchinit.rapporti", "string", "node"),
    KeyDef("d13", "pyarchinit.d_stratigrafica", "string", "node"),
    KeyDef("d14", "pyarchinit.d_interpretativa", "string", "node"),
    KeyDef("d15", "pyarchinit.documentazione", "string", "node"),
    KeyDef("d16", "pyarchinit.node_uuid", "string", "node"),
    KeyDef("d17", "pyarchinit.struttura", "string", "node"),
    KeyDef("d18", "pyarchinit.attivita", "string", "node"),
    KeyDef("d19", "pyarchinit.settore", "string", "node"),
    KeyDef("d20", "pyarchinit.ambient", "string", "node"),
    KeyDef("d21", "pyarchinit.saggio", "string", "node"),
    KeyDef("d22", "pyarchinit.quad_par", "string", "node"),
    KeyDef("d23", "pyarchinit.datazione_estesa", "string", "node"),
    KeyDef("d24", "pyarchinit.periodo", "string", "node"),
    KeyDef("d25", "pyarchinit.fase", "string", "node"),
    KeyDef("d26", "pyarchinit.cron_iniziale", "string", "node"),
    KeyDef("d27", "pyarchinit.cron_finale", "string", "node"),
    KeyDef("d28", "pyarchinit.datazione_estesa", "string", "node"),
    KeyDef("d29", "url", "string", "node"),
    KeyDef("d30", "description", "string", "node"),
    KeyDef("d31", None, None, "node", "nodegraphics"),
    KeyDef("d32", None, None, "graphml", "resources"),
    KeyDef("d33", "EMID", "string", "edge"),
    KeyDef("d34", "URI", "string", "edge"),
    KeyDef("d35", "url", "string", "edge"),
    KeyDef("d36", "description", "string", "edge"),
    KeyDef("d37", None, None, "edge", "edgegraphics"),
)


# Quick lookups used at parse/emit time.
KEY_BY_ID: dict[str, KeyDef] = {k.key_id: k for k in KEYS}
KEY_BY_ATTR_NAME: dict[str, KeyDef] = {k.attr_name: k for k in KEYS if k.attr_name}

# Subset of node keys whose values map 1:1 to us_table columns.
US_NODE_FIELDS = (
    "pyarchinit.us", "pyarchinit.area", "pyarchinit.sito",
    "pyarchinit.unita_tipo", "pyarchinit.periodo_iniziale",
    "pyarchinit.fase_iniziale", "pyarchinit.rapporti",
    "pyarchinit.d_stratigrafica", "pyarchinit.d_interpretativa",
    "pyarchinit.documentazione", "pyarchinit.node_uuid",
    "pyarchinit.struttura", "pyarchinit.attivita", "pyarchinit.settore",
    "pyarchinit.ambient", "pyarchinit.saggio", "pyarchinit.quad_par",
    "pyarchinit.datazione_estesa",
)
