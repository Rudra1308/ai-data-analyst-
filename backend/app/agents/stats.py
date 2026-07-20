from typing import Dict, Any
from backend.app.agents.base import BaseAgent

STATS_SYSTEM_PROMPT = """You are a Statistics Agent. Your job is to generate Python code using scipy.stats or statsmodels to run hypothesis tests (e.g. t-tests, ANOVA, Chi-Square, Pearson/Spearman correlation) and calculate confidence intervals.
Your response MUST be a single, valid JSON object with the following keys:
{
    "explanation": "Brief explanation of the statistical test chosen and the hypotheses being evaluated.",
    "code": "Python code block to perform the statistical calculations. The dataset is already loaded in variable `df` as a pandas DataFrame. Calculate values (p-value, test statistic, confidence intervals) and store a summary dictionary or pandas DataFrame of the test results in the variable `result`.",
    "hypothesis": {
        "null": "Null hypothesis statement",
        "alternative": "Alternative hypothesis statement"
    }
}
Do not use print() or st.write(). Assign your structured result to the variable `result`. Do not include formatting backticks around the JSON.
"""

STATS_USER_PROMPT_TEMPLATE = """Perform statistical testing on this dataset:
{dataset_context}

User statistical question:
"{user_query}"

Write clean Python code to execute the test, extract the statistical metrics, and format them.
"""


class StatsAgent(BaseAgent):
    """Agent in charge of performing statistical tests, hypothesis testing, and confidence intervals."""

    def perform_stats_test(
        self,
        dataset_profile: Dict[str, Any],
        user_query: str
    ) -> Dict[str, Any]:
        dataset_context = self.format_dataset_context(dataset_profile)
        user_prompt = STATS_USER_PROMPT_TEMPLATE.format(
            dataset_context=dataset_context,
            user_query=user_query
        )
        return self.call_llm(STATS_SYSTEM_PROMPT, user_prompt, temperature=0.1)
