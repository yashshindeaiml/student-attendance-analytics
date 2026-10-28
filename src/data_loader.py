"""Dataset loading and format detection module.

Handles loading of bundled sample datasets and user-uploaded CSV / Excel files.
"""

from io import BytesIO, StringIO
from pathlib import Path
from typing import Optional, Tuple, Union
import pandas as pd


# Default bundled data paths
DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DEFAULT_STUDENT_DATA_PATH = DEFAULT_DATA_DIR / "sample_students.csv"
DEFAULT_SUBJECT_DATA_PATH = DEFAULT_DATA_DIR / "sample_subject_marks.csv"

# Minimum required columns for canonical student dataset
REQUIRED_STUDENT_COLUMNS = {"student_id", "attendance_percentage", "average_marks"}

# Minimum required columns for subject-level dataset
REQUIRED_SUBJECT_COLUMNS = {
    "student_id",
    "subject",
    "marks_obtained",
    "maximum_marks",
    "attendance_percentage",
}


class DataLoaderError(Exception):
    """Custom exception raised for dataset loading failures."""

    pass


def normalize_column_name(col: str) -> str:
    """Normalize column header: lowercased, stripped, spaces/hyphens to underscores."""
    if not isinstance(col, str):
        col = str(col)
    return col.strip().lower().replace(" ", "_").replace("-", "_").replace(".", "_")


def normalize_dataframe_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Return a DataFrame with normalized column names."""
    df = df.copy()
    df.columns = [normalize_column_name(c) for c in df.columns]
    return df


def detect_dataset_type(df: pd.DataFrame) -> str:
    """Detect whether a dataframe conforms to student-level or subject-level schema.

    Returns:
        str: 'student_level', 'subject_level', or 'unknown'
    """
    normalized_cols = set(normalize_column_name(c) for c in df.columns)

    if REQUIRED_SUBJECT_COLUMNS.issubset(normalized_cols):
        return "subject_level"
    if REQUIRED_STUDENT_COLUMNS.issubset(normalized_cols):
        return "student_level"
    return "unknown"


def load_file(
    source: Union[str, Path, BytesIO, StringIO],
    filename: Optional[str] = None,
) -> pd.DataFrame:
    """Load a dataset from a filepath or file-like buffer (CSV or Excel).

    Args:
        source: File path or file-like object / buffer.
        filename: Optional file name used to determine parser if source is buffer.

    Returns:
        pd.DataFrame: Loaded DataFrame with normalized column names.

    Raises:
        DataLoaderError: If file is empty, unreadable, or of unsupported format.
    """
    try:
        # Determine file extension if available
        ext = ""
        if isinstance(source, (str, Path)):
            path = Path(source)
            if not path.exists():
                raise DataLoaderError(f"Dataset file not found at: {path}")
            ext = path.suffix.lower()
        elif filename:
            ext = Path(filename).suffix.lower()

        if ext in [".xlsx", ".xls"]:
            df = pd.read_excel(source)
        else:
            # Default to CSV parser
            df = pd.read_csv(source)

        if df.empty:
            raise DataLoaderError("The selected dataset is empty (0 rows).")

        df = normalize_dataframe_columns(df)
        return df

    except pd.errors.EmptyDataError:
        raise DataLoaderError("The uploaded file contains no data or is empty.")
    except pd.errors.ParserError as e:
        raise DataLoaderError(f"Could not parse CSV file. Error details: {str(e)}")
    except Exception as e:
        if isinstance(e, DataLoaderError):
            raise
        raise DataLoaderError(f"Failed to load dataset: {str(e)}")


def load_bundled_student_data(data_path: Optional[Path] = None) -> pd.DataFrame:
    """Load the bundled demonstration student dataset.

    Args:
        data_path: Optional custom path. Defaults to `data/sample_students.csv`.

    Returns:
        pd.DataFrame: Cleaned student dataset.
    """
    path = data_path or DEFAULT_STUDENT_DATA_PATH
    if not path.exists():
        # Fallback: dynamically generate if missing
        from src.data_generator import generate_and_save_all

        generate_and_save_all(data_dir=path.parent)

    return load_file(path)


def load_bundled_subject_data(data_path: Optional[Path] = None) -> pd.DataFrame:
    """Load the bundled demonstration subject marks dataset.

    Args:
        data_path: Optional custom path. Defaults to `data/sample_subject_marks.csv`.

    Returns:
        pd.DataFrame: Cleaned subject marks dataset.
    """
    path = data_path or DEFAULT_SUBJECT_DATA_PATH
    if not path.exists():
        from src.data_generator import generate_and_save_all

        generate_and_save_all(data_dir=path.parent)

    return load_file(path)
