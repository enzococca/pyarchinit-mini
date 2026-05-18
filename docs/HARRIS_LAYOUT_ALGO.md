# Harris Layout Algorithm

The server-side module `pyarchinit_mini/harris_swimlane/harris_layout.py`
computes (x, y) positions for each US node within its swimlane so the
editor canvas and yEd export produce identical geometry.

## Algorithm

For each lane:

1. Build a sub-graph using only edges labelled `overlies` or `is_after`
   that connect nodes within the lane.
2. Run Kahn's topological sort:
   - Sources (no incoming edges) get rank 0 (top of lane)
   - Each successor's rank = max(predecessor ranks) + 1
3. Orphan nodes (no edges) get rank = max_rank + 1 (bottom of lane).
4. Per rank: distribute siblings horizontally, centred in the lane width.

## Output

`{node_id: (x, y)}` with canvas-global coordinates. Lane x-offsets are
baked in by accumulating `lane_widths`.

## Determinism

The output is fully deterministic given the same inputs. Both the editor
and the writer call `compute_harris_positions` with the same arguments,
so the yEd export reproduces the editor view.

## Limits

- Cycles (rare but possible if rapporti are inconsistent) get rank =
  max_rank + 1 (treated as orphans).
- Lanes with > 10,000 nodes may experience performance degradation.
