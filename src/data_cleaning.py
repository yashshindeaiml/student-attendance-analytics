"""Data cleaning, validation, and schema aggregation module.

Performs validation, numeric coercion, out-of-range checking, duplicate detection,
missing value auditing, and subject-to-student aggregation without double counting.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from src.data_loader import (
    REQUIRED_STUDENT_COLUMNS,
    REQUIRED_SUBJECT_COLUMNS,
    detect_dataset_type,
    normalize_dataframe_columns,
)


@dataclass
class ValidationIssue:
    """Represents a specific validation issue in a dataset."""

    row_index: int
    student_id: str
    column: str
    issue_type: str  # 'missing', 'duplicate', 'invalid_range', 'type_error'
    details: str


@dataclass
class CleaningResult:
    """Summary of data cleaning and validation results."""

    original_df: pd.DataFrame
    cleaned_df: pd.DataFrame
    issues_df: pd.DataFrame
    total_rows: int
    valid_rows: int
    flagged_rows: int
    excluded_rows: int
    dataset_type: str
    missing_count: int
    duplicate_count: int
    out_of_range_count: int
    is_valid_for_analytics: bool
    validation_message: str
    metadata: Dict[str, Any] = field(default_factory=dict)


def validate_and_clean_student_data(
    df: pd.DataFrame,
    attendance_col: str = "attendance_percentage",
    marks_col: str = "average_marks",
) -> CleaningResult:
    """Validate and clean canonical student-level dataset.

    Args:
        df: Input dataframe.
        attendance_col: Column name for attendance percentage.
        marks_col: Column name for average marks.

    Returns:
        CleaningResult: Detailed cleaning result and validated dataframe.
    """
    df = normalize_dataframe_columns(df)
    total_rows = len(df)
    issues: List[ValidationIssue] = []

    # Check required columns
    missing_req = REQUIRED_STUDENT_COLUMNS - set(df.columns)
    if missing_req:
        return CleaningResult(
            original_df=df,
            cleaned_df=pd.DataFrame(),
            issues_df=pd.DataFrame(
                [
                    {
                        "row_index": -1,
                        "student_id": "N/A",
                        "column": ", ".join(missing_req),
                        "issue_type": "missing_required_column",
                        "details": f"Missing required column(s): {', '.join(missing_req)}",
                    }
                ]
            ),
            total_rows=total_rows,
            valid_rows=0,
            flagged_rows=total_rows,
            excluded_rows=total_rows,
            dataset_type="student_level",
            missing_count=len(missing_req),
            duplicate_count=0,
            out_of_range_count=0,
            is_valid_for_analytics=False,
            validation_message=f"Missing required columns: {', '.join(missing_req)}",
        )

    # Detect duplicate student IDs
    dup_mask = df.duplicated(subset=["student_id"], keep="first")
    duplicate_count = int(dup_mask.sum())
    for idx in df[dup_mask].index:
        issues.append(
            ValidationIssue(
                row_index=int(idx),
                student_id=str(df.loc[idx, "student_id"]),
                column="student_id",
                issue_type="duplicate",
                details="Duplicate student_id detected. Keeping first occurrence.",
            )
        )

    # Work on deduplicated copy
    work_df = df.drop_duplicates(subset=["student_id"], keep="first").copy()

    # Track missing values
    missing_val_mask = work_df[[attendance_col, marks_col]].isna().any(axis=1)
    missing_count = int(missing_val_mask.sum())
    for idx in work_df[missing_val_mask].index:
        for c in [attendance_col, marks_col]:
            if pd.isna(work_df.loc[idx, c]):
                issues.append(
                    ValidationIssue(
                        row_index=int(idx),
                        student_id=str(work_df.loc[idx, "student_id"]),
                        column=c,
                        issue_type="missing",
                        details="Missing numerical value.",
                    )
                )

    # Coerce to numeric
    work_df[attendance_col] = pd.to_numeric(work_df[attendance_col], errors="coerce")
    work_df[marks_col] = pd.to_numeric(work_df[marks_col], errors="coerce")

    # Range checks
    out_of_range_mask = pd.Series(False, index=work_df.index)
    out_of_range_count = 0

    for idx, row in work_df.iterrows():
        att = row[attendance_col]
        marks = row[marks_col]

        att_bad = False
        marks_bad = False

        if pd.notna(att) and (att < 0.0 or att > 100.0):
            att_bad = True
            issues.append(
                ValidationIssue(
                    row_index=int(idx),
                    student_id=str(row["student_id"]),
                    column=attendance_col,
                    issue_type="invalid_range",
                    details=f"Attendance percentage {att} is outside valid range [0, 100].",
                )
            )

        if pd.notna(marks) and (marks < 0.0 or marks > 100.0):
            marks_bad = True
            issues.append(
                ValidationIssue(
                    row_index=int(idx),
                    student_id=str(row["student_id"]),
                    column=marks_col,
                    issue_type="invalid_range",
                    details=f"Marks {marks} is outside typical scale [0, 100].",
                )
            )

        if att_bad or marks_bad:
            out_of_range_mask.loc[idx] = True
            out_of_range_count += 1

    # Valid rows: non-null and within valid ranges
    valid_mask = (
        work_df[attendance_col].notna()
        & work_df[marks_col].notna()
        & (work_df[attendance_col] >= 0.0)
        & (work_df[attendance_col] <= 100.0)
        & (work_df[marks_col] >= 0.0)
        & (work_df[marks_col] <= 100.0)
    )

    cleaned_df = work_df[valid_mask].copy()
    valid_rows = len(cleaned_df)
    excluded_rows = total_rows - valid_rows
    flagged_rows = len(issues)

    issues_df = pd.DataFrame(
        [
            {
                "row_index": iss.row_index,
                "student_id": iss.student_id,
                "column": iss.column,
                "issue_type": iss.issue_type,
                "details": iss.details,
            }
            for iss in issues
        ]
    )

    is_valid = valid_rows >= 2
    msg = (
        f"Validation passed: {valid_rows}/{total_rows} valid student records ready for analytics."
        if is_valid
        else f"Insufficient valid records ({valid_rows}). At least 2 valid records are required."
    )

    return CleaningResult(
        original_df=df,
        cleaned_df=cleaned_df,
        issues_df=issues_df,
        total_rows=total_rows,
        valid_rows=valid_rows,
        flagged_rows=flagged_rows,
        excluded_rows=excluded_rows,
        dataset_type="student_level",
        missing_count=missing_count,
        duplicate_count=duplicate_count,
        out_of_range_count=out_of_range_count,
        is_valid_for_analytics=is_valid,
        validation_message=msg,
    )


def validate_and_clean_subject_data(df: pd.DataFrame) -> CleaningResult:
    """Validate and clean subject-level dataset.

    Args:
        df: Input dataframe.

    Returns:
        CleaningResult: Detailed cleaning result.
    """
    df = normalize_dataframe_columns(df)
    total_rows = len(df)
    issues: List[ValidationIssue] = []

    missing_req = REQUIRED_SUBJECT_COLUMNS - set(df.columns)
    if missing_req:
        return CleaningResult(
            original_df=df,
            cleaned_df=pd.DataFrame(),
            issues_df=pd.DataFrame(
                [
                    {
                        "row_index": -1,
                        "student_id": "N/A",
                        "column": ", ".join(missing_req),
                        "issue_type": "missing_required_column",
                        "details": f"Missing required column(s): {', '.join(missing_req)}",
                    }
                ]
            ),
            total_rows=total_rows,
            valid_rows=0,
            flagged_rows=total_rows,
            excluded_rows=total_rows,
            dataset_type="subject_level",
            missing_count=len(missing_req),
            duplicate_count=0,
            out_of_range_count=0,
            is_valid_for_analytics=False,
            validation_message=f"Missing required columns for subject data: {', '.join(missing_req)}",
        )

    # Detect duplicate (student_id, subject) combinations
    dup_mask = df.duplicated(subset=["student_id", "subject"], keep="first")
    duplicate_count = int(dup_mask.sum())
    for idx in df[dup_mask].index:
        issues.append(
            ValidationIssue(
                row_index=int(idx),
                student_id=str(df.loc[idx, "student_id"]),
                column="student_id+subject",
                issue_type="duplicate",
                details=f"Duplicate entry for student {df.loc[idx, 'student_id']} in subject {df.loc[idx, 'subject']}.",
            )
        )

    work_df = df.drop_duplicates(subset=["student_id", "subject"], keep="first").copy()

    # Coerce numeric fields
    work_df["marks_obtained"] = pd.to_numeric(work_df["marks_obtained"], errors="coerce")
    work_df["maximum_marks"] = pd.to_numeric(work_df["maximum_marks"], errors="coerce")
    work_df["attendance_percentage"] = pd.to_numeric(
        work_df["attendance_percentage"], errors="coerce"
    )

    missing_count = int(
        work_df[["marks_obtained", "maximum_marks", "attendance_percentage"]]
        .isna()
        .any(axis=1)
        .sum()
    )

    out_of_range_count = 0
    for idx, row in work_df.iterrows():
        sid = str(row["student_id"])
        sub = str(row.get("subject", "N/A"))
        att = row["attendance_percentage"]
        marks = row["marks_obtained"]
        max_m = row["maximum_marks"]

        flagged = False
        if pd.notna(att) and (att < 0.0 or att > 100.0):
            flagged = True
            issues.append(
                ValidationIssue(
                    row_index=int(idx),
                    student_id=sid,
                    column="attendance_percentage",
                    issue_type="invalid_range",
                    details=f"Subject attendance {att} outside [0, 100].",
                )
            )

        if pd.notna(max_m) and max_m <= 0:
            flagged = True
            issues.append(
                ValidationIssue(
                    row_index=int(idx),
                    student_id=sid,
                    column="maximum_marks",
                    issue_type="invalid_range",
                    details=f"Maximum marks {max_m} must be greater than 0.",
                )
            )

        if pd.notna(marks) and pd.notna(max_m) and max_m > 0:
            if marks < 0.0 or marks > max_m:
                flagged = True
                issues.append(
                    ValidationIssue(
                        row_index=int(idx),
                        student_id=sid,
                        column="marks_obtained",
                        issue_type="invalid_range",
                        details=f"Marks obtained {marks} outside valid range [0, {max_m}].",
                    )
                )

        if flagged:
            out_of_range_count += 1

    # Valid rows
    valid_mask = (
        work_df["marks_obtained"].notna()
        & work_df["maximum_marks"].notna()
        & work_df["attendance_percentage"].notna()
        & (work_df["maximum_marks"] > 0)
        & (work_df["attendance_percentage"] >= 0.0)
        & (work_df["attendance_percentage"] <= 100.0)
        & (work_df["marks_obtained"] >= 0.0)
        & (work_df["marks_obtained"] <= work_df["maximum_marks"])
    )

    cleaned_df = work_df[valid_mask].copy()
    valid_rows = len(cleaned_df)
    excluded_rows = total_rows - valid_rows
    flagged_rows = len(issues)

    issues_df = pd.DataFrame(
        [
            {
                "row_index": iss.row_index,
                "student_id": iss.student_id,
                "column": iss.column,
                "issue_type": iss.issue_type,
                "details": iss.details,
            }
            for iss in issues
        ]
    )

    is_valid = valid_rows >= 2
    msg = (
        f"Validation passed: {valid_rows}/{total_rows} valid subject records."
        if is_valid
        else f"Insufficient valid records ({valid_rows})."
    )

    return CleaningResult(
        original_df=df,
        cleaned_df=cleaned_df,
        issues_df=issues_df,
        total_rows=total_rows,
        valid_rows=valid_rows,
        flagged_rows=flagged_rows,
        excluded_rows=excluded_rows,
        dataset_type="subject_level",
        missing_count=missing_count,
        duplicate_count=duplicate_count,
        out_of_range_count=out_of_range_count,
        is_valid_for_analytics=is_valid,
        validation_message=msg,
    )


def aggregate_subject_to_student(subject_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate subject-level records into student-level metrics.

    CRITICAL: Ensures each unique student is counted exactly once and avoids
    double-counting students in institutional and analytical summaries.

    Args:
        subject_df: Validated subject-level dataframe.

    Returns:
        pd.DataFrame: Student-level aggregated dataframe with:
            - student_id
            - attendance_percentage (mean of student's subject attendance)
            - average_marks (percentage marks: sum(obtained) / sum(max) * 100)
            - department (if available)
            - semester (if available)
            - class (if available)
            - subject_count (number of subjects contributing)
    """
    if subject_df.empty:
        return pd.DataFrame(
            columns=[
                "student_id",
                "attendance_percentage",
                "average_marks",
                "department",
                "semester",
                "class",
                "subject_count",
            ]
        )

    # Group by student_id
    grouped = subject_df.groupby("student_id")

    aggregated_records = []
    for sid, group in grouped:
        total_obtained = group["marks_obtained"].sum()
        total_max = group["maximum_marks"].sum()

        if total_max > 0:
            avg_marks_pct = round((total_obtained / total_max) * 100.0, 1)
        else:
            avg_marks_pct = round(group["marks_obtained"].mean(), 1)

        avg_att = round(group["attendance_percentage"].mean(), 1)

        # Meta attributes (take mode or first)
        dept = group["department"].iloc[0] if "department" in group.columns else "General"
        sem = group["semester"].iloc[0] if "semester" in group.columns else "General"
        cls = group["class"].iloc[0] if "class" in group.columns else "All"

        aggregated_records.append(
            {
                "student_id": sid,
                "attendance_percentage": avg_att,
                "average_marks": avg_marks_pct,
                "department": dept,
                "semester": sem,
                "class": cls,
                "subject_count": len(group),
            }
        )

    return pd.DataFrame(aggregated_records)


def clean_dataset(df: pd.DataFrame, dataset_type: str = "auto") -> CleaningResult:
    """General dispatcher to validate and clean any compatible dataset.

    Args:
        df: Input dataframe.
        dataset_type: 'auto', 'student_level', or 'subject_level'.

    Returns:
        CleaningResult: Cleaning summary and validated dataset.
    """
    if dataset_type == "auto":
        dataset_type = detect_dataset_type(df)

    if dataset_type == "subject_level":
        return validate_and_clean_subject_data(df)
    elif dataset_type == "student_level":
        return validate_and_clean_student_data(df)
    else:
        # Unknown schema
        df = normalize_dataframe_columns(df)
        return CleaningResult(
            original_df=df,
            cleaned_df=pd.DataFrame(),
            issues_df=pd.DataFrame(
                [
                    {
                        "row_index": -1,
                        "student_id": "N/A",
                        "column": "schema",
                        "issue_type": "unknown_schema",
                        "details": (
                            "Uploaded dataset matches neither canonical student-level schema "
                            "(student_id, attendance_percentage, average_marks) nor subject-level "
                            "schema (student_id, subject, marks_obtained, maximum_marks, attendance_percentage)."
                        ),
                    }
                ]
            ),
            total_rows=len(df),
            valid_rows=0,
            flagged_rows=len(df),
            excluded_rows=len(df),
            dataset_type="unknown",
            missing_count=0,
            duplicate_count=0,
            out_of_range_count=0,
            is_valid_for_analytics=False,
            validation_message="Unsupported file format or schema. Please inspect the canonical column format.",
        )
