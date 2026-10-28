"""Automated unit tests for analytical insights engine."""

import pandas as pd
import pytest
from src.analytics import calculate_summary_kpis
from src.correlation import calculate_correlation
from src.insights import generate_cohort_insights


def test_insights_generation_with_complete_data():
    """Verify all categories of insights are populated accurately."""
    df = pd.DataFrame(
        {
            "student_id": ["S1", "S2", "S3", "S4"],
            "attendance_percentage": [65.0, 72.0, 85.0, 92.0],
            "average_marks": [45.0, 58.0, 78.0, 88.0],
        }
    )
    kpis = calculate_summary_kpis(df, attendance_threshold=75.0, marks_threshold=50.0)
    corr = calculate_correlation(df)

    subject_df = pd.DataFrame(
        {
            "subject": ["Data Structures", "Mathematics"],
            "average_marks": [80.0, 65.0],
            "average_attendance": [85.0, 78.0],
        }
    )

    quality = {"duplicate_count": 0, "missing_count": 0, "out_of_range_count": 0}

    insights = generate_cohort_insights(
        kpis,
        correlation=corr,
        subject_perf_df=subject_df,
        quality_summary=quality,
    )

    categories = [ins.category for ins in insights]
    assert "attendance" in categories
    assert "performance" in categories
    assert "correlation" in categories
    assert "quality" in categories

    # Verify non-causal disclaimer present in correlation insight
    corr_insight = next(ins for ins in insights if ins.category == "correlation")
    assert "does not imply direct causation" in corr_insight.description.lower()


def test_insights_empty_cohort():
    """Verify empty dataset generates graceful warning insight."""
    empty_kpis = calculate_summary_kpis(pd.DataFrame())
    insights = generate_cohort_insights(empty_kpis)
    assert len(insights) == 1
    assert insights[0].title == "No Data Available"
    assert insights[0].severity == "warning"
