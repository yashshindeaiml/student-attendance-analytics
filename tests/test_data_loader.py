"""Automated unit tests for dataset loading and format detection."""

from io import StringIO
from pathlib import Path
import pytest
import pandas as pd
from src.data_loader import (
    DataLoaderError,
    detect_dataset_type,
    load_bundled_student_data,
    load_bundled_subject_data,
    load_file,
    normalize_column_name,
)


def test_normalize_column_name():
    """Verify column normalization rules."""
    assert normalize_column_name(" Student ID ") == "student_id"
    assert normalize_column_name("Attendance-Percentage") == "attendance_percentage"
    assert normalize_column_name("AVERAGE.MARKS") == "average_marks"


def test_detect_dataset_type():
    """Verify detection of student-level vs subject-level datasets."""
    student_df = pd.DataFrame(
        {
            "student_id": ["S1"],
            "attendance_percentage": [85.0],
            "average_marks": [72.0],
        }
    )
    assert detect_dataset_type(student_df) == "student_level"

    subject_df = pd.DataFrame(
        {
            "student_id": ["S1"],
            "subject": ["Math"],
            "marks_obtained": [80],
            "maximum_marks": [100],
            "attendance_percentage": [85.0],
        }
    )
    assert detect_dataset_type(subject_df) == "subject_level"

    unknown_df = pd.DataFrame({"random_col": [1, 2, 3]})
    assert detect_dataset_type(unknown_df) == "unknown"


def test_load_bundled_data():
    """Verify loading bundled datasets from project repository."""
    s_df = load_bundled_student_data()
    assert not s_df.empty
    assert len(s_df) >= 100
    assert "student_id" in s_df.columns
    assert "attendance_percentage" in s_df.columns
    assert "average_marks" in s_df.columns

    sub_df = load_bundled_subject_data()
    assert not sub_df.empty
    assert "subject" in sub_df.columns


def test_load_file_csv_buffer():
    """Verify loading dataset from in-memory CSV buffer."""
    csv_text = "student_id,attendance_percentage,average_marks\nSTD-01,80.5,75.0\nSTD-02,90.0,85.0\n"
    buf = StringIO(csv_text)
    df = load_file(buf, filename="test.csv")
    assert len(df) == 2
    assert "attendance_percentage" in df.columns


def test_load_empty_file_raises_error():
    """Verify empty file raises DataLoaderError."""
    buf = StringIO("")
    with pytest.raises(DataLoaderError):
        load_file(buf, filename="empty.csv")


def test_load_nonexistent_file_raises_error():
    """Verify nonexistent file path raises DataLoaderError."""
    with pytest.raises(DataLoaderError):
        load_file(Path("non_existent_file_12345.csv"))
