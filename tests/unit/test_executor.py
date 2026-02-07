from pathlib import Path

from skills_runner.executor import find_python_executable, run_script


def test_find_python_executable_prefers_unix(tmp_path):
    venv_path = tmp_path / "venv" / "bin"
    venv_path.mkdir(parents=True)
    python_path = venv_path / "python"
    python_path.write_text("")

    found = find_python_executable(tmp_path)

    assert found == python_path


def test_run_script_returns_error_for_invalid_executable(tmp_path):
    python_path = tmp_path / "python"
    python_path.write_text("")

    result = run_script(python_path, "print('hi')", tmp_path, timeout=1)

    assert result["timed_out"] is False
    assert "error" in result
