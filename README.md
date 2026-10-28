# Student Attendance and Performance Correlation Dashboard

An interactive dashboard for analysing student attendance, academic performance, and the statistical relationship between them.

Built using Python, Pandas, NumPy, Streamlit, and Plotly, this project provides visual insights into attendance patterns, subject-wise performance, and students who may benefit from additional academic support.

## Project Objectives

- Analyse student attendance and academic performance.
- Identify students below a configurable attendance threshold.
- Compare academic performance across subjects.
- Measure the statistical relationship between attendance and marks.
- Provide interactive visualizations and downloadable reports.
- Validate uploaded datasets and report data-quality issues.

## Features

### 1. Overview Dashboard
Displays key performance indicators, including student count, average attendance, average marks, and attendance-performance correlation.

### 2. Attendance Analysis
Examines attendance distributions, attendance categories, and students below the selected threshold.

### 3. Academic Performance
Displays marks distributions, subject-wise comparisons, top performers, and students who may need academic support.

### 4. Correlation Analysis
Uses Pearson and Spearman correlation to analyse the relationship between attendance and academic performance.

**Note:** Correlation does not establish causation.

### 5. Student Explorer
Supports student-level exploration through available search and filtering features.

### 6. Data Management
Supports CSV and Excel uploads, data validation, cleaning, and reporting of data-quality issues.

### 7. About the Project
Provides project information, objectives, and technology details.

## Technology Stack

- **Python** — core programming language
- **Pandas** — data manipulation and analysis
- **NumPy** — numerical computation
- **Streamlit** — interactive dashboard
- **Plotly** — interactive charts
- **Pytest** — automated testing

## Project Structure

```text
student_attendance/
├── app.py
├── requirements.txt
├── README.md
├── data/
│   ├── sample_students.csv
│   └── sample_subject_marks.csv
├── src/
│   ├── data_generator.py
│   ├── data_loader.py
│   ├── data_cleaning.py
│   ├── analytics.py
│   ├── correlation.py
│   ├── insights.py
│   └── visualizations.py
├── tests/
├── docs/
│   ├── PROJECT_REPORT.md
│   ├── USER_GUIDE.md
│   └── DEMO_SCRIPT.md
└── .gitignore
```

## Installation and Setup

### Prerequisites

- Python installed on your system
- Git, if you want to clone the repository

### 1. Clone the repository

```bash
git clone https://github.com/yashshindeaiml/student-attendance-analytics.git
cd student-attendance-analytics
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the environment

**Windows PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 5. Run the dashboard

```bash
python -m streamlit run app.py
```

Open the local URL displayed in the terminal, usually `http://localhost:8501`.

## Running Automated Tests

Run the test suite from the project directory:

```bash
python -m pytest -v
```

## Dataset Information

The project includes synthetic sample data for demonstration and testing.

The sample datasets are not actual institutional student records. Results from synthetic data should not be interpreted as findings about a real college or student population.

## Limitations

- Results depend on the quality and completeness of the uploaded data.
- Correlation analysis alone cannot establish cause and effect.
- Findings from synthetic data may not generalize to real students.
- The project does not replace professional academic assessment or institutional decision-making.

## Future Enhancements

- Integration with an authorized institutional database.
- Additional statistical models and analysis.
- More configurable reports and visualizations.
- Expanded data-quality monitoring.

## Author

Developed as an academic project focused on student attendance and academic performance analytics.