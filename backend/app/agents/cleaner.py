from typing import Dict, Any, Optional
from backend.app.agents.base import BaseAgent

CLEANER_SYSTEM_PROMPT = """You are a Data Cleaning Agent. Your task is to clean a dataset based on its data quality issues.
Your response MUST be a single, valid JSON object with the following keys:
{
    "explanation": "High level description of the cleaning steps proposed.",
    "cleaning_code": "Python code block that will perform the cleaning. The dataset is already loaded in variable `df` as a pandas DataFrame. Do NOT read any files. Store the cleaned DataFrame in `df`.",
    "quality_score_after": 95
}
Ensure the Python code is complete, handles missing values, removes duplicates, handles outliers or column names as requested, and sets the updated dataframe back in `df`. Do not include formatting backticks around the JSON.
"""

CLEANER_USER_PROMPT_TEMPLATE = """We need to clean the dataset. Here is the dataset profile information:
{dataset_context}

User-provided cleaning query/directives (if any):
"{user_query}"

Analyze the profile, identify duplicates, columns with high null values, column name styling, and outlier boundaries. Create complete pandas code that:
1. Removes duplicates if any exist.
2. Fills or drops null values depending on column type (e.g. median for numeric, mode/placeholder for categorical).
3. Renames columns to snake_case if suggested.
4. Stores the final cleaned DataFrame back in `df`.

Write the cleaning plan in 'explanation' and the python code block in 'cleaning_code'.
"""


class CleanerAgent(BaseAgent):
    """Agent in charge of generating Python pandas code for cleaning and normalizing data."""

    def clean_dataset(
        self,
        dataset_profile: Dict[str, Any],
        user_query: Optional[str] = None
    ) -> Dict[str, Any]:
        dataset_context = self.format_dataset_context(dataset_profile)
        user_query_str = user_query or "Perform standard auto-cleaning (remove duplicates, clean column names, impute moderate nulls)."
        
        user_prompt = CLEANER_USER_PROMPT_TEMPLATE.format(
            dataset_context=dataset_context,
            user_query=user_query_str
        )
        
        return self.call_llm(CLEANER_SYSTEM_PROMPT, user_prompt, temperature=0.1)
