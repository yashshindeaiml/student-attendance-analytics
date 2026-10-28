"""Synthetic Dataset Generator for Student Performance Analytics.

Generates reproducible synthetic datasets for:
1. Student-level attendance and performance (`sample_students.csv`).
2. Subject-level detailed marks and attendance (`sample_subject_marks.csv`).

All student IDs and performance figures are purely synthetic and generated
using fixed pseudorandom seeds for scientific reproducibility.
"""

from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd


# Default department list
DEPARTMENTS = [
    "Computer Science",
    "Information Technology",
    "Electronics & Comm.",
    "Mechanical Eng.",
    "Civil Eng.",
]

# Semesters
SEMESTERS = ["Semester 3", "Semester 4", "Semester 5", "Semester 6"]

# Class sections
CLASSES = ["Section A", "Section B", "Section C"]

# Curriculum subjects mapped by department
DEPARTMENT_SUBJECTS: Dict[str, List[str]] = {
    "Computer Science": [
        "Data Structures",
        "Algorithms",
        "Database Systems",
        "Operating Systems",
        "Computer Networks",
    ],
    "Information Technology": [
        "Web Technologies",
        "Cloud Computing",
        "Software Engineering",
        "Database Systems",
        "Information Security",
    ],
    "Electronics & Comm.": [
        "Signals & Systems",
        "Digital Electronics",
        "Microprocessors",
        "Communication Systems",
        "VLSI Design",
    ],
    "Mechanical Eng.": [
        "Thermodynamics",
        "Fluid Mechanics",
        "Machine Design",
        "Heat Transfer",
        "Manufacturing Processes",
    ],
    "Civil Eng.": [
        "Structural Analysis",
        "Fluid Mechanics",
        "Geotechnical Eng.",
        "Surveying",
        "Concrete Technology",
    ],
}


def generate_student_dataset(
    n_students: int = 150,
    random_seed: int = 42,
) -> pd.DataFrame:
    """Generate reproducible student-level synthetic dataset.

    Args:
        n_students: Number of fictional students to generate (default: 150).
        random_seed: Seed for numpy pseudorandom number generator.

    Returns:
        pd.DataFrame: Student-level dataframe with canonical columns:
            - student_id
            - attendance_percentage
            - average_marks
            - department
            - semester
            - class
    """
    rng = np.random.default_rng(random_seed)

    student_ids = [f"STD-{1000 + i + 1}" for i in range(n_students)]
    departments = rng.choice(DEPARTMENTS, size=n_students)
    semesters = rng.choice(SEMESTERS, size=n_students)
    classes = rng.choice(CLASSES, size=n_students)

    # Attendance: realistic beta-distribution-shaped variation centered around 76%
    # scaled and shifted with realistic spread, clipped strictly between 0 and 100
    raw_attendance = rng.beta(a=6.0, b=2.2, size=n_students) * 100.0
    # Add minor noise for edge variation
    attendance_noise = rng.normal(loc=0.0, scale=3.5, size=n_students)
    attendance = np.clip(raw_attendance + attendance_noise, 30.0, 99.5)
    attendance = np.round(attendance, 1)

    # Academic Marks: natural positive association with attendance plus individual aptitude
    # and realistic noise (does NOT force correlation to a fixed constant)
    base_aptitude = rng.normal(loc=58.0, scale=12.0, size=n_students)
    # attendance effect (modest slope, e.g. 0.32 point per % attendance)
    attendance_effect = 0.32 * (attendance - 75.0)
    # residual noise for natural variation (e.g. outliers who study independently or struggle)
    individual_variance = rng.normal(loc=0.0, scale=9.5, size=n_students)

    raw_marks = base_aptitude + attendance_effect + individual_variance
    marks = np.clip(raw_marks, 25.0, 98.5)
    marks = np.round(marks, 1)

    df = pd.DataFrame(
        {
            "student_id": student_ids,
            "attendance_percentage": attendance,
            "average_marks": marks,
            "department": departments,
            "semester": semesters,
            "class": classes,
        }
    )

    return df


def generate_subject_marks_dataset(
    student_df: pd.DataFrame = None,
    n_students: int = 150,
    random_seed: int = 42,
) -> pd.DataFrame:
    """Generate reproducible subject-level synthetic dataset.

    Args:
        student_df: Existing student dataframe to base subjects on.
            If None, `generate_student_dataset` will be called with `random_seed`.
        n_students: Number of students if student_df is None.
        random_seed: Random seed for reproducibility.

    Returns:
        pd.DataFrame: Subject-level dataframe containing:
            - student_id
            - subject
            - marks_obtained
            - maximum_marks
            - attendance_percentage
            - department
            - semester
    """
    if student_df is None:
        student_df = generate_student_dataset(n_students=n_students, random_seed=random_seed)

    rng = np.random.default_rng(random_seed + 101)

    records = []
    maximum_marks = 100.0

    for _, row in student_df.iterrows():
        sid = row["student_id"]
        dept = row["department"]
        sem = row["semester"]
        overall_marks = float(row["average_marks"])
        overall_att = float(row["attendance_percentage"])

        subjects = DEPARTMENT_SUBJECTS.get(dept, DEPARTMENT_SUBJECTS["Computer Science"])

        for subject in subjects:
            # Subject specific attendance varies around overall attendance
            sub_att_noise = rng.normal(loc=0.0, scale=4.0)
            sub_att = np.clip(overall_att + sub_att_noise, 20.0, 100.0)
            sub_att = round(float(sub_att), 1)

            # Subject specific marks vary around overall marks
            sub_marks_noise = rng.normal(loc=0.0, scale=6.5)
            sub_marks = np.clip(overall_marks + sub_marks_noise, 15.0, 100.0)
            sub_marks = round(float(sub_marks), 1)

            records.append(
                {
                    "student_id": sid,
                    "subject": subject,
                    "marks_obtained": sub_marks,
                    "maximum_marks": maximum_marks,
                    "attendance_percentage": sub_att,
                    "department": dept,
                    "semester": sem,
                }
            )

    return pd.DataFrame(records)


def generate_and_save_all(
    data_dir: Path = None,
    n_students: int = 150,
    random_seed: int = 42,
) -> Tuple[Path, Path]:
    """Generate both synthetic datasets and save them to the data directory.

    Args:
        data_dir: Destination directory. Defaults to 'data/' in current workspace.
        n_students: Number of students (default 150).
        random_seed: Fixed seed for reproducibility.

    Returns:
        Tuple[Path, Path]: Paths to (sample_students.csv, sample_subject_marks.csv).
    """
    if data_dir is None:
        data_dir = Path("data")

    data_dir.mkdir(parents=True, exist_ok=True)

    student_df = generate_student_dataset(n_students=n_students, random_seed=random_seed)
    students_path = data_dir / "sample_students.csv"
    student_df.to_csv(students_path, index=False)

    subject_df = generate_subject_marks_dataset(student_df=student_df, random_seed=random_seed)
    subject_path = data_dir / "sample_subject_marks.csv"
    subject_df.to_csv(subject_path, index=False)

    return students_path, subject_path


if __name__ == "__main__":
    s_path, sub_path = generate_and_save_all()
    print(f"Generated synthetic student dataset: {s_path}")
    print(f"Generated synthetic subject dataset: {sub_path}")
