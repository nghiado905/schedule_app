import calendar
from datetime import date, timedelta


def week_start(value: date) -> date:
    return value - timedelta(days=value.weekday())


def month_range(value: date) -> tuple[date, date]:
    last_day = calendar.monthrange(value.year, value.month)[1]
    return date(value.year, value.month, 1), date(value.year, value.month, last_day)


def year_range(value: date) -> tuple[date, date]:
    return date(value.year, 1, 1), date(value.year, 12, 31)
