from skills_runner.skills_tool import read_files_in_skill


def test_read_files_in_skill_reads_files(tmp_path):
    skill_dir = tmp_path / "docs"
    skill_dir.mkdir()
    (skill_dir / "SKILL.MD").write_text("# Docs")
    (skill_dir / "notes.txt").write_text("hello")
    (skill_dir / "guide.txt").write_text("world")

    result = read_files_in_skill("docs", ["notes.txt", "guide.txt"], tmp_path)

    assert result["success"] is True
    assert result["files"][0]["content"] == "hello"
    assert result["files"][1]["content"] == "world"