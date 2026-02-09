from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional
import logging
import subprocess
import sys
import time
import uuid
import venv

from .executor import find_python_executable, run_script

# In-memory store for pending skill creation requests awaiting user confirmation
_pending_creations: Dict[str, Dict[str, object]] = {}

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


def write_file_in_skill(
    skill_name: str,
    file_path: str,
    content: str,
    skills_folder: Path,
) -> Dict[str, object]:
    """Write or overwrite a file within a skill folder with path validation."""
    start_time = time.perf_counter()
    skills_folder = skills_folder.resolve()

    if not validate_skill_name(skill_name):
        return {"success": False, "error": "Invalid skill name"}

    if not file_path:
        return {"success": False, "error": "Invalid file path"}

    # Block writing to venv or hidden directories
    normalized = file_path.replace("\\", "/")
    if normalized.startswith("venv/") or "/venv/" in normalized:
        return {"success": False, "error": "Cannot write into the venv directory"}
    if any(part.startswith(".") for part in normalized.split("/")):
        return {"success": False, "error": "Cannot write to hidden directories/files"}

    skill_dir = skills_folder / skill_name
    if not skill_dir.exists():
        return {"success": False, "error": f"Skill '{skill_name}' not found"}

    target = (skill_dir / file_path).resolve()
    if not target.is_relative_to(skill_dir):
        return {"success": False, "error": "Path traversal detected: cannot write outside skill folder"}

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    except OSError as exc:
        return {"success": False, "error": f"Failed to write file: {exc}"}

    result: Dict[str, object] = {
        "success": True,
        "skill_name": skill_name,
        "file_path": file_path,
        "size_bytes": len(content.encode("utf-8")),
    }
    _log_duration("write_file_in_skill", start_time)
    return result


def create_skill(
    skill_name: str,
    skill_md_content: str,
    requirements: Optional[str],
    skills_folder: Path,
) -> Dict[str, object]:
    """Propose creating a new skill. Returns a preview requiring user confirmation."""
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
    if skill_path.exists():
        return {"error": f"Skill '{skill_name}' already exists"}

    # Build a preview of what will be created
    actions: List[str] = [
        f"Create folder: {skill_path}",
        f"Write SKILL.md ({len(skill_md_content)} chars)",
        "Create Python virtual environment (venv)",
    ]
    if requirements and requirements.strip():
        pkgs = [line.strip() for line in requirements.strip().splitlines() if line.strip() and not line.strip().startswith("#")]
        if pkgs:
            actions.append(f"pip install: {', '.join(pkgs)}")

    # Store the pending creation with a confirmation token
    token = uuid.uuid4().hex
    _pending_creations[token] = {
        "skill_name": skill_name,
        "skill_md_content": skill_md_content,
        "requirements": requirements,
        "skills_folder": str(skills_folder),
    }

    result: Dict[str, object] = {
        "requires_confirmation": True,
        "confirmation_token": token,
        "skill_name": skill_name,
        "preview_actions": actions,
        "message": "User must approve this action before the skill is created.",
    }
    _log_duration("create_skill", start_time)
    return result


def confirm_create_skill(token: str) -> Dict[str, object]:
    """Execute a previously proposed skill creation after user confirmation."""
    start_time = time.perf_counter()

    pending = _pending_creations.pop(token, None)
    if pending is None:
        return {"error": "Invalid or expired confirmation token"}

    skill_name = str(pending["skill_name"])
    skill_md_content = str(pending["skill_md_content"])
    requirements = pending.get("requirements")
    skills_folder = Path(str(pending["skills_folder"]))

    skill_path = skills_folder / skill_name

    # 1. Create folder
    try:
        skill_path.mkdir(parents=True, exist_ok=False)
    except OSError as exc:
        return {"error": f"Failed to create skill folder: {exc}"}

    # 2. Write SKILL.md
    try:
        (skill_path / "SKILL.md").write_text(skill_md_content, encoding="utf-8")
    except OSError as exc:
        return {"error": f"Failed to write SKILL.md: {exc}"}

    # 3. Write requirements.txt (if provided)
    has_requirements = False
    if requirements and requirements.strip():
        try:
            (skill_path / "requirements.txt").write_text(requirements.strip() + "\n", encoding="utf-8")
            has_requirements = True
        except OSError as exc:
            return {"error": f"Failed to write requirements.txt: {exc}"}

    # 4. Create venv
    venv_path = skill_path / "venv"
    try:
        venv.create(str(venv_path), with_pip=True)
    except Exception as exc:
        return {
            "warning": f"Skill folder created but venv creation failed: {exc}",
            "skill_name": skill_name,
            "folder_created": True,
            "venv_created": False,
        }

    # 5. pip install requirements
    pip_output = ""
    if has_requirements:
        pip_executable = venv_path / "bin" / "pip"
        if not pip_executable.exists():
            pip_executable = venv_path / "Scripts" / "pip.exe"

        if pip_executable.exists():
            try:
                proc = subprocess.run(
                    [str(pip_executable), "install", "-r", str(skill_path / "requirements.txt")],
                    cwd=str(skill_path),
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                pip_output = proc.stdout
                if proc.returncode != 0:
                    return {
                        "warning": f"Skill created but pip install failed",
                        "skill_name": skill_name,
                        "folder_created": True,
                        "venv_created": True,
                        "pip_stderr": proc.stderr,
                    }
            except subprocess.TimeoutExpired:
                return {
                    "warning": "Skill created but pip install timed out (120s)",
                    "skill_name": skill_name,
                    "folder_created": True,
                    "venv_created": True,
                }

    result: Dict[str, object] = {
        "success": True,
        "skill_name": skill_name,
        "folder_created": True,
        "venv_created": True,
        "requirements_installed": has_requirements,
        "pip_output": pip_output,
        "message": f"Skill '{skill_name}' created successfully!",
    }
    _log_duration("confirm_create_skill", start_time)
    return result
