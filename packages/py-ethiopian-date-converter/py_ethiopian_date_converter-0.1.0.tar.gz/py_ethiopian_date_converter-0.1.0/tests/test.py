import unittest
from datetime import datetime

from ethiopian_date_converter.ethiopian_date_convertor import (
    to_ethiopian,
    to_gregorian,
    is_leap_year_et,
    ethiopian_month_length,
    get_et_month_name,
    EthDate,
)


class TestEthiopianDateConverter(unittest.TestCase):
    def test_to_ethiopian(self):
        self.assertEqual(to_ethiopian(datetime(1996, 10, 7)),
                         EthDate(27, 1, 1989))
        self.assertEqual(to_ethiopian(datetime(2020, 9, 11)),
                         EthDate(1, 1, 2013))
        self.assertEqual(to_ethiopian(datetime(2023, 1, 7)),
                         EthDate(29, 4, 2015))

    def test_to_gregorian(self):
        self.assertEqual(to_gregorian(EthDate(24, 1, 2016)),
                         datetime(2023, 10, 5))
        self.assertEqual(to_gregorian(EthDate(1, 1, 2013)),
                         datetime(2020, 9, 11))
        self.assertEqual(to_gregorian(EthDate(28, 4, 2015)),
                         datetime(2023, 1, 6))

    def test_leap_year(self):
        self.assertTrue(is_leap_year_et(2015))
        self.assertFalse(is_leap_year_et(2016))
        self.assertTrue(is_leap_year_et(2019))

    def test_ethiopian_month_length(self):
        self.assertEqual(ethiopian_month_length(13, 2015),
                         6)
        self.assertEqual(ethiopian_month_length(13, 2016), 5)
        self.assertEqual(ethiopian_month_length(13, 2017), 5)
        self.assertEqual(ethiopian_month_length(1, 2016), 30)

    def test_ethiopian_holidays(self):
        self.assertEqual(to_ethiopian(
            datetime(2023, 9, 12)), EthDate(1, 1, 2016))
        # Ethiopian Christmas (Tir 29)
        self.assertEqual(to_ethiopian(datetime(2025, 1, 7)),
                         EthDate(29, 4, 2017))
        self.assertEqual(to_ethiopian(datetime(2025, 1, 19)),
                         EthDate(11, 5, 2017))

    def test_month_names(self):
        # Test Ethiopian month names
        self.assertEqual(get_et_month_name(1), "መስከረም")
        self.assertEqual(get_et_month_name(13), "ጳጉሜ")
        # Invalid month
        self.assertEqual(get_et_month_name(14), "")

    def test_day_of_week(self):
        self.assertEqual(EthDate(27, 1, 1989).day_of_week,
                         "ሰኞ")
        self.assertEqual(EthDate(28, 1, 1989).day_of_week, "ማክሰኞ")

    def test_add_days(self):
        # Test adding days to a date
        date = EthDate(1, 1, 2016)
        self.assertEqual(date.add_days(30), EthDate(
            1, 2, 2016))  # Add 30 days to Meskerem 1
        self.assertEqual(date.add_days(365), EthDate(1, 1, 2017))  # Add 1 year

    def test_add_years(self):
        # Test adding years to a date
        date = EthDate(6, 13, 2015)  # Leap year Pagume 6
        self.assertEqual(date.add_years(1), EthDate(
            5, 13, 2016))  # Non-leap year Pagume 5
        self.assertEqual(date.add_years(4), EthDate(
            6, 13, 2019))  # Leap year Pagume 6

    def test_comparison(self):
        # Test date comparisons
        date1 = EthDate(1, 1, 2016)
        date2 = EthDate(2, 1, 2016)
        self.assertTrue(date1 < date2)
        self.assertTrue(date1 <= date2)
        self.assertFalse(date1 > date2)
        self.assertFalse(date1 >= date2)
        self.assertTrue(date1 == EthDate(1, 1, 2016))

    def test_subtraction(self):
        # Test date subtraction
        date1 = EthDate(1, 1, 2016)
        date2 = EthDate(2, 1, 2016)
        self.assertEqual(date2 - date1, 1)  # Difference of 1 day

    def test_formatted_date(self):
        # Test formatted date output
        date = EthDate(1, 1, 2016)
        self.assertEqual(date.formatted(), "መስከረም 1, 2016")


if __name__ == "__main__":
    unittest.main()
