from datetime import date, timedelta
from typing import Iterable, Set, Union


def add_business_days(
    start: date,
    n: int,
    holidays: Iterable[date] = ()
) -> date:
    """
    Add `n` business days to `start` date, skipping weekends (Saturday, Sunday) and holidays.

    If n == 0, returns `start` if it is already a business day, otherwise advances to the next business day.
    If n > 0, advances forward by n business days.
    If n < 0, moves backward by |n| business days.
    """
    holiday_set: Set[date] = set(holidays)

    def is_business_day(d: date) -> bool:
        return d.weekday() < 5 and d not in holiday_set

    current = start

    if n == 0:
        while not is_business_day(current):
            current += timedelta(days=1)
        return current

    step = 1 if n > 0 else -1
    remaining = abs(n)

    while remaining > 0:
        current += timedelta(days=step)
        if is_business_day(current):
            remaining -= 1

    return current
