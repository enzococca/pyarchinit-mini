# yEd Integration — Round-trip + Limits

The Harris Swimlane Editor produces yEd-flavored GraphML files at
`data/exports/harris_yed/<site>-harris-yed.graphml`, openable in
[yEd Desktop](https://www.yworks.com/products/yed).

## Structure

The export uses yEd's `y:TableNode` with one `y:Row` per
`(period_name, phase_name)` pair:

```xml
<node id="swimlane_root" yfiles.foldertype="group">
  <data key="d6">
    <y:TableNode>
      <y:Table>
        <y:Rows>
          <y:Row id="row_medieval_b" height="80.0"/>
          <y:Row id="row_medieval_a" height="80.0"/>
          ...
        </y:Rows>
      </y:Table>
    </y:TableNode>
  </data>
  <graph id="swimlane_root:" edgedefault="directed">
    <node id="us_5">
      <data key="d6"><y:ShapeNode>...</y:ShapeNode></data>
    </node>
    ...
  </graph>
</node>
```

US visual styles (color, shape, border) come from
`VocabProvider.get_visual_style(unit_type)` (Spec 1's canonical source).

## Workflow

1. From the editor, click **⬇ Export yEd GraphML**.
2. Open the downloaded file in yEd Desktop.
3. Use yEd's swimlane tools (Layout → Hierarchical → Swimlanes) to
   refine row placement, add edge labels, adjust colors.
4. Save the yEd file separately (do NOT overwrite — round-trip not
   yet supported).

## Limits

- **No round-trip yet**: editor → yEd works; yEd back to editor is
  Spec 3-ter.
- **Edge auto-routing inside TableNode**: yEd hierarchical layout may
  produce routings you don't like. Use yEd's "Edge Routing" tool.
- **Cross-row edges**: `rapporti` produces edges between US in
  different rows; yEd renders across rows but may overlap.

## Future work

- **Spec 3-ter** (proposed): GraphML re-import from yEd-edited file
- **Spec 4**: Real-time concurrent editing, conflict resolution UI

## Related

- Spec 1: VocabProvider — canonical visual styles
- Spec 2: GraphProjector + s3dgraphy.exporter.graphml — EM Datacenter
  consumption (clean GraphML, no TableNode)
- This Spec 3-bis: yEd-flavored output for yEd Desktop workflows
