"""
Data Loader Module
Handles CSV file upload, parsing, and DataFrame management.
"""
import pandas as pd
import streamlit as st


def load_csv(uploaded_file) -> pd.DataFrame:
    """
    Load a CSV file into a Pandas DataFrame.
    Handles encoding issues and common CSV quirks.
    """
    try:
        df = pd.read_csv(uploaded_file)

        # Clean column names — strip whitespace
        df.columns = df.columns.str.strip()

        # Try to parse date columns automatically
        for col in df.columns:
            if df[col].dtype == "object":
                try:
                    parsed = pd.to_datetime(df[col], infer_datetime_format=True)
                    # Only convert if most values parsed successfully
                    if parsed.notna().sum() > len(df) * 0.5:
                        df[col] = parsed
                except (ValueError, TypeError):
                    pass

        return df

    except UnicodeDecodeError:
        # Retry with latin-1 encoding
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, encoding="latin-1")
        df.columns = df.columns.str.strip()
        return df

    except Exception as e:
        st.error(f"Error loading CSV: {str(e)}")
        return None


def get_data_summary(df: pd.DataFrame) -> dict:
    """
    Generate a comprehensive summary of the dataset.
    Returns a dictionary with key statistics.
    """
    summary = {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "column_names": df.columns.tolist(),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "null_counts": df.isnull().sum().to_dict(),
        "null_percentage": (df.isnull().sum() / len(df) * 100).round(2).to_dict(),
        "numeric_columns": df.select_dtypes(include="number").columns.tolist(),
        "categorical_columns": df.select_dtypes(include=["object", "category"]).columns.tolist(),
        "datetime_columns": df.select_dtypes(include="datetime").columns.tolist(),
        "memory_usage": f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB",
        "duplicates": int(df.duplicated().sum()),
    }

    # Numeric stats
    if summary["numeric_columns"]:
        summary["numeric_stats"] = df[summary["numeric_columns"]].describe().round(2).to_dict()

    # Categorical stats
    if summary["categorical_columns"]:
        cat_stats = {}
        for col in summary["categorical_columns"]:
            cat_stats[col] = {
                "unique": int(df[col].nunique()),
                "top_values": df[col].value_counts().head(5).to_dict(),
            }
        summary["categorical_stats"] = cat_stats

    return summary


def get_sample_rows(df: pd.DataFrame, n: int = 5) -> pd.DataFrame:
    """Return the first N rows of the DataFrame."""
    return df.head(n)
