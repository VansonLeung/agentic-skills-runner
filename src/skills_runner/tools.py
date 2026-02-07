LIST_SKILLS_DEF = {
    "type": "function",
    "function": {
        "name": "list_skills",
        "description": "List all available skills in the skills folder. Returns skill names.",
        "parameters": {"type": "object", "properties": {}, "required": []},
    },
}

GET_SKILL_DEF = {
    "type": "function",
    "function": {
        "name": "get_skill",
        "description": "Read the SKILL.MD documentation for a specific skill. SKILL.MD serves as the table of contents.",
        "parameters": {
            "type": "object",
            "properties": {
                "skill_name": {
                    "type": "string",
                    "description": "Name of the skill (folder name)",
                }
            },
            "required": ["skill_name"],
        },
    },
}

READ_FILE_IN_SKILL_DEF = {
    "type": "function",
    "function": {
        "name": "read_file_in_skill",
        "description": "Read any file within a skill's folder. Use this when SKILL.MD references additional files.",
        "parameters": {
            "type": "object",
            "properties": {
                "skill_name": {
                    "type": "string",
                    "description": "Name of the skill (folder name)",
                },
                "file_path": {
                    "type": "string",
                    "description": "Relative path within skill (e.g., 'examples/usage.py')",
                },
            },
            "required": ["skill_name", "file_path"],
        },
    },
}

RUN_PYTHON_SCRIPT_DEF = {
    "type": "function",
    "function": {
        "name": "run_python_script",
        "description": "Execute a Python script in the specified skill's venv and return stdout/stderr.",
        "parameters": {
            "type": "object",
            "properties": {
                "skill_name": {
                    "type": "string",
                    "description": "Name of the skill (folder name)",
                },
                "script": {
                    "type": "string",
                    "description": "Python code to execute",
                },
            },
            "required": ["skill_name", "script"],
        },
    },
}

SKILLS_TOOLS = [LIST_SKILLS_DEF, GET_SKILL_DEF, READ_FILE_IN_SKILL_DEF, RUN_PYTHON_SCRIPT_DEF]
