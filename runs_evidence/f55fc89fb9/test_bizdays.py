import unittest
from datetime import date
from bizdays import add_business_days


class TestAddBusinessDays(unittest.TestCase):
    def test_friday_plus_one(self):
        # Friday Oct 13, 2023 + 1 business day -> Monday Oct 16, 2023
        start = date(2023, 10, 13)
        expected = date(2023, 10, 16)
        self.assertEqual(add_business_days(start, 1), expected)

    def test_holiday_monday(self):
        # Friday May 24, 2024 + 1 business day with Monday May 27, 2024 as holiday -> Tuesday May 28, 2024
        start = date(2024, 5, 24)
        holidays = [date(2024, 5, 27)]
        expected = date(2024, 5, 28)
        self.assertEqual(add_business_days(start, 1, holidays=holidays), expected)

    def test_year_boundary_forward(self):
        # Friday Dec 29, 2023 + 1 business day with Monday Jan 1, 2024 as holiday -> Tuesday Jan 2, 2024
        start = date(2023, 12, 29)
        holidays = [date(2024, 1, 1)]
        expected = date(2024, 1, 2)
        self.assertEqual(add_business_days(start, 1, holidays=holidays), expected)

    def test_year_boundary_backward(self):
        # Tuesday Jan 2, 2024 - 1 business day with Monday Jan 1, 2024 as holiday -> Friday Dec 29, 2023
        start = date(2024, 1, 2)
        holidays = [date(2024, 1, 1)]
        expected = date(2023, 12, 29)
        self.assertEqual(add_business_days(start, -1, holidays=holidays), expected)

    def test_negative_n_across_weekend(self):
        # Monday Oct 16, 2023 - 1 business day -> Friday Oct 13, 2023
        start = date(2023, 10, 16)
        expected = date(2023, 10, 13)
        self.assertEqual(add_business_days(start, -1), expected)

    def test_negative_n_starting_from_weekend(self):
        # Sunday Oct 15, 2023 - 1 business day -> Friday Oct 13, 2023
        start = date(2023, 10, 15)
        expected = date(2023, 10, 13)
        self.assertEqual(add_business_days(start, -1), expected)

    def test_zero_on_business_day(self):
        # Wednesday Oct 11, 2023 + 0 business days -> Wednesday Oct 11, 2023
        start = date(2023, 10, 11)
        self.assertEqual(add_business_days(start, 0), start)

    def test_zero_on_saturday(self):
        # Saturday Oct 14, 2023 + 0 business days -> Monday Oct 16, 2023
        start = date(2023, 10, 14)
        expected = date(2023, 10, 16)
        self.assertEqual(add_business_days(start, 0), expected)

    def test_zero_on_sunday(self):
        # Sunday Oct 15, 2023 + 0 business days -> Monday Oct 16, 2023
        start = date(2023, 10, 15)
        expected = date(2023, 10, 16)
        self.assertEqual(add_business_days(start, 0), expected)

    def test_zero_on_holiday_monday(self):
        # Monday May 27, 2024 (holiday) + 0 business days -> Tuesday May 28, 2024
        start = date(2024, 5, 27)
        holidays = [start]
        expected = date(2024, 5, 28)
        self.assertEqual(add_business_days(start, 0, holidays=holidays), expected)

    def test_multi_day_with_consecutive_holidays(self):
        # Wednesday Dec 20, 2023 + 5 business days with Dec 25 and Dec 26 as holidays
        # Day 1: Thu Dec 21
        # Day 2: Fri Dec 22
        # Weekend: Dec 23, 24
        # Holidays: Mon Dec 25, Tue Dec 26
        # Day 3: Wed Dec 27
        # Day 4: Thu Dec 28
        # Day 5: Fri Dec 29
        start = date(2023, 12, 20)
        holidays = [date(2023, 12, 25), date(2023, 12, 26)]
        expected = date(2023, 12, 29)
        self.assertEqual(add_business_days(start, 5, holidays=holidays), expected)


if __name__ == "__main__":
    unittest.main()
