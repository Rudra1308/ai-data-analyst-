from typing import Dict, Any, List
from backend.app.agents.base import BaseAgent

INSIGHT_SYSTEM_PROMPT = """You are a Senior Business Intelligence & Product Insights Agent.
Your job is to read user queries and the results of data execution (e.g. stats, tables, forecasts, ML metrics), and compose a professional, enterprise-grade business report.

Your response MUST be a single, valid JSON object in this exact format (no formatting backticks):
{
    "executive_summary": "High-level summary of what happened, key trends, and conclusions.",
    "business_insights": [
        "Insight 1 with business context",
        "Insight 2 with business context"
    ],
    "statistical_findings": [
        "Statistical details, p-values, regression metrics, or anomalies detected"
    ],
    "confidence_level": "high|medium|low",
    "recommended_actions": [
        "Strategic action item 1",
        "Strategic action item 2"
    ],
    "potential_risks": [
        "Risk 1 to keep in mind (e.g. data quality issues, extrapolation error)"
    ],
    "follow_up_questions": [
        "Suggested next logical question 1",
        "Suggested next logical question 2"
    ]
}
Ensure the content is highly insightful, and directly addresses the business query.
"""

INSIGHT_USER_PROMPT_TEMPLATE = """Generate a business report.
User Query:
"{user_query}"

Dataset Schema Context:
{dataset_context}

Execution Results / Data Summary:
{execution_summary}

Analyze these details and compile the JSON report.
"""


class InsightAgent(BaseAgent):
    """Agent in charge of reading query results and distilling them into business reports, actions, and risks."""

    def generate_report(
        self,
        user_query: str,
        dataset_profile: Dict[str, Any],
        execution_result_summary: str
    ) -> Dict[str, Any]:
        dataset_context = self.format_dataset_context(dataset_profile)
        user_prompt = INSIGHT_USER_PROMPT_TEMPLATE.format(
            user_query=user_query,
            dataset_context=dataset_context,
            execution_summary=execution_result_summary
        )
        return self.call_llm(INSIGHT_SYSTEM_PROMPT, user_prompt, temperature=0.2)
