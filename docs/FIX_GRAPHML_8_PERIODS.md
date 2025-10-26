# Fix GraphML Export - Periodization Display (v1.5.0)

**Status**: ✅ Fixed in version 1.5.0
**Date**: 2025-10-26

## Problem Summary

GraphML export was showing only 3-4 periods instead of all 8 archaeological periods (datazioni) for large sites like Dom zu Lund (760 US nodes).

## Root Cause

The `parse_clusters()` function in `dot_parser.py` was expecting quoted values in the DOT file:
- Expected: `label="Geologisch"` and `"SU14" [...]`
- Actual: `label=Geologisch` and `SU14 [...]` (no quotes)

This caused the parser to:
1. Fail to extract cluster labels → only 4 clusters found instead of 8
2. Fail to extract node labels → 0 nodes found in each cluster
3. Result: incomplete period rows in GraphML

## Solution Applied

**File**: `pyarchinit_mini/graphml_converter/dot_parser.py`
**Function**: `parse_clusters()` (lines 1259-1331)

### Changes Made:

1. **Label parsing** - Handle both quoted and unquoted formats:
   ```python
   # Try quoted format: label="value"
   label_match = re.search(r'label="([^"]+)"', line)
   if label_match:
       cluster_label = label_match.group(1)
   else:
       # Try unquoted format: label=value
       label_match = re.search(r'label=(\S+)', line)
       if label_match:
           cluster_label = label_match.group(1)
   ```

2. **Node parsing** - Handle both quoted and unquoted node labels:
   ```python
   # Try quoted format: "NODE" [
   node_match = re.match(r'\s*"([^"]+)"\s*\[', line)
   if node_match:
       node_label = node_match.group(1)
   else:
       # Try unquoted format: NODE [
       node_match = re.match(r'\s*(\w+)\s*\[', line)
       if node_match:
           node_label = node_match.group(1)
   ```

3. **Bracket counting** - Initialize on the same line as subgraph declaration:
   ```python
   # Count brackets on the same line as subgraph declaration
   bracket_count = line.count('{') - line.count('}')
   ```

4. **Cluster end detection** - Check for balanced brackets:
   ```python
   # Check if cluster ended (brackets balanced)
   if bracket_count == 0 and cluster_id and cluster_label:
       clusters[cluster_id] = {
           'label': cluster_label,
           'nodes': cluster_nodes
       }
   ```

## Verification Results

### Normal Export

File: `/Users/enzo/Desktop/dom_zu_lund_harris_matrix.graphml`

**All 8 periods present:**
1. ✅ Geologisch (53 nodes)
2. ✅ Vorgeschichte bis Wikingerzeit (12 nodes)
3. ✅ Wikingerzeit (236 nodes)
4. ✅ Hochmittelalter (204 nodes)
5. ✅ Hochmittelalter bis Spätmittelalter (32 nodes)
6. ✅ Spätmittelalter (42 nodes)
7. ✅ Neuzeit (68 nodes)
8. ✅ Non datato (111 nodes)

**Total**: 758 nodes (all US from Dom zu Lund)

### Reverse Export

File: `/Users/enzo/Desktop/dom_zu_lund_harris_matrix_REVERSE.graphml`

**All 8 periods present** (sorted alphabetically when reversed)

### Performance

- Export time: ~0.5 seconds
- File size: 0.81 MB
- Layout: sfdp (fast mode for large graphs)

## Testing

Run these scripts to verify the fix:

```bash
# Test cluster parsing
.venv/bin/python debug_parse_clusters.py

# Test normal export
.venv/bin/python test_sfdp_export.py

# Verify periods in GraphML
.venv/bin/python verify_graphml_periods.py

# Test reverse export
.venv/bin/python test_sfdp_export_reverse.py

# Verify reverse periods
.venv/bin/python verify_graphml_reverse.py
```

## Next Steps

1. Open the GraphML file in yEd: `/Users/enzo/Desktop/dom_zu_lund_harris_matrix.graphml`
2. Apply layout: Layout → Hierarchical
3. Verify all 8 period rows are visible
4. Verify all 758 US nodes are present
5. Export to desired format (PDF, PNG, etc.)

## Notes

- The DOT file correctly contains all 8 clusters with proper labels
- The GraphML converter now properly extracts these clusters
- Period rows in GraphML match the datazione_estesa values from the database
- Each US node is positioned in its corresponding period row based on cluster assignment

## Files Modified

- `pyarchinit_mini/graphml_converter/dot_parser.py` - parse_clusters() function

## Files Created for Testing

- `debug_parse_clusters.py` - Test cluster parsing
- `verify_graphml_periods.py` - Verify GraphML contains all 8 periods
- `verify_graphml_reverse.py` - Verify reverse epochs export