markdown
Copy
# Ethiopian Date Converter

A Python package to convert dates between the **Gregorian** and **Ethiopian** calendars. It supports localization, formatting, and various utilities for working with Ethiopian dates.

---

## **Installation**

You can install the package using
`pip install ethiopian-date-converter`

## **Features**

**Date Conversion:**

- Convert Gregorian dates to Ethiopian dates.
- Convert Ethiopian dates to Gregorian dates.

**Formatting:**
- Format Ethiopian dates with month names and time.

**Utilities:**
- Check if a year is a leap year in the Ethiopian calendar.
- Get the number of days in a month.
- Add days or years to an Ethiopian date.
- Compare Ethiopian dates.
- Calculate the difference in days between two dates.

## **Usage**

### **Basic Conversion**

```python
from ethiopian_date_converter import to_ethiopian, to_gregorian, EtDate

# Convert Gregorian to Ethiopian
gregorian_date = "2023-10-05"
ethiopian_date = to_ethiopian(gregorian_date)
print("Ethiopian Date:", ethiopian_date)  # Output: EtDate(day=25, month=1, year=2016)

# Convert Ethiopian to Gregorian
ethiopian_date = EtDate(25, 1, 2016)
gregorian_date = to_gregorian(ethiopian_date)
print("Gregorian Date:", gregorian_date.strftime("%Y-%m-%d"))  # Output: 2023-10-05

# Get month name in Amharic
month_name = get_et_month_name(1, locale="AMH")
print("Month Name:", month_name)  # Output: መስከረም

# Get month name in African Orthodox
month_name = get_et_month_name(1, locale="AO")
print("Month Name:", month_name)  # Output: Fulbaana

# Format Ethiopian date
ethiopian_date = EtDate(25, 1, 2016)
print("Formatted Date:", ethiopian_date.formatted)  # Output: መስከረም 25, 2016

# Check if a year is a leap year
print("Is 2015 a leap year?", EtDate(1, 1, 2015).is_leap_year)  # Output: True

# Add days to a date
new_date = EtDate(1, 1, 2016).add_days(30)
print("New Date:", new_date)  # Output: EtDate(day=1, month=2, year=2016)

# Compare dates
date1 = EtDate(1, 1, 2016)
date2 = EtDate(2, 1, 2016)
print("Is date1 earlier than date2?", date1 < date2)  # Output: True

# Format Ethiopian date
ethiopian_date = EtDate(25, 1, 2016)
print("Formatted Date:", ethiopian_date.formatted)  # Output: መስከረም 25, 2016

# Get the number of days in a month
days = ethiopian_month_length(1, 2016)
print("Days in January 2016:", days)  # Output: 30

# Get the day of the week
day_of_week = EtDate(1, 1, 2016).day_of_week
print("Day of the week:", day_of_week)  # Output: ሰኞ


# Check if a year is a leap year
print("Is 2015 a leap year?", EtDate(1, 1, 2015).is_leap_year)  # Output: True

# Add days to a date
new_date = EtDate(1, 1, 2016).add_days(30)
print("New Date:", new_date)  # Output: EtDate(day=1, month=2, year=2016)

# Compare dates
date1 = EtDate(1, 1, 2016)
date2 = EtDate(2, 1, 2016)
print("Is date1 earlier than date2?", date1 < date2)  # Output: True

# Ethiopian New Year (Meskerem 1)
ethiopian_new_year = to_ethiopian("2023-09-11")
print("Ethiopian New Year:", ethiopian_new_year)  # Output: EtDate(day=1, month=1, year=2016)

# Ethiopian Christmas (Tir 29)
ethiopian_christmas = to_ethiopian("2023-01-07")
print("Ethiopian Christmas:", ethiopian_christmas)  # Output: EtDate(day=28, month=4, year=2015)
```

## **API Reference**

### **Functions**

- `to_ethiopian(gregorian_date: str) -> EtDate`: Convert a Gregorian date to an Ethiopian date.

- `to_gregorian(ethiopian_date: EtDate) -> datetime`: Convert an Ethiopian date to a Gregorian date.

- `is_leap_year_et(year: int) -> bool`: Check if a year is a leap year in the Ethiopian calendar.

- `ethiopian_month_length(month: int, year: int) -> int`: Get the number of days in a month.

- `get_et_month_name(month: int, locale: str = "AMH") -> str`: Get the name of an Ethiopian month.

### **Class**

- `EtDate(day: int, month: int, year: int)`: Represents an Ethiopian date.

- `add_days(days: int) -> EtDate`: Add days to the date.

- `add_years(years: int) -> EtDate`: Add years to the date.

- `to_gregorian() -> datetime`: Convert the date to a Gregorian date.

- `is_leap_year -> bool`: Check if the year is a leap year.

- `month_length -> int`: Get the number of days in the month.

- `day_of_week -> str`: Get the day of the week in Amharic.

- `formatted -> str`: Get the formatted date string.

## **Contributing**

Contributions are welcome! Please open an issue or submit a pull request on GitHub.


# Future Features
 - integrate with django
 - 

