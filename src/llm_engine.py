"""
LLM Engine Module
Handles communication with OpenRouter API using OpenAI-compatible SDK.
Converts user natural language queries into executable Python code.
"""
import json
import re
from openai import OpenAI

SYSTEM_PROMPT = """You are an expert data analyst AI assistant. The user has uploaded a CSV dataset loaded into a Pandas DataFrame called `df`.

Your job is to answer the user's question about the data by generating Python code that operates on `df`.

## RULES:
1. Always operate on the DataFrame variable called `df`. It is already loaded — do NOT load or read any files.
2. Use pandas, numpy, plotly.express, plotly.graph_objects, and sklearn as needed.
3. For visualizations, ALWAYS use Plotly (never matplotlib). Use `plotly.express` or `plotly.graph_objects`.
4. Store the final result in a variable called `result`.
   - If the result is a chart/figure, `result` must be a Plotly figure object.
   - If the result is a DataFrame/table, `result` must be a pandas DataFrame.
   - If the result is a number or text, `result` must be a string.
5. NEVER use `print()` or `st.write()` — just assign to `result`.
6. NEVER call `.show()` on Plotly figures.
7. For Plotly charts, always use a dark theme: `template='plotly_dark'` and set `paper_bgcolor='rgba(0,0,0,0)'` and `plot_bgcolor='rgba(0,0,0,0)'`.
8. Write clean, efficient code. Add brief comments.
9. If the user asks for predictions/ML, use scikit-learn.
10. Handle edge cases (empty data, missing values) gracefully.

## RESPONSE FORMAT:
You MUST respond with ONLY a valid JSON object in this exact format (no markdown, no backticks):
{
    "explanation": "Brief explanation of what the code does and what insights it reveals",
    "code": "python code here as a single string",
    "type": "insight|chart|prediction|table"
}

## DATASET INFO:
{dataset_info}
"""


class LLMEngine:
    """Manages communication with OpenRouter API."""

    def __init__(self, api_key: str, model: str = "google/gemini-2.0-flash-exp:free"):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.model = model
        self.chat_history = []

    def set_model(self, model: str):
        """Change the active model."""
        self.model = model

    def clear_history(self):
        """Clear conversation history."""
        self.chat_history = []

    def generate_response(self, query: str, dataset_info: str) -> dict:
        """
        Send a natural language query to the LLM and get structured response.

        Args:
            query: User's natural language question
            dataset_info: String summary of the dataset

        Returns:
            dict with keys: explanation, code, type
        """
        system_msg = SYSTEM_PROMPT.replace("{dataset_info}", dataset_info)

        messages = [{"role": "system", "content": system_msg}]

        # Add conversation history for context (last 6 exchanges max)
        for msg in self.chat_history[-12:]:
            messages.append(msg)

        messages.append({"role": "user", "content": query})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,
                max_tokens=2000,
            )

            assistant_content = response.choices[0].message.content.strip()

            # Store in history
            self.chat_history.append({"role": "user", "content": query})
            self.chat_history.append({"role": "assistant", "content": assistant_content})

            # Parse JSON response
            parsed = self._parse_response(assistant_content)
            return parsed

        except Exception as e:
            return {
                "explanation": f"Error communicating with LLM: {str(e)}",
                "code": "",
                "type": "error",
            }

    def _parse_response(self, content: str) -> dict:
        """Parse the LLM response into a structured dict."""
        # Try direct JSON parse
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # Try to extract JSON from markdown code blocks
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to find JSON object anywhere in the text
        brace_match = re.search(r"\{[^{}]*\"explanation\"[^{}]*\"code\"[^{}]*\}", content, re.DOTALL)
        if brace_match:
            try:
                return json.loads(brace_match.group(0))
            except json.JSONDecodeError:
                pass

        # Fallback — return explanation only
        return {
            "explanation": content,
            "code": "",
            "type": "insight",
        }
