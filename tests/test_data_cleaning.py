"""Automated unit tests for data cleaning, validation, and aggregation."""

import pandas as pd
import pytest
from src.data_cleaning import (
    aggregate_subject_to_student,
    clean_dataset,
    validate_and_clean_student_data,
    validate_and_clean_subject_data,
)


def test_missing_required_columns():
    """Verify missing required columns are flagged as invalid for analytics."""
    bad_df = pd.DataFrame({"student_id": ["S1"], "some_other_col": [10]})
    res = validate_and_clean_student_data(bad_df)
    assert not res.is_valid_for_analytics
    assert res.valid_rows == 0
    assert "missing_required_column" in res.issues_df["issue_type"].values


def test_duplicate_records_handled():
    """Verify duplicate student IDs are detected and only first is kept."""
    dup_df = pd.DataFrame(
        {
            "student_id": ["STD-1", "STD-1", "STD-2"],
            "attendance_percentage": [80.0, 85.0, 90.0],
            "average_marks": [70.0, 75.0, 80.0],
        }
    )
    res = validate_and_clean_student_data(dup_df)
    assert res.duplicate_count == 1
    assert len(res.cleaned_df) == 2
    assert "duplicate" in res.issues_df["issue_type"].values


def test_non_numeric_and_missing_values():
    """Verify non-numeric values are coerced and missing rows are flagged."""
    dirty_df = pd.DataFrame(
        {
            "student_id": ["STD-1", "STD-2", "STD-3"],
            "attendance_percentage": ["85.5", "invalid_string", None],
            "average_marks": [75.0, 80.0, 90.0],
        }
    )
    res = validate_and_clean_student_data(dirty_df)
    assert res.missing_count >= 1
    # Only STD-1 has valid numeric attendance and marks
    assert len(res.cleaned_df) == 1
    assert res.cleaned_df.iloc[0]["student_id"] == "STD-1"


def test_out_of_range_attendance_and_marks():
    """Verify attendance <0 or >100 and marks <0 or >100 are flagged and excluded."""
    range_df = pd.DataFrame(
        {
            "student_id": ["S1", "S2", "S3", "S4"],
            "attendance_percentage": [-5.0, 105.0, 80.0, 90.0],
            "average_marks": [60.0, 70.0, -10.0, 110.0],
        }
    )
    res = validate_and_clean_student_data(range_df)
    assert res.out_of_range_count == 4
    assert len(res.cleaned_df) == 0


def test_subject_level_validation_and_cleaning():
    """Verify subject-level dataset validation and duplicate student+subject detection."""
    sub_df = pd.DataFrame(
        {
            "student_id": ["STD-1", "STD-1", "STD-2"],
            "subject": ["Math", "Math", "Science"],
            "marks_obtained": [85.0, 90.0, 70.0],
            "maximum_marks": [100.0, 100.0, 100.0],
            "attendance_percentage": [90.0, 92.0, 80.0],
        }
    )
    res = validate_and_clean_subject_data(sub_df)
    assert res.duplicate_count == 1
    assert len(res.cleaned_df) == 2


def test_subject_level_aggregation_no_double_counting():
    """CRITICAL: Verify student-level aggregation eliminates multiple subject records per student."""
    sub_df = pd.DataFrame(
        {
            "student_id": ["STD-1", "STD-1", "STD-1", "STD-2", "STD-2"],
            "subject": ["Math", "Physics", "Chemistry", "Math", "Physics"],
            "marks_obtained": [80.0, 90.0, 70.0, 60.0, 80.0],
            "maximum_marks": [100.0, 100.0, 100.0, 100.0, 100.0],
            "attendance_percentage": [80.0, 90.0, 85.0, 70.0, 75.0],
            "department": ["CS", "CS", "CS", "IT", "IT"],
            "semester": ["Sem 3", "Sem 3", "Sem 3", "Sem 3", "Sem 3"],
        }
    )
    agg_df = aggregate_subject_to_student(sub_df)

    # Must contain exactly 2 unique students
    assert len(agg_df) == 2
    assert set(agg_df["student_id"]) == {"STD-1", "STD-2"}

    # STD-1 averages: marks (80+90+70)/300 = 80.0%, attendance (80+90+85)/3 = 85.0%
    std1_row = agg_df[agg_df["student_id"] == "STD-1"].iloc[0]
    assert std1_row["average_marks"] == 80.0
    assert std1_row["attendance_percentage"] == 85.0
    assert std1_row["subject_count"] == 3

    # STD-2 averages: marks (60+80)/200 = 70.0%, attendance (70+75)/2 = 72.5%
    std2_row = agg_df[agg_df["student_id"] == "STD-2"].iloc[0]
    assert std2_row["average_marks"] == 70.0
    assert std2_row["attendance_percentage"] == 72.5
    assert std2_row["subject_count"] == 2
