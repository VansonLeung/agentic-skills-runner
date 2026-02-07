# Tool Contract: get_skill

**Operation**: Read skill documentation from SKILL.MD file

**Tool Name**: `get_skill`

**Description**: Read the SKILL.MD documentation for a specific skill. Returns the full text content of the documentation file.

## Input Schema

**Parameters**:
```json
{
  "type": "object",
  "properties": {
    "skill_name": {
      "type": "string",
      "description": "Name of the skill (folder name)"
    }
  },
  "required": ["skill_name"]
}
```

**Example LLM Tool Call**:
```json
{
  "id": "call_xyz789",
  "type": "function",
  "function": {
    "name": "get_skill",
    "arguments": "{\"skill_name\": \"calculator\"}"
  }
}
```

## Output Schema

**Success Response**:
```json
{
  "skill_name": "calculator",
  "documentation": "# Calculator Skill\n\nThis skill provides..."
}
```

**Error Response**:
```json
{
  "error": "Error message describing what went wrong"
}
```

## Examples

### Example 1: Successful Read

**Input**:
```json
{
  "skill_name": "calculator"
}
```

**Output**:
```json
{
  "skill_name": "calculator",
  "documentation": "# Calculator Skill\n\nProvides basic arithmetic operations.\n\n## Usage\n\n```python\nresult = 2 + 2\nprint(result)\n```"
}
```

**Tool Result Message**:
```json
{
  "role": "tool",
  "tool_call_id": "call_xyz789",
  "name": "get_skill",
  "content": "{\"skill_name\": \"calculator\", \"documentation\": \"# Calculator Skill\\n\\nProvides basic arithmetic operations...\"}"
}
```

### Example 2: SKILL.MD Not Found

**Input**:
```json
{
  "skill_name": "calculator"
}
```

**Output**:
```json
{
  "error": "SKILL.MD not found for skill 'calculator'"
}
```

### Example 3: Invalid Skill Name (Security)

**Input**:
```json
{
  "skill_name": "../../../etc/passwd"
}
```

**Output**:
```json
{
  "error": "Invalid skill name: '../../../etc/passwd'. Skill names must not contain '/', '\\', or '..'"
}
```

### Example 4: Skill Folder Doesn't Exist

**Input**:
```json
{
  "skill_name": "nonexistent"
}
```

**Output**:
```json
{
  "error": "Skill 'nonexistent' not found in skills folder"
}
```

## Behavior

1. **Validation**: Verify skill_name is safe (no directory traversal)
2. **Location**: Look for `{skills_folder}/{skill_name}/SKILL.MD`
3. **Reading**: Read entire file content as UTF-8 text
4. **Size Limit**: Support files up to 1MB (per performance target)
5. **Performance**: Complete in <500ms for 1MB files

## Error Conditions

| Condition | Response |
|-----------|----------|
| Skill name contains `/`, `\`, or `..` | `{"error": "Invalid skill name: '...'. Skill names must not contain..."}` |
| Skill folder doesn't exist | `{"error": "Skill '...' not found in skills folder"}` |
| SKILL.MD file doesn't exist | `{"error": "SKILL.MD not found for skill '...'"}` |
| File not readable | `{"error": "Permission denied reading SKILL.MD for skill '...'"}` |
| File too large (>1MB) | `{"error": "SKILL.MD too large (>1MB) for skill '...'"}` |
| File not UTF-8 | `{"error": "SKILL.MD contains invalid UTF-8 for skill '...'"}` |

## Security Requirements

- **MUST** validate skill_name before constructing file path
- **MUST** reject names with `/`, `\`, or `..`
- **MUST** only read files within configured skills folder
- **MUST** handle symbolic links safely (resolve or reject)

## Implementation Notes

```python
def validate_skill_name(name: str) -> bool:
    return (
        name and 
        '/' not in name and 
        '\\' not in name and 
        '..' not in name
    )

def get_skill(skill_name: str, skills_folder: Path) -> dict:
    if not validate_skill_name(skill_name):
        return {"error": f"Invalid skill name: '{skill_name}'..."}
    
    skill_path = skills_folder / skill_name
    if not skill_path.exists():
        return {"error": f"Skill '{skill_name}' not found..."}
    
    doc_path = skill_path / "SKILL.MD"
    if not doc_path.exists():
        return {"error": f"SKILL.MD not found for skill '{skill_name}'"}
    
    try:
        content = doc_path.read_text(encoding="utf-8")
        return {"skill_name": skill_name, "documentation": content}
    except Exception as e:
        return {"error": f"Error reading SKILL.MD: {e}"}
```
