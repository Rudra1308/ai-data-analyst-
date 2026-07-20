from typing import Dict, Any
from backend.app.agents.base import BaseAgent

ML_SYSTEM_PROMPT = """You are a Machine Learning Agent. Your job is to generate Python code using scikit-learn to build classification, regression, or clustering models.
Your response MUST be a single, valid JSON object with the following keys:
{
    "explanation": "Summary of the model choice, preprocessing steps, and evaluation strategy.",
    "code": "Python code block that performs training, prediction, evaluation (metrics like MSE, R2, accuracy, F1), and feature importances/SHAP values. The dataset is already loaded in variable `df` as a pandas DataFrame. Store a dictionary containing the evaluation metrics, feature importances, and predicted values in the variable `result`."
}
Ensure the Python code is complete, doesn't print, and stores the final result dict in the variable `result`. Do not include formatting backticks around the JSON.
"""

ML_USER_PROMPT_TEMPLATE = """Perform machine learning tasks on this dataset:
{dataset_context}

User ML Request:
"{user_query}"

Write code that preprocesses the data, splits into train/test, fits a scikit-learn model, calculates feature importances or metrics, and outputs the model evaluation details in `result`.
"""


class MLAgent(BaseAgent):
    """Agent in charge of training scikit-learn classification, regression, and clustering models."""

    def run_ml_task(
        self,
        dataset_profile: Dict[str, Any],
        user_query: str
    ) -> Dict[str, Any]:
        dataset_context = self.format_dataset_context(dataset_profile)
        user_prompt = ML_USER_PROMPT_TEMPLATE.format(
            dataset_context=dataset_context,
            user_query=user_query
        )
        return self.call_llm(ML_SYSTEM_PROMPT, user_prompt, temperature=0.1)
