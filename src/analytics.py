"""Core analytical and descriptive statistics module.

Computes KPI summaries, distribution categories, support recommendations,
and subject-level performance metrics without double-counting students.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd


@dataclass
class SummaryKPIs:
    """Institutional and cohort summary metrics."""

    total_students: int
    average_attendance: float
    median_attendance: float
    min_attendance: float
    max_attendance: float
    std_attendance: float

    average_marks: float
    median_marks: float
    min_marks: float
    max_marks: float
    std_marks: float

    attendance_threshold: float
    students_below_threshold: int
    percentage_below_threshold: float

    marks_support_threshold: float
    students_needing_support: int
    percentage_needing_support: float


def calculate_summary_kpis(
    df: pd.DataFrame,
    attendance_col: str = "attendance_percentage",
    marks_col: str = "average_marks",
    attendance_threshold: float = 75.0,
    marks_threshold: float = 50.0,
) -> SummaryKPIs:
    """Calculate core summary KPIs for a student-level cohort.

    Args:
        df: Cleaned student dataframe (each row = 1 student).
        attendance_col: Column for attendance percentage.
        marks_col: Column for average marks.
        attendance_threshold: Benchmark threshold (default 75.0%).
        marks_threshold: Performance benchmark (default 50.0%).

    Returns:
        SummaryKPIs: Cohort KPI container.
    """
    if df.empty or len(df) == 0:
        return SummaryKPIs(
            total_students=0,
            average_attendance=0.0,
            median_attendance=0.0,
            min_attendance=0.0,
            max_attendance=0.0,
            std_attendance=0.0,
            average_marks=0.0,
            median_marks=0.0,
            min_marks=0.0,
            max_marks=0.0,
            std_marks=0.0,
            attendance_threshold=attendance_threshold,
            students_below_threshold=0,
            percentage_below_threshold=0.0,
            marks_support_threshold=marks_threshold,
            students_needing_support=0,
            percentage_needing_support=0.0,
        )

    att = df[attendance_col].dropna()
    marks = df[marks_col].dropna()
    n_students = len(df)

    avg_att = float(att.mean()) if not att.empty else 0.0
    med_att = float(att.median()) if not att.empty else 0.0
    min_att = float(att.min()) if not att.empty else 0.0
    max_att = float(att.max()) if not att.empty else 0.0
    std_att = float(att.std()) if len(att) > 1 else 0.0

    avg_m = float(marks.mean()) if not marks.empty else 0.0
    med_m = float(marks.median()) if not marks.empty else 0.0
    min_m = float(marks.min()) if not marks.empty else 0.0
    max_m = float(marks.max()) if not marks.empty else 0.0
    std_m = float(marks.std()) if len(marks) > 1 else 0.0

    below_att = int((att < attendance_threshold).sum())
    pct_below_att = round((below_att / n_students) * 100.0, 1) if n_students > 0 else 0.0

    # Students needing academic support: attendance < threshold OR marks < threshold
    need_support_mask = (df[attendance_col] < attendance_threshold) | (
        df[marks_col] < marks_threshold
    )
    support_count = int(need_support_mask.sum())
    pct_support = round((support_count / n_students) * 100.0, 1) if n_students > 0 else 0.0

    return SummaryKPIs(
        total_students=n_students,
        average_attendance=round(avg_att, 1),
        median_attendance=round(med_att, 1),
        min_attendance=round(min_att, 1),
        max_attendance=round(max_att, 1),
        std_attendance=round(std_att, 1),
        average_marks=round(avg_m, 1),
        median_marks=round(med_m, 1),
        min_marks=round(min_m, 1),
        max_marks=round(max_m, 1),
        std_marks=round(std_m, 1),
        attendance_threshold=attendance_threshold,
        students_below_threshold=below_att,
        percentage_below_threshold=pct_below_att,
        marks_support_threshold=marks_threshold,
        students_needing_support=support_count,
        percentage_needing_support=pct_support,
    )


def categorize_attendance(
    df: pd.DataFrame,
    threshold: float = 75.0,
    attendance_col: str = "attendance_percentage",
) -> pd.DataFrame:
    """Assign attendance categories and threshold status to each student.

    Categories:
        - Critical (< 60%)
        - Low (60% to < threshold)
        - Good (threshold to < 85%)
        - Excellent (>= 85%)
    """
    df = df.copy()
    if df.empty or attendance_col not in df.columns:
        df["attendance_category"] = pd.Series(dtype="object")
        df["threshold_status"] = pd.Series(dtype="object")
        return df

    def _cat(val: float) -> str:
        if pd.isna(val):
            return "Unrecorded"
        if val < 60.0:
            return "Critical (< 60%)"
        if val < threshold:
            return f"Low (60% - {threshold}%)"
        if val < 85.0:
            return f"Good ({threshold}% - 85%)"
        return "Excellent (>= 85%)"

    df["attendance_category"] = df[attendance_col].apply(_cat)
    df["threshold_status"] = df[attendance_col].apply(
        lambda x: "Below Threshold" if x < threshold else "Meeting Threshold"
    )
    return df


def categorize_marks(
    df: pd.DataFrame,
    marks_col: str = "average_marks",
) -> pd.DataFrame:
    """Assign performance bands to each student.

    Bands:
        - Below 40 (Remedial Required)
        - 40 - 59.9 (Average / Passing)
        - 60 - 74.9 (Good / Commendable)
        - 75 - 100 (Distinction / Outstanding)
    """
    df = df.copy()
    if df.empty or marks_col not in df.columns:
        df["performance_band"] = pd.Series(dtype="object")
        return df

    def _band(val: float) -> str:
        if pd.isna(val):
            return "Unrecorded"
        if val < 40.0:
            return "Below 40 (Remedial)"
        if val < 60.0:
            return "40 - 59.9 (Average)"
        if val < 75.0:
            return "60 - 74.9 (Good)"
        return "75 - 100 (Distinction)"

    df["performance_band"] = df[marks_col].apply(_band)
    return df


def get_top_performers(
    df: pd.DataFrame,
    n: int = 10,
    marks_col: str = "average_marks",
) -> pd.DataFrame:
    """Retrieve top performing students ranked by marks."""
    if df.empty or marks_col not in df.columns:
        return pd.DataFrame()
    return df.sort_values(by=marks_col, ascending=False).head(n).copy()


def get_students_needing_support(
    df: pd.DataFrame,
    attendance_threshold: float = 75.0,
    marks_threshold: float = 50.0,
    attendance_col: str = "attendance_percentage",
    marks_col: str = "average_marks",
) -> pd.DataFrame:
    """Identify students who meet criteria for academic advisory outreach.

    Criteria:
        - Attendance below specified threshold, OR
        - Marks below specified threshold.
    """
    if df.empty or attendance_col not in df.columns or marks_col not in df.columns:
        return pd.DataFrame()

    mask = (df[attendance_col] < attendance_threshold) | (df[marks_col] < marks_threshold)
    support_df = df[mask].copy()

    # Add descriptive flag for clear interpretation
    def _reason(row: pd.Series) -> str:
        att_low = row[attendance_col] < attendance_threshold
        m_low = row[marks_col] < marks_threshold
        if att_low and m_low:
            return "Both Attendance & Performance Below Target"
        if att_low:
            return "Low Attendance"
        return "Performance Below Target"

    support_df["support_reason"] = support_df.apply(_reason, axis=1)
    return support_df.sort_values(by=[attendance_col, marks_col], ascending=True)


def get_subject_performance(subject_df: pd.DataFrame) -> pd.DataFrame:
    """Compute aggregated performance metrics per subject from subject-level data.

    Returns:
        pd.DataFrame with:
            - subject
            - average_marks
            - average_attendance
            - highest_marks
            - lowest_marks
            - student_count
            - pass_percentage (marks >= 40% of max)
    """
    if subject_df.empty or "subject" not in subject_df.columns:
        return pd.DataFrame()

    records = []
    for sub, group in subject_df.groupby("subject"):
        avg_m = group["marks_obtained"].mean()
        avg_att = group["attendance_percentage"].mean()
        high_m = group["marks_obtained"].max()
        low_m = group["marks_obtained"].min()
        count = len(group)

        # Pass criteria: obtained >= 40% of maximum marks
        pass_mask = group["marks_obtained"] >= (0.40 * group["maximum_marks"])
        pass_rate = (pass_mask.sum() / count) * 100.0 if count > 0 else 0.0

        records.append(
            {
                "subject": sub,
                "average_marks": round(float(avg_m), 1),
                "average_attendance": round(float(avg_att), 1),
                "highest_marks": round(float(high_m), 1),
                "lowest_marks": round(float(low_m), 1),
                "student_count": count,
                "pass_percentage": round(float(pass_rate), 1),
            }
        )

    res_df = pd.DataFrame(records)
    return res_df.sort_values(by="average_marks", ascending=False)


def filter_dataset(
    df: pd.DataFrame,
    department: Optional[str] = None,
    semester: Optional[str] = None,
    class_section: Optional[str] = None,
    min_attendance: Optional[float] = None,
    max_attendance: Optional[float] = None,
    min_marks: Optional[float] = None,
    max_marks: Optional[float] = None,
    search_query: Optional[str] = None,
    attendance_col: str = "attendance_percentage",
    marks_col: str = "average_marks",
) -> pd.DataFrame:
    """Filter dataset dynamically based on UI selectors."""
    if df.empty:
        return df

    filtered = df.copy()

    if department and department != "All" and "department" in filtered.columns:
        filtered = filtered[filtered["department"] == department]

    if semester and semester != "All" and "semester" in filtered.columns:
        filtered = filtered[filtered["semester"] == semester]

    if class_section and class_section != "All" and "class" in filtered.columns:
        filtered = filtered[filtered["class"] == class_section]

    if min_attendance is not None and attendance_col in filtered.columns:
        filtered = filtered[filtered[attendance_col] >= min_attendance]

    if max_attendance is not None and attendance_col in filtered.columns:
        filtered = filtered[filtered[attendance_col] <= max_attendance]

    if min_marks is not None and marks_col in filtered.columns:
        filtered = filtered[filtered[marks_col] >= min_marks]

    if max_marks is not None and marks_col in filtered.columns:
        filtered = filtered[filtered[marks_col] <= max_marks]

    if search_query and "student_id" in filtered.columns:
        q = search_query.strip().lower()
        if q:
            filtered = filtered[filtered["student_id"].astype(str).str.lower().str.contains(q)]

    return filtered
