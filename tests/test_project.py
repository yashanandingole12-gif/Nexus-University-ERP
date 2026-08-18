import pandas as pd

from src.analytics import portfolio_metrics
from src.data_processing import department_summary, load_student_data
from src.model import train_and_evaluate


def sample_data():
    return pd.DataFrame({
        "StudentCode": [f"STU-{number:04d}" for number in range(1, 11)],
        "Department": ["CS", "CS", "EE", "EE", "CS", "EE", "CS", "EE", "CS", "EE"],
        "Year": [1, 2, 1, 2, 3, 3, 4, 4, 1, 2],
        "Semester": [1, 3, 1, 3, 5, 5, 7, 7, 2, 4],
        "CGPA": [7.0, 8.0, 6.0, 9.0, 7.5, 6.5, 8.5, 7.0, 7.2, 8.1],
        "Attendance": ["70%", "80%", "60%", "90%", "75%", "85%", "95%", "65%", "78%", "88%"],
        "Club": ["A"] * 10, "Hosteller": ["Yes"] * 10,
    })


def test_load_and_summarise_data(tmp_path):
    path = tmp_path / "students.csv"
    sample_data().to_csv(path, index=False)
    data = load_student_data(path)
    assert data["Attendance"].dtype.kind in "fi"
    assert department_summary(data)["students"].sum() == 10


def test_portfolio_metrics_counts_at_risk_students():
    data = sample_data()
    data["Attendance"] = data["Attendance"].str.rstrip("%").astype(float)
    assert portfolio_metrics(data)["at_risk_students"] == 3


def test_model_trains_and_returns_metrics():
    data = sample_data()
    data["Attendance"] = data["Attendance"].str.rstrip("%").astype(float)
    model, metrics = train_and_evaluate(data)
    assert hasattr(model, "predict")
    assert set(metrics) == {"mae", "r2"}
