from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Row:
    row_id: str
    period_name: str
    phase_name: Optional[str]
    start_date: Optional[int]
    end_date: Optional[int]
    color: str
    source: str
