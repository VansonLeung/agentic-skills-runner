from skills_runner.skills_tool import run_python_script


def test_run_python_script_missing_skill(tmp_path):
    result = run_python_script("missing", "print('hi')", tmp_path, timeout_seconds=5)

    assert "error" in result
