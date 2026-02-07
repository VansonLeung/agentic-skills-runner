from __future__ import annotations

from typing import Any, Dict, List
import requests

from .exceptions import ToolExecutionError


class LLMClient:
    """OpenAI-compatible chat client for LLM interactions."""
    def __init__(self, api_key: str, api_base_url: str, model_name: str, timeout_seconds: int = 30) -> None:
        self.api_key = api_key
        self.api_base_url = api_base_url.rstrip("/")
        self.model_name = model_name
        self.timeout_seconds = timeout_seconds

    def chat(self, messages: List[Dict[str, Any]], tools: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Send a chat completion request and return the assistant message."""
        url = f"{self.api_base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model_name,
            "messages": messages,
            "tools": tools,
            "tool_choice": "auto",
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=self.timeout_seconds)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as exc:
            raise ToolExecutionError(f"LLM API request failed: {exc}") from exc
        except ValueError as exc:
            raise ToolExecutionError("LLM API returned invalid JSON") from exc

        if not isinstance(data, dict):
            raise ToolExecutionError("LLM API response is not a JSON object")

        choices = data.get("choices")
        if not isinstance(choices, list) or not choices:
            raise ToolExecutionError("LLM API response missing choices")

        first_choice = choices[0]
        if not isinstance(first_choice, dict):
            raise ToolExecutionError("LLM API response has invalid choice format")

        message = first_choice.get("message")
        if not isinstance(message, dict):
            raise ToolExecutionError("LLM API response missing message")

        return message
