from typing import Dict, Any, List
from backend.app.agents.base import BaseAgent

PLANNER_SYSTEM_PROMPT = """You are a Planner Agent for an AI Data Analyst platform.
Your job is to read the user's query and the dataset's schema profile, and decide a plan of action.
You must choose which agents should run in sequence.

The available specialized agents are:
- `cleaner`: For data cleaning requests (e.g. drop duplicates, handle missing values).
- `eda`: For general queries, aggregations, descriptive stats, correlations, group-by.
- `stats`: For statistical hypothesis testing, confidence intervals, correlation tests, t-tests, ANOVA.
- `ml`: For machine learning modeling (classification, regression, clustering, feature importance).
- `forecaster`: For time series forecasting.
- `visualizer`: For creating plots and charts.

Your response MUST be a single, valid JSON object in this exact format (no formatting backticks):
{
    "intent": "Brief description of user intent (e.g. forecast_sales)",
    "reasoning_chain": [
        "Step-by-step logical reasoning explaining why you chose this path."
    ],
    "task_sequence": [
        {"agent": "cleaner|eda|stats|ml|forecaster|visualizer", "task": "Description of the task to perform"}
    ]
}
RULES:
1. If the user asks for a chart/visualization, always ensure `visualizer` is in the task sequence.
2. If the user asks to predict the future or forecast, use `forecaster`.
3. If the user asks for correlation, regression models, classification models, or clustering, use `eda` or `ml` or `stats` accordingly.
4. Keep the task sequence minimal and logical. Typically 1 to 3 steps max.
"""

PLANNER_USER_PROMPT_TEMPLATE = """Plan the analysis workflow.
User Query:
"{user_query}"

Dataset Profiling Summary:
{dataset_context}

Analyze the user's intent and select the appropriate sequence of agents to run.
"""


class PlannerAgent(BaseAgent):
    """Agent in charge of coordinating workflows and mapping user questions to agent execution chains."""

    def plan_workflow(
        self,
        user_query: str,
        dataset_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        dataset_context = self.format_dataset_context(dataset_profile)
        user_prompt = PLANNER_USER_PROMPT_TEMPLATE.format(
            user_query=user_query,
            dataset_context=dataset_context
        )
        return self.call_llm(PLANNER_SYSTEM_PROMPT, user_prompt, temperature=0.1)
