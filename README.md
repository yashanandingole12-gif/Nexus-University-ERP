# Student Performance Analytics

A compact, privacy-aware data analytics portfolio project. It turns de-identified student performance records into department-level indicators and includes a simple, reproducible CGPA baseline model in a Streamlit dashboard.

## What this project demonstrates

- Data quality checks and standardisation for CGPA and attendance
- Department-level performance analysis and review indicators
- A tested baseline model using department, year, semester, and attendance
- A deployable Streamlit dashboard with filtering and an interactive estimate form
- Responsible analytics: the public dataset contains no names, contact details, addresses, or family information

## Project structure

```text
student-performance-analytics/
├── app.py                    # Streamlit dashboard
├── data/
│   └── student_performance_sample.csv
├── src/                      # Processing, metrics, and model modules
├── tests/                    # Automated tests
└── archive/                  # Original scripts and visual assets, retained locally for reference
```

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pytest
streamlit run app.py
```

## Model note

The model is a baseline estimator, not a production decision system. The dashboard reports holdout MAE and R² so its limits are visible. Do not use it for admissions, scholarships, discipline, or other high-stakes decisions without a fuller validation and governance process.

## Data note

The original export and department-level source exports were moved to `data/private/` and are ignored by Git because they contain unnecessary personal fields. The versioned sample retains only fields needed for the analysis.

## Deploy

Push this folder to GitHub, then create a Streamlit Community Cloud app with `app.py` as the entry point. Install dependencies from `requirements.txt`.
