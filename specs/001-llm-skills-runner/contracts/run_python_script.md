# Tool Contract: run_python_script

**Operation**: Execute Python script in skill's virtual environment

**Tool Name**: `run_python_script`

**Description**: Execute a Python script in the specified skill's virtual environment. Script has full filesystem access (MVP simplification). Returns stdout, stderr, and exit code. Script runs with the skill folder as working directory.

## Input Schema

**Parameters**:
```json
{
  "type": "object",
  "properties": {
    "skill_name": {
      "type": "string",
      "description": "Name of the skill whose venv to use"
    },
    "script": {
      "type": "string",
      "description": "Python code to execute"
    }
  },
  "required": ["skill_name", "script"]
}
```

**Example LLM Tool Call**:
```json
{
  "id": "call_def456",
  "type": "function",
  "function": {
    "name": "run_python_script",
    "arguments": "{\"skill_name\": \"calculator\", \"script\": \"print(2 + 2)\"}"
  }
}
```

## Output Schema

**Success Response**:
```json
{
  "skill_name": "calculator",
  "stdout": "output text",
  "stderr": "error text (if any)",
  "returncode": 0,
  "timed_out": false
}
```

**Timeout Response**:
```json
{
  "skill_name": "calculator",
  "stdout": "partial output if any",
  "stderr": "partial errors if any",
  "returncode": -1,
  "timed_out": true,
  "error": "Script execution exceeded timeout of 30 seconds"
}
```

**Error Response**:
```json
{
  "error": "Error message describing what went wrong"
}
```

## Examples

### Example 1: Successful Execution

**Input**:
```json
{
  "skill_name": "calculator",
  "script": "result = 2 + 2\nprint(f'Result: {result}')"
}
```

**Output**:
```json
{
  "skill_name": "calculator",
  "stdout": "Result: 4\n",
  "stderr": "",
  "returncode": 0,
  "timed_out": false
}
```

**Tool Result Message**:
```json
{
  "role": "tool",
  "tool_call_id": "call_def456",
  "name": "run_python_script",
  "content": "{\"skill_name\": \"calculator\", \"stdout\": \"Result: 4\\n\", \"stderr\": \"\", \"returncode\": 0, \"timed_out\": false}"
}
```

### Example 2: Script with Syntax Error

**Input**:
```json
{
  "skill_name": "calculator",
  "script": "print(2 + )"
}
```

**Output**:
```json
{
  "skill_name": "calculator",
  "stdout": "",
  "stderr": "  File \"<string>\", line 1\n    print(2 + )\n              ^\nSyntaxError: invalid syntax\n",
  "returncode": 1,
  "timed_out": false
}
```

### Example 3: Script with Runtime Error

**Input**:
```json
{
  "skill_name": "calculator",
  "script": "x = 1 / 0"
}
```

**Output**:
```json
{
  "skill_name": "calculator",
  "stdout": "",
  "stderr": "Traceback (most recent call last):\n  File \"<string>\", line 1, in <module>\nZeroDivisionError: division by zero\n",
  "returncode": 1,
  "timed_out": false
}
```

### Example 4: Timeout

**Input**:
```json
{
  "skill_name": "calculator",
  "script": "import time\nwhile True:\n    time.sleep(1)"
}
```

**Output**:
```json
{
  "skill_name": "calculator",
  "stdout": "",
  "stderr": "",
  "returncode": -1,
  "timed_out": true,
  "error": "Script execution exceeded timeout of 30 seconds"
}
```

### Example 5: Skill Without venv

**Input**:
```json
{
  "skill_name": "no_venv_skill",
  "script": "print('hello')"
}
```

**Output**:
```json
{
  "error": "Skill 'no_venv_skill' does not have a venv. Cannot execute script."
}
```

### Example 6: Invalid Skill Name

**Input**:
```json
{
  "skill_name": "../../../etc",
  "script": "print('hello')"
}
```

**Output**:
```json
{
  "error": "Invalid skill name: '../../../etc'. Skill names must not contain '/', '\\', or '..'"
}
```

### Example 7: File Operations in Skill Folder

**Input**:
```json
{
  "skill_name": "calculator",
  "script": "with open('output.txt', 'w') as f:\n    f.write('Result: 42')\nprint('File written')"
}
```

**Output**:
```json
{
  "skill_name": "calculator",
  "stdout": "File written\n",
  "stderr": "",
  "returncode": 0,
  "timed_out": false
}
```

**Note**: File is written to `skills/calculator/output.txt` (working directory is skill folder)

### Example 8: Using Skill-Specific Packages

**Input**:
```json
{
  "skill_name": "data_analysis",
  "script": "import pandas as pd\ndf = pd.DataFrame({'a': [1, 2, 3]})\nprint(df.sum())"
}
```

**Output**:
```json
{
  "skill_name": "data_analysis",
  "stdout": "a    6\ndtype: int64\n",
  "stderr": "",
  "returncode": 0,
  "timed_out": false
}
```

**Note**: Packages installed in skill's venv are available (pandas in this case)

## Behavior

1. **Validation**: Verify skill_name is safe and skill exists
2. **venv Check**: Verify skill has a venv with Python interpreter
3. **Execution**: Run script using subprocess with:
   - Python interpreter: `{skill_folder}/venv/bin/python` (or `Scripts\python.exe` on Windows)
   - Working directory: `{skill_folder}`
   - Command: `python -c "<script>"`
   - Timeout: 30 seconds (configurable)
   - Capture: stdout and stderr
4. **Result**: Return all output and exit code
5. **Performance**: Complete simple scripts (<100 lines) in <5 seconds

## Error Conditions

| Condition | Response |
|-----------|----------|
| Invalid skill name | `{"error": "Invalid skill name: '...'. Skill names must not contain..."}` |
| Skill not found | `{"error": "Skill '...' not found in skills folder"}` |
| Skill has no venv | `{"error": "Skill '...' does not have a venv. Cannot execute script."}` |
| Python interpreter not found | `{"error": "Python interpreter not found in venv for skill '...'"}` |
| Timeout exceeded | `{..., "timed_out": true, "error": "Script execution exceeded timeout..."}` |
| Permission denied | `{"error": "Permission denied executing script in skill '...'"}` |

## Security Considerations

### MVP Simplified Security Model

**Enforced (MUST)**:
- **Skill name validation**: Reject names with directory traversal characters (`/`, `\`, `..`)
- **Working directory**: Always set to skill folder (convention for relative paths)
- **Timeout**: Enforce maximum execution time (default 30 seconds)
- **venv isolation**: Use skill's Python interpreter (package/dependency isolation only)

**NOT Enforced (MVP Simplification - User's Responsibility)**:
- **Filesystem access**: Scripts have **full filesystem access** (read/write anywhere)
- **Network access**: Scripts can make network requests (Python's strength, useful for API skills)
- **Resource limits**: No CPU/memory limits beyond OS process limits
- **Subprocess spawning**: Scripts can spawn subprocesses
- **Privilege escalation**: No prevention (relies on OS user permissions)

**MVP Trade-off Rationale**: 
- Security/sandboxing adds significant complexity (Docker, seccomp, chroot)
- Violates KISS/YAGNI principles for MVP validation
- **Trust Model**: MVP assumes users control installed skills and LLM behavior
- **User Responsibility**: Users must audit skills and monitor LLM-generated code
- **Post-MVP Migration Path**: Add Docker containers, chroot jails, or seccomp-bpf filters after MVP validation

**Risk Awareness**:
- Scripts can read/write sensitive files (e.g., `/etc/passwd`, `~/.ssh/`)
- Scripts can make network requests to any endpoint
- Scripts can consume system resources
- LLM-generated code should be visible to user before execution (FR-044)

**Future Enhancements** (Post-MVP):
- Docker container execution for full isolation
- Resource limits (cgroups, ulimit)
- Network isolation (firewall rules, no-network mode)
- Filesystem restrictions (read-only mounts, chroot)
- Approval workflow for filesystem writes outside skill folder

## Implementation Notes

```python
import subprocess
from pathlib import Path

def run_python_script(skill_name: str, script: str, skills_folder: Path, timeout: int = 30) -> dict:
    # Validate skill name
    if not validate_skill_name(skill_name):
        return {"error": f"Invalid skill name: '{skill_name}'..."}
    
    # Check skill exists
    skill_path = skills_folder / skill_name
    if not skill_path.exists():
        return {"error": f"Skill '{skill_name}' not found..."}
    
    # Check venv exists
    venv_path = skill_path / "venv"
    python_exe = venv_path / "bin" / "python"  # Linux/Mac
    if not python_exe.exists():
        python_exe = venv_path / "Scripts" / "python.exe"  # Windows
    
    if not python_exe.exists():
        return {"error": f"Skill '{skill_name}' does not have a venv..."}
    
    # Execute script
    try:
        result = subprocess.run(
            [str(python_exe), "-c", script],
            cwd=str(skill_path),
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return {
            "skill_name": skill_name,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "timed_out": False
        }
    except subprocess.TimeoutExpired as e:
        return {
            "skill_name": skill_name,
            "stdout": e.stdout or "",
            "stderr": e.stderr or "",
            "returncode": -1,
            "timed_out": True,
            "error": f"Script execution exceeded timeout of {timeout} seconds"
        }
    except Exception as e:
        return {"error": f"Error executing script: {e}"}
```

## Performance Requirements

- **Simple scripts** (<100 lines): Complete in <5 seconds (SC-006)
- **Timeout**: Configurable, default 30 seconds
- **Overhead**: <200ms subprocess spawn and teardown
