"""Automated unit tests for synthetic dataset generator."""

import pytest
import pandas as pd
from pathlib import Path
from src.data_generator import (
    generate_student_dataset,
    generate_subject_marks_dataset,
    generate_and_save_all,
)


def test_student_dataset_generation_count():
    """Verify exact count of students generated."""
    df = generate_student_dataset(n_students=150, random_seed=42)
    assert len(df) == 150
    assert df["student_id"].nunique() == 150


def test_student_dataset_columns():
    """Verify all required canonical columns are present."""
    df = generate_student_dataset(n_students=10, random_seed=42)
    expected_cols = [
        "student_id",
        "attendance_percentage",
        "average_marks",
        "department",
        "semester",
        "class",
    ]
    for col in expected_cols:
        assert col in df.columns


def test_student_dataset_bounds():
    """Verify attendance is between 0-100 and marks between 0-100."""
    df = generate_student_dataset(n_students=200, random_seed=123)
    assert (df["attendance_percentage"] >= 0.0).all()
    assert (df["attendance_percentage"] <= 100.0).all()
    assert (df["average_marks"] >= 0.0).all()
    assert (df["average_marks"] <= 100.0).all()


def test_student_dataset_reproducibility():
    """Verify that using the same random seed produces identical datasets."""
    df1 = generate_student_dataset(n_students=50, random_seed=999)
    df2 = generate_student_dataset(n_students=50, random_seed=999)
    pd.testing.assert_frame_equal(df1, df2)


def test_subject_dataset_generation():
    """Verify subject dataset structure, multiple subjects per student, and bounds."""
    df_students = generate_student_dataset(n_students=20, random_seed=42)
    df_subjects = generate_subject_marks_dataset(student_df=df_students, random_seed=42)

    assert len(df_subjects) > len(df_students)
    assert set(df_subjects["student_id"].unique()) == set(df_students["student_id"].unique())

    required_cols = [
        "student_id",
        "subject",
        "marks_obtained",
        "maximum_marks",
        "attendance_percentage",
        "department",
        "semester",
    ]
    for col in required_cols:
        assert col in df_subjects.columns

    assert (df_subjects["attendance_percentage"] >= 0.0).all()
    assert (df_subjects["attendance_percentage"] <= 100.0).all()
    assert (df_subjects["marks_obtained"] >= 0.0).all()
    assert (df_subjects["marks_obtained"] <= df_subjects["maximum_marks"]).all()


def test_generate_and_save_all(tmp_path: Path):
    """Verify file creation in specified target directory."""
    s_path, sub_path = generate_and_save_all(data_dir=tmp_path, n_students=25, random_seed=42)
    assert s_path.exists()
    assert sub_path.exists()

    df_s = pd.read_csv(s_path)
    df_sub = pd.read_csv(sub_path)
    assert len(df_s) == 25
    assert len(df_sub) > 25
