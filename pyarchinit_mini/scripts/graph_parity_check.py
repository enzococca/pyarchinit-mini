"""Compare the new s3dgraphy projection with the old S3DProjector on a real DB.

Usage: DATABASE_URL=postgresql://… python -m pyarchinit_mini.scripts.graph_parity_check "<site>"
Prints node/edge counts of both pipelines, the per-canonical edge histogram, and wall time.
Acceptance (spec §7): |edges_new - edges_old| <= 5 % and populate_graph < 3 s.
"""
import os, sys, time
from collections import Counter
from pyarchinit_mini.database.connection import DatabaseConnection
from pyarchinit_mini.graphproj.projector import GraphProjector
from pyarchinit_mini.graphproj.s3d_projector import S3DProjector
from pyarchinit_mini.graphproj.strat_graph import stratigraphic_edges, stratigraphic_nodes

site = sys.argv[1]
conn = DatabaseConnection.from_url(os.environ["DATABASE_URL"])
with conn.get_session() as s:
    t0 = time.perf_counter(); old = S3DProjector.from_site(s, site, "none"); t_old = time.perf_counter() - t0
    t0 = time.perf_counter(); new = GraphProjector.populate_graph(s, site); t_new = time.perf_counter() - t0
print(f"old: {len(old.nodes)} nodes {len(old.edges)} edges in {t_old:.2f}s")
print(f"new: {len(stratigraphic_nodes(new))} nodes {len(stratigraphic_edges(new))} edges in {t_new:.2f}s (graph total {len(new.nodes)} nodes)")
print("old by canonical:", Counter(e.canonical for e in old.edges))
print("new by canonical:", Counter(e.edge_type for e in stratigraphic_edges(new)))
