import os
from typing import Dict, Any, List, Optional
import openai
from anthropic import Anthropic
import google.generativeai as genai
from backend.app.core.config import settings


class LLMProviderClient:
    """Unified client adapter supporting OpenAI, Anthropic, Gemini, Groq, and OpenRouter."""

    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self.provider = (provider or settings.DEFAULT_PROVIDER).lower()
        self.model = model or settings.DEFAULT_MODEL
        self.api_key = api_key
        self.base_url = base_url

        # Select API keys from settings if not passed explicitly
        if not self.api_key:
            if self.provider == "openai":
                self.api_key = settings.OPENAI_API_KEY
            elif self.provider == "anthropic":
                self.api_key = settings.ANTHROPIC_API_KEY
            elif self.provider == "gemini":
                self.api_key = settings.GEMINI_API_KEY
            elif self.provider == "groq":
                self.api_key = settings.GROQ_API_KEY
            elif self.provider == "openrouter":
                self.api_key = settings.OPENROUTER_API_KEY

        # Initialize raw clients
        self._init_client()

    def _init_client(self):
        if self.provider == "openai":
            self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
        elif self.provider == "anthropic":
            self.client = Anthropic(api_key=self.api_key)
        elif self.provider == "gemini":
            if self.api_key:
                genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model)
        elif self.provider == "groq":
            self.client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url or "https://api.groq.com/openai/v1"
            )
        elif self.provider == "openrouter":
            self.client = openai.OpenAI(
                api_key=self.api_key or os.getenv("OPENROUTER_API_KEY", ""),
                base_url=self.base_url or "https://openrouter.ai/api/v1"
            )
        elif self.provider in ("ollama", "lmstudio", "local"):
            # Local endpoints pointing to localhost by default
            default_url = "http://localhost:11434/v1" if self.provider == "ollama" else "http://localhost:1234/v1"
            self.client = openai.OpenAI(
                api_key=self.api_key or "local-key",
                base_url=self.base_url or default_url
            )
        else:
            # Fallback to OpenRouter
            self.provider = "openrouter"
            self.client = openai.OpenAI(
                api_key=settings.OPENROUTER_API_KEY or os.getenv("OPENROUTER_API_KEY", ""),
                base_url="https://openrouter.ai/api/v1"
            )

    def generate(self, messages: List[Dict[str, str]], temperature: float = 0.1, response_format: Optional[str] = None) -> str:
        """Call LLM provider and return response text."""
        # 1. Gemini Client Path
        if self.provider == "gemini":
            # Translate message list to Google format
            contents = []
            for msg in messages:
                role = "user" if msg["role"] == "user" else "model"
                if msg["role"] == "system":
                    # Prepend system prompt to the user contents for Gemini simple client compatibility
                    contents.append({"role": "user", "parts": [f"System instruction: {msg['content']}\n"]})
                else:
                    contents.append({"role": role, "parts": [msg["content"]]})
            
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                response_mime_type="application/json" if response_format == "json" else "text/plain"
            )
            
            response = self.client.generate_content(contents, generation_config=generation_config)
            return response.text

        # 2. Anthropic Client Path
        elif self.provider == "anthropic":
            system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
            user_msgs = [m for m in messages if m["role"] != "system"]
            
            # Reformat roles
            formatted_msgs = []
            for m in user_msgs:
                formatted_msgs.append({
                    "role": "user" if m["role"] == "user" else "assistant",
                    "content": m["content"]
                })

            kwargs = {
                "model": self.model,
                "messages": formatted_msgs,
                "max_tokens": 4000,
                "temperature": temperature
            }
            if system_msg:
                kwargs["system"] = system_msg

            response = self.client.messages.create(**kwargs)
            return response.content[0].text

        # 3. OpenAI and Compatible Client Paths (OpenRouter, Groq, Ollama, LM Studio)
        else:
            api_kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature
            }
            if response_format == "json" and self.provider != "openrouter":
                # Some providers on OpenRouter might not support strict JSON schema
                api_kwargs["response_format"] = {"type": "json_object"}

            completion = self.client.chat.completions.create(**api_kwargs)
            return completion.choices[0].message.content
