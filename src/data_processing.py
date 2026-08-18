"""Data loading and quality checks for the student analytics dataset."""

from pathlib import Path
import pandas as pd

REQUIRED_COLUMNS = {"StudentID", "RollNumber", "Name", "Department", "Year", "Semester", "CGPA", "Attendance", "Club", "Hosteller"}


def load_student_data(file_path: str | Path) -> pd.DataFrame:
    """Load and standardise the public, de-identified student dataset."""
    data = pd.read_csv(file_path)
    missing = REQUIRED_COLUMNS.difference(data.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")
    data = data.copy()
    data["CGPA"] = pd.to_numeric(data["CGPA"], errors="coerce")
    data["Attendance"] = pd.to_numeric(data["Attendance"].astype(str).str.replace("%", "", regex=False), errors="coerce")
    data["Year"] = pd.to_numeric(data["Year"], errors="coerce")
    data["Semester"] = pd.to_numeric(data["Semester"], errors="coerce")
    data["Department"] = data["Department"].astype(str).str.strip().str.upper()
    return data.dropna(subset=["CGPA", "Attendance", "Year", "Semester", "Department"])


def department_summary(data: pd.DataFrame) -> pd.DataFrame:
    """Return portfolio-ready performance measures by department."""
    return (data.groupby("Department", as_index=False)
        .agg(students=("CGPA", "size"), average_cgpa=("CGPA", "mean"), average_attendance=("Attendance", "mean"))
        .sort_values("average_cgpa", ascending=False))
