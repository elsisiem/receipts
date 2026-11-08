from datetime import date, timedelta
from typing import Iterable, Set, Union


def add_business_days(
    start: date,
    n: int,
    holidays: Iterable[date] = ()
) -> date:
    """
    Add `n` business days to `start` date, skipping Saturdays, Sundays, and holidays.

    :param start: Starting datetime.date.
    :param n: Number of business days to add (can be positive, negative, or zero).
    :param holidays: Iterable of holiday datetime.date objects to skip.
    :return: The resulting datetime.date.
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
