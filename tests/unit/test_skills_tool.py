from skills_runner.skills_tool import get_skill, list_skills, read_file_in_skill, run_python_script


def test_list_skills_filters_invalid_names(tmp_path):
    (tmp_path / "valid").mkdir()
    (tmp_path / "..").mkdir(exist_ok=True)

    result = list_skills(tmp_path)

    assert "valid" in result.get("skills", [])


def test_get_skill_returns_error_for_missing_skill(tmp_path):
    result = get_skill("missing", tmp_path)

    assert "error" in result


def test_read_file_in_skill_blocks_traversal(tmp_path):
    (tmp_path / "docs").mkdir()

    result = read_file_in_skill("docs", "../secret.txt", tmp_path)

    assert result.get("success") is False


def test_run_python_script_missing_skill(tmp_path):
    result = run_python_script("missing", "print('hi')", tmp_path, timeout_seconds=5)

    assert "error" in result
