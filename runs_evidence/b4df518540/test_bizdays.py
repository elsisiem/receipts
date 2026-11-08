import unittest
from datetime import date
from bizdays import add_business_days


class TestAddBusinessDays(unittest.TestCase):
    def test_positive_days_within_week(self):
        start = date(2023, 10, 2)  # Monday
        self.assertEqual(add_business_days(start, 1), date(2023, 10, 3))
        self.assertEqual(add_business_days(start, 4), date(2023, 10, 6))

    def test_friday_plus_one(self):
        start = date(2023, 10, 6)  # Friday
        self.assertEqual(add_business_days(start, 1), date(2023, 10, 9))  # Following Monday

    def test_holiday_monday(self):
        start = date(2023, 10, 6)  # Friday
        holiday = date(2023, 10, 9)  # Monday holiday
        self.assertEqual(add_business_days(start, 1, holidays=[holiday]), date(2023, 10, 10))  # Tuesday

    def test_n_zero_business_day(self):
        start = date(2023, 10, 2)  # Monday (business day)
        self.assertEqual(add_business_days(start, 0), date(2023, 10, 2))

    def test_n_zero_weekend(self):
        saturday = date(2023, 10, 7)
        sunday = date(2023, 10, 8)
        self.assertEqual(add_business_days(saturday, 0), date(2023, 10, 9))
        self.assertEqual(add_business_days(sunday, 0), date(2023, 10, 9))

    def test_n_zero_holiday(self):
        holiday_monday = date(2023, 10, 9)
        self.assertEqual(add_business_days(holiday_monday, 0, holidays=[holiday_monday]), date(2023, 10, 10))

    def test_n_zero_weekend_followed_by_holiday(self):
        saturday = date(2023, 10, 7)
        holiday_monday = date(2023, 10, 9)
        self.assertEqual(add_business_days(saturday, 0, holidays=[holiday_monday]), date(2023, 10, 10))

    def test_negative_days(self):
        start = date(2023, 10, 9)  # Monday
        self.assertEqual(add_business_days(start, -1), date(2023, 10, 6))  # Previous Friday

    def test_negative_days_with_holiday(self):
        start = date(2023, 10, 10)  # Tuesday
        holiday_monday = date(2023, 10, 9)
        self.assertEqual(add_business_days(start, -1, holidays=[holiday_monday]), date(2023, 10, 6))

    def test_negative_days_from_weekend(self):
        sunday = date(2023, 10, 8)
        self.assertEqual(add_business_days(sunday, -1), date(2023, 10, 6))  # Previous Friday

    def test_year_boundary_forward(self):
        start = date(2023, 12, 29)  # Friday
        new_years = date(2024, 1, 1)  # Monday
        self.assertEqual(add_business_days(start, 1, holidays=[new_years]), date(2024, 1, 2))

    def test_year_boundary_backward(self):
        start = date(2024, 1, 2)  # Tuesday
        new_years = date(2024, 1, 1)  # Monday
        self.assertEqual(add_business_days(start, -1, holidays=[new_years]), date(2023, 12, 29))


if __name__ == "__main__":
    unittest.main()
