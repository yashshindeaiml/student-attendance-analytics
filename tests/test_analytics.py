"""Automated unit tests for core analytical statistics and KPI calculations."""

import pandas as pd
import pytest
from src.analytics import (
    calculate_summary_kpis,
    categorize_attendance,
    categorize_marks,
    filter_dataset,
    get_students_needing_support,
    get_subject_performance,
    get_top_performers,
)


@pytest.fixture
def sample_student_df():
    """Deterministic fixture with known metrics."""
    return pd.DataFrame(
        {
            "student_id": ["S1", "S2", "S3", "S4"],
            "attendance_percentage": [60.0, 70.0, 80.0, 90.0],
            "average_marks": [40.0, 60.0, 80.0, 100.0],
            "department": ["CS", "CS", "IT", "IT"],
            "semester": ["Sem 3", "Sem 4", "Sem 3", "Sem 4"],
            "class": ["Section A", "Section B", "Section A", "Section B"],
        }
    )


def test_calculate_summary_kpis(sample_student_df):
    """Verify calculated metrics match exact mathematical values."""
    kpis = calculate_summary_kpis(
        sample_student_df,
        attendance_threshold=75.0,
        marks_threshold=50.0,
    )
    assert kpis.total_students == 4
    assert kpis.average_attendance == 75.0
    assert kpis.median_attendance == 75.0
    assert kpis.min_attendance == 60.0
    assert kpis.max_attendance == 90.0

    assert kpis.average_marks == 70.0
    assert kpis.median_marks == 70.0
    assert kpis.min_marks == 40.0
    assert kpis.max_marks == 100.0

    # Students below 75% attendance: S1 (60) and S2 (70) -> 2 out of 4 (50%)
    assert kpis.students_below_threshold == 2
    assert kpis.percentage_below_threshold == 50.0

    # Students needing support: S1 (att 60 < 75 or marks 40 < 50), S2 (att 70 < 75) -> 2
    assert kpis.students_needing_support == 2
    assert kpis.percentage_needing_support == 50.0


def test_empty_dataframe_kpis():
    """Verify empty dataframe returns zeroed summary KPIs without raising exceptions."""
    kpis = calculate_summary_kpis(pd.DataFrame())
    assert kpis.total_students == 0
    assert kpis.average_attendance == 0.0
    assert kpis.average_marks == 0.0


def test_categorize_attendance(sample_student_df):
    """Verify category assignment and threshold status."""
    cat_df = categorize_attendance(sample_student_df, threshold=75.0)
    assert "attendance_category" in cat_df.columns
    assert "threshold_status" in cat_df.columns

    # S1 is 60.0 -> Low (60% - 75%)
    assert "Low" in cat_df.loc[cat_df["student_id"] == "S1", "attendance_category"].iloc[0]
    # S4 is 90.0 -> Excellent (>= 85%)
    assert "Excellent" in cat_df.loc[cat_df["student_id"] == "S4", "attendance_category"].iloc[0]
    # S1 & S2 below threshold
    assert (
        cat_df.loc[cat_df["student_id"] == "S1", "threshold_status"].iloc[0] == "Below Threshold"
    )
    assert (
        cat_df.loc[cat_df["student_id"] == "S4", "threshold_status"].iloc[0] == "Meeting Threshold"
    )


def test_categorize_marks(sample_student_df):
    """Verify performance band assignment."""
    band_df = categorize_marks(sample_student_df)
    assert "performance_band" in band_df.columns
    # S1 is 40.0 -> Average
    assert "Average" in band_df.loc[band_df["student_id"] == "S1", "performance_band"].iloc[0]
    # S4 is 100.0 -> Distinction
    assert "Distinction" in band_df.loc[band_df["student_id"] == "S4", "performance_band"].iloc[0]


def test_get_top_performers(sample_student_df):
    """Verify top performers ranking."""
    top_df = get_top_performers(sample_student_df, n=2)
    assert len(top_df) == 2
    assert top_df.iloc[0]["student_id"] == "S4"
    assert top_df.iloc[1]["student_id"] == "S3"


def test_get_students_needing_support(sample_student_df):
    """Verify correct identification of students needing academic support."""
    supp_df = get_students_needing_support(
        sample_student_df,
        attendance_threshold=75.0,
        marks_threshold=50.0,
    )
    assert len(supp_df) == 2
    assert set(supp_df["student_id"]) == {"S1", "S2"}


def test_get_subject_performance():
    """Verify subject-level metric aggregation."""
    sub_df = pd.DataFrame(
        {
            "subject": ["Math", "Math", "Science", "Science"],
            "marks_obtained": [70.0, 90.0, 40.0, 60.0],
            "maximum_marks": [100.0, 100.0, 100.0, 100.0],
            "attendance_percentage": [80.0, 90.0, 60.0, 70.0],
        }
    )
    res = get_subject_performance(sub_df)
    assert len(res) == 2
    math_row = res[res["subject"] == "Math"].iloc[0]
    assert math_row["average_marks"] == 80.0
    assert math_row["average_attendance"] == 85.0
    assert math_row["highest_marks"] == 90.0
    assert math_row["lowest_marks"] == 70.0
    assert math_row["pass_percentage"] == 100.0


def test_filter_dataset(sample_student_df):
    """Verify multi-criteria filtering."""
    # Filter by department
    f_dept = filter_dataset(sample_student_df, department="CS")
    assert len(f_dept) == 2
    assert (f_dept["department"] == "CS").all()

    # Filter by attendance range
    f_att = filter_dataset(sample_student_df, min_attendance=75.0, max_attendance=85.0)
    assert len(f_att) == 1
    assert f_att.iloc[0]["student_id"] == "S3"

    # Filter by search query
    f_search = filter_dataset(sample_student_df, search_query="S2")
    assert len(f_search) == 1
    assert f_search.iloc[0]["student_id"] == "S2"
