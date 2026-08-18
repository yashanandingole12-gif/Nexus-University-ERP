"""Streamlit dashboard for de-identified student performance analytics."""

from pathlib import Path
import pandas as pd
import streamlit as st

from src.analytics import attendance_cgpa_correlation, portfolio_metrics
from src.data_processing import department_summary, load_student_data
from src.model import FEATURES, train_and_evaluate

DATA_PATH = Path(__file__).parent / "data" / "student_performance_sample.csv"
st.set_page_config(page_title="Student Performance Analytics", layout="wide")

@st.cache_data
def get_data() -> pd.DataFrame:
    return load_student_data(DATA_PATH)

@st.cache_resource
def get_model(data: pd.DataFrame):
    return train_and_evaluate(data)

data = get_data()
model, model_metrics = get_model(data)
st.title("Student Performance Analytics")
st.caption("A de-identified portfolio dashboard for academic planning. This is not an ERP system of record.")
selected = st.sidebar.multiselect("Department", sorted(data["Department"].unique()), default=sorted(data["Department"].unique()))
filtered = data[data["Department"].isin(selected)]
metrics = portfolio_metrics(filtered)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Students", f"{metrics['students']:,}")
col2.metric("Average CGPA", f"{metrics['average_cgpa']:.2f}")
col3.metric("Average attendance", f"{metrics['average_attendance']:.1f}%")
col4.metric("Students requiring review", f"{metrics['at_risk_students']:,}")
left, right = st.columns(2)
with left:
    st.subheader("Performance by department")
    st.bar_chart(department_summary(filtered).set_index("Department")[["average_cgpa"]])
with right:
    st.subheader("Attendance and CGPA")
    st.scatter_chart(filtered, x="Attendance", y="CGPA", color="Department")
    st.caption(f"Correlation: {attendance_cgpa_correlation(filtered):.2f}")
st.subheader("CGPA baseline estimate")
st.caption(f"Holdout MAE: {model_metrics['mae']:.2f}; R²: {model_metrics['r2']:.2f}. Use this exploratory baseline for planning, not high-stakes individual decisions.")
with st.form("prediction"):
    department = st.selectbox("Department", sorted(data["Department"].unique()))
    year = st.selectbox("Year", [1, 2, 3, 4])
    semester = st.selectbox("Semester", list(range(1, 9)))
    attendance = st.slider("Attendance (%)", min_value=0, max_value=100, value=80)
    submitted = st.form_submit_button("Estimate CGPA")
if submitted:
    candidate = pd.DataFrame([[department, year, semester, attendance]], columns=FEATURES)
    st.success(f"Estimated CGPA: {model.predict(candidate)[0]:.2f}")
