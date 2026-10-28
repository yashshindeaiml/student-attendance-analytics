"""Automated unit tests for correlation analysis and edge cases."""

import numpy as np
import pandas as pd
import pytest
from src.correlation import (
    calculate_correlation,
    generate_correlation_report,
    interpret_correlation,
)


def test_perfect_positive_correlation():
    """Verify r = 1.0 for perfectly linear proportional data."""
    df = pd.DataFrame(
        {
            "attendance_percentage": [50.0, 60.0, 70.0, 80.0, 90.0],
            "average_marks": [50.0, 60.0, 70.0, 80.0, 90.0],
        }
    )
    res = calculate_correlation(df)
    assert res.is_valid
    assert res.pearson_r == 1.0
    assert res.spearman_rho == 1.0
    assert res.direction == "positive"
    assert res.strength == "strong"
    assert res.p_value_pearson is not None
    assert res.p_value_pearson < 0.01


def test_perfect_negative_correlation():
    """Verify r = -1.0 for perfectly inverse linear data."""
    df = pd.DataFrame(
        {
            "attendance_percentage": [50.0, 60.0, 70.0, 80.0, 90.0],
            "average_marks": [90.0, 80.0, 70.0, 60.0, 50.0],
        }
    )
    res = calculate_correlation(df)
    assert res.is_valid
    assert res.pearson_r == -1.0
    assert res.spearman_rho == -1.0
    assert res.direction == "negative"
    assert res.strength == "strong"


def test_empty_dataframe_correlation():
    """Verify empty dataframe handling."""
    res = calculate_correlation(pd.DataFrame())
    assert not res.is_valid
    assert res.status == "empty"
    assert res.pearson_r is None
    assert "empty" in res.interpretation.lower()


def test_single_row_correlation():
    """Verify fewer than 2 valid observations gives insufficient_data status."""
    df = pd.DataFrame({"attendance_percentage": [85.0], "average_marks": [75.0]})
    res = calculate_correlation(df)
    assert not res.is_valid
    assert res.status == "insufficient_data"
    assert res.valid_count == 1
    assert "Fewer than 2 valid" in res.interpretation


def test_constant_valued_columns_zero_variance():
    """Verify zero variance columns are flagged without division by zero errors."""
    df = pd.DataFrame(
        {
            "attendance_percentage": [75.0, 75.0, 75.0, 75.0],
            "average_marks": [50.0, 60.0, 70.0, 80.0],
        }
    )
    res = calculate_correlation(df)
    assert not res.is_valid
    assert res.status == "zero_variance"
    assert res.pearson_r is None
    assert "Zero variance detected" in res.interpretation


def test_missing_values_handled_correctly():
    """Verify rows with missing values are excluded from calculation and counted."""
    df = pd.DataFrame(
        {
            "attendance_percentage": [50.0, 60.0, None, 80.0, 90.0],
            "average_marks": [50.0, None, 70.0, 80.0, 90.0],
        }
    )
    res = calculate_correlation(df)
    assert res.is_valid
    assert res.valid_count == 3  # (50, 50), (80, 80), (90, 90)
    assert res.missing_count == 2
    assert res.pearson_r == 1.0


def test_interpret_correlation_thresholds():
    """Verify documented interpretation thresholds."""
    # |r| < 0.20
    d, s, _ = interpret_correlation(0.15)
    assert s == "negligible"

    # 0.20 <= |r| < 0.40
    d, s, _ = interpret_correlation(0.35)
    assert s == "weak"
    assert d == "positive"

    # 0.40 <= |r| < 0.70
    d, s, _ = interpret_correlation(-0.55)
    assert s == "moderate"
    assert d == "negative"

    # 0.70 <= |r| <= 1.00
    d, s, _ = interpret_correlation(0.85)
    assert s == "strong"
    assert d == "positive"


def test_generate_correlation_report():
    """Verify report formatting includes essential sections."""
    df = pd.DataFrame(
        {
            "attendance_percentage": [60.0, 70.0, 80.0, 90.0],
            "average_marks": [55.0, 65.0, 78.0, 88.0],
        }
    )
    res = calculate_correlation(df)
    report = generate_correlation_report(res)
    assert "Correlation Analysis Report" in report
    assert "Pearson Correlation" in report
    assert "Spearman" in report
    assert "Methodological & Ethical Disclaimer" in report
