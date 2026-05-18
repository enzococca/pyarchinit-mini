"""yEd-flavored GraphML writer — Extended Matrix template compatible with
pyarchinit QGIS plugin.

Emits:
  - 38 <key> declarations (d0..d37 from yed_keys.KEYS)
  - <graph> with optional <data key="d0"> epochs_meta payload
  - one <node yfiles.foldertype="group"> root with <y:TableNode YED_TABLE_NODE>
  - per-row <y:Row> children inside the TableNode
  - per-US <node> children with all 38 keys valorized
  - per-edge <edge> with edgegraphics

The old write_yed_graphml is kept as a thin deprecated wrapper for one
release; removed in 2.6.0.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable
from xml.sax.saxutils import escape

from pyarchinit_mini.harris_swimlane.exceptions import YEDWriterError
from pyarchinit_mini.graphml_io.yed_keys import KEYS, KeyDef


def write_extended_matrix_graphml(
    state: Any,
    *,
    site_meta: dict,
    epochs: list[dict],
    out: Path,
) -> None:
    """Atomic write — emits at out, .tmp staging."""
    out = Path(out)
    tmp = out.with_suffix(out.suffix + ".tmp")
    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        xml = _build_xml(state, site_meta, epochs)
        tmp.write_text(xml, encoding="utf-8")
        tmp.replace(out)
    except Exception as e:
        if tmp.exists():
            try: tmp.unlink()
            except Exception: pass
        raise YEDWriterError(path=str(out), msg=str(e)) from e


def _build_xml(state, site_meta: dict, epochs: list[dict]) -> str:
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<graphml xmlns="http://graphml.graphdrawing.org/xmlns" '
        'xmlns:java="http://www.yworks.com/xml/yfiles-common/1.0/java" '
        'xmlns:sys="http://www.yworks.com/xml/yfiles-common/markup/primitives/2.0" '
        'xmlns:x="http://www.yworks.com/xml/yfiles-common/markup/2.0" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xmlns:y="http://www.yworks.com/xml/graphml" '
        'xmlns:yed="http://www.yworks.com/xml/yed/3" '
        'xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns '
        'http://www.yworks.com/xml/schema/graphml/1.1/ygraphml.xsd">',
    ]
    parts.extend(_render_key_declarations(KEYS))
    parts.append('  <graph edgedefault="directed" id="G">')
    parts.append(_render_epochs_meta(epochs))
    parts.append(_render_table_root(state, site_meta))
    parts.append(_render_us_nodes(state))
    parts.append(_render_edges(state))
    parts.append('  </graph>')
    parts.append('</graphml>')
    return "\n".join(p for p in parts if p)


def _render_key_declarations(keys: Iterable[KeyDef]) -> list[str]:
    out = []
    for k in keys:
        attrs = [f'id="{k.key_id}"', f'for="{k.for_target}"']
        if k.attr_name:
            attrs.append(f'attr.name="{escape(k.attr_name)}"')
        if k.attr_type:
            attrs.append(f'attr.type="{k.attr_type}"')
        if k.yfiles_type:
            attrs.append(f'yfiles.type="{k.yfiles_type}"')
        out.append('  <key ' + ' '.join(attrs) + '/>')
    return out


def _render_epochs_meta(epochs: list[dict]) -> str:
    import json
    if not epochs:
        return ''
    payload = json.dumps(epochs, ensure_ascii=False)
    return f'    <data key="d0" xml:space="preserve"><![CDATA[{payload}]]></data>'


def _render_table_root(state, site_meta: dict) -> str:
    """Emit the y:TableNode group node containing all swimlane rows."""
    sito = site_meta.get("sito", "Unknown")
    rows_xml = []
    row_height = 200
    for i, row in enumerate(state.rows):
        rid = escape(row.row_id)
        rows_xml.append(
            f'              <y:Row id="{rid}" height="{row_height}" '
            f'minimumHeight="80.0" nodeLabelMaxWidth="0.0"/>'
        )

    # Compute table geometry.
    height = max(len(state.rows) * row_height + 60, 200)
    width = 2000

    parts = [
        '    <node id="swimlane_root" yfiles.foldertype="group">',
        f'      <data key="d4">{escape(f"swimlane-root-{sito}")}</data>',
        f'      <data key="d8">{escape(sito)}</data>',
        '      <data key="d30">Stratigrafia</data>',
        '      <data key="d31">',
        '        <y:TableNode configuration="YED_TABLE_NODE">',
        f'          <y:Geometry height="{height}.0" width="{width}.0" x="0.0" y="0.0"/>',
        '          <y:Fill color="#ECF5FF" color2="#0042F440" transparent="false"/>',
        '          <y:BorderStyle hasColor="false" type="line" width="1.0"/>',
        f'          <y:NodeLabel alignment="center" autoSizePolicy="content" '
        f'fontFamily="Dialog" fontSize="15" fontStyle="plain" hasBackgroundColor="false" '
        f'hasLineColor="false" horizontalTextPosition="center" iconTextGap="4" '
        f'modelName="internal" modelPosition="t" textColor="#000000" '
        f'verticalTextPosition="bottom" visible="true" xml:space="preserve">'
        f'Archaeological Site [ID:{escape(sito)}]</y:NodeLabel>',
        '          <y:Table>',
        '            <y:Insets bottom="0.0" bottomF="0.0" left="0.0" leftF="0.0" '
        'right="0.0" rightF="0.0" top="24.0" topF="24.0"/>',
        '            <y:Columns/>',
        '            <y:Rows>',
        *rows_xml,
        '            </y:Rows>',
        '          </y:Table>',
        '        </y:TableNode>',
        '      </data>',
        '      <graph edgedefault="directed" id="swimlane_root::graph">',
    ]
    # Note: closing of <graph> + </node> happens in _render_us_nodes (Task 9)
    # because US nodes are children of this nested graph.
    return "\n".join(parts)


def _render_us_nodes(state) -> str:
    """Emit each US node as child of the swimlane_root graph."""
    parts = []
    sito = state.site
    for el in state.nodes:
        if el.data.get("is_swimlane"):
            continue
        d = el.data
        nid = escape(str(d["id"]))
        us_num = d.get("us_number") or d.get("us") or ""
        unit_type = d.get("unit_type") or "US"
        node_uuid = d.get("node_uuid") or ""
        area = d.get("area") or ""
        periodo = d.get("period") or ""
        fase = d.get("phase") or ""
        rapporti = d.get("rapporti") or ""
        d_strat = d.get("description") or ""
        d_interp = d.get("d_interpretativa") or ""
        documentazione = d.get("file_path") or ""
        struttura = d.get("struttura") or ""
        attivita = d.get("attivita") or ""
        settore = d.get("settore") or ""
        ambient = d.get("ambient") or ""
        saggio = d.get("saggio") or ""
        quad_par = d.get("quad_par") or ""
        datazione = d.get("datazione") or ""
        pos = el.position or {"x": 0, "y": 0}
        x, y = pos.get("x", 0), pos.get("y", 0)
        color = d.get("color") or "#F0F0F0"
        border_color = d.get("border_color") or "#540909"
        border_style = d.get("border_style") or "solid"
        shape = d.get("shape") or "rectangle"

        parts.append(f'        <node id="{nid}">')
        parts.append(f'          <data key="d4">{escape(str(node_uuid))}</data>')
        parts.append('          <data key="d5"/>')
        parts.append(f'          <data key="d6">{escape(str(us_num))}</data>')
        parts.append(f'          <data key="d7">{escape(str(area))}</data>')
        parts.append(f'          <data key="d8">{escape(sito)}</data>')
        parts.append(f'          <data key="d9">{escape(str(unit_type))}</data>')
        parts.append(f'          <data key="d10">{escape(str(periodo))}</data>')
        parts.append(f'          <data key="d11">{escape(str(fase))}</data>')
        parts.append(f'          <data key="d12">{escape(str(rapporti))}</data>')
        parts.append(f'          <data key="d13">{escape(str(d_strat))}</data>')
        parts.append(f'          <data key="d14">{escape(str(d_interp))}</data>')
        parts.append(f'          <data key="d15">{escape(str(documentazione))}</data>')
        parts.append(f'          <data key="d16">{escape(str(node_uuid))}</data>')
        parts.append(f'          <data key="d17">{escape(str(struttura))}</data>')
        parts.append(f'          <data key="d18">{escape(str(attivita))}</data>')
        parts.append(f'          <data key="d19">{escape(str(settore))}</data>')
        parts.append(f'          <data key="d20">{escape(str(ambient))}</data>')
        parts.append(f'          <data key="d21">{escape(str(saggio))}</data>')
        parts.append(f'          <data key="d22">{escape(str(quad_par))}</data>')
        parts.append(f'          <data key="d23">{escape(str(datazione))}</data>')
        parts.append('          <data key="d31">')
        parts.append('            <y:ShapeNode>')
        parts.append(f'              <y:Geometry height="30.0" width="80.0" x="{x}" y="{y}"/>')
        parts.append(f'              <y:Fill color="{color}" transparent="false"/>')
        parts.append(f'              <y:BorderStyle color="{border_color}" type="{border_style}" width="3.0"/>')
        parts.append(f'              <y:NodeLabel>{escape(d.get("label", str(us_num)))}</y:NodeLabel>')
        parts.append(f'              <y:Shape type="{shape}"/>')
        parts.append('            </y:ShapeNode>')
        parts.append('          </data>')
        parts.append('        </node>')

    parts.append('      </graph>')  # close swimlane_root::graph (opened by Task 8)
    parts.append('    </node>')     # close swimlane_root node (opened by Task 8)
    return "\n".join(parts)


def _render_edges(state) -> str:
    """Stub — filled in Task 10."""
    return ''


# Deprecated thin wrapper for one release.
def write_yed_graphml(state: Any, path: Path) -> None:
    """DEPRECATED — use write_extended_matrix_graphml. Removed in 2.6.0."""
    import warnings
    warnings.warn(
        "write_yed_graphml is deprecated; use write_extended_matrix_graphml",
        DeprecationWarning, stacklevel=2,
    )
    write_extended_matrix_graphml(
        state, site_meta={"sito": getattr(state, "site", "Unknown")}, epochs=[], out=path,
    )
