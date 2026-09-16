from dataclasses import dataclass
from datetime import date, time


@dataclass(slots=True)
class FixedLesson:
    weekday: int
    start_time: time
    end_time: time
    title: str
    address: str = ""
    room: str = ""
    note: str = ""
    color: str = "#20A4E8"
    effective_from: date | None = None
    id: int | None = None
