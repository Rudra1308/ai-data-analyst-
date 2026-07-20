import json
import re
from typing import Dict, Any, List, Optional
from backend.app.core.llm_client import LLMProviderClient


class BaseAgent:
    """Base Agent class specifying standard structures, prompt formatting, and JSON extraction."""

    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self.client = LLMProviderClient(provider=provider, model=model, api_key=api_key, base_url=base_url)


    def format_dataset_context(self, dataset_profile: Dict[str, Any]) -> str:
        """Format dataset profiling JSON into a concise summary prompt injection."""
        summary = dataset_profile.get("summary", {})
        col_info = dataset_profile.get("columns", {})
        
        info = [
            f"Dataset dimensions: {summary.get('rows', 0)} rows x {summary.get('columns', 0)} columns",
            f"Duplicate rows detected: {summary.get('duplicates', 0)}",
            "Columns:"
        ]
        
        for name, col in col_info.items():
            type_grp = col.get("type_group", "unknown")
            dtype = col.get("dtype", "unknown")
            null_pct = col.get("null_percentage", 0.0)
            
            col_desc = f"  - {name} ({dtype}, {type_grp}) | {null_pct}% nulls"
            
            # Append range/statistics summaries if present to give LLM better context
            if "stats" in col and col["stats"]:
                stats = col["stats"]
                if type_grp == "numeric":
                    col_desc += f" | Min: {stats.get('min')}, Max: {stats.get('max')}, Mean: {stats.get('mean')}"
                elif type_grp == "temporal":
                    col_desc += f" | Range: {stats.get('min')} to {stats.get('max')}"
            
            info.append(col_desc)
            
        return "\n".join(info)

    def extract_json(self, response_text: str) -> Dict[str, Any]:
        """Safely extract and parse JSON object from LLM response text."""
        # Clean text
        text = response_text.strip()
        
        # Try raw JSON parse first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try regex to extract markdown block
        markdown_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if markdown_match:
            try:
                return json.loads(markdown_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to find brace matching JSON
        brace_match = re.search(r"(\{.*\})", text, re.DOTALL)
        if brace_match:
            try:
                return json.loads(brace_match.group(1))
            except json.JSONDecodeError:
                pass
                
        raise ValueError(f"Could not parse response content as valid JSON. Response received:\n{response_text}")

    def call_llm(self, system_prompt: str, user_prompt: str, temperature: float = 0.1) -> Dict[str, Any]:
        """Send formatted messaging context and return parsed JSON response."""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        response_text = self.client.generate(messages, temperature=temperature, response_format="json")
        return self.extract_json(response_text)
