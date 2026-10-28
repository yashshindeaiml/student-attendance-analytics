# VIDEO DEMONSTRATION SCRIPT
## Student Attendance and Performance Correlation Dashboard

---

### Speaker Introduction:
> **"Hello, my name is [Your Name]. I am presenting my project, Student Attendance and Performance Correlation Dashboard."**

---

### Step 1: Project Introduction
- **Visual**: Show project cover slide or README header.
- **Narrative**:
  "Educational institutions continuously strive to understand student academic outcomes. Class attendance is widely regarded as a key indicator of student engagement, but understanding how attendance systematically connects with marks across diverse departments requires sound statistical analysis. This project, **Student Performance Analytics**, provides a centralized, interactive analytics platform for evaluating student attendance patterns and academic performance."

---

### Step 2: Problem Statement
- **Visual**: Highlight problem statement slide or documentation.
- **Narrative**:
  "In many institutions, attendance records and examination marks exist in disparate spreadsheets. Academic advisors often struggle to identify at-risk students before final examinations. Moreover, when datasets contain multiple subject records per student, manual spreadsheet calculations frequently double-count students, skewing population statistics. Crucially, institutions often lack tools to mathematically assess correlation while avoiding the trap of assuming correlation proves causation."

---

### Step 3: Project Objectives
- **Visual**: Show objectives list.
- **Narrative**:
  "Our objectives were to build a reliable web application using Python that:
  First, computes institutional descriptive statistics without double-counting students.
  Second, performs rigorous bivariate correlation using Pearson and Spearman methods.
  Third, enables early warning advisory identification for students below configurable thresholds.
  And fourth, ensures complete reproducibility with synthetic datasets to safeguard student privacy."

---

### Step 4: Technology Stack
- **Visual**: Show `requirements.txt` and architectural diagram.
- **Narrative**:
  "The application is built using standard, reliable Python technologies:
  - **Python** for core application logic.
  - **Pandas** and **NumPy** for data manipulation and statistical calculations.
  - **Plotly** for interactive data visualizations.
  - **Streamlit** for the responsive, modern web interface.
  - And **pytest** for automated verification across 36 unit tests."

---

### Step 5: Launching the Application
- **Visual**: Open Windows PowerShell, show virtual environment, and run command:
  ```powershell
  python -m streamlit run app.py
  ```
- **Narrative**:
  "Launching the application is straightforward. In Windows PowerShell, we run `python -m streamlit run app.py`. The local web server starts immediately at port 8501 and loads in our browser."

---

### Step 6: Automatic Bundled Demonstration Dataset Loading
- **Visual**: Show browser at `http://localhost:8501`.
- **Narrative**:
  "Upon opening, the application automatically loads our bundled demonstration dataset containing 150 synthetic students across five engineering departments. Both student-level and subject-level datasets are generated with fixed pseudorandom seeds, ensuring full scientific reproducibility with zero real personal data."

---

### Step 7: Overview Dashboard & KPI Cards
- **Visual**: Point cursor to the 5 KPI cards, scatter plot, histograms, and analytical insights.
- **Narrative**:
  "On the Overview page, five executive KPI cards instantly display:
  - Total cohort size: 150 students.
  - Average attendance: 72.1% (median: 71.9%).
  - Average academic marks: 57.3% with a standard deviation of 13.9 points.
  - Number of students below our 75% attendance benchmark: 86 students.
  - And the observed Pearson correlation coefficient: +0.37, indicating a weak-to-moderate positive association.
  Below, we see our interactive scatter plot with an OLS trendline, attendance and marks distribution histograms, subject comparisons, and automated, strictly data-driven insight statements."

---

### Step 8: Dedicated Attendance Analysis
- **Visual**: Click 'Attendance Analysis' in sidebar navigation.
- **Narrative**:
  "Navigating to Attendance Analysis, we explore attendance distribution across four tiers: Critical (<60%), Low (60% to 75%), Good (75% to 85%), and Excellent (85% and above). If we adjust the attendance benchmark slider in the sidebar—for instance, changing it from 75% to 80%—the metrics and charts update in real time. We also have a dedicated table of students below the benchmark and a one-click CSV download."

---

### Step 9: Academic Performance Analysis
- **Visual**: Click 'Academic Performance' in sidebar navigation.
- **Narrative**:
  "In Academic Performance, we inspect grade distributions, curriculum subject averages, top 15 performing students, and our Academic Advisory Support recommendations. This tab identifies students who fall below either the attendance or marks benchmarks, providing counselors with an outreach list for voluntary tutoring."

---

### Step 10: Statistical Correlation Analysis
- **Visual**: Click 'Correlation Analysis' in sidebar navigation.
- **Narrative**:
  "This is the core statistical engine of the project. We calculate both the parametric Pearson correlation coefficient (r = 0.373) and the non-parametric Spearman rank correlation (rho = 0.359). The calculated p-value of less than 0.001 demonstrates statistical significance.
  Most importantly, we include a prominent ethical disclaimer: correlation reflects statistical co-occurrence, not causation. We cannot assume low attendance alone causes low marks, as study habits, illness, and course difficulty also play critical roles."

---

### Step 11: Student Explorer & Slicing
- **Visual**: Click 'Student Explorer', type 'STD-1015' into search bar, adjust range sliders.
- **Narrative**:
  "The Student Explorer enables administrators to search for specific students, filter by attendance and marks score ranges, and sort records. When searching for an individual student, the system displays their specific subject marks breakdown."

---

### Step 12: Data Management & File Upload
- **Visual**: Click 'Data Management' in sidebar navigation.
- **Narrative**:
  "In Data Management, users can upload their own CSV or Excel datasets. The system supports both canonical student-level files and multi-subject long-format files."

---

### Step 13: Data Validation & Quality Control
- **Visual**: Show Quality & Validation Audit tab.
- **Narrative**:
  "Our validation engine automatically normalizes column names, coerces data types, detects duplicate records, and flags values outside valid ranges (0–100%). Crucially, when multi-subject datasets are loaded, the system aggregates them so each student is counted exactly once, preventing double-counting."

---

### Step 14: Exporting Analytical Reports
- **Visual**: Click download buttons: 'Download Cleaned Dataset' and 'Download Correlation Report'.
- **Narrative**:
  "Administrators can export reports at any time. We can download cleaned datasets, audit reports, low-attendance rosters, and a complete correlation analysis report in Markdown format for departmental meetings."

---

### Step 15: Limitations
- **Visual**: Return to presentation slide or documentation.
- **Narrative**:
  "As an educational Phase I analytics project, there are a few acknowledged limitations:
  First, data is ingested via CSV or Excel files rather than direct connections to live production ERP databases.
  Second, bivariate correlation analyzes pairs of variables rather than multivariate models controlling for socioeconomic background or independent study hours."

---

### Step 16: Conclusion
- **Visual**: Concluding slide with repository and project details.
- **Narrative**:
  "In conclusion, the **Student Attendance and Performance Correlation Dashboard** delivers an intuitive, statistically rigorous, and ethically grounded tool for academic decision support. All 36 automated unit tests pass, and the application is ready for institutional deployment. Thank you for your time!"
