from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class Lesson:
    title: str
    start_at: datetime
    end_at: datetime
    address: str
    id: int | None = None
    room: str = ""
    note: str = ""
    color: str = "#20A4E8"
    priority: str = "normal"
