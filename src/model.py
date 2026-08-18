"""Small, reproducible CGPA baseline model used by the dashboard."""

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

FEATURES = ["Department", "Year", "Semester", "Attendance"]
TARGET = "CGPA"


def build_model() -> Pipeline:
    preprocessor = ColumnTransformer([("department", OneHotEncoder(handle_unknown="ignore"), ["Department"])], remainder="passthrough")
    return Pipeline([("preprocessor", preprocessor), ("regressor", RandomForestRegressor(n_estimators=100, random_state=42))])


def train_and_evaluate(data: pd.DataFrame) -> tuple[Pipeline, dict[str, float]]:
    """Train a baseline estimator and return transparent holdout metrics."""
    X_train, X_test, y_train, y_test = train_test_split(data[FEATURES], data[TARGET], test_size=0.2, random_state=42)
    model = build_model()
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    return model, {"mae": float(mean_absolute_error(y_test, predictions)), "r2": float(r2_score(y_test, predictions))}
