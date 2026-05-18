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
    """Stub for Task 7."""
    return ""


def _build_edges(state) -> str:
    """Stub for Task 7."""
    return ""
