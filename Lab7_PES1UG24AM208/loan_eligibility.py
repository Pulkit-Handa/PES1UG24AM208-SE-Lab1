"""Loan eligibility helpers.

These functions are intentionally defensive: every public function accepts
*any* input and returns a safe, well-typed value instead of raising an
exception.  Invalid input is reported with a neutral fallback value.
"""

import math

CATEGORIES = {"P": "Individual", "C": "Company", "H": "HUF", "F": "Firm"}

# Fallback values used when input cannot be interpreted.
INVALID_INCOME = 0
INVALID_EMI = 0.0
UNKNOWN_CATEGORY = "Unknown"

# Sanity limits for a loan term / interest rate (also prevent float overflow).
MAX_YEARS = 100
MAX_RATE_PERCENT = 100.0


def _to_nonnegative_number(value, default):
    """Convert a numeric-looking string to a finite, non-negative float."""
    if not isinstance(value, str):
        return default
    try:
        number = float(value.strip().replace(",", ""))
    except (TypeError, ValueError, OverflowError):
        return default
    if not math.isfinite(number) or number < 0:
        return default
    return number


def parse_income(income):
    """Return a non-negative integer income, or 0 for invalid input.

    Handles thousands separators, surrounding whitespace, wrong types,
    empty strings, negative values and non-numeric text.
    """
    if isinstance(income, bool):
        return INVALID_INCOME
    if isinstance(income, int):
        return income if income >= 0 else INVALID_INCOME

    if not isinstance(income, str):
        return INVALID_INCOME

    cleaned = income.replace(",", "").strip()
    # Reject signs, decimal points, scientific notation and stray text.
    if not cleaned or not cleaned.isdigit():
        return INVALID_INCOME
    try:
        return int(cleaned)
    except (ValueError, OverflowError):
        # int() limits very long digit strings (and unicode digits may not
        # be decimal digits), so treat those as invalid too.
        return INVALID_INCOME


def monthly_emi(details):
    """Return the monthly EMI for 'principal,rate,years', or 0.0 if invalid.

    ``rate`` is an annual percentage (decimals are accepted).  A zero rate
    is handled as simple principal / number-of-months division instead of
    dividing by zero in the standard annuity formula.
    """
    if not isinstance(details, str):
        return INVALID_EMI

    fields = details.split(",")
    if len(fields) != 3:
        return INVALID_EMI

    principal = _to_nonnegative_number(fields[0], INVALID_EMI)
    rate = _to_nonnegative_number(fields[1], INVALID_EMI)
    years = _to_nonnegative_number(fields[2], INVALID_EMI)

    if not 0 < years <= MAX_YEARS:
        return INVALID_EMI
    if rate > MAX_RATE_PERCENT:
        return INVALID_EMI

    months = years * 12
    if rate == 0:
        return round(principal / months, 2)

    r = rate / 1200
    try:
        growth = (1 + r) ** months
        emi = principal * r * growth / (growth - 1)
    except (OverflowError, ZeroDivisionError, ValueError):
        return INVALID_EMI

    if not math.isfinite(emi) or emi < 0:
        return INVALID_EMI
    return round(emi, 2)


def pan_category(pan):
    """Return the category selected by the 4th PAN character, or 'Unknown'.

    ``P`` -> Individual, ``C`` -> Company, ``H`` -> HUF, ``F`` -> Firm.
    Short strings, wrong types and unrecognised codes are safe.
    """
    if not isinstance(pan, str) or len(pan) < 4:
        return UNKNOWN_CATEGORY
    return CATEGORIES.get(pan[3].upper(), UNKNOWN_CATEGORY)


def main():
    print("==== Running parse_income ====")
    user_input = input("Enter monthly income (e.g. 50,000): ")
    result = parse_income(user_input)
    print("Income:", result)

    print("\n==== Running monthly_emi ====")
    user_input = input("Enter principal,rate,years (e.g. 500000,10,5): ")
    result = monthly_emi(user_input)
    print("Monthly EMI:", result)

    print("\n==== Running pan_category ====")
    user_input = input("Enter a PAN number (e.g. ABCPE1234F): ")
    result = pan_category(user_input)
    print("PAN Category:", result)


if __name__ == "__main__":
    main()
