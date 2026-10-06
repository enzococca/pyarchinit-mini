import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_projected_graph_model_is_gone():
    hits = subprocess.run(["grep", "-rn", "ProjectedGraph\\|s3d_projector", str(ROOT / "pyarchinit_mini")],
                          capture_output=True, text=True).stdout
    assert hits == "", hits
