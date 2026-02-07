from skills_runner.skills_tool import read_file_in_skill


def test_read_file_in_skill_reads_file(tmp_path):
    skill_dir = tmp_path / "docs"
    skill_dir.mkdir()
    (skill_dir / "SKILL.MD").write_text("# Docs")
    (skill_dir / "notes.txt").write_text("hello")

    result = read_file_in_skill("docs", "notes.txt", tmp_path)

    assert result["content"] == "hello"
