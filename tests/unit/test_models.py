from pathlib import Path

from skills_runner.models import ScriptExecution, Skill


def test_skill_model_fields(tmp_path):
    skill_path = tmp_path / "calc"
    doc_path = skill_path / "SKILL.MD"

    skill = Skill(
        name="calc",
        folder_path=skill_path,
        documentation_path=doc_path,
        venv_path=None,
        has_venv=False,
        has_documentation=False,
    )

    assert skill.name == "calc"
    assert skill.folder_path == skill_path
    assert skill.documentation_path == doc_path


def test_script_execution_fields(tmp_path):
    execution = ScriptExecution(
        skill_name="calc",
        script="print(1)",
        working_directory=tmp_path,
        python_executable=tmp_path / "python",
        timeout=30,
        stdout="ok",
        stderr="",
        returncode=0,
        timed_out=False,
        error=None,
    )

    assert execution.skill_name == "calc"
    assert execution.returncode == 0
