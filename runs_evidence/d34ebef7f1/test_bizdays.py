import unittest
from datetime import date
from bizdays import add_business_days


class TestAddBusinessDays(unittest.TestCase):
    def test_friday_plus_one(self):
        # 2023-10-06 is Friday -> +1 business day is Monday 2023-10-09
        friday = date(2023, 10, 6)
        expected = date(2023, 10, 9)
        self.assertEqual(add_business_days(friday, 1), expected)

    def test_friday_plus_one_with_holiday_monday(self):
        # 2023-10-06 is Friday, Monday 2023-10-09 is a holiday -> Tuesday 2023-10-10
        friday = date(2023, 10, 6)
        holiday_monday = date(2023, 10, 9)
        expected = date(2023, 10, 10)
        self.assertEqual(add_business_days(friday, 1, holidays=[holiday_monday]), expected)

    def test_n_zero_on_business_day(self):
        wednesday = date(2023, 10, 4)
        self.assertEqual(add_business_days(wednesday, 0), wednesday)

    def test_n_zero_on_saturday(self):
        saturday = date(2023, 10, 7)
        expected_monday = date(2023, 10, 9)
        self.assertEqual(add_business_days(saturday, 0), expected_monday)

    def test_n_zero_on_sunday(self):
        sunday = date(2023, 10, 8)
        expected_monday = date(2023, 10, 9)
        self.assertEqual(add_business_days(sunday, 0), expected_monday)

    def test_n_zero_on_holiday_weekday(self):
        monday = date(2023, 10, 9)
        expected_tuesday = date(2023, 10, 10)
        self.assertEqual(add_business_days(monday, 0, holidays=[monday]), expected_tuesday)

    def test_n_zero_on_weekend_with_following_holiday(self):
        # Saturday with Monday holiday should roll forward to Tuesday
        saturday = date(2023, 10, 7)
        holiday_monday = date(2023, 10, 9)
        expected_tuesday = date(2023, 10, 10)
        self.assertEqual(add_business_days(saturday, 0, holidays=[holiday_monday]), expected_tuesday)

    def test_negative_n_single_step(self):
        # Monday minus 1 business day -> previous Friday
        monday = date(2023, 10, 9)
        expected_friday = date(2023, 10, 6)
        self.assertEqual(add_business_days(monday, -1), expected_friday)

    def test_negative_n_with_holiday(self):
        # Tuesday minus 1 day where Monday is a holiday -> previous Friday
        tuesday = date(2023, 10, 10)
        holiday_monday = date(2023, 10, 9)
        expected_friday = date(2023, 10, 6)
        self.assertEqual(add_business_days(tuesday, -1, holidays=[holiday_monday]), expected_friday)

    def test_negative_n_starting_from_weekend(self):
        # Sunday minus 1 business day -> Friday
        sunday = date(2023, 10, 8)
        expected_friday = date(2023, 10, 6)
        self.assertEqual(add_business_days(sunday, -1), expected_friday)

    def test_year_boundary_forward(self):
        # 2023-12-29 is Friday. New Year's Day (Monday 2024-01-01) is a holiday.
        # Adding 1 business day should be Tuesday 2024-01-02.
        friday = date(2023, 12, 29)
        nyd = date(2024, 1, 1)
        expected = date(2024, 1, 2)
        self.assertEqual(add_business_days(friday, 1, holidays=[nyd]), expected)

    def test_year_boundary_backward(self):
        # Tuesday 2024-01-02 minus 1 business day with New Year's Day holiday -> Friday 2023-12-29
        tuesday = date(2024, 1, 2)
        nyd = date(2024, 1, 1)
        expected = date(2023, 12, 29)
        self.assertEqual(add_business_days(tuesday, -1, holidays=[nyd]), expected)

    def test_multiple_business_days(self):
        # Wednesday + 5 business days: Thu(1), Fri(2), Mon(3), Tue(4), Wed(5)
        start = date(2023, 10, 4)
        expected = date(2023, 10, 11)
        self.assertEqual(add_business_days(start, 5), expected)

    def test_multiple_negative_business_days(self):
        # Wednesday - 5 business days: Tue(1), Mon(2), Fri(3), Thu(4), Wed(5)
        start = date(2023, 10, 11)
        expected = date(2023, 10, 4)
        self.assertEqual(add_business_days(start, -5), expected)


if __name__ == "__main__":
    unittest.main()
