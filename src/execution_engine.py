"""
Execution Engine Module
Safely executes LLM-generated Python code against the DataFrame.
Restricts available imports and catches errors gracefully.
"""
import pandas as pd
import numpy as np
import re
import traceback


# Whitelist of modules the LLM is allowed to import
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
    """
    Strip or rewrite import statements from LLM-generated code.
    All safe modules are already pre-loaded in the execution namespace.
    """
    lines = code.split("\n")
    cleaned = []
    for line in lines:
        stripped = line.strip()
        # Skip common import lines — these modules are pre-loaded
        if re.match(r"^import\s+(pandas|numpy|plotly|sklearn|math|statistics|collections|itertools|functools|datetime|re|json)", stripped):
            cleaned.append(f"# {line}  # (auto-skipped: module pre-loaded)")
            continue
        if re.match(r"^from\s+(pandas|numpy|plotly|sklearn|math|statistics|collections|itertools|functools|datetime|re|json)", stripped):
            cleaned.append(f"# {line}  # (auto-skipped: module pre-loaded)")
            continue
        cleaned.append(line)
    return "\n".join(cleaned)


def execute_code(code: str, df: pd.DataFrame) -> dict:
    """
    Execute LLM-generated Python code in a restricted environment.

    Args:
        code: Python code string to execute
        df: The user's DataFrame

    Returns:
        dict with keys:
            - success (bool)
            - result (any): The value of the `result` variable after execution
            - error (str): Error message if execution failed
    """
    if not code or not code.strip():
        return {"success": False, "result": None, "error": "No code to execute."}

    # Sanitize — strip import statements (modules are pre-loaded)
    code = _sanitize_code(code)

    # Restricted namespace — only allow safe imports
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
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
    import sklearn
    import math
    import datetime
    import json as json_mod

    # Safe import function — only allows whitelisted modules
    _allowed_imports = {
        "pandas": pd, "numpy": np, "math": math, "datetime": datetime,
        "json": json_mod, "re": re, "collections": __import__("collections"),
        "itertools": __import__("itertools"), "functools": __import__("functools"),
        "statistics": __import__("statistics"),
        "plotly": __import__("plotly"), "plotly.express": px,
        "plotly.graph_objects": go, "plotly.graph_objs": go,
        "plotly.subplots": __import__("plotly.subplots"),
        "sklearn": sklearn,
        "sklearn.linear_model": linear_model,
        "sklearn.ensemble": ensemble,
        "sklearn.tree": tree,
        "sklearn.preprocessing": preprocessing,
        "sklearn.model_selection": model_selection,
        "sklearn.metrics": metrics,
    }

    def _safe_import(name, *args, **kwargs):
        if name in _allowed_imports:
            return _allowed_imports[name]
        # Check if it's a submodule of allowed packages
        root = name.split(".")[0]
        if root in ("pandas", "numpy", "plotly", "sklearn", "collections",
                     "itertools", "functools", "math", "datetime", "json",
                     "re", "statistics"):
            return __import__(name, *args, **kwargs)
        raise ImportError(f"Module '{name}' is not allowed in this environment.")

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
            "any": any,
            "all": all,
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
            "frozenset": frozenset,
            "isinstance": isinstance,
            "issubclass": issubclass,
            "type": type,
            "hasattr": hasattr,
            "getattr": getattr,
            "setattr": setattr,
            "callable": callable,
            "iter": iter,
            "next": next,
            "repr": repr,
            "format": format,
            "id": id,
            "hash": hash,
            "slice": slice,
            "property": property,
            "staticmethod": staticmethod,
            "classmethod": classmethod,
            "super": super,
            "object": object,
            "ValueError": ValueError,
            "TypeError": TypeError,
            "KeyError": KeyError,
            "IndexError": IndexError,
            "AttributeError": AttributeError,
            "RuntimeError": RuntimeError,
            "StopIteration": StopIteration,
            "Exception": Exception,
            "ZeroDivisionError": ZeroDivisionError,
            "print": lambda *a, **k: None,  # Suppress print
            "True": True,
            "False": False,
            "None": None,
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
        "df": df.copy(),  # Work on a copy to protect original data
    }

    safe_locals = {}

    try:
        exec(code, safe_globals, safe_locals)

        result = safe_locals.get("result", None)

        if result is None:
            # Try to find any Plotly figure or DataFrame in locals
            for val in safe_locals.values():
                if hasattr(val, "update_layout"):  # Plotly figure
                    result = val
                    break
                elif isinstance(val, pd.DataFrame):
                    result = val
                    break

        if result is None:
            return {
                "success": True,
                "result": "Code executed successfully but no `result` variable was set.",
                "error": None,
            }

        return {"success": True, "result": result, "error": None}

    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        tb = traceback.format_exc()
        # Extract only the relevant part of the traceback
        lines = tb.split("\n")
        relevant = [l for l in lines if "exec" not in l and "File" not in l]
        return {
            "success": False,
            "result": None,
            "error": error_msg,
        }
