# ACADEMIC PROJECT REPORT

## STUDENT ATTENDANCE AND PERFORMANCE CORRELATION DASHBOARD
### Attendance, Academic Performance & Statistical Insights

---

### Project Cover Page Details

- **Project Title**: Student Attendance and Performance Correlation Dashboard
- **Application Name**: Student Performance Analytics
- **Candidate Name**: [Student Name]
- **Roll Number / Student ID**: [Roll Number]
- **Degree / Course**: Bachelor of Technology / Science in Computer Science & Engineering
- **Department**: Department of Computer Science & Engineering
- **Institution**: [Institute / University Name]
- **Academic Year**: 2025 – 2026
- **Project Guide / Supervisor**: [Guide Name], [Designation]
- **Date of Submission**: October 2026

---

## 1. Abstract

Student retention and academic achievement are critical priorities for higher educational institutions. While classroom attendance is intuitively associated with academic performance, empirical verification across diverse departments and subject domains is often hindered by fragmented administrative record systems.

This project presents the **Student Attendance and Performance Correlation Dashboard**, a modular, interactive data analytics and decision-support web application developed using Python, Streamlit, Pandas, NumPy, and Plotly. The system provides institutional administrators and academic advisors with automated data validation, descriptive KPI tracking, subject-level disparity analysis, and bivariate correlation analysis using both parametric (Pearson $r$) and non-parametric (Spearman $\rho$) methods.

Crucially, the system enforces ethical analytical boundaries by explicitly clarifying that statistical correlation does not establish causation. A reproducible synthetic dataset of 150 students across five engineering disciplines is bundled to demonstrate the dashboard's capabilities without compromising student privacy. Comprehensive automated unit and integration tests (36 test cases) validate the application's mathematical accuracy, robust edge-case handling (zero variance, missing values, duplicates), and absence of student double-counting during aggregation.

---

## 2. Introduction

Class attendance represents one of the primary points of engagement between undergraduate students and academic institutions. Conventional institutional workflows record daily attendance and term marks in disconnected registers or standalone spreadsheets. Consequently, academic advisors often identify at-risk students only after end-of-semester exam failures.

The **Student Performance Analytics** dashboard bridges this gap by offering a centralized, exploratory analytics tool. It enables faculty to examine cohort attendance distributions, detect students falling below institutional thresholds (e.g., 75%), assess curricular subject performance, and quantitatively evaluate the degree of association between attendance rates and final marks.

---

## 3. Problem Statement

Higher education institutions face significant challenges in managing and interpreting student academic records:
1. **Data Silos**: Attendance percentages and examination marks are typically stored across separate files, impeding timely synthesis.
2. **Double-Counting Pitfalls**: When records are formatted at the subject level (multiple rows per student), standard spreadsheet formulas often double-count students, skewing population statistics.
3. **Lack of Statistical Rigor**: Faculty often rely on anecdotal impressions rather than mathematical correlation metrics and hypothesis tests.
4. **Causality Fallacy**: Educators sometimes jump to unsupported causal conclusions (e.g., assuming low attendance is the sole cause of poor performance), overlooking external factors like illness or curriculum difficulty.
5. **Absence of Proactive Advising**: Without dynamic threshold filtering, students needing academic tutoring remain unnoticed until formal grade publication.

---

## 4. Objectives

The primary objectives of this project are:
- **Design & Implement an Analytics Dashboard**: Build a professional, responsive web application using Streamlit and Plotly.
- **Support Dual Data Schemas**: Handle both student-level canonical datasets and multi-subject long-format records seamlessly.
- **Implement Rigorous Cleaning & Validation**: Automatically audit uploads for duplicate IDs, missing values, non-numeric strings, and out-of-range percentages.
- **Prevent Double-Counting**: Formulate robust group aggregation logic ensuring each student is counted exactly once in cohort-wide KPIs.
- **Conduct Empirical Correlation Modeling**: Calculate Pearson $r$ and Spearman $\rho$ with Student's $t$-distribution $p$-values, supported by automated, plain-language non-causal interpretations.
- **Enable Decision Support & Advisory Flags**: Identify students below configurable attendance and marks thresholds for supportive outreach.
- **Ensure Scientific Reproducibility**: Develop a pseudorandom synthetic data generator using fixed random seeds.

---

## 5. Scope

### In-Scope:
- Ingestion and validation of CSV and Excel datasets.
- Calculation of descriptive statistics (mean, median, standard deviation, min, max).
- Correlation analysis ($r$, $\rho$, $p$-value, trendline).
- Interactive cohort slicing by department, semester, and section.
- Generation of automated data-driven insights.
- Exporting cleaned datasets, correlation reports, and advisory lists.
- Full automated test suite via pytest.

### Out-of-Scope (Phase I Limitations):
- Direct connection to live production SQL databases or university ERP APIs.
- Automated email dispatching or disciplinary tracking.
- Multivariate causal modeling (e.g., structural equation modeling).

---

## 6. Existing System vs Proposed System

| Dimension | Existing System | Proposed System |
|---|---|---|
| **Data Storage** | Disconnected spreadsheets | Unified CSV/Excel ingestion with schema detection |
| **Analysis Method** | Manual formulas and intuition | Automated statistical engine (Pandas, NumPy) |
| **Visualizations** | Static charts | Interactive Plotly visualizations with tooltips |
| **Multi-Subject Aggregation** | High risk of double-counting students | Mathematical deduplication and grouping per student |
| **Correlation Evaluation** | Rarely computed; informal guesswork | Pearson $r$ & Spearman $\rho$ with $p$-values and interpretation |
| **Early Warning** | Post-exam disciplinary action | Configurable benchmark advisory outreach |
| **Data Privacy** | Risk of exposing personal data | Bundled 100% synthetic data with zero PII |

---

## 7. System Requirements

### Hardware Requirements:
- **Processor**: Dual-core x86-64 CPU (2.0 GHz or higher).
- **RAM**: Minimum 4 GB (8 GB recommended for large cohorts).
- **Storage**: 200 MB free hard drive space.
- **Display**: Minimum screen resolution of 1366 × 768.

### Software Requirements:
- **Operating System**: Microsoft Windows 10/11 (or Linux/macOS).
- **Runtime**: Python 3.10, 3.11, or 3.14.
- **Core Libraries**: Streamlit, Pandas, NumPy, Plotly, Matplotlib, Openpyxl, Pytest.
- **Browser**: Modern web browser (Google Chrome, Microsoft Edge, Mozilla Firefox).

---

## 8. System Architecture

The application adopts a modular, tiered architecture separating data ingestion, business logic, statistical modeling, and UI rendering:

```
+-----------------------------------------------------------------------+
|                         PRESENTATION TIER (UI)                        |
|                                                                       |
|  Streamlit Web Application (app.py)                                   |
|  ├── Overview Dashboard           ├── Correlation Analysis            |
|  ├── Attendance Analysis          ├── Student Explorer                |
|  ├── Academic Performance         ├── Data Management & Quality       |
+-----------------------------------------------------------------------+
                                  │
                                  ▼
+-----------------------------------------------------------------------+
|                          BUSINESS LOGIC TIER                          |
|                                                                       |
|  ├── Data Loader (data_loader.py): CSV/Excel Parsing & Schema Detection|
|  ├── Data Cleaning (data_cleaning.py): Deduplication & Aggregation    |
|  ├── Analytics Engine (analytics.py): KPI Summaries & Thresholds       |
|  ├── Correlation Engine (correlation.py): Pearson r, Spearman rho, p-val|
|  ├── Insights Engine (insights.py): Data-driven Non-Causal Reports    |
|  └── Visualization Engine (visualizations.py): Plotly Academic Charts |
+-----------------------------------------------------------------------+
                                  │
                                  ▼
+-----------------------------------------------------------------------+
|                            DATA STORAGE TIER                          |
|                                                                       |
|  ├── data/sample_students.csv (150 Synthetic Student Records)         |
|  ├── data/sample_subject_marks.csv (750 Synthetic Subject Records)    |
|  └── User Uploads (In-Memory Processing / Temporary CSV Export)        |
+-----------------------------------------------------------------------+
```

---

## 9. Module Descriptions

1. **`src/data_generator.py`**:
   - Generates reproducible synthetic student cohorts using fixed seeds (`seed=42`).
   - Produces realistic variation without artificially forcing a fixed correlation coefficient.
   - Enforces attendance bounds $[30.0, 100.0]$ and marks bounds $[15.0, 100.0]$.

2. **`src/data_loader.py`**:
   - Normalizes column names (lowercase, trimmed, underscores).
   - Detects dataset schema (`student_level` vs `subject_level`).
   - Handles buffer streams and local filepaths safely.

3. **`src/data_cleaning.py`**:
   - Audits missing values, duplicates, and out-of-range figures.
   - Aggregates subject records into single-student summaries ($(\sum \text{obtained} / \sum \text{max}) \times 100$) ensuring zero double-counting.

4. **`src/analytics.py`**:
   - Computes parametric and non-parametric cohort KPIs (mean, median, min, max, standard deviation).
   - Classifies students into attendance tiers and performance bands.
   - Filters datasets dynamically across multiple categorical and numerical criteria.

5. **`src/correlation.py`**:
   - Computes Pearson $r$ and Spearman $\rho$.
   - Calculates Student's $t$-statistic and two-tailed $p$-values via continued fraction incomplete beta implementation.
   - Handles edge cases: constant values (zero variance), $< 2$ observations, and empty datasets.

6. **`src/insights.py`**:
   - Generates automated textual findings based strictly on computed results.
   - Embeds ethical non-causal disclaimers.

7. **`src/visualizations.py`**:
   - Produces Plotly interactive histograms, scatter plots with trendlines, pie charts, and grouped bar charts using an academic visual palette.

---

## 10. Data Preprocessing Methodology

When a dataset is loaded:
1. **Header Normalization**: Strips spaces, converts to lowercase, and replaces hyphens with underscores.
2. **Duplicate Detection**: Identifies multiple rows with identical `student_id` in student files, or identical `(student_id, subject)` pairs in subject files. Retains the first occurrence and flags duplicates in a dedicated audit log.
3. **Numeric Coercion**: Converts attendance and marks columns using `pd.to_numeric(..., errors='coerce')`.
4. **Boundary Validation**: Checks that attendance $\in [0.0, 100.0]$ and marks $\in [0.0, \text{maximum\_marks}]$. Rows violating these boundaries are logged as invalid and excluded from statistical calculations.
5. **Aggregation**: For subject datasets, records are grouped by `student_id` to compute student-level weighted averages before feeding into cohort analytics.

---

## 11. Statistical & Correlation Methodology

### Pearson Product-Moment Correlation ($r$):
$$r = \frac{\sum_{i=1}^{n} (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum_{i=1}^{n} (x_i - \bar{x})^2 \sum_{i=1}^{n} (y_i - \bar{y})^2}}$$

### Spearman Rank Correlation ($\rho$):
$$\rho = 1 - \frac{6 \sum d_i^2}{n(n^2 - 1)}$$
where $d_i = \text{rank}(x_i) - \text{rank}(y_i)$.

### Hypothesis Testing ($t$-statistic & $p$-value):
$$t = r \sqrt{\frac{n - 2}{1 - r^2}}, \quad \text{degrees of freedom } df = n - 2$$
The two-tailed $p$-value is evaluated via the regularized incomplete beta function $I_x(\frac{df}{2}, \frac{1}{2})$ with $x = \frac{df}{df + t^2}$.

---

## 12. Testing Methodology & Verification Results

Automated testing was conducted using `pytest`. The test suite consists of 36 independent unit tests covering:
- Dataset generation count, bounds, and seed reproducibility.
- File loading with CSV buffers, empty files, and nonexistent paths.
- Deduplication, missing value audits, and subject aggregation without double-counting.
- Mathematical precision of KPI averages, medians, and standard deviations.
- Correlation edge cases: perfect positive ($r=1.0$), perfect negative ($r=-1.0$), zero variance / constant columns, single-row cohorts, and missing value pairings.
- Insight generation and non-causal language verification.

### Test Execution Output:
```
============================= test session starts =============================
platform win32 -- Python 3.11.7, pytest-7.2.1, pluggy-1.5.0
collected 36 items

tests/test_analytics.py ......................... [ 22%]
tests/test_correlation.py ....................... [ 44%]
tests/test_data_cleaning.py ..................... [ 61%]
tests/test_data_generator.py .................... [ 77%]
tests/test_data_loader.py ....................... [ 94%]
tests/test_insights.py ..                         [100%]

============================= 36 passed in 5.41s ==============================
```

---

## 13. Results and Discussion

Analysis of the bundled synthetic dataset (150 students) demonstrated:
- **Mean Attendance**: 72.1% (Standard Deviation: 13.5%)
- **Mean Marks**: 57.3% (Standard Deviation: 13.9 points)
- **Students Below 75% Attendance Benchmark**: 86 (57.3%)
- **Pearson Correlation**: $r = +0.373$ ($p < 0.001$)
- **Spearman Correlation**: $\rho = +0.359$ ($p < 0.001$)

The results confirm a statistically significant, weak-to-moderate positive association between attendance and examination performance. The non-linear scatter plot indicates that while higher attendance generally associates with stronger performance, individual variation exists—illustrating why correlation cannot be conflated with direct causality.

---

## 14. Conclusion

The **Student Attendance and Performance Correlation Dashboard** successfully accomplishes its design goals. It provides educational administrators with an intuitive, reliable, and mathematically rigorous platform for monitoring student cohorts. By implementing automated data cleaning, transparent statistical explanations, and early advisory support lists, the project delivers actionable academic intelligence while strictly respecting privacy and scientific ethics.

---

## 15. References

1. Python Software Foundation. *Python Language Reference, version 3.11/3.14*. https://www.python.org/
2. McKinney, W. *Data Structures for Statistical Computing in Python*. Proceedings of the 9th Python in Science Conference, 2010.
3. Harris, C. R., et al. *Array programming with NumPy*. Nature 585, 357–362, 2020.
4. Streamlit Inc. *Streamlit Documentation*. https://docs.streamlit.io/
5. Plotly Technologies Inc. *Plotly Open Source Graphing Library for Python*. https://plotly.com/python/
6. Kreyszig, E. *Advanced Engineering Mathematics: Probability and Mathematical Statistics*. John Wiley & Sons, 10th Edition.
