from __future__ import annotations

from pathlib import Path
from typing import Dict, List
import logging
import time

from .executor import find_python_executable, run_script

_logger = logging.getLogger(__name__)


def _log_duration(operation: str, start_time: float) -> None:
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    _logger.info("%s completed in %.2fms", operation, elapsed_ms)


def validate_skill_name(name: str) -> bool:
    """Validate a skill name to prevent directory traversal."""
    if not name:
        return False
    return "/" not in name and "\\" not in name and ".." not in name


def list_skills(skills_folder: Path) -> Dict[str, object]:
    """List available skills under the configured skills folder."""
    start_time = time.perf_counter()
    skills_folder = skills_folder.resolve()
    if not skills_folder.exists():
        return {"error": f"Skills folder not found at path: {skills_folder}"}
    if not skills_folder.is_dir():
        return {"error": f"Skills folder path is not a directory: {skills_folder}"}

    skills: List[str] = []
    for entry in skills_folder.iterdir():
        if not entry.is_dir():
            continue
        if not validate_skill_name(entry.name):
            continue
        skills.append(entry.name)

    result: Dict[str, object] = {"skills": sorted(skills)}
    _log_duration("list_skills", start_time)
    return result


def get_skill(skill_name: str, skills_folder: Path) -> Dict[str, object]:
    """Read the SKILL.MD content for a given skill."""
    start_time = time.perf_counter()
    skills_folder = skills_folder.resolve()
    if not validate_skill_name(skill_name):
        return {
            "error": (
                f"Invalid skill name: '{skill_name}'. Skill names must not contain '/', "
                "'\\', or '..'"
            )
        }

    skill_path = skills_folder / skill_name
    if not skill_path.exists():
        return {"error": f"Skill '{skill_name}' not found in skills folder"}

    doc_path = skill_path / "SKILL.MD"
    if not doc_path.exists():
        return {"error": f"SKILL.MD not found for skill '{skill_name}'"}

    try:
        if doc_path.stat().st_size > 1024 * 1024:
            return {"error": f"SKILL.MD too large (>1MB) for skill '{skill_name}'"}
        content = doc_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return {"error": f"SKILL.MD contains invalid UTF-8 for skill '{skill_name}'"}
    except OSError as exc:
        return {"error": f"Error reading SKILL.MD for skill '{skill_name}': {exc}"}

    result: Dict[str, object] = {"skill_name": skill_name, "documentation": content}
    _log_duration("get_skill", start_time)
    return result


def read_file_in_skill(skill_name: str, file_path: str, skills_folder: Path) -> Dict[str, object]:
    """Read a file within a skill folder with path validation."""
    start_time = time.perf_counter()
    skills_folder = skills_folder.resolve()
    if not validate_skill_name(skill_name):
        return {"success": False, "skill_name": skill_name, "file_path": file_path, "error": "Invalid skill name"}

    if not file_path:
        return {"success": False, "skill_name": skill_name, "file_path": file_path, "error": "Invalid file path"}

    skill_dir = skills_folder / skill_name
    if not skill_dir.exists():
        return {
            "success": False,
            "skill_name": skill_name,
            "file_path": file_path,
            "error": f"Skill '{skill_name}' not found in skills folder",
        }

    requested_file = (skill_dir / file_path).resolve()
    if not requested_file.is_relative_to(skill_dir):
        return {
            "success": False,
            "skill_name": skill_name,
            "file_path": file_path,
            "error": "Path traversal detected: cannot access files outside skill folder",
        }

    if not requested_file.exists():
        return {
            "success": False,
            "skill_name": skill_name,
            "file_path": file_path,
            "error": f"File '{file_path}' not found in skill '{skill_name}'",
        }

    try:
        content = requested_file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return {
            "success": False,
            "skill_name": skill_name,
            "file_path": file_path,
            "error": f"Cannot read file '{file_path}': invalid UTF-8",
        }
    except OSError as exc:
        return {
            "success": False,
            "skill_name": skill_name,
            "file_path": file_path,
            "error": f"Cannot read file '{file_path}': {exc}",
        }

    result = {
        "success": True,
        "skill_name": skill_name,
        "file_path": file_path,
        "content": content,
        "size_bytes": requested_file.stat().st_size,
        "encoding": "utf-8",
    }
    _log_duration("read_file_in_skill", start_time)
    return result


def run_python_script(
    skill_name: str,
    script: str,
    skills_folder: Path,
    timeout_seconds: int,
) -> Dict[str, object]:
    """Execute a Python script using the skill's venv interpreter."""
    start_time = time.perf_counter()
    skills_folder = skills_folder.resolve()
    if not validate_skill_name(skill_name):
        return {
            "error": (
                f"Invalid skill name: '{skill_name}'. Skill names must not contain '/', "
                "'\\', or '..'"
            )
        }

    skill_path = (skills_folder / skill_name).resolve()
    if not skill_path.exists():
        return {"error": f"Skill '{skill_name}' not found in skills folder"}

    python_executable = find_python_executable(skill_path)
    if python_executable is None:
        return {"error": f"Skill '{skill_name}' does not have a venv. Cannot execute script."}

    result = run_script(python_executable, script, skill_path, timeout_seconds)

    payload: Dict[str, object] = {
        "skill_name": skill_name,
        "stdout": result.get("stdout", ""),
        "stderr": result.get("stderr", ""),
        "returncode": result.get("returncode", -1),
        "timed_out": result.get("timed_out", False),
    }

    if "error" in result:
        payload["error"] = result["error"]

    _log_duration("run_python_script", start_time)
    return payload
