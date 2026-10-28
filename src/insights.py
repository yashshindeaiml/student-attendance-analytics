"""Analytical insights generation module.

Generates automated, strictly data-driven, non-causal analytical statements
from calculated summary KPIs, correlation results, and subject statistics.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import pandas as pd

from src.analytics import SummaryKPIs
from src.correlation import CorrelationResult


@dataclass
class InsightItem:
    """Represents a single generated analytical insight."""

    title: str
    description: str
    category: str  # 'attendance', 'performance', 'correlation', 'quality'
    severity: str  # 'info', 'success', 'warning', 'neutral'


def generate_cohort_insights(
    kpis: SummaryKPIs,
    correlation: Optional[CorrelationResult] = None,
    subject_perf_df: Optional[pd.DataFrame] = None,
    quality_summary: Optional[Dict[str, Any]] = None,
) -> List[InsightItem]:
    """Generate structured, strictly data-driven insights.

    Separates analytics from UI rendering to enable comprehensive unit testing.
    """
    insights: List[InsightItem] = []

    if kpis.total_students == 0:
        insights.append(
            InsightItem(
                title="No Data Available",
                description="The selected dataset or filtered view contains no student records to analyze.",
                category="quality",
                severity="warning",
            )
        )
        return insights

    # 1. Attendance Insights
    att_severity = "warning" if kpis.percentage_below_threshold > 25.0 else "info"
    insights.append(
        InsightItem(
            title="Cohort Attendance Baseline",
            description=(
                f"The cohort average attendance is {kpis.average_attendance:.1f}% "
                f"(median: {kpis.median_attendance:.1f}%), spanning from a minimum of "
                f"{kpis.min_attendance:.1f}% to a maximum of {kpis.max_attendance:.1f}%."
            ),
            category="attendance",
            severity="info",
        )
    )

    insights.append(
        InsightItem(
            title=f"Attendance Threshold ({kpis.attendance_threshold}%) Adherence",
            description=(
                f"{kpis.students_below_threshold} out of {kpis.total_students} students "
                f"({kpis.percentage_below_threshold:.1f}%) have attendance below the institutional "
                f"analytical benchmark of {kpis.attendance_threshold}%."
            ),
            category="attendance",
            severity=att_severity,
        )
    )

    # 2. Performance Insights
    perf_severity = "warning" if kpis.average_marks < 50.0 else "info"
    insights.append(
        InsightItem(
            title="Academic Marks Overview",
            description=(
                f"The cohort mean academic score is {kpis.average_marks:.1f}% "
                f"(standard deviation: {kpis.std_marks:.1f} points), with recorded scores "
                f"ranging between {kpis.min_marks:.1f}% and {kpis.max_marks:.1f}%."
            ),
            category="performance",
            severity=perf_severity,
        )
    )

    if kpis.students_needing_support > 0:
        insights.append(
            InsightItem(
                title="Advisory Support Identification",
                description=(
                    f"{kpis.students_needing_support} students ({kpis.percentage_needing_support:.1f}%) "
                    f"fall below the attendance threshold (<{kpis.attendance_threshold}%) or academic benchmark "
                    f"(<{kpis.marks_support_threshold}%) and may benefit from proactive advising."
                ),
                category="performance",
                severity="warning" if kpis.percentage_needing_support > 30 else "info",
            )
        )

    # 3. Subject-wise Insights (if available)
    if subject_perf_df is not None and not subject_perf_df.empty:
        highest_sub = subject_perf_df.iloc[0]
        lowest_sub = subject_perf_df.iloc[-1]

        insights.append(
            InsightItem(
                title="Subject Performance Disparity",
                description=(
                    f"Highest average marks were recorded in '{highest_sub['subject']}' "
                    f"({highest_sub['average_marks']:.1f}%), while lowest average marks were in "
                    f"'{lowest_sub['subject']}' ({lowest_sub['average_marks']:.1f}%)."
                ),
                category="performance",
                severity="info",
            )
        )

    # 4. Correlation Insights
    if correlation is not None:
        if correlation.is_valid and correlation.pearson_r is not None:
            r = correlation.pearson_r
            rho = correlation.spearman_rho
            insights.append(
                InsightItem(
                    title="Attendance–Performance Statistical Relationship",
                    description=(
                        f"Analysis shows a Pearson r of {r:.2f} and Spearman rho of {rho:.2f} "
                        f"across {correlation.valid_count} valid observations, reflecting a "
                        f"{correlation.strength} {correlation.direction} association. Note: "
                        "This statistical association does not imply direct causation."
                    ),
                    category="correlation",
                    severity="success" if r > 0.3 else "info",
                )
            )
        else:
            insights.append(
                InsightItem(
                    title="Correlation Evaluation Notice",
                    description=correlation.interpretation,
                    category="correlation",
                    severity="neutral",
                )
            )

    # 5. Data Quality Insights
    if quality_summary:
        dups = quality_summary.get("duplicate_count", 0)
        missing = quality_summary.get("missing_count", 0)
        out_of_range = quality_summary.get("out_of_range_count", 0)

        if dups > 0 or missing > 0 or out_of_range > 0:
            insights.append(
                InsightItem(
                    title="Data Quality Audit",
                    description=(
                        f"Data cleaning identified {dups} duplicate records, {missing} rows with missing "
                        f"attributes, and {out_of_range} values outside valid bounds, which were handled "
                        "prior to analytical aggregation."
                    ),
                    category="quality",
                    severity="warning",
                )
            )
        else:
            insights.append(
                InsightItem(
                    title="Data Quality Audit",
                    description="Dataset audit verified 100% complete records with zero duplicates and all values within expected ranges.",
                    category="quality",
                    severity="success",
                )
            )

    return insights
