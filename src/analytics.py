"""Reusable business metrics for the dashboard and notebook work."""

import pandas as pd


def portfolio_metrics(data: pd.DataFrame) -> dict[str, float | int]:
    return {
        "students": int(len(data)),
        "average_cgpa": float(data["CGPA"].mean()),
        "average_attendance": float(data["Attendance"].mean()),
        "at_risk_students": int(((data["CGPA"] < 6.0) | (data["Attendance"] < 75)).sum()),
    }


def attendance_cgpa_correlation(data: pd.DataFrame) -> float:
    return float(data[["Attendance", "CGPA"]].corr().iloc[0, 1])
