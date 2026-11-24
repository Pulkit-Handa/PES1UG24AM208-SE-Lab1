"""Code (line) coverage tests for loan_eligibility.py.

Every executable line of the application is exercised at least once.

Run with:
    coverage erase
    coverage run -m pytest CodeCoverageTest_loan_eligibility_application.py -q
    coverage report -m
"""

import pytest

from loan_eligibility import credit_band, interest_rate, is_eligible


# ------------------------------------------------------------------ credit_band
def test_credit_band_rejects_invalid_score():
    """Line 6: an out-of-range score raises ValueError."""
    with pytest.raises(ValueError, match="invalid score"):
        credit_band(150)


def test_credit_band_excellent():
    """Line 8: score >= 750."""
    assert credit_band(750) == "excellent"


def test_credit_band_good():
    """Line 10: 650 <= score < 750."""
    assert credit_band(650) == "good"


def test_credit_band_fair():
    """Line 12: 550 <= score < 650."""
    assert credit_band(550) == "fair"


def test_credit_band_poor():
    """Line 13: score < 550."""
    assert credit_band(549) == "poor"


# ----------------------------------------------------------------- is_eligible
def test_is_eligible_rejects_unknown_employment():
    """Line 18: employment outside MIN_INCOME raises ValueError."""
    with pytest.raises(ValueError, match="unknown employment"):
        is_eligible(30, 50000, "intern", 800)


def test_is_eligible_rejects_young_applicant():
    """Line 20: age < 21."""
    assert is_eligible(20, 50000, "salaried", 800) is False


def test_is_eligible_rejects_low_income():
    """Line 22: income below the minimum for salaried employment."""
    assert is_eligible(30, 24999, "salaried", 800) is False


def test_is_eligible_rejects_poor_credit():
    """Line 24: credit band is poor."""
    assert is_eligible(30, 50000, "salaried", 500) is False


def test_is_eligible_accepts_valid_applicant():
    """Line 25: every eligibility check passes."""
    assert is_eligible(30, 50000, "salaried", 800) is True


# ---------------------------------------------------------------- interest_rate
def test_interest_rate_excellent_band_base_rate():
    """Line 31: excellent band base rate is 8."""
    assert interest_rate(800, "salaried", False) == 8


def test_interest_rate_good_band_base_rate():
    """Line 33: good band base rate is 10."""
    assert interest_rate(700, "salaried", False) == 10


def test_interest_rate_fair_and_poor_band_base_rate():
    """Line 35: fair and poor bands both use the 13% base rate."""
    assert interest_rate(600, "salaried", False) == 13
    assert interest_rate(500, "salaried", False) == 13


def test_interest_rate_self_employed_surcharge():
    """Line 37: self-employed applicants pay 1% more."""
    assert interest_rate(800, "self_employed", False) == 9


def test_interest_rate_collateral_discount():
    """Line 39: collateral reduces the rate by 2%."""
    assert interest_rate(800, "salaried", True) == 6
