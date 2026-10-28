"""Student Performance Analytics Dashboard.

Attendance, Academic Performance & Statistical Insights.
An academic decision-support and data analytics platform.
"""

from io import BytesIO
from pathlib import Path
import streamlit as st
import pandas as pd

from src.analytics import (
    calculate_summary_kpis,
    categorize_attendance,
    categorize_marks,
    filter_dataset,
    get_students_needing_support,
    get_subject_performance,
    get_top_performers,
)
from src.correlation import (
    calculate_correlation,
    generate_correlation_report,
)
from src.data_cleaning import (
    aggregate_subject_to_student,
    clean_dataset,
)
from src.data_loader import (
    load_bundled_student_data,
    load_bundled_subject_data,
    load_file,
)
from src.insights import generate_cohort_insights
from src.visualizations import (
    plot_attendance_categories,
    plot_attendance_distribution,
    plot_correlation_scatter,
    plot_department_comparison,
    plot_marks_distribution,
    plot_subject_performance,
)


# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Student Performance Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling (Light academic theme with navy/indigo accents)
st.markdown(
    """
    <style>
    /* Global font & background adjustments */
    .main {
        background-color: #f8fafc;
    }
    .metric-card {
        background: #ffffff;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
        border: 1px solid #e2e8f0;
        margin-bottom: 12px;
    }
    .metric-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1e3a8a;
        margin-top: 4px;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 2px;
    }
    .banner-title {
        color: #0f172a;
        font-weight: 800;
        font-size: 2.1rem;
        margin-bottom: 2px;
    }
    .banner-subtitle {
        color: #475569;
        font-size: 1.05rem;
        font-weight: 400;
        margin-bottom: 18px;
    }
    .badge-info {
        background-color: #e0f2fe;
        color: #0369a1;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .badge-warning {
        background-color: #fef3c7;
        color: #b45309;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .badge-success {
        background-color: #dcfce7;
        color: #15803d;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --- SESSION STATE INITIALIZATION ---
def init_session_state():
    """Initialize session state and auto-load bundled demonstration data."""
    if "data_loaded" not in st.session_state:
        st.session_state.data_loaded = False
        st.session_state.dataset_source_name = "Bundled Demonstration Dataset (Synthetic)"
        try:
            # Auto-load bundled synthetic data
            raw_students = load_bundled_student_data()
            raw_subjects = load_bundled_subject_data()

            clean_res = clean_dataset(raw_students, dataset_type="student_level")
            st.session_state.student_df = clean_res.cleaned_df
            st.session_state.cleaning_result = clean_res

            sub_clean_res = clean_dataset(raw_subjects, dataset_type="subject_level")
            st.session_state.subject_df = sub_clean_res.cleaned_df
            st.session_state.has_subject_data = True
            st.session_state.data_loaded = True
        except Exception as e:
            st.session_state.student_df = pd.DataFrame()
            st.session_state.subject_df = pd.DataFrame()
            st.session_state.has_subject_data = False
            st.session_state.cleaning_result = None
            st.session_state.load_error = str(e)


init_session_state()


# --- SIDEBAR CONTROLS & NAVIGATION ---
with st.sidebar:
    st.markdown("### 🎓 Student Analytics")
    st.caption("Attendance, Marks & Correlation Engine")

    nav_choice = st.radio(
        "Navigation",
        [
            "Overview",
            "Attendance Analysis",
            "Academic Performance",
            "Correlation Analysis",
            "Student Explorer",
            "Data Management",
            "About the Project",
        ],
        index=0,
    )

    st.markdown("---")
    st.markdown("#### ⚙️ Analytical Settings")

    attendance_threshold = st.slider(
        "Attendance Benchmark (%)",
        min_value=50.0,
        max_value=90.0,
        value=75.0,
        step=1.0,
        help="Institutional benchmark used to classify students below attendance threshold.",
    )

    marks_support_threshold = st.slider(
        "Marks Support Benchmark (%)",
        min_value=35.0,
        max_value=70.0,
        value=50.0,
        step=1.0,
        help="Marks score threshold used to identify students who may benefit from academic tutoring.",
    )

    st.markdown("---")
    st.markdown("#### 🗂️ Cohort Filters")

    # Dynamic filter options based on active student dataframe
    student_data = st.session_state.get("student_df", pd.DataFrame())

    if not student_data.empty and "department" in student_data.columns:
        dept_options = ["All"] + sorted(student_data["department"].dropna().unique().tolist())
        selected_dept = st.selectbox("Department", dept_options, index=0)
    else:
        selected_dept = "All"

    if not student_data.empty and "semester" in student_data.columns:
        sem_options = ["All"] + sorted(student_data["semester"].dropna().unique().tolist())
        selected_sem = st.selectbox("Semester", sem_options, index=0)
    else:
        selected_sem = "All"

    if not student_data.empty and "class" in student_data.columns:
        class_options = ["All"] + sorted(student_data["class"].dropna().unique().tolist())
        selected_class = st.selectbox("Class / Section", class_options, index=0)
    else:
        selected_class = "All"

    st.caption(f"Active Data: {st.session_state.get('dataset_source_name', 'None')}")


# --- DATA PREPARATION ---
active_df = student_data.copy() if not student_data.empty else pd.DataFrame()

# Apply cohort filters
if not active_df.empty:
    filtered_df = filter_dataset(
        active_df,
        department=selected_dept,
        semester=selected_sem,
        class_section=selected_class,
    )
    # Categorize
    filtered_df = categorize_attendance(filtered_df, threshold=attendance_threshold)
    filtered_df = categorize_marks(filtered_df)
else:
    filtered_df = pd.DataFrame()

# Filter subject data if present
subject_df = st.session_state.get("subject_df", pd.DataFrame())
if not subject_df.empty:
    filtered_sub_df = subject_df.copy()
    if selected_dept != "All" and "department" in filtered_sub_df.columns:
        filtered_sub_df = filtered_sub_df[filtered_sub_df["department"] == selected_dept]
    if selected_sem != "All" and "semester" in filtered_sub_df.columns:
        filtered_sub_df = filtered_sub_df[filtered_sub_df["semester"] == selected_sem]
else:
    filtered_sub_df = pd.DataFrame()


# Compute Core Analytics
kpis = calculate_summary_kpis(
    filtered_df,
    attendance_threshold=attendance_threshold,
    marks_threshold=marks_support_threshold,
)

correlation_res = calculate_correlation(filtered_df)
subject_perf_df = get_subject_performance(filtered_sub_df) if not filtered_sub_df.empty else None

quality_dict = None
if st.session_state.get("cleaning_result") is not None:
    cr = st.session_state.cleaning_result
    quality_dict = {
        "duplicate_count": cr.duplicate_count,
        "missing_count": cr.missing_count,
        "out_of_range_count": cr.out_of_range_count,
    }


# --- HEADER BANNER ---
st.markdown('<div class="banner-title">Student Performance Analytics</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="banner-subtitle">Attendance, Academic Performance & Statistical Insights</div>',
    unsafe_allow_html=True,
)


# --- SECTION 1: OVERVIEW ---
if nav_choice == "Overview":
    st.markdown("### 📊 Cohort Overview Dashboard")

    if filtered_df.empty:
        st.warning("No student records available under current filters. Please adjust your sidebar settings.")
    else:
        # KPI Cards Row
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">Total Students</div>
                    <div class="metric-value">{kpis.total_students}</div>
                    <div class="metric-sub">Cohort population</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">Avg Attendance</div>
                    <div class="metric-value">{kpis.average_attendance:.1f}%</div>
                    <div class="metric-sub">Median: {kpis.median_attendance:.1f}%</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">Avg Marks</div>
                    <div class="metric-value">{kpis.average_marks:.1f}%</div>
                    <div class="metric-sub">Std Dev: {kpis.std_marks:.1f}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c4:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">Below Threshold</div>
                    <div class="metric-value" style="color: #dc2626;">{kpis.students_below_threshold}</div>
                    <div class="metric-sub">{kpis.percentage_below_threshold:.1f}% &lt; {attendance_threshold:.0f}%</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c5:
            corr_text = f"{correlation_res.pearson_r:.2f}" if correlation_res.is_valid and correlation_res.pearson_r is not None else "N/A"
            corr_color = "#15803d" if (correlation_res.pearson_r or 0) > 0.3 else "#1e3a8a"
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-title">Correlation (r)</div>
                    <div class="metric-value" style="color: {corr_color};">{corr_text}</div>
                    <div class="metric-sub">{correlation_res.strength.capitalize()} {correlation_res.direction}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Main Charts Grid
        row1_col1, row1_col2 = st.columns([1, 1])
        with row1_col1:
            st.plotly_chart(
                plot_correlation_scatter(
                    filtered_df,
                    threshold=attendance_threshold,
                    show_trendline=True,
                ),
                use_container_width=True,
            )
        with row1_col2:
            st.plotly_chart(
                plot_attendance_distribution(filtered_df, threshold=attendance_threshold),
                use_container_width=True,
            )

        row2_col1, row2_col2 = st.columns([1, 1])
        with row2_col1:
            st.plotly_chart(
                plot_marks_distribution(filtered_df),
                use_container_width=True,
            )
        with row2_col2:
            if subject_perf_df is not None and not subject_perf_df.empty:
                st.plotly_chart(
                    plot_subject_performance(subject_perf_df),
                    use_container_width=True,
                )
            else:
                st.plotly_chart(
                    plot_attendance_categories(filtered_df),
                    use_container_width=True,
                )

        # Department comparison if multiple departments present
        if "department" in filtered_df.columns and filtered_df["department"].nunique() > 1:
            st.plotly_chart(
                plot_department_comparison(filtered_df),
                use_container_width=True,
            )

        # Analytical Insights Section
        st.markdown("### 💡 Automated Analytical Insights")
        insights = generate_cohort_insights(
            kpis,
            correlation=correlation_res,
            subject_perf_df=subject_perf_df,
            quality_summary=quality_dict,
        )

        for ins in insights:
            badge_class = (
                "badge-warning"
                if ins.severity == "warning"
                else "badge-success"
                if ins.severity == "success"
                else "badge-info"
            )
            st.markdown(
                f"""
                <div style="background: #ffffff; border-left: 4px solid #3b82f6; border-radius: 6px; padding: 12px 16px; margin-bottom: 8px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                        <span style="font-weight: 700; color: #0f172a; font-size: 0.95rem;">{ins.title}</span>
                        <span class="{badge_class}">{ins.category.title()}</span>
                    </div>
                    <div style="color: #475569; font-size: 0.9rem; line-height: 1.4;">{ins.description}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# --- SECTION 2: ATTENDANCE ANALYSIS ---
elif nav_choice == "Attendance Analysis":
    st.markdown("### 📅 Dedicated Attendance Analysis")

    if filtered_df.empty:
        st.warning("No data available to display.")
    else:
        # Summary Row
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Average Attendance", f"{kpis.average_attendance:.1f}%")
        col2.metric("Median Attendance", f"{kpis.median_attendance:.1f}%")
        col3.metric("Minimum Attendance", f"{kpis.min_attendance:.1f}%")
        col4.metric("Maximum Attendance", f"{kpis.max_attendance:.1f}%")
        col5.metric(
            f"Below {attendance_threshold:.0f}%",
            f"{kpis.students_below_threshold} ({kpis.percentage_below_threshold:.1f}%)",
        )

        st.caption(
            f"Note: The default benchmark of {attendance_threshold:.0f}% is an analytical parameter "
            "configured in the sidebar and may not reflect specific statutory or institutional requirements."
        )

        st.markdown("---")
        c_left, c_right = st.columns([1, 1])
        with c_left:
            st.plotly_chart(
                plot_attendance_distribution(filtered_df, threshold=attendance_threshold),
                use_container_width=True,
            )
        with c_right:
            st.plotly_chart(
                plot_attendance_categories(filtered_df),
                use_container_width=True,
            )

        # Tabular breakdown: Students below threshold
        st.markdown(f"#### ⚠️ Students Below Attendance Benchmark ({attendance_threshold:.0f}%)")
        below_df = filtered_df[filtered_df["attendance_percentage"] < attendance_threshold].sort_values(
            by="attendance_percentage", ascending=True
        )

        if not below_df.empty:
            st.dataframe(
                below_df[
                    [
                        c
                        for c in [
                            "student_id",
                            "department",
                            "semester",
                            "class",
                            "attendance_percentage",
                            "average_marks",
                            "attendance_category",
                        ]
                        if c in below_df.columns
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )

            csv_data = below_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download Low Attendance Report (CSV)",
                data=csv_data,
                file_name="low_attendance_students.csv",
                mime="text/csv",
            )
        else:
            st.success("All students in the selected filter meet or exceed the attendance threshold!")


# --- SECTION 3: ACADEMIC PERFORMANCE ---
elif nav_choice == "Academic Performance":
    st.markdown("### 🏆 Academic Performance Analysis")

    if filtered_df.empty:
        st.warning("No data available.")
    else:
        # KPI Row
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Cohort Mean Marks", f"{kpis.average_marks:.1f}%")
        c2.metric("Median Marks", f"{kpis.median_marks:.1f}%")
        c3.metric("Highest Mark", f"{kpis.max_marks:.1f}%")
        c4.metric("Lowest Mark", f"{kpis.min_marks:.1f}%")
        c5.metric("Standard Deviation", f"{kpis.std_marks:.1f}")

        st.markdown("---")
        p_col1, p_col2 = st.columns([1, 1])
        with p_col1:
            st.plotly_chart(plot_marks_distribution(filtered_df), use_container_width=True)
        with p_col2:
            if subject_perf_df is not None and not subject_perf_df.empty:
                st.plotly_chart(plot_subject_performance(subject_perf_df), use_container_width=True)
            else:
                st.info("Subject-level breakdown requires a subject marks dataset.")

        # Performance bands & Support list
        t1, t2 = st.tabs(["Top Performers", "Advisory Support Recommendations"])
        with t1:
            st.markdown("#### Top Performing Students")
            top_df = get_top_performers(filtered_df, n=15)
            st.dataframe(
                top_df[
                    [
                        c
                        for c in [
                            "student_id",
                            "department",
                            "semester",
                            "class",
                            "average_marks",
                            "attendance_percentage",
                            "performance_band",
                        ]
                        if c in top_df.columns
                    ]
                ],
                use_container_width=True,
                hide_index=True,
            )

        with t2:
            st.markdown(
                f"#### Students Recommended for Academic Advisory (<{attendance_threshold:.0f}% Att. or <{marks_support_threshold:.0f}% Marks)"
            )
            support_df = get_students_needing_support(
                filtered_df,
                attendance_threshold=attendance_threshold,
                marks_threshold=marks_support_threshold,
            )
            st.caption(
                "Informational Advisory Note: Identification flags are intended solely for "
                "academic counseling and tutoring invitations, not disciplinary consequences."
            )
            if not support_df.empty:
                st.dataframe(
                    support_df[
                        [
                            c
                            for c in [
                                "student_id",
                                "department",
                                "semester",
                                "class",
                                "attendance_percentage",
                                "average_marks",
                                "support_reason",
                            ]
                            if c in support_df.columns
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True,
                )
                st.download_button(
                    label="📥 Download Academic Advisory List (CSV)",
                    data=support_df.to_csv(index=False).encode("utf-8"),
                    file_name="students_needing_support.csv",
                    mime="text/csv",
                )
            else:
                st.success("No students currently fall below the advisory support thresholds.")


# --- SECTION 4: CORRELATION ANALYSIS ---
elif nav_choice == "Correlation Analysis":
    st.markdown("### 📈 Statistical Correlation Analysis")
    st.markdown(
        "Quantitative evaluation of the mathematical association between student attendance "
        "percentages and academic marks."
    )

    if filtered_df.empty:
        st.warning("Insufficient data.")
    else:
        # Display statistical coefficients
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            pr_val = f"{correlation_res.pearson_r:.3f}" if correlation_res.pearson_r is not None else "N/A"
            st.metric("Pearson Correlation (r)", pr_val)
        with col2:
            sr_val = f"{correlation_res.spearman_rho:.3f}" if correlation_res.spearman_rho is not None else "N/A"
            st.metric("Spearman Rank (rho)", sr_val)
        with col3:
            pv_val = (
                f"{correlation_res.p_value_pearson:.4f}"
                if correlation_res.p_value_pearson is not None
                else "N/A"
            )
            st.metric("p-value (Pearson)", pv_val)
        with col4:
            st.metric("Valid Observations", f"{correlation_res.valid_count}")

        # Plain language interpretation box
        st.info(f"**Interpretation**: {correlation_res.interpretation}")

        # Cautionary disclaimer box
        st.warning(f"⚠️ **Scientific & Ethical Disclaimer**: {correlation_res.disclaimer}")

        # Interactive scatter plot with trendline
        st.plotly_chart(
            plot_correlation_scatter(
                filtered_df,
                threshold=attendance_threshold,
                show_trendline=True,
            ),
            use_container_width=True,
        )

        # Correlation Report Export
        report_text = generate_correlation_report(correlation_res)
        st.download_button(
            label="📥 Download Statistical Correlation Report (Markdown)",
            data=report_text.encode("utf-8"),
            file_name="correlation_analysis_report.md",
            mime="text/markdown",
        )

        # Technical methodology notes
        with st.expander("ℹ️ Statistical Methodology & Assumptions"):
            st.markdown(
                r"""
                - **Pearson Correlation Coefficient ($r$)**: Measures the linear bivariate association between continuous variables.
                  Assumes approximate bivariate normality and absence of extreme distorting outliers.
                - **Spearman Rank Correlation ($\rho$)**: Non-parametric measure of monotonic relationship based on ranked values.
                  Resistant to outliers and does not assume linear relationships.
                - **Interpretation Standards**:
                  - $|r| < 0.20$: Negligible or very weak association.
                  - $0.20 \le |r| < 0.40$: Weak association.
                  - $0.40 \le |r| < 0.70$: Moderate association.
                  - $0.70 \le |r| \le 1.00$: Strong association.
                - **Causality Warning**: Even when statistically significant ($p < 0.05$), correlation does **not** prove causation.
                """
            )


# --- SECTION 5: STUDENT EXPLORER ---
elif nav_choice == "Student Explorer":
    st.markdown("### 🔍 Student Explorer")
    st.markdown("Search, filter, and inspect student records individually or in cohorts.")

    search_term = st.text_input("Search by Student ID (e.g., STD-1015)", "")

    e_col1, e_col2 = st.columns(2)
    with e_col1:
        att_range = st.slider("Filter by Attendance Range (%)", 0.0, 100.0, (0.0, 100.0))
    with e_col2:
        marks_range = st.slider("Filter by Marks Range (%)", 0.0, 100.0, (0.0, 100.0))

    explored_df = filter_dataset(
        filtered_df,
        min_attendance=att_range[0],
        max_attendance=att_range[1],
        min_marks=marks_range[0],
        max_marks=marks_range[1],
        search_query=search_term,
    )

    st.markdown(f"**Found {len(explored_df)} matching students.**")

    if not explored_df.empty:
        sort_by = st.selectbox(
            "Sort Records By",
            ["attendance_percentage", "average_marks", "student_id"],
            index=0,
        )
        sort_order = st.radio("Order", ["Descending", "Ascending"], horizontal=True)
        explored_df = explored_df.sort_values(
            by=sort_by,
            ascending=(sort_order == "Ascending"),
        )

        display_cols = [
            c
            for c in [
                "student_id",
                "department",
                "semester",
                "class",
                "attendance_percentage",
                "average_marks",
                "attendance_category",
                "performance_band",
            ]
            if c in explored_df.columns
        ]

        st.dataframe(explored_df[display_cols], use_container_width=True, hide_index=True)

        st.download_button(
            label="📥 Export Filtered Student Data (CSV)",
            data=explored_df.to_csv(index=False).encode("utf-8"),
            file_name="filtered_student_explorer.csv",
            mime="text/csv",
        )

        # Subject-level inspect if single student selected
        if search_term.strip():
            matched_sid = search_term.strip().upper()
            if not subject_df.empty and "student_id" in subject_df.columns:
                sub_records = subject_df[
                    subject_df["student_id"].str.upper() == matched_sid
                ]
                if not sub_records.empty:
                    st.markdown(f"#### Subject Marks Detail for {matched_sid}")
                    st.dataframe(
                        sub_records[
                            [
                                "subject",
                                "marks_obtained",
                                "maximum_marks",
                                "attendance_percentage",
                            ]
                        ],
                        use_container_width=True,
                        hide_index=True,
                    )


# --- SECTION 6: DATA MANAGEMENT ---
elif nav_choice == "Data Management":
    st.markdown("### 🗄️ Data Management & Quality Control")
    st.markdown(
        "Upload user CSV or Excel files, review data quality audits, or restore bundled demonstration data."
    )

    upload_tab, quality_tab, schema_tab = st.tabs(
        ["Upload Dataset", "Quality & Validation Audit", "Schema Specifications"]
    )

    with upload_tab:
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel dataset to analyze",
            type=["csv", "xlsx", "xls"],
            help="Upload student-level or subject-level academic datasets.",
        )

        col_up1, col_up2 = st.columns(2)
        with col_up1:
            if uploaded_file is not None:
                if st.button("🚀 Process & Validate Uploaded File", type="primary"):
                    try:
                        raw_upload = load_file(uploaded_file, filename=uploaded_file.name)
                        cleaning_res = clean_dataset(raw_upload, dataset_type="auto")

                        st.session_state.cleaning_result = cleaning_res
                        st.session_state.dataset_source_name = f"Uploaded: {uploaded_file.name}"

                        if cleaning_res.dataset_type == "subject_level":
                            st.session_state.subject_df = cleaning_res.cleaned_df
                            st.session_state.student_df = aggregate_subject_to_student(
                                cleaning_res.cleaned_df
                            )
                            st.session_state.has_subject_data = True
                        else:
                            st.session_state.student_df = cleaning_res.cleaned_df
                            st.session_state.subject_df = pd.DataFrame()
                            st.session_state.has_subject_data = False

                        st.session_state.data_loaded = True
                        st.success(f"File processed successfully! {cleaning_res.validation_message}")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to process uploaded file: {str(e)}")

        with col_up2:
            if st.button("🔄 Reset to Bundled Demonstration Dataset"):
                try:
                    init_session_state()
                    st.session_state.dataset_source_name = "Bundled Demonstration Dataset (Synthetic)"
                    st.success("Reset to bundled synthetic dataset complete.")
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to load bundled dataset: {str(e)}")

    with quality_tab:
        st.markdown("#### Data Quality & Cleaning Audit Summary")
        cr = st.session_state.get("cleaning_result")
        if cr is not None:
            q1, q2, q3, q4 = st.columns(4)
            q1.metric("Total Rows in Raw File", cr.total_rows)
            q2.metric("Valid Rows Accepted", cr.valid_rows)
            q3.metric("Duplicate Rows Flagged", cr.duplicate_count)
            q4.metric("Values Out of Range", cr.out_of_range_count)

            st.markdown(f"**Validation Status**: `{cr.validation_message}`")

            if not cr.issues_df.empty:
                st.markdown("##### Detected Validation Issues")
                st.dataframe(cr.issues_df, use_container_width=True, hide_index=True)
                st.download_button(
                    "📥 Download Validation Issues Report (CSV)",
                    data=cr.issues_df.to_csv(index=False).encode("utf-8"),
                    file_name="validation_issues.csv",
                    mime="text/csv",
                )
            else:
                st.success("No validation issues or data corruption detected in current dataset.")

            if not cr.cleaned_df.empty:
                st.markdown("##### Cleaned Dataset Preview")
                st.dataframe(cr.cleaned_df.head(10), use_container_width=True, hide_index=True)
                st.download_button(
                    "📥 Download Cleaned Analytical Dataset (CSV)",
                    data=cr.cleaned_df.to_csv(index=False).encode("utf-8"),
                    file_name="cleaned_student_dataset.csv",
                    mime="text/csv",
                )
        else:
            st.info("No cleaning audit available yet.")

    with schema_tab:
        st.markdown("#### Supported Dataset Formats")
        st.markdown(
            """
            ##### 1. Canonical Student-Level Format (Recommended)
            One record per student. Minimum required columns:
            - `student_id`: Unique identifier (e.g. `STD-1001`)
            - `attendance_percentage`: Numeric percentage between 0 and 100
            - `average_marks`: Numeric percentage between 0 and 100
            - *Optional*: `department`, `semester`, `class`

            ##### 2. Subject-Level Long Format
            Multiple records per student, one per curriculum subject:
            - `student_id`: Student identifier
            - `subject`: Name of subject (e.g. `Mathematics`)
            - `marks_obtained`: Marks scored (numeric)
            - `maximum_marks`: Max possible marks (numeric, e.g. 100)
            - `attendance_percentage`: Subject-level attendance (numeric, 0–100)
            - *Optional*: `department`, `semester`
            """
        )


# --- SECTION 7: ABOUT THE PROJECT ---
elif nav_choice == "About the Project":
    st.markdown("### 📖 About Student Performance Analytics")
    st.markdown(
        """
        #### Project Objective
        The **Student Attendance and Performance Correlation Dashboard** is an academic data analytics
        platform developed to examine the relationship between student class attendance and academic
        performance using rigorous exploratory data analysis, statistical modeling, and interactive visualization.

        #### Key Capabilities
        - **Descriptive Analytics**: KPI metrics for cohort attendance, mark distributions, standard deviations, and median baselines.
        - **Bivariate Correlation**: Pearson product-moment ($r$) and Spearman rank ($\rho$) coefficients with hypothesis testing ($p$-value).
        - **Early Advisory Outreach**: Configurable threshold tracking to identify students who may benefit from academic support.
        - **Data Quality Control**: Automated deduplication, type validation, out-of-range checking, and subject-to-student aggregation without double counting.
        - **Exportable Reports**: One-click downloads of cleaned datasets, low-attendance reports, advisory lists, and correlation analyses.

        #### Technology Stack
        - **Language**: Python 3.10+
        - **Data Analysis**: Pandas, NumPy
        - **Visualization**: Plotly Express & Graph Objects
        - **Dashboard Framework**: Streamlit
        - **Testing & Quality Assurance**: pytest

        #### Ethical & Academic Disclaimer
        1. **Correlation vs Causation**: Statistical association does **not** imply direct causation.
        2. **Synthetic Data**: All bundled sample datasets represent purely synthetic, reproducible data generated for demonstration purposes. No real student personal identifiable information (PII) is included or processed.
        3. **Advisory Purpose**: This tool provides exploratory decision support for academic counseling and does not perform automated disciplinary or grading determinations.
        """
    )
