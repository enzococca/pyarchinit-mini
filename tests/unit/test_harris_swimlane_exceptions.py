import pytest
from pyarchinit_mini.harris_swimlane.exceptions import (
    SwimlaneError,
    RowProviderError,
    PeriodSyncError,
    SwimlaneStateError,
    YEDWriterError,
)


def test_swimlane_error_is_base():
    assert issubclass(RowProviderError, SwimlaneError)
    assert issubclass(PeriodSyncError, SwimlaneError)
    assert issubclass(SwimlaneStateError, SwimlaneError)
    assert issubclass(YEDWriterError, SwimlaneError)


def test_row_provider_error_carries_site():
    err = RowProviderError("missing rows", site="X")
    assert err.site == "X"
    assert "missing rows" in str(err)


def test_period_sync_error_carries_period():
    err = PeriodSyncError("duplicate", period_name="P1", phase_name="a")
    assert err.period_name == "P1"
    assert err.phase_name == "a"


def test_yed_writer_error_carries_path():
    err = YEDWriterError(path="/tmp/x.graphml", msg="disk full")
    assert err.path == "/tmp/x.graphml"
    assert "disk full" in str(err)


def test_swimlane_state_error_carries_op():
    err = SwimlaneStateError("rollback", op="save")
    assert err.op == "save"
