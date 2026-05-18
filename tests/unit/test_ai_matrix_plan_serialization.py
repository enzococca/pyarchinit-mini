"""Round-trip serialization tests for AIPlan dataclasses."""
import pytest

from pyarchinit_mini.ai_matrix.plan import USRow, EdgeRow, AIPlan, ExtractResult


def test_aiplan_round_trip_empty():
    plan = AIPlan(detected_site=None, detected_area=None, us=[], edges=[])
    d = plan.as_dict()
    assert d == {"detected_site": None, "detected_area": None, "us": [], "edges": []}
    assert AIPlan.from_dict(d) == plan


def test_aiplan_round_trip_full():
    plan = AIPlan(
        detected_site="Foro Boario",
        detected_area="Saggio 3",
        us=[USRow(us_num="11a", area="Saggio 3", unit_type="USM",
                  descrizione="Muratura", fase_recente=1, fase_iniziale=1)],
        edges=[EdgeRow(us_from="11a", us_to="12", tipo="copre")],
    )
    d = plan.as_dict()
    assert d["us"][0]["us_num"] == "11a"
    assert d["edges"][0]["tipo"] == "copre"
    assert AIPlan.from_dict(d) == plan


def test_extract_result_rejected_has_no_plan():
    r = ExtractResult(rejected=True, reason="not a matrix", confidence=0.1, plan=None)
    assert r.rejected is True
    assert r.plan is None


def test_extract_result_accepted_has_plan():
    plan = AIPlan(detected_site=None, detected_area=None, us=[], edges=[])
    r = ExtractResult(rejected=False, reason="OK", confidence=0.9, plan=plan)
    assert r.rejected is False
    assert r.plan == plan
