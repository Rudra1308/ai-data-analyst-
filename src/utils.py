"""
Utility functions shared across modules.
"""
import pandas as pd
import io


def format_dataframe_info(df: pd.DataFrame) -> str:
    """Generate a concise text summary of a DataFrame for LLM context."""
    buf = io.StringIO()
    df.info(buf=buf)
    info_str = buf.getvalue()

    summary_parts = [
        f"Shape: {df.shape[0]} rows × {df.shape[1]} columns",
        f"Columns: {', '.join(df.columns.tolist())}",
        "",
        "Column Details:",
    ]

    for col in df.columns:
        dtype = df[col].dtype
        nulls = df[col].isnull().sum()
        uniques = df[col].nunique()
        line = f"  - {col} (type: {dtype}, nulls: {nulls}, unique: {uniques})"
        if pd.api.types.is_numeric_dtype(df[col]):
            line += f" | min: {df[col].min()}, max: {df[col].max()}, mean: {df[col].mean():.2f}"
        elif pd.api.types.is_string_dtype(df[col]) or pd.api.types.is_object_dtype(df[col]):
            top_vals = df[col].value_counts().head(5).index.tolist()
            line += f" | top values: {top_vals}"
        summary_parts.append(line)

    summary_parts.append("")
    summary_parts.append("First 3 rows:")
    summary_parts.append(df.head(3).to_string(index=False))

    return "\n".join(summary_parts)


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to a maximum length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


# Available free models on OpenRouter (updated April 2026)
OPENROUTER_MODELS = {
    "Auto — Free Router (Recommended)": "openrouter/free",
    "Meta Llama 3.3 70B (Free)": "meta-llama/llama-3.3-70b-instruct:free",
    "Qwen 3.6 Plus (Free)": "qwen/qwen3.6-plus:free",
    "StepFun Step 3.5 Flash (Free)": "stepfun/step-3.5-flash:free",
    "NVIDIA Nemotron 120B (Free)": "nvidia/nemotron-3-super-120b-a12b:free",
    "Z.ai GLM 4.5 Air (Free)": "z-ai/glm-4.5-air:free",
    "Arcee Trinity Mini (Free)": "arcee/trinity-mini:free",
}
