from pathlib import Path

from skills_runner.skills_tool import list_skills


def test_list_skills_returns_sorted_names(tmp_path):
    (tmp_path / "beta").mkdir()
    (tmp_path / "alpha").mkdir()
    (tmp_path / "not_a_dir.txt").write_text("ignore")

    result = list_skills(tmp_path)

    assert result == {"skills": ["alpha", "beta"]}
