from __future__ import annotations

from typing import Any, Dict, List
from pathlib import Path
import json

from .exceptions import ToolExecutionError
from .llm_client import LLMClient
from .models import Message
from .skills_tool import get_skill, list_skills, read_file_in_skill, run_python_script


class Conversation:
    """Manage chat history and tool execution loop."""
    def __init__(self, client: LLMClient, tools: List[Dict[str, Any]], skills_folder: Path) -> None:
        self.client = client
        self.tools = tools
        self.skills_folder = skills_folder
        self.messages: List[Message] = [
            Message(
                role="system",
                content=(
                    "You are a helpful assistant with access to tools. "
                    "Before using any skill name, call list_skills to discover available skills. "
                    "Do not guess skill names."
                ),
            )
        ]

    def send(self, user_input: str) -> str:
        """Send user input to the LLM and return the final assistant response."""
        self.messages.append(Message(role="user", content=user_input))

        while True:
            response_message = self.client.chat(self._serialize_messages(), self.tools)
            tool_calls = response_message.get("tool_calls")
            content = response_message.get("content")

            self.messages.append(
                Message(role="assistant", content=content, tool_calls=tool_calls)
            )

            if tool_calls:
                for tool_call in tool_calls:
                    result = self._execute_tool(tool_call)
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
