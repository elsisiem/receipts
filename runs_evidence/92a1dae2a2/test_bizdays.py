import unittest
from datetime import date
from bizdays import add_business_days


class TestAddBusinessDays(unittest.TestCase):
    def test_friday_plus_one(self):
        # 2023-10-06 is Friday -> next business day is Monday 2023-10-09
        start = date(2023, 10, 6)
        expected = date(2023, 10, 9)
        self.assertEqual(add_business_days(start, 1), expected)

    def test_friday_plus_one_with_holiday_monday(self):
        # 2023-10-06 is Friday, Monday 2023-10-09 is a holiday -> Tuesday 2023-10-10
        start = date(2023, 10, 6)
        holidays = [date(2023, 10, 9)]
        expected = date(2023, 10, 10)
        self.assertEqual(add_business_days(start, 1, holidays=holidays), expected)

    def test_n_zero_on_business_day(self):
        # Wednesday 2023-10-04 is a business day -> returns same day
        start = date(2023, 10, 4)
        self.assertEqual(add_business_days(start, 0), start)

    def test_n_zero_on_saturday(self):
        # Saturday 2023-10-07 -> Monday 2023-10-09
        start = date(2023, 10, 7)
        expected = date(2023, 10, 9)
        self.assertEqual(add_business_days(start, 0), expected)

    def test_n_zero_on_sunday(self):
        # Sunday 2023-10-08 -> Monday 2023-10-09
        start = date(2023, 10, 8)
        expected = date(2023, 10, 9)
        self.assertEqual(add_business_days(start, 0), expected)

    def test_n_zero_on_holiday_with_holiday_monday(self):
        # Saturday 2023-10-07, Monday 2023-10-09 is holiday -> Tuesday 2023-10-10
        start = date(2023, 10, 7)
        holidays = [date(2023, 10, 9)]
        expected = date(2023, 10, 10)
        self.assertEqual(add_business_days(start, 0, holidays=holidays), expected)

    def test_negative_n_monday_minus_one(self):
        # Monday 2023-10-09 minus 1 business day -> Friday 2023-10-06
        start = date(2023, 10, 9)
        expected = date(2023, 10, 6)
        self.assertEqual(add_business_days(start, -1), expected)

    def test_negative_n_with_holiday(self):
        # Tuesday 2023-10-10 minus 1 business day, with Monday holiday -> Friday 2023-10-06
        start = date(2023, 10, 10)
        holidays = [date(2023, 10, 9)]
        expected = date(2023, 10, 6)
        self.assertEqual(add_business_days(start, -1, holidays=holidays), expected)

    def test_negative_n_from_weekend(self):
        # Sunday 2023-10-08 minus 1 business day -> Friday 2023-10-06
        start = date(2023, 10, 8)
        expected = date(2023, 10, 6)
        self.assertEqual(add_business_days(start, -1), expected)

    def test_year_boundary_forward(self):
        # Friday 2021-12-31 (New Year's Eve) + 1 day, where Monday 2022-01-03 is holiday -> Tuesday 2022-01-04
        start = date(2021, 12, 31)
        holidays = [date(2022, 1, 3)]
        expected = date(2022, 1, 4)
        self.assertEqual(add_business_days(start, 1, holidays=holidays), expected)

    def test_year_boundary_backward(self):
        # Monday 2024-01-01 (holiday) minus 1 business day -> Friday 2023-12-29
        start = date(2024, 1, 1)
        holidays = [date(2024, 1, 1)]
        expected = date(2023, 12, 29)
        self.assertEqual(add_business_days(start, -1, holidays=holidays), expected)

    def test_multiple_days_forward_spanning_weeks_and_holidays(self):
        # Start on Wednesday 2023-11-22, add 5 business days
        # Holidays: Thanksgiving (2023-11-23), Day after Thanksgiving (2023-11-24)
        # Wed 11-22 -> skip Thu, Fri, Sat, Sun -> 1: Mon 11-27, 2: Tue 11-28, 3: Wed 11-29, 4: Thu 11-30, 5: Fri 12-01
        start = date(2023, 11, 22)
        holidays = [date(2023, 11, 23), date(2023, 11, 24)]
        expected = date(2023, 12, 1)
        self.assertEqual(add_business_days(start, 5, holidays=holidays), expected)


if __name__ == "__main__":
    unittest.main()
