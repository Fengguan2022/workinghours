from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Employee:
    id: Optional[int]
    name: str
    pin: str
    active: bool = True
    created_at: Optional[str] = None


@dataclass
class TimeEntry:
    id: Optional[int]
    employee_id: int
    event_type: str  # 'IN' or 'OUT'
    timestamp: str

    @property
    def datetime(self) -> datetime:
        return datetime.strptime(self.timestamp, "%Y-%m-%d %H:%M:%S")
