# Contract: READ_FILE_IN_SKILL

**Tool Name**: `read_file_in_skill`  
**Feature**: 001-llm-skills-runner  
**Created**: 2026-02-07  
**Purpose**: LLM tool contract for reading files within a skill folder

## Overview

READ_FILE_IN_SKILL allows the LLM to read any file within a skill's folder structure. SKILL.MD serves as the main table of contents, referencing additional documentation, examples, or configuration files. This tool provides access to those referenced files.

## Tool Definition

```json
{
  "type": "function",
  "function": {
    "name": "read_file_in_skill",
    "description": "Read any file within a skill's folder. Use this when SKILL.MD references additional documentation, examples, or configuration files. Path must be relative to skill folder.",
    "parameters": {
      "type": "object",
      "properties": {
        "skill_name": {
          "type": "string",
          "description": "Name of the skill (folder name containing the file)"
        },
        "file_path": {
          "type": "string",
          "description": "Relative path to file within skill folder (e.g., 'examples/usage.py', 'docs/api.md')"
        }
      },
      "required": ["skill_name", "file_path"]
    }
  }
}
```

## Input Schema

```python
{
    "skill_name": str,    # Skill folder name
    "file_path": str      # Relative path within skill folder
}
```

**Validation Rules**:
- `skill_name` must not be empty
- `skill_name` must not contain `/`, `\`, or `..` (prevent directory traversal)
- `file_path` must not be empty
- Resolved path must be within skill folder (security boundary)

## Output Schema

### Success Response

```python
{
    "success": True,
    "skill_name": str,
    "file_path": str,
    "content": str,           # File contents as text
    "size_bytes": int,
    "encoding": str           # e.g., "utf-8"
}
```

**Returned to LLM** (as tool result message):
```json
{
  "role": "tool",
  "tool_call_id": "call_abc123",
  "name": "read_file_in_skill",
  "content": "<file contents as text>"
}
```

### Error Response

```python
{
    "success": False,
    "skill_name": str,
    "file_path": str,
    "error": str              # Error message
}
```

**Common Error Messages**:
- `"Skill 'skill_name' not found in skills folder"`
- `"File 'file_path' not found in skill 'skill_name'"`
- `"Path traversal detected: cannot access files outside skill folder"`
- `"Cannot read file 'file_path': <reason>"`
- `"Invalid skill name: must not contain special characters"`

## Behavior Specification

### File Reading

1. **Skill Lookup**: Locate skill folder at `{skills_folder}/{skill_name}`
2. **Path Resolution**: Resolve `{skill_folder}/{file_path}` to absolute path
3. **Security Check**: Verify resolved path is within skill folder (prevent `../../../etc/passwd`)
4. **File Read**: Read file contents as text (assume UTF-8, fallback to other encodings)
5. **Return**: File contents as string

### Security Boundaries

- **Directory Traversal Prevention**: Use `pathlib.Path.resolve()` and check `is_relative_to(skill_folder)`
- **Skill Folder Isolation**: Files outside skill folder are inaccessible
- **Parent Skills Directory Access**: NOT allowed (each skill is isolated)

**Example Security Check**:
```python
from pathlib import Path

def read_file_in_skill(skill_name: str, file_path: str) -> str:
    # Validate skill name
    if any(c in skill_name for c in ['/', '\\', '..']):
        raise ValueError("Invalid skill name")
    
    # Build paths
    skill_dir = Path(skills_folder) / skill_name
    requested_file = (skill_dir / file_path).resolve()
    
    # Security: ensure resolved path is within skill folder
    if not requested_file.is_relative_to(skill_dir):
        raise ValueError(f"Path traversal detected: {file_path}")
    
    # Read file
    return requested_file.read_text()
```

### Error Handling

| Condition | Behavior |
|-----------|----------|
| Skill folder not found | Return error: "Skill 'X' not found" |
| File not found | Return error: "File 'X' not found in skill 'Y'" |
| Path traversal attempt | Return error: "Path traversal detected" |
| Invalid skill name | Return error: "Invalid skill name" |
| Binary file (unreadable as text) | Attempt text decode, return error if fails |
| Insufficient permissions | Return error: "Cannot read file" |

## Examples

### Example 1: Read Python Example File

**LLM Tool Call**:
```json
{
  "id": "call_abc123",
  "type": "function",
  "function": {
    "name": "read_file_in_skill",
    "arguments": "{\"skill_name\": \"calculator\", \"file_path\": \"examples/basic.py\"}"
  }
}
```

**System Execution**:
```python
# Locate: skills/calculator/examples/basic.py
# Read file contents
content = """
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b
"""
```

**Tool Result Message** (sent to LLM):
```json
{
  "role": "tool",
  "tool_call_id": "call_abc123",
  "name": "read_file_in_skill",
  "content": "\ndef add(a, b):\n    return a + b\n\ndef subtract(a, b):\n    return a - b\n"
}
```

**User Visibility**:
```
[Tool Call] read_file_in_skill(skill_name="calculator", file_path="examples/basic.py")
[Tool Result] <file contents displayed>
```

---

### Example 2: Read Documentation Markdown

**LLM Tool Call**:
```json
{
  "function": {
    "name": "read_file_in_skill",
    "arguments": "{\"skill_name\": \"weather\", \"file_path\": \"docs/api_reference.md\"}"
  }
}
```

**System Execution**:
```python
# Locate: skills/weather/docs/api_reference.md
content = "# Weather API Reference\n\n## get_forecast(location)\n..."
```

**Tool Result**:
```json
{
  "role": "tool",
  "content": "# Weather API Reference\n\n## get_forecast(location)\n..."
}
```

---

### Example 3: File Not Found

**LLM Tool Call**:
```json
{
  "function": {
    "name": "read_file_in_skill",
    "arguments": "{\"skill_name\": \"calculator\", \"file_path\": \"examples/missing.py\"}"
  }
}
```

**Tool Result**:
```json
{
  "role": "tool",
  "content": "ERROR: File 'examples/missing.py' not found in skill 'calculator'"
}
```

---

### Example 4: Path Traversal Attempt

**LLM Tool Call**:
```json
{
  "function": {
    "name": "read_file_in_skill",
    "arguments": "{\"skill_name\": \"calculator\", \"file_path\": \"../../../etc/passwd\"}"
  }
}
```

**System Execution**:
```python
# Resolved path: /etc/passwd (outside skills/calculator/)
# Security check fails
```

**Tool Result**:
```json
{
  "role": "tool",
  "content": "ERROR: Path traversal detected: cannot access files outside skill folder"
}
```

---

### Example 5: Skill Not Found

**LLM Tool Call**:
```json
{
  "function": {
    "name": "read_file_in_skill",
    "arguments": "{\"skill_name\": \"nonexistent\", \"file_path\": \"README.md\"}"
  }
}
```

**Tool Result**:
```json
{
  "role": "tool",
  "content": "ERROR: Skill 'nonexistent' not found in skills folder"
}
```

---

### Example 6: Read Configuration File

**LLM Tool Call**:
```json
{
  "function": {
    "name": "read_file_in_skill",
    "arguments": "{\"skill_name\": \"data_processor\", \"file_path\": \"config.json\"}"
  }
}
```

**System Execution**:
```python
# Locate: skills/data_processor/config.json
content = '{"api_endpoint": "https://example.com", "timeout": 30}'
```

**Tool Result**:
```json
{
  "role": "tool",
  "content": "{\"api_endpoint\": \"https://example.com\", \"timeout\": 30}"
}
```

---

### Example 7: Subdirectory Navigation

**LLM Tool Call**:
```json
{
  "function": {
    "name": "read_file_in_skill",
    "arguments": "{\"skill_name\": \"ml_model\", \"file_path\": \"data/samples/input.txt\"}"
  }
}
```

**System Execution**:
```python
# Locate: skills/ml_model/data/samples/input.txt
# Allowed: within skill folder hierarchy
content = "sample1\nsample2\nsample3"
```

**Tool Result**:
```json
{
  "role": "tool",
  "content": "sample1\nsample2\nsample3"
}
```

---

## Performance Requirements

- **File Read**: Complete in <500ms for files up to 1MB
- **Path Resolution**: <10ms for security validation
- **Error Response**: <100ms for invalid requests

## Testing Checklist

- [ ] Read file in skill root directory
- [ ] Read file in skill subdirectory (examples/)
- [ ] Read file in nested subdirectory (docs/advanced/)
- [ ] Read various file types (.py, .md, .json, .txt, .yaml)
- [ ] File not found error
- [ ] Skill not found error
- [ ] Path traversal attempt (`../../../etc/passwd`)
- [ ] Path traversal attempt (`..\\..\\..\\Windows\\System32`)
- [ ] Invalid skill name with special characters
- [ ] Large file (1MB+) performance
- [ ] Binary file handling (graceful error)
- [ ] Empty file
- [ ] Unicode content (non-ASCII)
- [ ] Tool result visible to user (transparency)

## Notes

- **SKILL.MD as Index**: LLM should read SKILL.MD first to understand what additional files exist
- **Lazy Loading**: Files are only read when explicitly requested by LLM
- **No Caching**: Each tool call reads from disk (MVP simplicity)
- **Text Files Only**: Binary files require special handling or encoding
- **Cross-Platform**: Path handling works on Windows, Linux, macOS
