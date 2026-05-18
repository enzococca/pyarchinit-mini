"""yEd-flavored GraphML writer — y:TableNode + y:Rows + per-node y:ShapeNode.

Separate from s3dgraphy.exporter.graphml (Spec 2). Used by Harris Swimlane Editor
for on-demand export. Visual styles per US come from VocabProvider (Spec 1).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from pyarchinit_mini.harris_swimlane.exceptions import YEDWriterError


def write_yed_graphml(state: Any, path: Path) -> None:
    """Emit yEd-flavored GraphML to path. Atomic write via tmp + os.replace."""
    path = Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        xml = _build_xml(state)
        tmp.write_text(xml, encoding="utf-8")
        tmp.replace(path)
    except Exception as e:
        if tmp.exists():
            try:
                tmp.unlink()
            except Exception:
                pass
        raise YEDWriterError(path=str(path), msg=str(e)) from e


def _build_xml(state) -> str:
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<graphml xmlns="http://graphml.graphdrawing.org/xmlns" '
        'xmlns:y="http://www.yworks.com/xml/graphml" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
        'xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns '
        'http://www.yworks.com/xml/schema/graphml/1.1/ygraphml.xsd">',
        '  <key for="node" id="d6" yfiles.type="nodegraphics"/>',
        '  <key for="edge" id="d10" yfiles.type="edgegraphics"/>',
        '  <graph id="G" edgedefault="directed">',
        _build_swimlane_root(state),
        _build_edges(state),
        '  </graph>',
        '</graphml>',
    ]
    return "\n".join(parts)


def _build_swimlane_root(state) -> str:
    row_xml = _build_table_rows(state.rows)
    nodes_xml = _build_us_nodes(state.nodes)
    return (
        '    <node id="swimlane_root" yfiles.foldertype="group">\n'
        '      <data key="d6">\n'
        '        <y:TableNode>\n'
        '          <y:Geometry height="800" width="2000" x="0" y="0"/>\n'
        '          <y:Fill color="#FAFAFA" transparent="false"/>\n'
        '          <y:BorderStyle color="#000000" type="line" width="1.0"/>\n'
        '          <y:Table>\n'
        f'{row_xml}'
        '            <y:Columns>\n'
        '              <y:Column id="col_main" width="1900.0"/>\n'
        '            </y:Columns>\n'
        '          </y:Table>\n'
        '        </y:TableNode>\n'
        '      </data>\n'
        '      <graph id="swimlane_root:" edgedefault="directed">\n'
        f'{nodes_xml}'
        '      </graph>\n'
        '    </node>\n'
    )


def _build_table_rows(rows) -> str:
    if not rows:
        return '            <y:Rows/>\n'
    lines = ['            <y:Rows>']
    for r in rows:
        lines.append(
            f'              <y:Row id="{r.row_id}" height="80.0" minimumHeight="40.0"/>'
        )
    lines.append('            </y:Rows>\n')
    return "\n".join(lines)


def _build_us_nodes(nodes) -> str:
    """Emit y:ShapeNode per US with VocabProvider visual styles."""
    if not nodes:
        return ""
    from pyarchinit_mini.vocab.provider import VocabProvider
    from pyarchinit_mini.vocab.types import VisualStyle
    try:
        provider = VocabProvider.instance()
    except Exception:
        provider = None

    lines = []
    for el in nodes:
        nid = el.data.get("id", "")
        label = el.data.get("label", nid)
        unit_type = el.data.get("unit_type", "US")
        if provider:
            style = provider.get_visual_style(unit_type)
        else:
            style = VisualStyle.fallback()
        fill = style.fill_color
        border = style.border_color
        shape = style.shape
        lines.append(
            f'        <node id="{nid}">\n'
            f'          <data key="d6">\n'
            f'            <y:ShapeNode>\n'
            f'              <y:Geometry x="50" y="20" width="80" height="50"/>\n'
            f'              <y:Fill color="{fill}" transparent="false"/>\n'
            f'              <y:BorderStyle color="{border}" type="line" width="3.0"/>\n'
            f'              <y:NodeLabel fontSize="12">{_xml_escape(label)}</y:NodeLabel>\n'
            f'              <y:Shape type="{shape}"/>\n'
            f'            </y:ShapeNode>\n'
            f'          </data>\n'
            f'        </node>'
        )
    return "\n".join(lines) + "\n"


def _build_edges(state) -> str:
    """Emit y:GenericEdge per stratigraphic edge."""
    if not state.edges:
        return ""
    lines = []
    for el in state.edges:
        eid = el.data.get("id", "")
        src = el.data.get("source", "")
        tgt = el.data.get("target", "")
        lbl = el.data.get("label", "")
        lines.append(
            f'    <edge id="{eid}" source="{src}" target="{tgt}">\n'
            f'      <data key="d10">\n'
            f'        <y:GenericEdge>\n'
            f'          <y:LineStyle color="#000000" type="line" width="1.0"/>\n'
            f'          <y:Arrows source="none" target="standard"/>\n'
            f'          <y:EdgeLabel>{_xml_escape(lbl)}</y:EdgeLabel>\n'
            f'        </y:GenericEdge>\n'
            f'      </data>\n'
            f'    </edge>'
        )
    return "\n".join(lines) + "\n"


def _xml_escape(s: str) -> str:
    """Minimal XML escape for safe content embedding."""
    return (str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))
