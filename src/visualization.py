"""
Visualization Module
Generates automatic exploratory data analysis (EDA) charts using Plotly.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# Consistent dark theme for all charts
CHART_THEME = {
    "template": "plotly_dark",
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font_color": "#E0E0E0",
    "colorway": [
        "#6C63FF", "#FF6584", "#43E97B", "#F8D800",
        "#38F9D7", "#FA709A", "#A18CD1", "#FBC2EB",
    ],
}


def apply_theme(fig):
    """Apply the consistent dark theme to a Plotly figure."""
    fig.update_layout(
        template=CHART_THEME["template"],
        paper_bgcolor=CHART_THEME["paper_bgcolor"],
        plot_bgcolor=CHART_THEME["plot_bgcolor"],
        font=dict(color=CHART_THEME["font_color"], family="Inter, sans-serif"),
        colorway=CHART_THEME["colorway"],
        margin=dict(l=40, r=40, t=50, b=40),
        legend=dict(
            bgcolor="rgba(0,0,0,0.3)",
            bordercolor="rgba(255,255,255,0.1)",
            borderwidth=1,
        ),
    )
    return fig


def quick_eda(df: pd.DataFrame) -> list:
    """
    Generate a set of automatic EDA charts for the dataset.

    Returns:
        List of tuples: (title, plotly_figure)
    """
    charts = []
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    # 1. Data types distribution
    dtype_counts = df.dtypes.astype(str).value_counts()
    fig_dtypes = px.pie(
        values=dtype_counts.values,
        names=dtype_counts.index,
        title="Column Data Types",
        hole=0.4,
    )
    charts.append(("Data Types", apply_theme(fig_dtypes)))

    # 2. Missing values
    null_counts = df.isnull().sum()
    if null_counts.sum() > 0:
        null_data = null_counts[null_counts > 0].sort_values(ascending=True)
        fig_nulls = px.bar(
            x=null_data.values,
            y=null_data.index,
            orientation="h",
            title="Missing Values by Column",
            labels={"x": "Count", "y": "Column"},
        )
        charts.append(("Missing Values", apply_theme(fig_nulls)))

    # 3. Numeric distributions (histograms for first 4 numeric cols)
    for col in numeric_cols[:4]:
        fig_hist = px.histogram(
            df, x=col,
            title=f"Distribution of {col}",
            nbins=30,
            marginal="box",
        )
        charts.append((f"Distribution: {col}", apply_theme(fig_hist)))

    # 4. Categorical value counts (top 10 for first 3 categorical cols)
    for col in categorical_cols[:3]:
        top_vals = df[col].value_counts().head(10)
        fig_bar = px.bar(
            x=top_vals.index.astype(str),
            y=top_vals.values,
            title=f"Top Values: {col}",
            labels={"x": col, "y": "Count"},
        )
        charts.append((f"Top Values: {col}", apply_theme(fig_bar)))

    # 5. Correlation heatmap (if enough numeric columns)
    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr().round(2)
        fig_corr = go.Figure(data=go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.columns,
            colorscale="RdBu_r",
            zmin=-1, zmax=1,
            text=corr.values,
            texttemplate="%{text}",
            textfont={"size": 10},
        ))
        fig_corr.update_layout(title="Correlation Heatmap")
        charts.append(("Correlation", apply_theme(fig_corr)))

    return charts
