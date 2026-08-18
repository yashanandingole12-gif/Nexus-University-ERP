"""Streamlit dashboard for de-identified student performance analytics."""

from pathlib import Path

import pandas as pd
import streamlit as st

from src.analytics import club_summary, portfolio_metrics, top_performer
from src.data_processing import department_summary, load_student_data
from src.model import FEATURES, train_and_evaluate


DATA_PATH = Path(__file__).parent / "data" / "student_performance_sample.csv"
st.set_page_config(page_title="Nexus University ERP", layout="wide")


@st.cache_data
def get_data() -> pd.DataFrame:
    return load_student_data(DATA_PATH)


@st.cache_resource
def get_model(data: pd.DataFrame):
    return train_and_evaluate(data)


data = get_data()
model, model_metrics = get_model(data)

st.title("Nexus University ERP")
st.caption("Student performance, club participation, and academic planning dashboard")

selected_departments = st.sidebar.multiselect(
    "Filter departments",
    sorted(data["Department"].unique()),
    default=sorted(data["Department"].unique()),
)
filtered = data[data["Department"].isin(selected_departments)]
if filtered.empty:
    st.warning("Select at least one department to view dashboard results.")
    st.stop()

overview_tab, student_tab, clubs_tab, model_tab = st.tabs(
    ["Overview", "Student record", "Clubs", "CGPA estimate"]
)

with overview_tab:
    metrics = portfolio_metrics(filtered)
    topper = top_performer(filtered)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Students", f"{metrics['students']:,}")
    col2.metric("Average CGPA", f"{metrics['average_cgpa']:.2f}")
    col3.metric("Average attendance", f"{metrics['average_attendance']:.1f}%")
    col4.metric("Students requiring review", f"{metrics['at_risk_students']:,}")

    st.subheader("Top performer")
    topper_columns = st.columns(4)
    topper_columns[0].metric("Student code", topper["StudentCode"])
    topper_columns[1].metric("CGPA", f"{topper['CGPA']:.2f}")
    topper_columns[2].metric("Department", topper["Department"])
    topper_columns[3].metric("Attendance", f"{topper['Attendance']:.0f}%")

    left, right = st.columns(2)
    with left:
        st.subheader("Performance by department")
        st.bar_chart(department_summary(filtered).set_index("Department")[["average_cgpa"]])
    with right:
        st.subheader("Attendance and CGPA")
        st.scatter_chart(filtered, x="Attendance", y="CGPA", color="Department")

with student_tab:
    st.subheader("Student record lookup")
    student_code = st.selectbox("Student code", sorted(filtered["StudentCode"].unique()))
    student = filtered.loc[filtered["StudentCode"] == student_code].iloc[0]
    left, middle, right = st.columns(3)
    left.write(f"**Department:** {student['Department']}")
    left.write(f"**Year / semester:** {student['Year']} / {student['Semester']}")
    middle.metric("CGPA", f"{student['CGPA']:.2f}")
    middle.metric("Attendance", f"{student['Attendance']:.0f}%")
    right.write(f"**Club:** {student['Club']}")
    right.write(f"**Hosteller:** {student['Hosteller']}")
    if student["CGPA"] < 6.0 or student["Attendance"] < 75:
        st.warning("This record meets the academic-review rule: CGPA below 6.0 or attendance below 75%.")
    else:
        st.success("This record does not meet the academic-review rule.")

with clubs_tab:
    st.subheader("Club participation")
    clubs = club_summary(filtered)
    left, right = st.columns(2)
    with left:
        st.bar_chart(clubs.set_index("Club")[["members"]])
    with right:
        st.dataframe(clubs.style.format({"average_cgpa": "{:.2f}"}), width="stretch", hide_index=True)
    selected_club = st.selectbox("View club members", clubs["Club"].tolist())
    members = filtered.loc[filtered["Club"] == selected_club, ["StudentCode", "Department", "Year", "CGPA", "Attendance"]]
    st.dataframe(members.sort_values("CGPA", ascending=False), width="stretch", hide_index=True)

with model_tab:
    st.subheader("CGPA baseline estimate")
    st.caption(
        f"Holdout MAE: {model_metrics['mae']:.2f}; R²: {model_metrics['r2']:.2f}. "
        "Use this exploratory baseline for planning, not high-stakes individual decisions."
    )
    with st.form("prediction"):
        department = st.selectbox("Department", sorted(data["Department"].unique()))
        year = st.selectbox("Year", [1, 2, 3, 4])
        semester = st.selectbox("Semester", list(range(1, 9)))
        attendance = st.slider("Attendance (%)", min_value=0, max_value=100, value=80)
        submitted = st.form_submit_button("Estimate CGPA")
    if submitted:
        candidate = pd.DataFrame([[department, year, semester, attendance]], columns=FEATURES)
        st.success(f"Estimated CGPA: {model.predict(candidate)[0]:.2f}")
