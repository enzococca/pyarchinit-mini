from typing import Optional


class SwimlaneError(Exception):
    """Base for harris_swimlane errors."""


class RowProviderError(SwimlaneError):
    def __init__(self, msg: str, *, site: Optional[str] = None) -> None:
        super().__init__(msg)
        self.site = site


class PeriodSyncError(SwimlaneError):
    def __init__(self, msg: str, *, period_name: Optional[str] = None,
                 phase_name: Optional[str] = None) -> None:
        super().__init__(msg)
        self.period_name = period_name
        self.phase_name = phase_name


class SwimlaneStateError(SwimlaneError):
    def __init__(self, msg: str, *, op: Optional[str] = None) -> None:
        super().__init__(msg)
        self.op = op


class YEDWriterError(SwimlaneError):
    def __init__(self, *, path: str, msg: str) -> None:
        super().__init__(f"{msg} (path={path})")
        self.path = path
