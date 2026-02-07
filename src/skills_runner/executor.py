from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Dict


def find_python_executable(skill_path: Path) -> Path | None:
    """Locate the venv Python interpreter for a skill folder."""
    venv_path = skill_path / "venv"
    unix_python = venv_path / "bin" / "python"
    windows_python = venv_path / "Scripts" / "python.exe"

    if unix_python.exists():
        return unix_python
    if windows_python.exists():
        return windows_python

    return None


def run_script(python_executable: Path, script: str, cwd: Path, timeout: int) -> Dict[str, object]:
    """Run a Python script with timeout and capture output."""
    try:
        result = subprocess.run(
            [str(python_executable), "-c", script],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or "",
            "returncode": -1,
            "timed_out": True,
            "error": f"Script execution exceeded timeout of {timeout} seconds",
        }
    except OSError as exc:
        return {
            "stdout": "",
            "stderr": "",
            "returncode": -1,
            "timed_out": False,
            "error": f"Error executing script: {exc}",
        }
