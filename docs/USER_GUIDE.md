# STUDENT PERFORMANCE ANALYTICS — USER GUIDE
### Operational Handbook for Academic Administrators and Faculty

---

## 1. Quick Start

### Starting the Application
Open Windows PowerShell, navigate to the project directory, and run:
```powershell
python -m streamlit run app.py
```
Your browser will open automatically at `http://localhost:8501`.

### Default Demonstration Data
The dashboard loads a bundled synthetic dataset of 150 students across five engineering departments upon launch. You can begin exploring immediately without uploading any files.

---

## 2. Navigating the Dashboard

Use the left sidebar radio buttons to switch between seven specialized modules:

1. **Overview**: Executive high-level KPI cards, attendance and marks distribution histograms, attendance-marks scatter plot with trendline, and automated data-driven insights.
2. **Attendance Analysis**: In-depth attendance distribution, tier breakdown (Critical, Low, Good, Excellent), and a filtered list of students below the attendance benchmark.
3. **Academic Performance**: Score distributions, highest/lowest marks, standard deviation, subject-wise comparisons, top 15 performers, and advisory support recommendations.
4. **Correlation Analysis**: Pearson ($r$) and Spearman ($\rho$) correlation coefficients, hypothesis test $p$-values, scatter plot with trendline, and downloadable correlation report.
5. **Student Explorer**: Search individual students by ID, filter by attendance and marks ranges, sort records, and inspect subject-level breakdowns.
6. **Data Management**: Upload user CSV/Excel files, review data quality audits, view detected issues, download cleaned data, or restore bundled sample data.
7. **About the Project**: System overview, technology stack, and academic ethics principles.

---

## 3. Sidebar Controls & Settings

- **Attendance Benchmark (%)**: Adjust the threshold slider (default: `75%`) to evaluate how many students meet institutional requirements. All pages update dynamically.
- **Marks Support Benchmark (%)**: Adjust the performance benchmark (default: `50%`) used to flag students who may benefit from academic tutoring.
- **Cohort Filters**: Filter by Department (e.g. `Computer Science`), Semester (e.g. `Semester 4`), and Class Section (`Section A`, `Section B`, etc.).

---

## 4. Uploading Custom Datasets

Navigate to the **Data Management** page.

### Supported File Formats:
You can upload either `.csv` or `.xlsx` files adhering to one of two schemas:

#### Option 1: Student-Level Dataset (Canonical)
Must contain at least these three columns:
- `student_id`: Unique identifier (e.g., `STD-1001`)
- `attendance_percentage`: Numeric value between 0 and 100
- `average_marks`: Numeric value between 0 and 100
- *Optional columns*: `department`, `semester`, `class`

#### Option 2: Subject-Level Long Format Dataset
Must contain:
- `student_id`: Student identifier
- `subject`: Name of curriculum subject
- `marks_obtained`: Numeric marks scored
- `maximum_marks`: Max possible marks (e.g., 100)
- `attendance_percentage`: Subject attendance
- *Optional columns*: `department`, `semester`

When a subject-level dataset is uploaded, the system automatically computes student-level weighted averages without double-counting students.

### Quality Audit & Validation:
- If duplicate IDs or subject entries are detected, the first occurrence is kept, and duplicates are logged in the audit table.
- Values outside 0–100 are flagged and safely excluded from statistical calculations.
- You can download both the **Cleaned Dataset** and the **Validation Issues Report** with one click.

---

## 5. Exporting Reports

Download buttons are provided throughout the dashboard:
- **Low Attendance Report**: Download a CSV roster of all students below the attendance benchmark.
- **Academic Advisory List**: Download a CSV list of students recommended for academic tutoring.
- **Filtered Student Data**: Download customized student slices from the Student Explorer.
- **Correlation Analysis Report**: Export a formatted Markdown report summarizing correlation coefficients, $t$-statistics, $p$-values, and plain-language interpretations.
- **Cleaned Dataset & Audit Issues**: Download validated datasets from the Data Management page.

---

## 6. Understanding Correlation vs Causation

- **Positive Correlation ($r > 0$)**: Indicates that students with higher attendance generally tend to achieve higher marks in the observed cohort.
- **Not Causation**: A high correlation does **not** mean attendance alone caused the marks. Study habits, prior knowledge, health, and instruction quality also contribute. The tool is designed to support proactive academic counseling, not punitive measures.
