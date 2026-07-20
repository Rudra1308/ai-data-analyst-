import re
import traceback
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, Union
from plotly.subplots import make_subplots
import sklearn
from sklearn import (
    linear_model,
    ensemble,
    tree,
    svm,
    neighbors,
    cluster,
    preprocessing,
    model_selection,
    metrics,
)
import math
import datetime
import json as json_mod

SAFE_MODULES = {
    "pandas", "pd", "numpy", "np",
    "plotly", "plotly.express", "plotly.graph_objects", "plotly.graph_objs",
    "plotly.subplots", "plotly.figure_factory",
    "sklearn", "sklearn.linear_model", "sklearn.ensemble", "sklearn.tree",
    "sklearn.svm", "sklearn.neighbors", "sklearn.cluster",
    "sklearn.preprocessing", "sklearn.model_selection", "sklearn.metrics",
    "sklearn.pipeline", "sklearn.compose",
    "math", "statistics", "collections", "itertools", "functools",
    "datetime", "re", "json",
}


def _sanitize_code(code: str) -> str:
    """Rewrite generated import statements to use preloaded sandboxed references."""
    lines = code.split("\n")
    cleaned = []
    for line in lines:
        stripped = line.strip()
        if re.match(r"^import\s+(pandas|numpy|plotly|sklearn|math|statistics|collections|itertools|functools|datetime|re|json)", stripped):
            cleaned.append(f"# {line}  # (auto-skipped: module pre-loaded)")
            continue
        if re.match(r"^from\s+(pandas|numpy|plotly|sklearn|math|statistics|collections|itertools|functools|datetime|re|json)", stripped):
            cleaned.append(f"# {line}  # (auto-skipped: module pre-loaded)")
            continue
        cleaned.append(line)
    return "\n".join(cleaned)


def execute_code_safely(code: str, df: pd.DataFrame) -> Dict[str, Any]:
    """
    Execute generated Python code inside a secure local sandbox.
    Returns: { "success": bool, "result_type": str, "data": Any, "error": Optional[str] }
    """
    if not code or not code.strip():
        return {"success": False, "result_type": "error", "data": None, "error": "No code to execute."}

    # Clean potential markdown wrapping if LLM made a mistake
    if code.startswith("```python"):
        code = code[9:]
    if code.endswith("```"):
        code = code[:-3]

    sanitized_code = _sanitize_code(code)

    def _safe_import(name, *args, **kwargs):
        if name in SAFE_MODULES or name.split(".")[0] in SAFE_MODULES:
            return __import__(name, *args, **kwargs)
        raise ImportError(f"Module '{name}' is blocked in this environment.")

    # Sandbox environment setup
    safe_globals = {
        "__builtins__": {
            "__import__": _safe_import,
            "len": len,
            "range": range,
            "enumerate": enumerate,
            "zip": zip,
            "map": map,
            "filter": filter,
            "sorted": sorted,
            "reversed": reversed,
            "min": min,
            "max": max,
            "sum": sum,
            "abs": abs,
            "round": round,
            "int": int,
            "float": float,
            "str": str,
            "bool": bool,
            "list": list,
            "dict": dict,
            "tuple": tuple,
            "set": set,
            "isinstance": isinstance,
            "type": type,
            "ValueError": ValueError,
            "TypeError": TypeError,
            "KeyError": KeyError,
            "IndexError": IndexError,
            "AttributeError": AttributeError,
            "RuntimeError": RuntimeError,
            "Exception": Exception,
            "True": True,
            "False": False,
            "None": None,
            "print": lambda *a, **k: None,  # Block stdout printing
        },
        "pd": pd,
        "pandas": pd,
        "np": np,
        "numpy": np,
        "px": px,
        "go": go,
        "make_subplots": make_subplots,
        "sklearn": sklearn,
        "linear_model": linear_model,
        "ensemble": ensemble,
        "tree": tree,
        "svm": svm,
        "neighbors": neighbors,
        "cluster": cluster,
        "preprocessing": preprocessing,
        "model_selection": model_selection,
        "metrics": metrics,
        "math": math,
        "datetime": datetime,
        "json": json_mod,
        "re": re,
        "df": df.copy(),  # Copy to avoid side-effects on active session cache
    }

    safe_locals = {}

    try:
        # Run code block
        exec(sanitized_code, safe_globals, safe_locals)

        result = safe_locals.get("result", None)

        # Fallback inspection if variable wasn't explicitly assigned
        if result is None:
            for val in safe_locals.values():
                if hasattr(val, "to_plotly_json") or hasattr(val, "update_layout"):
                    result = val
                    break
                elif isinstance(val, pd.DataFrame):
                    result = val
                    break

        if result is None:
            # Check if df was modified in-place
            modified_df = safe_globals.get("df")
            if modified_df is not None and not modified_df.equals(df):
                result = modified_df

        # Format returned content based on type
        if hasattr(result, "to_plotly_json"):
            # Plotly Chart
            return {
                "success": True,
                "result_type": "plotly",
                "data": result.to_plotly_json(),
                "error": None
            }
        elif isinstance(result, pd.DataFrame):
            # DataFrame Table
            # Cap table response to first 100 rows to prevent networking bottleneck
            preview_df = result.head(100)
            return {
                "success": True,
                "result_type": "dataframe",
                "data": {
                    "columns": preview_df.columns.tolist(),
                    "rows": preview_df.replace({np.nan: None}).to_dict(orient="records"),
                    "total_rows": len(result)
                },
                "error": None
            }
        elif isinstance(result, (dict, list, str, int, float)):
            # Structured metrics/values
            return {
                "success": True,
                "result_type": "scalar",
                "data": result,
                "error": None
            }
        else:
            return {
                "success": True,
                "result_type": "scalar",
                "data": str(result) if result is not None else "Execution completed successfully.",
                "error": None
            }

    except Exception as e:
        tb = traceback.format_exc()
        # Clean trace file locations to avoid paths leak
        clean_tb = "\n".join([line for line in tb.split("\n") if "exec" not in line])
        return {
            "success": False,
            "result_type": "error",
            "data": None,
            "error": f"{type(e).__name__}: {str(e)}\n{clean_tb}"
        }
