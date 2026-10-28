"""Visualization module generating Plotly charts with academic visual styling.

Uses clean, professional color palettes (navy, indigo, slate, teal, coral)
with crisp typography, reference lines, and rich tooltips.
"""

from typing import Optional
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# Academic styling palette
PRIMARY_BLUE = "#1e40af"  # Deep royal/navy blue
ACCENT_INDIGO = "#4f46e5"  # Indigo
TEAL = "#0d9488"
CORAL_ALERT = "#dc2626"
AMBER_WARN = "#d97706"
SUCCESS_GREEN = "#16a34a"
MUTED_SLATE = "#64748b"
BG_LIGHT = "#ffffff"
GRID_COLOR = "#f1f5f9"


def _apply_academic_theme(fig: go.Figure, title: str, x_title: str = "", y_title: str = "") -> go.Figure:
    """Apply consistent academic theme to a Plotly figure."""
    fig.update_layout(
        title={
            "text": f"<b>{title}</b>",
            "x": 0.02,
            "y": 0.95,
            "xanchor": "left",
            "yanchor": "top",
            "font": {"size": 16, "color": "#0f172a", "family": "Inter, -apple-system, sans-serif"},
        },
        paper_bgcolor=BG_LIGHT,
        plot_bgcolor="#f8fafc",
        margin=dict(l=40, r=30, t=55, b=45),
        hoverlabel=dict(
            bgcolor="#1e293b",
            font_size=12,
            font_color="#ffffff",
            font_family="Inter, sans-serif",
        ),
        xaxis=dict(
            title={"text": x_title, "font": {"size": 13, "color": "#334155"}},
            gridcolor=GRID_COLOR,
            linecolor="#cbd5e1",
            tickfont={"size": 11, "color": "#475569"},
        ),
        yaxis=dict(
            title={"text": y_title, "font": {"size": 13, "color": "#334155"}},
            gridcolor=GRID_COLOR,
            linecolor="#cbd5e1",
            tickfont={"size": 11, "color": "#475569"},
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font={"size": 11, "color": "#334155"},
        ),
    )
    return fig


def plot_attendance_distribution(
    df: pd.DataFrame,
    threshold: float = 75.0,
    attendance_col: str = "attendance_percentage",
) -> go.Figure:
    """Generate attendance distribution histogram with threshold and mean lines."""
    if df.empty or attendance_col not in df.columns:
        fig = go.Figure()
        return _apply_academic_theme(fig, "Attendance Distribution", "Attendance (%)", "Student Count")

    fig = px.histogram(
        df,
        x=attendance_col,
        nbins=20,
        color_discrete_sequence=[ACCENT_INDIGO],
        opacity=0.85,
    )

    mean_val = df[attendance_col].mean()

    # Add threshold reference line
    fig.add_vline(
        x=threshold,
        line_dash="dash",
        line_color=CORAL_ALERT,
        line_width=2,
        annotation_text=f"Threshold ({threshold:.0f}%)",
        annotation_position="top left",
        annotation_font_color=CORAL_ALERT,
    )

    # Add mean reference line
    fig.add_vline(
        x=mean_val,
        line_dash="dot",
        line_color=PRIMARY_BLUE,
        line_width=2,
        annotation_text=f"Mean ({mean_val:.1f}%)",
        annotation_position="top right",
        annotation_font_color=PRIMARY_BLUE,
    )

    fig = _apply_academic_theme(
        fig,
        "Attendance Percentage Distribution",
        "Attendance (%)",
        "Number of Students",
    )
    return fig


def plot_marks_distribution(
    df: pd.DataFrame,
    marks_col: str = "average_marks",
) -> go.Figure:
    """Generate academic marks distribution histogram with mean and passing lines."""
    if df.empty or marks_col not in df.columns:
        fig = go.Figure()
        return _apply_academic_theme(fig, "Marks Distribution", "Marks (%)", "Student Count")

    fig = px.histogram(
        df,
        x=marks_col,
        nbins=20,
        color_discrete_sequence=[PRIMARY_BLUE],
        opacity=0.85,
    )

    mean_val = df[marks_col].mean()

    fig.add_vline(
        x=mean_val,
        line_dash="dot",
        line_color=ACCENT_INDIGO,
        line_width=2,
        annotation_text=f"Cohort Mean ({mean_val:.1f}%)",
        annotation_position="top right",
        annotation_font_color=ACCENT_INDIGO,
    )

    fig.add_vline(
        x=50.0,
        line_dash="dash",
        line_color=AMBER_WARN,
        line_width=1.5,
        annotation_text="Benchmark (50%)",
        annotation_position="top left",
        annotation_font_color=AMBER_WARN,
    )

    fig = _apply_academic_theme(
        fig,
        "Academic Marks Distribution",
        "Average Marks (%)",
        "Number of Students",
    )
    return fig


def plot_correlation_scatter(
    df: pd.DataFrame,
    attendance_col: str = "attendance_percentage",
    marks_col: str = "average_marks",
    threshold: float = 75.0,
    show_trendline: bool = True,
) -> go.Figure:
    """Generate interactive scatter plot with trendline and student identification tooltip."""
    if df.empty or attendance_col not in df.columns or marks_col not in df.columns:
        fig = go.Figure()
        return _apply_academic_theme(fig, "Attendance vs Marks Scatter", "Attendance (%)", "Marks (%)")

    hover_data = {}
    if "student_id" in df.columns:
        hover_data["student_id"] = True
    if "department" in df.columns:
        hover_data["department"] = True
    if "semester" in df.columns:
        hover_data["semester"] = True

    # Color by threshold status if available or continuous attendance
    color_col = None
    if "threshold_status" in df.columns:
        color_col = "threshold_status"
        color_map = {"Below Threshold": CORAL_ALERT, "Meeting Threshold": PRIMARY_BLUE}
    else:
        color_map = None

    fig = px.scatter(
        df,
        x=attendance_col,
        y=marks_col,
        color=color_col,
        color_discrete_map=color_map,
        hover_name="student_id" if "student_id" in df.columns else None,
        hover_data=hover_data,
        opacity=0.8,
    )

    # Optional OLS trendline via numpy polyfit if valid observations >= 2
    if show_trendline:
        valid_df = df[[attendance_col, marks_col]].dropna()
        if len(valid_df) >= 2 and valid_df[attendance_col].nunique() > 1:
            x_vals = valid_df[attendance_col].values
            y_vals = valid_df[marks_col].values
            slope, intercept = np.polyfit(x_vals, y_vals, 1)

            x_line = np.linspace(x_vals.min(), x_vals.max(), 100)
            y_line = slope * x_line + intercept

            fig.add_trace(
                go.Scatter(
                    x=x_line,
                    y=y_line,
                    mode="lines",
                    name=f"Trendline (slope: {slope:+.2f})",
                    line=dict(color="#0f172a", width=2.2, dash="solid"),
                    hoverinfo="skip",
                )
            )

    # Add threshold reference line
    fig.add_vline(
        x=threshold,
        line_dash="dash",
        line_color=CORAL_ALERT,
        line_width=1.5,
        annotation_text=f"Threshold {threshold:.0f}%",
        annotation_position="bottom right",
    )

    fig = _apply_academic_theme(
        fig,
        "Student Attendance vs Academic Performance Correlation",
        "Attendance Percentage (%)",
        "Average Academic Marks (%)",
    )
    return fig


def plot_attendance_categories(
    df: pd.DataFrame,
    category_col: str = "attendance_category",
) -> go.Figure:
    """Generate categorical bar / donut chart for attendance tiers."""
    if df.empty or category_col not in df.columns:
        fig = go.Figure()
        return _apply_academic_theme(fig, "Attendance Categories", "", "Count")

    counts = df[category_col].value_counts().reset_index()
    counts.columns = ["Category", "Count"]

    color_seq = [CORAL_ALERT, AMBER_WARN, TEAL, SUCCESS_GREEN]

    fig = px.pie(
        counts,
        names="Category",
        values="Count",
        hole=0.45,
        color_discrete_sequence=color_seq,
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hoverinfo="label+value+percent",
    )
    fig = _apply_academic_theme(fig, "Cohort Attendance Tier Breakdown")
    return fig


def plot_subject_performance(subject_df: pd.DataFrame) -> go.Figure:
    """Generate bar chart comparing subjects by average marks and attendance."""
    if subject_df.empty or "subject" not in subject_df.columns:
        fig = go.Figure()
        return _apply_academic_theme(fig, "Subject Performance", "Subject", "Average Score")

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=subject_df["subject"],
            y=subject_df["average_marks"],
            name="Average Marks (%)",
            marker_color=PRIMARY_BLUE,
            text=subject_df["average_marks"].apply(lambda v: f"{v:.1f}%"),
            textposition="auto",
        )
    )

    if "average_attendance" in subject_df.columns:
        fig.add_trace(
            go.Bar(
                x=subject_df["subject"],
                y=subject_df["average_attendance"],
                name="Average Attendance (%)",
                marker_color=TEAL,
                text=subject_df["average_attendance"].apply(lambda v: f"{v:.1f}%"),
                textposition="auto",
            )
        )

    fig.update_layout(barmode="group")
    fig = _apply_academic_theme(
        fig,
        "Subject-wise Marks and Attendance Comparison",
        "Curriculum Subject",
        "Percentage (%)",
    )
    return fig


def plot_department_comparison(
    df: pd.DataFrame,
    dept_col: str = "department",
    marks_col: str = "average_marks",
    att_col: str = "attendance_percentage",
) -> go.Figure:
    """Generate box plot or grouped summary comparing departments."""
    if df.empty or dept_col not in df.columns:
        fig = go.Figure()
        return _apply_academic_theme(fig, "Department Breakdown")

    dept_summary = (
        df.groupby(dept_col)[[att_col, marks_col]].mean().reset_index()
    )

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=dept_summary[dept_col],
            y=dept_summary[marks_col].round(1),
            name="Mean Marks (%)",
            marker_color=PRIMARY_BLUE,
            text=dept_summary[marks_col].round(1).apply(lambda x: f"{x:.1f}%"),
            textposition="auto",
        )
    )
    fig.add_trace(
        go.Bar(
            x=dept_summary[dept_col],
            y=dept_summary[att_col].round(1),
            name="Mean Attendance (%)",
            marker_color=ACCENT_INDIGO,
            text=dept_summary[att_col].round(1).apply(lambda x: f"{x:.1f}%"),
            textposition="auto",
        )
    )

    fig.update_layout(barmode="group")
    fig = _apply_academic_theme(
        fig,
        "Department-wise Average Attendance & Performance",
        "Department",
        "Percentage (%)",
    )
    return fig
