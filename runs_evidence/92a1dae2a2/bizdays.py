from datetime import date, timedelta
from typing import Iterable, Union


def _is_business_day(d: date, holiday_set: set) -> bool:
    return d.weekday() < 5 and d not in holiday_set


def add_business_days(start: date, n: int, holidays: Iterable[date] = ()) -> date:
    """
    Add `n` business days to `start` date.

    Skips Saturdays, Sundays, and dates present in `holidays`.
    - If n == 0: returns `start` if it is a business day, otherwise advances to the next business day.
    - If n > 0: moves forward `n` business days.
    - If n < 0: moves backward `|n|` business days.
    """
    holiday_set = set(holidays)
    current = start

    if n == 0:
        while not _is_business_day(current, holiday_set):
            current += timedelta(days=1)
        return current

    step = timedelta(days=1 if n > 0 else -1)
    remaining = abs(n)

    while remaining > 0:
        current += step
        if _is_business_day(current, holiday_set):
            remaining -= 1

    return current
