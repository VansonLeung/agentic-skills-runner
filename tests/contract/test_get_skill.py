from pathlib import Path

from skills_runner.skills_tool import get_skill


def test_get_skill_reads_skill_md(tmp_path):
    skill_dir = tmp_path / "calculator"
    skill_dir.mkdir()
    (skill_dir / "SKILL.MD").write_text("# Calculator")

    result = get_skill("calculator", tmp_path)

    assert result["skill_name"] == "calculator"
    assert "Calculator" in result["documentation"]
