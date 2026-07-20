from typing import Dict, Any
from backend.app.agents.base import BaseAgent

VISUALIZER_SYSTEM_PROMPT = """You are a Visualization Agent. Your task is to generate Python code using Plotly Express (`px`) or Plotly Graph Objects (`go`) to create a beautiful, interactive chart.
Your response MUST be a single, valid JSON object with the following keys:
{
    "explanation": "Brief description of the selected chart and why it fits the request.",
    "code": "Python code block to create the Plotly chart. The dataset is already loaded in variable `df` as a pandas DataFrame. Store the final Plotly figure object in the variable `result`.",
    "plotly_spec": {
        "chart_type": "scatter|bar|line|pie|heatmap|histogram|box",
        "x": "Column name for x-axis",
        "y": "Column name for y-axis"
    }
}
RULES:
1. EXCLUSIVELY use Plotly Express (`px`) or Plotly Graph Objects (`go`). Matplotlib and Seaborn are strictly forbidden.
2. Store the final figure object in a variable called `result`.
3. NEVER call `print()`, `.show()`, or write to streamlit inside the code.
4. For Plotly charts, use a professional design: set paper_bgcolor and plot_bgcolor to transparent ('rgba(0,0,0,0)') or matching theme colors.
5. Do not include markdown backticks around the JSON.
"""

VISUALIZER_USER_PROMPT_TEMPLATE = """Generate a visualization for the dataset:
{dataset_context}

User visualization request:
"{user_query}"

Write code that aggregates or filters the data if necessary, then builds the Plotly figure, and assigns the figure to `result`.
"""


class VisualizerAgent(BaseAgent):
    """Agent in charge of generating Python Plotly code to build interactive charts."""

    def generate_chart(
        self,
        dataset_profile: Dict[str, Any],
        user_query: str
    ) -> Dict[str, Any]:
        dataset_context = self.format_dataset_context(dataset_profile)
        user_prompt = VISUALIZER_USER_PROMPT_TEMPLATE.format(
            dataset_context=dataset_context,
            user_query=user_query
        )
        return self.call_llm(VISUALIZER_SYSTEM_PROMPT, user_prompt, temperature=0.1)
