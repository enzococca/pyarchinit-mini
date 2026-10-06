"""Guard the SQLAlchemy upper bound.

SQLAlchemy 2.1 resolves plain ``postgresql://`` URLs to the psycopg 3 driver,
which this project does not ship (it depends on psycopg2-binary). An
unbounded ``sqlalchemy>=2.0`` therefore produced a Railway build on
2026-10-06 that crashed at boot with ``No module named 'psycopg'``.
Raising the bound is fine, but only together with a driver decision
(psycopg 3 dependency or explicit ``postgresql+psycopg2://`` URLs).
"""
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _requirement(text: str) -> str:
    for line in text.splitlines():
        item = line.split("#", 1)[0].strip().rstrip(",").strip('"')
        if item.lower().startswith("sqlalchemy"):
            return item[len("sqlalchemy"):].replace(" ", "")
    raise AssertionError("sqlalchemy requirement not found")


@pytest.mark.parametrize("path", ["requirements.txt", "pyproject.toml"])
def test_sqlalchemy_is_bounded_below_2_1(path):
    spec = _requirement((ROOT / path).read_text(encoding="utf-8"))
    assert "<2.1" in spec, f"{path}: sqlalchemy spec {spec!r} lacks the <2.1 upper bound"
