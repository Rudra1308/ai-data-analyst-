from typing import Dict, Any, Optional
from backend.app.agents.base import BaseAgent

EDA_SYSTEM_PROMPT = """You are an EDA (Exploratory Data Analysis) Agent. Your task is to perform exploratory analysis on the dataset.
Your response MUST be a single, valid JSON object with the following keys:
{
    "explanation": "Summary of what the EDA reveals about trends, correlations, or structure.",
    "code": "Python code block that will perform the analysis. The dataset is already loaded in variable `df` as a pandas DataFrame. Save the analysis result in variable `result` (e.g. a pandas DataFrame of correlations, a dict of feature statistics, etc.).",
    "type": "table|insight|chart"
}
Ensure the Python code is complete, doesn't print, and stores the final result in the variable `result`. Do not include formatting backticks around the JSON.
"""

EDA_USER_PROMPT_TEMPLATE = """Perform exploratory data analysis on the dataset. Here is the dataset context:
{dataset_context}

User question/instructions:
"{user_query}"

Write code that calculates descriptive statistics, correlation matrices, group-by statistics, or distributions. Assign the final output (typically a table/DataFrame) to `result`.
"""


class EDAAgent(BaseAgent):
    """Agent in charge of performing exploratory data analysis, descriptive stats, and correlations."""

    def perform_eda(
        self,
        dataset_profile: Dict[str, Any],
        user_query: str
    ) -> Dict[str, Any]:
        dataset_context = self.format_dataset_context(dataset_profile)
        user_prompt = EDA_USER_PROMPT_TEMPLATE.format(
            dataset_context=dataset_context,
            user_query=user_query
        )
        return self.call_llm(EDA_SYSTEM_PROMPT, user_prompt, temperature=0.1)
