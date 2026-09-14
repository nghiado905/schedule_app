from dataclasses import dataclass


@dataclass(slots=True)
class Settings:
    dark_mode: bool = False
    notifications_enabled: bool = True
    start_hour: int = 7
    end_hour: int = 24
