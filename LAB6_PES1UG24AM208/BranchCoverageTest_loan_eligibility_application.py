"""Branch coverage tests for loan_eligibility.py.

Every decision point in the application is taken in both directions:
    * credit_band       -> 4 if/elif statements
    * is_eligible       -> 4 if statements
    * interest_rate     -> 4 if/elif statements

Run with:
    coverage erase
    coverage run --branch -m pytest BranchCoverageTest_loan_eligibility_application.py -q
    coverage report -m
"""

import pytest

from loan_eligibility import credit_band, interest_rate, is_eligible


# ------------------------------------------------------------------ credit_band
@pytest.mark.parametrize("score", [299, 901])
def test_credit_band_invalid_score_both_sides_of_or(score):
    """Line 5 TRUE -> line 6 (both score < 300 and score > 900)."""
    with pytest.raises(ValueError, match="invalid score"):
        credit_band(score)


@pytest.mark.parametrize(
    "score, expected",
    [
        (750, "excellent"),  # line 7 TRUE  -> line 8
        (650, "good"),       # line 7 FALSE -> line 9 TRUE  -> line 10
        (550, "fair"),       # line 9 FALSE -> line 11 TRUE -> line 12
        (549, "poor"),       # line 11 FALSE -> line 13 (fall-through)
    ],
)
def test_credit_band_all_bands_and_fall_through(score, expected):
    """Both outcomes of every if/elif in credit_band."""
    assert credit_band(score) == expected


# ----------------------------------------------------------------- is_eligible
def test_is_eligible_unknown_employment_raises():
    """Line 17 TRUE -> line 18."""
    with pytest.raises(ValueError, match="unknown employment"):
        is_eligible(30, 50000, "intern", 800)


@pytest.mark.parametrize("age", [20, 61])
def test_is_eligible_age_out_of_range(age):
    """Line 19 TRUE -> line 20 (both age < 21 and age > 60)."""
    assert is_eligible(age, 50000, "salaried", 800) is False


@pytest.mark.parametrize(
    "employment, income",
    [
        ("salaried", 24999),      # just below 25000
        ("self_employed", 39999),  # just below 40000
    ],
)
def test_is_eligible_income_below_minimum(employment, income):
    """Line 21 TRUE -> line 22 for both employment types."""
    assert is_eligible(30, income, employment, 800) is False


def test_is_eligible_rejected_for_poor_credit():
    """Line 23 TRUE -> line 24."""
    assert is_eligible(30, 50000, "salaried", 500) is False


@pytest.mark.parametrize(
    "age, income, employment, score",
    [
        (30, 50000, "salaried", 800),       # boundary-friendly normal case
        (21, 25000, "salaried", 550),       # lower age/income/score boundaries
        (60, 40000, "self_employed", 900),  # upper age/score boundaries
    ],
)
def test_is_eligible_accepted_on_false_branches(age, income, employment, score):
    """Line 17 FALSE -> 19 -> 21 -> 23 FALSE -> line 25."""
    assert is_eligible(age, income, employment, score) is True


# ---------------------------------------------------------------- interest_rate
@pytest.mark.parametrize(
    "score, expected",
    [
        (800, 8),  # line 30 TRUE  -> line 31 (excellent)
        (700, 10), # line 30 FALSE -> line 32 TRUE -> line 33 (good)
        (600, 13), # line 30/32 FALSE -> else line 35 (fair)
        (500, 13), # line 30/32 FALSE -> else line 35 (poor)
    ],
)
def test_interest_rate_all_band_branches(score, expected):
    """Both outcomes of the band-selection if/elif."""
    assert interest_rate(score, "salaried", False) == expected


@pytest.mark.parametrize("employment, expected", [("salaried", 8), ("self_employed", 9)])
def test_interest_rate_employment_branch(employment, expected):
    """Line 36 TRUE -> line 37 and FALSE -> line 38."""
    assert interest_rate(800, employment, False) == expected


@pytest.mark.parametrize("has_collateral, expected", [(True, 6), (False, 8)])
def test_interest_rate_collateral_branch(has_collateral, expected):
    """Line 38 TRUE -> line 39 and FALSE -> line 40."""
    assert interest_rate(800, "salaried", has_collateral) == expected
