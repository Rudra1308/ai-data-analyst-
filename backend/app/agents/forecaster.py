from typing import Dict, Any
from backend.app.agents.base import BaseAgent

FORECASTER_SYSTEM_PROMPT = """You are a Time Series Forecasting Agent. Your job is to generate Python code using statsmodels, prophet, or simple exponential smoothing to forecast future trends.
Your response MUST be a single, valid JSON object with the following keys:
{
    "explanation": "Summary of the chosen forecasting method, trends spotted, and confidence assumptions.",
    "code": "Python code block to perform the time-series forecasting. The dataset is already loaded in variable `df` as a pandas DataFrame. Parse dates, aggregate if needed, fit the model, project future steps, and assign the final forecast DataFrame (containing dates, historical values, predicted values, and confidence intervals) to the variable `result`."
}
Assign the forecast results to the variable `result`. Do not include formatting backticks around the JSON.
"""

FORECASTER_USER_PROMPT_TEMPLATE = """Generate a time-series forecast on the dataset:
{dataset_context}

User Forecasting request:
"{user_query}"

Write code that aggregates the dataset by date/time, handles date parsing, checks for missing dates, runs the forecast (e.g. ARIMA, SARIMAX, Holt-Winters, or Prophet), and sets a DataFrame of results to the variable `result`.
"""


class ForecasterAgent(BaseAgent):
    """Agent in charge of performing time series decomposition and forecasting projections."""

    def run_forecast(
        self,
        dataset_profile: Dict[str, Any],
        user_query: str
    ) -> Dict[str, Any]:
        dataset_context = self.format_dataset_context(dataset_profile)
        user_prompt = FORECASTER_USER_PROMPT_TEMPLATE.format(
            dataset_context=dataset_context,
            user_query=user_query
        )
        return self.call_llm(FORECASTER_SYSTEM_PROMPT, user_prompt, temperature=0.1)
