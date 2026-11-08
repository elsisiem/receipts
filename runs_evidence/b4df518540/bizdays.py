from datetime import date, timedelta
from typing import Iterable, Union


def add_business_days(
    start: date,
    n: int,
    holidays: Iterable[date] = ()
) -> date:
    """
    Add business days to a date, skipping weekends (Saturday, Sunday) and holidays.

    :param start: Starting date (datetime.date)
    :param n: Number of business days to add (can be positive, zero, or negative)
    :param holidays: Iterable of datetime.date objects representing holidays
    :return: The resulting business day (datetime.date)
    """
    holiday_set = set(holidays)

    def is_business_day(d: date) -> bool:
        return d.weekday() < 5 and d not in holiday_set

    current = start

    if n == 0:
        while not is_business_day(current):
            current += timedelta(days=1)
        return current

    step = timedelta(days=1 if n > 0 else -1)
    remaining = abs(n)

    while remaining > 0:
        current += step
        if is_business_day(current):
            remaining -= 1

    return current
