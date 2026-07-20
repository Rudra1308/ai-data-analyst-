import os
import uuid
import polars as pl
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple, List
from fastapi import UploadFile
from backend.app.core.config import settings

# Support Excel, Parquet, Feather, CSV, JSON
SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".parquet", ".feather", ".ipc", ".json"}


def save_uploaded_file(upload_file: UploadFile, project_id: str) -> str:
    """Save upload stream to disk under a project-specific path."""
    upload_file.file.seek(0)
    ext = os.path.splitext(upload_file.filename)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file format: {ext}. Allowed formats: {', '.join(SUPPORTED_EXTENSIONS)}")

    project_dir = os.path.join(settings.UPLOAD_DIR, project_id)
    os.makedirs(project_dir, exist_ok=True)

    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(project_dir, unique_filename)

    with open(file_path, "wb") as f:
        # Read in chunks for safety with large files
        while chunk := upload_file.file.read(1024 * 1024):
            f.write(chunk)

    return file_path


def load_dataset_as_polars(file_path: str) -> pl.DataFrame:
    """Load dataset into Polars DataFrame based on file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        # Handle common CSV parsing fallbacks
        try:
            return pl.read_csv(file_path, ignore_errors=True)
        except Exception:
            # Try parsing with pandas as fallback and convert to polars
            df_pd = pd.read_csv(file_path, encoding="latin-1")
            return pl.from_pandas(df_pd)
    elif ext == ".parquet":
        return pl.read_parquet(file_path)
    elif ext in (".feather", ".ipc"):
        return pl.read_ipc(file_path)
    elif ext == ".json":
        return pl.read_json(file_path)
    elif ext in (".xlsx", ".xls"):
        # Polars excel reading requires extra engines, fallback to pandas
        df_pd = pd.read_excel(file_path)
        return pl.from_pandas(df_pd)
    else:
        raise ValueError(f"Unsupported file format: {ext}")


def detect_outliers_iqr(col_data: List[float]) -> Dict[str, Any]:
    """Find outliers using Interquartile Range (IQR) method."""
    if len(col_data) < 4:
        return {"count": 0, "percentage": 0.0, "thresholds": None}

    q1, q3 = np.percentile(col_data, [25, 75])
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    outliers = [x for x in col_data if x < lower_bound or x > upper_bound]

    return {
        "count": len(outliers),
        "percentage": round(len(outliers) / len(col_data) * 100, 2),
        "thresholds": {"lower": float(lower_bound), "upper": float(upper_bound)}
    }


def suggest_clean_name(name: str) -> str:
    """Provide a database-friendly column renaming suggestion."""
    import re
    clean = name.strip().lower()
    # Replace any character that is not lowercase alphanumeric with underscore
    clean = re.sub(r"[^a-z0-9]", "_", clean)
    # Clean contiguous underscores
    while "__" in clean:
        clean = clean.replace("__", "_")
    clean = clean.strip("_")
    return clean if clean else f"col_{uuid.uuid4().hex[:4]}"



def profile_dataset(file_path: str) -> Tuple[Dict[str, Any], Dict[str, Any], int, int]:
    """
    Profile dataset using Polars for high performance.
    Returns: (schema_json, profile_json, row_count, col_count)
    """
    lf = load_dataset_as_polars(file_path)
    row_count = lf.height
    col_count = lf.width

    schema_json = {}
    profile_json = {
        "summary": {
            "rows": row_count,
            "columns": col_count,
            "duplicates": 0,
            "memory_bytes": 0,
        },
        "columns": {},
        "quality_report": {
            "overall_score": 100,
            "issues": []
        }
    }

    # Calculate duplicate count (needs full evaluation)
    profile_json["summary"]["duplicates"] = lf.height - lf.unique().height
    profile_json["summary"]["memory_bytes"] = lf.estimated_size()

    total_cells = row_count * col_count
    total_missing = 0

    for col in lf.columns:
        series = lf[col]
        dtype = str(series.dtype)
        schema_json[col] = dtype

        null_count = series.null_count()
        total_missing += null_count
        null_pct = round((null_count / row_count) * 100, 2) if row_count > 0 else 0.0

        col_profile = {
            "name": col,
            "suggested_name": suggest_clean_name(col),
            "dtype": dtype,
            "null_count": null_count,
            "null_percentage": null_pct,
            "unique_count": series.n_unique(),
            "type_group": "numeric" if series.dtype.is_numeric() else "temporal" if series.dtype.is_temporal() else "categorical"
        }

        # Check for column renaming suggestion if name differs
        if col_profile["suggested_name"] != col:
            profile_json["quality_report"]["issues"].append({
                "severity": "info",
                "column": col,
                "type": "renaming_suggestion",
                "message": f"Rename column '{col}' to '{col_profile['suggested_name']}' for cleaner syntax."
            })

        # Add data quality issue warnings
        if null_pct > 30:
            profile_json["quality_report"]["issues"].append({
                "severity": "warning",
                "column": col,
                "type": "high_null_percentage",
                "message": f"Column '{col}' has {null_pct}% missing values."
            })
        elif null_pct > 0:
            profile_json["quality_report"]["issues"].append({
                "severity": "info",
                "column": col,
                "type": "missing_values",
                "message": f"Column '{col}' has {null_count} missing values."
            })

        # Compute specific statistics based on type group
        if col_profile["type_group"] == "numeric":
            # Extract non-nulls for numpy/scipy operations
            valid_vals = series.drop_nulls().to_list()
            if valid_vals:
                col_profile["stats"] = {
                    "mean": float(np.mean(valid_vals)),
                    "median": float(np.median(valid_vals)),
                    "min": float(np.min(valid_vals)),
                    "max": float(np.max(valid_vals)),
                    "std": float(np.std(valid_vals)),
                    "q25": float(np.percentile(valid_vals, 25)),
                    "q75": float(np.percentile(valid_vals, 75)),
                }
                # Outlier detection
                outlier_info = detect_outliers_iqr(valid_vals)
                col_profile["outliers"] = outlier_info
                if outlier_info["count"] > 0:
                    profile_json["quality_report"]["issues"].append({
                        "severity": "warning",
                        "column": col,
                        "type": "outliers_detected",
                        "message": f"Detected {outlier_info['count']} outliers in numeric column '{col}' ({outlier_info['percentage']}%)."
                    })
            else:
                col_profile["stats"] = None

        elif col_profile["type_group"] == "temporal":
            valid_vals = series.drop_nulls().to_list()
            if valid_vals:
                col_profile["stats"] = {
                    "min": str(np.min(valid_vals)),
                    "max": str(np.max(valid_vals))
                }
            else:
                col_profile["stats"] = None

        else:  # Categorical/Other
            # Get value distribution
            value_counts = series.value_counts().sort(by="count", descending=True).head(10)
            dist = {}
            for row in value_counts.iter_rows():
                # row is (value, count)
                val_str = str(row[0]) if row[0] is not None else "NULL"
                dist[val_str] = row[1]
            col_profile["value_distribution"] = dist

            # Check cardinality
            cardinality = col_profile["unique_count"]
            if cardinality == 1:
                profile_json["quality_report"]["issues"].append({
                    "severity": "warning",
                    "column": col,
                    "type": "single_value_column",
                    "message": f"Column '{col}' has only 1 unique value. It offers no analytical benefit."
                })

        profile_json["columns"][col] = col_profile

    # Calculate overall quality score
    # Start at 100, deduct for high missingness, outliers, single value cols, duplicates
    deductions = 0
    if total_cells > 0:
        deductions += (total_missing / total_cells) * 40  # up to 40 points off for missing cells
    if row_count > 0:
        deductions += (profile_json["summary"]["duplicates"] / row_count) * 20  # up to 20 points off for duplicate rows
    
    # Check severity counts
    warning_count = len([i for i in profile_json["quality_report"]["issues"] if i["severity"] == "warning"])
    deductions += warning_count * 5  # 5 points off per warning issue

    profile_json["quality_report"]["overall_score"] = max(10, int(100 - deductions))

    return schema_json, profile_json, row_count, col_count
