# Student Performance Analytics
## Attendance, Academic Performance & Statistical Insights

An academic data analytics and interactive decision-support platform built with Python, Streamlit, Pandas, NumPy, and Plotly. This platform evaluates the empirical statistical association between student class attendance percentages and academic performance while upholding strict scientific and ethical principles—specifically recognizing that **statistical correlation does not establish causation**.

---

## 1. Project Overview

The **Student Attendance and Performance Correlation Dashboard** provides educational administrators, department heads, and academic advisors with transparent, data-driven insights into cohort attendance, grade distributions, and curriculum performance. By combining descriptive statistical summaries with bivariate correlation modeling, the system highlights at-risk students who may benefit from early academic intervention, tutoring, or counseling.

> **Important Academic & Privacy Note**: All demonstration datasets (`sample_students.csv` and `sample_subject_marks.csv`) are 100% **synthetic**, generated via reproducible pseudorandom algorithms using fixed seeds. No real student personal identifiable information (PII) is included, collected, or transmitted.

---

## 2. Problem Statement

Academic institutions often observe variations in student performance across diverse departments, semesters, and subjects. However:
- Attendance records and examination grades frequently reside in siloed spreadsheets.
- Institutional leaders lack interactive tools to examine whether attendance trends systematically associate with academic scores.
- Crude analytical systems often oversimplify findings or mistakenly assume low attendance is the sole cause of lower grades, overlooking extraneous factors such as curriculum difficulty, illness, or external commitments.
- Systems often double-count students when processing multi-subject long-format records.

---

## 3. Objectives

1. **Provide Institutional Visibility**: Deliver real-time KPIs on attendance, average marks, and threshold adherence across departments and classes.
2. **Empirical Correlation Analysis**: Compute Pearson product-moment ($r$) and Spearman rank ($\rho$) correlation coefficients with rigorous edge-case handling (zero variance, missing values, small samples).
3. **Early Advisory Support**: Automatically flag students falling below configurable attendance benchmarks (default: 75%) or marks benchmarks (default: 50%) for proactive advising.
4. **Subject Disparity Analysis**: Compare curriculum subjects by average scores, pass rates, and attendance engagement.
5. **Data Quality & Integrity Assurance**: Validate user-uploaded datasets, detect duplicates, flag out-of-range figures, and aggregate subject-level records without double-counting students.
6. **Exportable Reporting**: Generate downloadable reports (CSV, Markdown) for departmental meetings and academic committees.

---

## 4. Main Features

- **Executive KPI Dashboard**: Instant metrics for total cohort population, mean/median attendance, mean marks, threshold adherence, and correlation strength.
- **Dedicated Attendance Analysis**: Configurable benchmark threshold slider, histogram distribution, tier breakdown, and downloadable low-attendance student rosters.
- **Academic Performance Analysis**: Score distribution, highest/lowest marks, standard deviation, top performers ranking, and academic advisory lists.
- **Statistical Correlation Engine**: Interactive scatter plot with trendline, Pearson $r$, Spearman $\rho$, Student's $t$ hypothesis test $p$-values, plain-language non-causal interpretations, and downloadable report.
- **Student Explorer**: Multi-dimensional filtering by department, semester, class, attendance range, marks range, and fuzzy student ID search.
- **Data Management & Quality Control**: One-click restore to bundled demonstration dataset, CSV/Excel file upload, schema normalization, missing value audits, duplicate detection, and cleaned data export.

---

## 5. Technology Stack

- **Core Language**: Python 3.10+ (tested on Python 3.11 & 3.14)
- **Interactive Web Dashboard**: Streamlit (v1.30.0+)
- **Data Manipulation & Preprocessing**: Pandas (v2.0.0+ / v3.0+)
- **Numerical Operations & Reproducible Simulation**: NumPy (v1.24.0+ / v2.0+)
- **Data Visualization**: Plotly Express & Plotly Graph Objects (v5.18.0+)
- **Unit & Integration Testing**: pytest (v8.0.0+)
- **Data Storage**: Local CSV and optional Excel files

---

## 6. Project Folder Structure

```
student_attendance/
├── app.py                      # Main interactive Streamlit application
├── requirements.txt            # Python dependencies
├── pytest.ini                  # Pytest configuration
├── .gitignore                  # Git ignore rules for virtualenvs, caches, secrets
│
├── data/
│   ├── sample_students.csv     # Bundled synthetic student-level dataset (150 students)
│   └── sample_subject_marks.csv# Bundled synthetic subject-level dataset (750 records)
│
├── src/
│   ├── __init__.py             # Package marker
│   ├── data_generator.py       # Reproducible synthetic dataset generator
│   ├── data_loader.py          # CSV/Excel reader and schema detector
│   ├── data_cleaning.py        # Validation, auditing & subject-to-student aggregation
│   ├── analytics.py            # Summary KPIs, categorization & cohort filtering
│   ├── correlation.py          # Pearson/Spearman correlation & non-causal interpreter
│   ├── insights.py             # Reusable automated data-driven insight generator
│   └── visualizations.py       # Plotly charts with academic color theme
│
├── tests/
│   ├── __init__.py
│   ├── test_data_generator.py  # Tests for synthetic data bounds and reproducibility
│   ├── test_data_loader.py     # Tests for file loading and schema detection
│   ├── test_data_cleaning.py   # Tests for validation, duplicates, and aggregation
│   ├── test_analytics.py       # Tests for KPI calculations, bands, and filtering
│   ├── test_correlation.py     # Tests for correlation, zero-variance & edge cases
│   └── test_insights.py        # Tests for automated analytical insights
│
└── docs/
    ├── PROJECT_REPORT.md       # Comprehensive academic project report
    ├── USER_GUIDE.md           # Step-by-step end-user guide
    └── DEMO_SCRIPT.md          # 16-step video demonstration script
```

---

## 7. System Requirements

- **Operating System**: Windows 10/11, macOS 12+, or Ubuntu Linux 20.04+
- **Processor**: Intel Core i3 / AMD Ryzen 3 or higher
- **RAM**: Minimum 4 GB (8 GB recommended)
- **Disk Space**: 200 MB free space
- **Python**: Version 3.10, 3.11, 3.12, 3.13, or 3.14

---

## 8. Installation & Setup (Windows PowerShell)

### Step 1: Clone or Navigate to the Workspace
```powershell
cd d:\student_attendance
```

### Step 2: Create a Virtual Environment (Recommended)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(If PowerShell restricts script execution, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

### Step 3: Install Required Dependencies
```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

## 9. Running the Application

Launch the Streamlit web dashboard:
```powershell
python -m streamlit run app.py
```

The application will start automatically and open in your default browser at:
```
Local URL: http://localhost:8501
```

---

## 10. Synthetic Datasets & Generation

Both demonstration datasets are bundled under `data/`. If you wish to regenerate them with custom sample sizes or random seeds:

```powershell
python -m src.data_generator
```

### Supported Dataset Formats:

#### Format A: Canonical Student-Level Format (`sample_students.csv`)
| Column | Type | Description |
|---|---|---|
| `student_id` | String | Unique identifier (e.g., `STD-1001`) |
| `attendance_percentage` | Float | Value between 0.0 and 100.0 |
| `average_marks` | Float | Aggregate score between 0.0 and 100.0 |
| `department` *(optional)* | String | Academic department |
| `semester` *(optional)* | String | Current semester |
| `class` *(optional)* | String | Section or division |

#### Format B: Subject-Level Long Format (`sample_subject_marks.csv`)
| Column | Type | Description |
|---|---|---|
| `student_id` | String | Student identifier |
| `subject` | String | Curriculum course title |
| `marks_obtained` | Float | Score achieved |
| `maximum_marks` | Float | Maximum possible score (e.g., 100.0) |
| `attendance_percentage` | Float | Subject-specific attendance |
| `department` | String | Academic department |
| `semester` | String | Semester label |

---

## 11. Explanation of Correlation Analysis

The dashboard calculates two complementary coefficients:
1. **Pearson Correlation Coefficient ($r$)**: Evaluates the degree of linear association between continuous attendance and marks. Assumes approximate bivariate normality.
2. **Spearman Rank Correlation ($\rho$)**: Evaluates monotonic trends by ranking observations. Robust to non-linear associations and outliers.

### Interpretation Thresholds:
- $|r| < 0.20$: **Negligible / very weak association**
- $0.20 \le |r| < 0.40$: **Weak positive/negative association**
- $0.40 \le |r| < 0.70$: **Moderate positive/negative association**
- $0.70 \le |r| \le 1.00$: **Strong positive/negative association**

### Statistical Significance ($p$-value):
Calculated using the Student's $t$-distribution with $n - 2$ degrees of freedom. A $p < 0.05$ indicates that the observed association is unlikely to be a product of random sampling error.

### Scientific Disclaimer:
> **Correlation $\neq$ Causation**: A positive correlation indicates that higher attendance and higher marks tend to co-occur in the observed cohort. It does not establish that increasing attendance will automatically raise marks for every student, as student motivation, prior preparation, health, and instruction quality are confounding variables.

---

## 12. Sample Analytical Findings (Bundled Dataset)

Based on the bundled synthetic dataset of 150 students across 5 engineering departments:
- **Total Students**: 150
- **Average Attendance**: 72.1% (Median: 71.9%)
- **Average Academic Marks**: 57.3% (Std Dev: 13.9 points)
- **Students Below 75% Attendance Benchmark**: 86 students (57.3%)
- **Pearson Correlation ($r$)**: `+0.373` ($p < 0.001$, statistically significant)
- **Spearman Rank Correlation ($\rho$)**: `+0.359` ($p < 0.001$)
- **Interpretation**: Weak-to-moderate positive association. Higher attendance moderately co-occurs with higher academic scores.

---

## 13. Running Automated Tests

Run the full pytest suite:
```powershell
pytest
```

For verbose execution with coverage:
```powershell
pytest -v
```

All 36 unit tests cover:
- Synthetic dataset bounds (0-100), structure, and seed reproducibility
- Clean CSV and Excel loading and error handling on malformed files
- Missing required column detection, duplicate detection, and non-numeric coercion
- Single-student aggregation avoiding double-counting in multi-subject records
- Edge cases: empty cohorts, 1-row datasets, zero-variance / constant columns
- Formula accuracy for Pearson $r$, Spearman $\rho$, and $t$-distribution $p$-values
- Automated insight phrasing and filtering logic

---

## 14. Known Limitations & Future Enhancements

### Known Limitations:
- Initial version processes CSV and Excel files locally; does not connect directly to live institutional SQL databases or ERP APIs.
- Correlation analysis evaluates pairwise relationships; does not perform multivariate regression controlling for socioeconomic factors or student study hours.

### Planned Enhancements:
- Direct database connector for PostgreSQL, MySQL, and SQLite.
- Longitudinal semester-over-semester trend tracking.
- Automated email alerts for academic advisors.

---

## 15. Academic Project Disclaimer

This software was engineered as an educational data analytics and visualization system for academic project demonstration. It is designed to assist faculty in identifying students who might need voluntary tutoring or counseling. It must **not** be used as an automated disciplinary tool or for making high-stakes academic judgments without holistic human review.
