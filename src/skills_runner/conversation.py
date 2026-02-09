from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional
from pathlib import Path
import json

from .exceptions import ToolExecutionError
from .llm_client import LLMClient
from .models import Message
from .skills_tool import get_skill, list_skills, read_file_in_skill, run_python_script

_FALLBACK_SYSTEM_PROMPT = (
    "Before you think you cannot assist the user in doing something, e.g. access external websites, "
    "you MUST ALWAYS call this tool: \"list_skills\" to discover your available skills to help the user. "
    "Before using any skill name, call \"list_skills\" to discover available skills. "
    "Do not guess skill names."
)


def _load_soul_prompt() -> str:
    """Load the system prompt from soul.md at the project root.

    Searches upward from this file's location for soul.md.
    Falls back to a minimal hardcoded prompt if not found.
    """
    search_dir = Path(__file__).resolve().parent
    for _ in range(5):
        candidate = search_dir / "soul.md"
        if candidate.is_file():
            return candidate.read_text(encoding="utf-8").strip()
        search_dir = search_dir.parent
    return _FALLBACK_SYSTEM_PROMPT


class Conversation:
    """Manage chat history and tool execution loop."""
    def __init__(self, client: LLMClient, tools: List[Dict[str, Any]], skills_folder: Path) -> None:
        self.client = client
        self.tools = tools
        self.skills_folder = skills_folder
        self.messages: List[Message] = [
            Message(role="system", content=_load_soul_prompt())
        ]

    def load_messages(self, messages: List[Dict[str, Any]]) -> None:
        """Replace the conversation history with OpenAI-format messages."""
        has_system = any(message.get("role") == "system" for message in messages)
        self.messages = []
        if not has_system:
            self.messages.append(
                Message(role="system", content=_load_soul_prompt())
            )

        for message in messages:
            if not isinstance(message, dict):
                continue
            self.messages.append(
                Message(
                    role=message.get("role", "user"),
                    content=message.get("content"),
                    tool_calls=message.get("tool_calls"),
                    tool_call_id=message.get("tool_call_id"),
                    name=message.get("name"),
                )
            )

    def send(
        self,
        user_input: str,
        tool_event_handler: Optional[
            Callable[[str, Dict[str, Any], Optional[Dict[str, Any]]], None]
        ] = None,
    ) -> str:
        """Send user input to the LLM and return the final assistant response."""
        self.messages.append(Message(role="user", content=user_input))
        return self.run(tool_event_handler=tool_event_handler)

    def run(
        self,
        tool_event_handler: Optional[
            Callable[[str, Dict[str, Any], Optional[Dict[str, Any]]], None]
        ] = None,
    ) -> str:
        """Run a conversation turn using the current message history."""
        while True:
            response_message = self.client.chat(self._serialize_messages(), self.tools)
            tool_calls = response_message.get("tool_calls")
            content = response_message.get("content")

            self.messages.append(
                Message(role="assistant", content=content, tool_calls=tool_calls)
            )

            if tool_calls:
                for tool_call in tool_calls:
                    if tool_event_handler:
                        tool_event_handler("start", tool_call, None)
                    result = self._execute_tool(tool_call)
                    if tool_event_handler:
                        tool_event_handler("end", tool_call, result)
                    else:
                        self._display_tool_event(tool_call, result)
                    self.messages.append(
                        Message(
                            role="tool",
                            tool_call_id=tool_call.get("id"),
                            name=tool_call.get("function", {}).get("name"),
                            content=json.dumps(result),
                        )
                    )
                continue

            if not isinstance(content, str):
                raise ToolExecutionError("LLM response missing content")
            return content

    def _serialize_messages(self) -> List[Dict[str, Any]]:
        """Convert Message objects to API payload dictionaries."""
        return [message.to_dict() for message in self.messages]

    def _execute_tool(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch a tool call and return its result payload."""
        function = tool_call.get("function", {})
        name = function.get("name")
        arguments = function.get("arguments", "{}")

        try:
            params = json.loads(arguments)
        except json.JSONDecodeError as exc:
            return {"error": f"Invalid tool arguments: {exc}"}

        if name == "list_skills":
            return list_skills(self.skills_folder)
        if name == "get_skill":
            return get_skill(params.get("skill_name", ""), self.skills_folder)
        if name == "read_file_in_skill":
            return read_file_in_skill(
                params.get("skill_name", ""),
                params.get("file_path", ""),
                self.skills_folder,
            )
        if name == "run_python_script":
            return run_python_script(
                params.get("skill_name", ""),
                params.get("script", ""),
                self.skills_folder,
                self.client.timeout_seconds,
            )

        return {"error": f"Unknown tool: {name}"}

    def _display_tool_event(self, tool_call: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Print tool call and result for user visibility."""
        name = tool_call.get("function", {}).get("name", "unknown")
        args = tool_call.get("function", {}).get("arguments", "{}")
        print(f"[Tool Call] {name}({args})")
        print(f"[Tool Result] {json.dumps(result)}")
