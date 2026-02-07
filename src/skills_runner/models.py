from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class Message:
    """Conversation message in OpenAI-compatible format."""
    role: str
    content: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"role": self.role}
        if self.content is not None:
            payload["content"] = self.content
        if self.tool_calls is not None:
            payload["tool_calls"] = self.tool_calls
        if self.tool_call_id is not None:
            payload["tool_call_id"] = self.tool_call_id
        if self.name is not None:
            payload["name"] = self.name
        return payload


@dataclass
class Skill:
    """Skill metadata derived from the filesystem."""
    name: str
    folder_path: Path
    documentation_path: Path
    venv_path: Optional[Path]
    has_venv: bool
    has_documentation: bool


@dataclass
class ScriptExecution:
    """Script execution results for a skill."""
    skill_name: str
    script: str
    working_directory: Path
    python_executable: Path
    timeout: int
    stdout: str
    stderr: str
    returncode: int
    timed_out: bool
    error: Optional[str] = None
