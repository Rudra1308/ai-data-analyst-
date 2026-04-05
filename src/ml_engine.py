"""
ML Engine Module
Handles machine learning model training, evaluation, and prediction
using Scikit-learn.
"""
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    mean_squared_error, mean_absolute_error, r2_score,
)
from src.visualization import apply_theme


def detect_task_type(df: pd.DataFrame, target_col: str) -> str:
    """Auto-detect whether the task is classification or regression."""
    target = df[target_col]
    if target.dtype == "object" or target.dtype.name == "category":
        return "classification"
    if target.nunique() <= 10 and target.nunique() / len(target) < 0.05:
        return "classification"
    return "regression"


def prepare_data(df: pd.DataFrame, target_col: str, feature_cols: list = None):
    """
    Prepare data for ML training.
    - Encodes categorical features
    - Handles missing values
    - Splits into train/test sets
    """
    df_ml = df.copy()

    if feature_cols is None:
        feature_cols = [c for c in df_ml.columns if c != target_col]

    # Drop rows with missing target
    df_ml = df_ml.dropna(subset=[target_col])

    # Encode categorical features
    encoders = {}
    for col in feature_cols:
        if df_ml[col].dtype == "object" or df_ml[col].dtype.name == "category":
            le = LabelEncoder()
            df_ml[col] = le.fit_transform(df_ml[col].astype(str))
            encoders[col] = le

    # Fill numeric NaNs with median
    for col in feature_cols:
        if df_ml[col].isnull().any():
            df_ml[col] = df_ml[col].fillna(df_ml[col].median())

    # Encode target if categorical
    target_encoder = None
    if df_ml[target_col].dtype == "object" or df_ml[target_col].dtype.name == "category":
        target_encoder = LabelEncoder()
        df_ml[target_col] = target_encoder.fit_transform(df_ml[target_col].astype(str))

    X = df_ml[feature_cols].values
    y = df_ml[target_col].values

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    return {
        "X_train": X_train, "X_test": X_test,
        "y_train": y_train, "y_test": y_test,
        "feature_names": feature_cols,
        "encoders": encoders,
        "target_encoder": target_encoder,
    }


def train_model(data: dict, task_type: str) -> dict:
    """
    Train a model based on the task type.

    Returns:
        dict with model, metrics, and evaluation results
    """
    X_train, X_test = data["X_train"], data["X_test"]
    y_train, y_test = data["y_train"], data["y_test"]

    if task_type == "classification":
        model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        metrics_dict = {
            "Accuracy": f"{accuracy_score(y_test, y_pred):.4f}",
            "Report": classification_report(y_test, y_pred, output_dict=True),
        }

        # Confusion matrix chart
        cm = confusion_matrix(y_test, y_pred)
        labels = data["target_encoder"].classes_ if data["target_encoder"] else [str(i) for i in range(cm.shape[0])]
        fig_cm = go.Figure(data=go.Heatmap(
            z=cm, x=labels, y=labels,
            colorscale="Purples",
            text=cm, texttemplate="%{text}",
        ))
        fig_cm.update_layout(
            title="Confusion Matrix",
            xaxis_title="Predicted", yaxis_title="Actual",
        )
        metrics_dict["confusion_matrix_fig"] = apply_theme(fig_cm)

    else:  # regression
        model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        metrics_dict = {
            "R² Score": f"{r2_score(y_test, y_pred):.4f}",
            "MAE": f"{mean_absolute_error(y_test, y_pred):.4f}",
            "RMSE": f"{np.sqrt(mean_squared_error(y_test, y_pred)):.4f}",
        }

        # Actual vs Predicted chart
        fig_avp = px.scatter(
            x=y_test, y=y_pred,
            labels={"x": "Actual", "y": "Predicted"},
            title="Actual vs Predicted",
        )
        fig_avp.add_trace(go.Scatter(
            x=[y_test.min(), y_test.max()],
            y=[y_test.min(), y_test.max()],
            mode="lines", name="Perfect Prediction",
            line=dict(color="#FF6584", dash="dash"),
        ))
        metrics_dict["actual_vs_predicted_fig"] = apply_theme(fig_avp)

    # Feature Importance
    importances = model.feature_importances_
    feat_imp_df = pd.DataFrame({
        "Feature": data["feature_names"],
        "Importance": importances,
    }).sort_values("Importance", ascending=True)

    fig_imp = px.bar(
        feat_imp_df, x="Importance", y="Feature",
        orientation="h", title="Feature Importance",
    )
    metrics_dict["feature_importance_fig"] = apply_theme(fig_imp)

    return {
        "model": model,
        "task_type": task_type,
        "metrics": metrics_dict,
        "data": data,
    }
