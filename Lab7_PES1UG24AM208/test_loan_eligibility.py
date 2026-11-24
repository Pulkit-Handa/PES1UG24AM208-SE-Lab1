"""Property-based fuzz tests for loan_eligibility.py.

Run with:  python -m pytest test_loan_eligibility.py -v

The ``*_no_crash`` tests are the core fuzzing tests: Hypothesis generates
arbitrary/malformed inputs and asserts that the functions always return a
safe, well-typed value instead of raising an exception.  The remaining tests
check that valid inputs are still handled correctly.
"""

from string import ascii_letters, digits

from hypothesis import given, settings, strategies as st

from loan_eligibility import CATEGORIES, parse_income, monthly_emi, pan_category

# Deliberately wide input domain: text, None, numbers, containers, booleans.
ANY_INPUT = (
    st.text()
    | st.none()
    | st.integers()
    | st.floats(allow_nan=True, allow_infinity=True)
    | st.booleans()
    | st.lists(st.text())
    | st.dictionaries(st.text(), st.text())
)


# ---------------------------------------------------------------------------
# parse_income
# ---------------------------------------------------------------------------

@settings(max_examples=200, deadline=None)
@given(ANY_INPUT)
def test_parse_income_no_crash(value):
    """Any input must produce a non-negative int (never an exception)."""
    result = parse_income(value)
    assert isinstance(result, int) and not isinstance(result, bool)
    assert result >= 0


@settings(max_examples=200, deadline=None)
@given(st.integers(min_value=0, max_value=10 ** 12))
def test_parse_income_valid_numbers(amount):
    """Well-formed income strings must still parse to the exact integer."""
    assert parse_income(str(amount)) == amount
    assert parse_income(f"{amount:,}") == amount


# ---------------------------------------------------------------------------
# monthly_emi
# ---------------------------------------------------------------------------

@settings(max_examples=200, deadline=None)
@given(ANY_INPUT)
def test_monthly_emi_no_crash(value):
    """Any input must produce a non-negative finite number (no exception)."""
    result = monthly_emi(value)
    assert isinstance(result, (int, float)) and not isinstance(result, bool)
    assert result >= 0


@settings(max_examples=200, deadline=None)
@given(
    st.integers(min_value=1_000, max_value=10_000_000),
    st.integers(min_value=1, max_value=30),
    st.integers(min_value=1, max_value=40),
)
def test_monthly_emi_valid_inputs(principal, rate, years):
    """Valid principal,rate,years triples must give a positive EMI."""
    result = monthly_emi(f"{principal},{rate},{years}")
    assert isinstance(result, float)
    assert result > 0


def test_monthly_emi_zero_rate():
    """A zero interest rate must not divide by zero."""
    assert monthly_emi("120000,0,1") == 10000.0


# ---------------------------------------------------------------------------
# pan_category
# ---------------------------------------------------------------------------

@settings(max_examples=200, deadline=None)
@given(ANY_INPUT)
def test_pan_category_no_crash(value):
    """Any input must return a known category or 'Unknown' (no exception)."""
    result = pan_category(value)
    assert result in set(CATEGORIES.values()) | {"Unknown"}


@settings(max_examples=200, deadline=None)
@given(st.sampled_from(sorted(CATEGORIES)), st.booleans())
def test_pan_category_valid_codes(code, use_upper_case):
    """The 4th PAN character selects the category, in either case."""
    letter = code if use_upper_case else code.lower()
    assert pan_category(f"ABC{letter}E1234F") == CATEGORIES[code]


# Extra guard: a PAN built entirely from random text must stay well-typed.
@settings(max_examples=200, deadline=None)
@given(st.text(alphabet=ascii_letters + digits + " @-#", max_size=40))
def test_pan_category_random_text(text):
    assert pan_category(text) in set(CATEGORIES.values()) | {"Unknown"}
