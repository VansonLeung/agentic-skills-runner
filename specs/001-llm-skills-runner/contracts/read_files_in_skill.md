# Contract: READ_FILES_IN_SKILL

**Tool Name**: `read_files_in_skill`  
**Feature**: 001-llm-skills-runner  
**Created**: 2026-02-07  
**Purpose**: LLM tool contract for reading one or more files within a skill folder

## Overview

READ_FILES_IN_SKILL allows the LLM to read one or more files within a skill's folder structure. SKILL.MD serves as the main table of contents, referencing additional documentation, examples, or configuration files. This tool provides access to those referenced files in a single batched call.

## Tool Definition

```json
{
  "type": "function",
  "function": {
    "name": "read_files_in_skill",
    "description": "Read one or more files within a skill's folder. Use this when SKILL.MD references additional documentation, examples, or configuration files. Paths must be relative to the skill folder.",
    "parameters": {
      "type": "object",
      "properties": {
        "skill_name": {
          "type": "string",
          "description": "Name of the skill (folder name containing the files)"
        },
        "file_paths": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "description": "Relative paths to files within the skill folder (e.g., ['examples/usage.py', 'docs/api.md'])"
        }
      },
      "required": ["skill_name", "file_paths"]
    }
  }
}
```

## Input Schema

```python
{
    "skill_name": str,
    "file_paths": list[str]
}
```

**Validation Rules**:
- `skill_name` must not be empty
- `skill_name` must not contain `/`, `\`, or `..`
- `file_paths` must be a non-empty list
- Each entry in `file_paths` must be a non-empty relative path
- Each resolved path must remain within the skill folder

## Output Schema

### Success Or Partial-Success Response

```python
{
    "success": bool,
    "skill_name": str,
    "file_paths": list[str],
    "files": [
        {
            "success": bool,
            "file_path": str,
            "content": str,
            "size_bytes": int,
            "encoding": str
        }
        # or
        {
            "success": False,
            "file_path": str,
            "error": str
        }
    ]
}
```

`success` is `True` only when all requested files are read successfully.

### Error Response

```python
{
    "success": False,
    "skill_name": str,
    "file_paths": list[str],
    "error": str
}
```

**Common Error Messages**:
- `"Skill 'skill_name' not found in skills folder"`
- `"File 'file_path' not found in skill 'skill_name'"`
- `"Path traversal detected: cannot access files outside skill folder"`
- `"Cannot read file 'file_path': <reason>"`
- `"Invalid skill name"`
- `"Invalid file paths"`

## Behavior Specification

### File Reading

1. **Skill Lookup**: Locate skill folder at `{skills_folder}/{skill_name}`
2. **Batch Resolution**: Resolve each `{skill_folder}/{file_path}` to an absolute path
3. **Security Check**: Verify each resolved path is within the skill folder
4. **File Read**: Read each file as UTF-8 text
5. **Return**: Return one result entry per requested file

### Security Boundaries

- **Directory Traversal Prevention**: Use `pathlib.Path.resolve()` and check `is_relative_to(skill_folder)`
- **Skill Folder Isolation**: Files outside the skill folder are inaccessible
- **Per-File Validation**: Every requested path is validated independently

**Example Security Check**:
```python
from pathlib import Path

def read_files_in_skill(skill_name: str, file_paths: list[str]) -> dict:
    skill_dir = Path(skills_folder) / skill_name
    files = []

    for file_path in file_paths:
        requested_file = (skill_dir / file_path).resolve()
        if not requested_file.is_relative_to(skill_dir):
            files.append({
                "success": False,
                "file_path": file_path,
                "error": "Path traversal detected: cannot access files outside skill folder",
            })
            continue

        files.append({
            "success": True,
            "file_path": file_path,
            "content": requested_file.read_text(),
        })

    return {
        "success": all(item["success"] for item in files),
        "skill_name": skill_name,
        "file_paths": file_paths,
        "files": files,
    }
```

### Error Handling

| Condition | Behavior |
|-----------|----------|
| Skill folder not found | Return top-level error |
| Empty `file_paths` | Return top-level error |
| File not found | Return per-file error entry |
| Path traversal attempt | Return per-file error entry |
| Invalid skill name | Return top-level error |
| Binary file (unreadable as text) | Return per-file error entry |
| Insufficient permissions | Return per-file error entry |

## Examples

### Example 1: Read Two Referenced Files

**LLM Tool Call**:
```json
{
  "id": "call_abc123",
  "type": "function",
  "function": {
    "name": "read_files_in_skill",
    "arguments": "{\"skill_name\": \"calculator\", \"file_paths\": [\"examples/basic.py\", \"docs/api_reference.md\"]}"
  }
}
```

**Tool Result Message**:
```json
{
  "role": "tool",
  "tool_call_id": "call_abc123",
  "name": "read_files_in_skill",
  "content": "{\"success\": true, \"skill_name\": \"calculator\", \"file_paths\": [\"examples/basic.py\", \"docs/api_reference.md\"], \"files\": [...]}"
}
```

### Example 2: Partial Success

**LLM Tool Call**:
```json
{
  "function": {
    "name": "read_files_in_skill",
    "arguments": "{\"skill_name\": \"weather\", \"file_paths\": [\"docs/api_reference.md\", \"docs/missing.md\"]}"
  }
}
```

**Tool Result**:
```json
{
  "success": false,
  "skill_name": "weather",
  "file_paths": ["docs/api_reference.md", "docs/missing.md"],
  "files": [
    {
      "success": true,
      "file_path": "docs/api_reference.md",
      "content": "# Weather API Reference"
    },
    {
      "success": false,
      "file_path": "docs/missing.md",
      "error": "File 'docs/missing.md' not found in skill 'weather'"
    }
  ]
}
```

### Example 3: Path Traversal Attempt

**LLM Tool Call**:
```json
{
  "function": {
    "name": "read_files_in_skill",
    "arguments": "{\"skill_name\": \"calculator\", \"file_paths\": [\"../../../etc/passwd\"]}"
  }
}
```

**Tool Result**:
```json
{
  "success": false,
  "skill_name": "calculator",
  "file_paths": ["../../../etc/passwd"],
  "files": [
    {
      "success": false,
      "file_path": "../../../etc/passwd",
      "error": "Path traversal detected: cannot access files outside skill folder"
    }
  ]
}
```

## Performance Requirements

- **Batch Read**: Complete in <500ms for small batches totaling up to 1MB
- **Path Resolution**: <10ms per path for security validation
- **Error Response**: <100ms for invalid top-level requests

## Testing Checklist

- [ ] Read a single file in the skill root directory
- [ ] Read multiple files in one call
- [ ] Read nested files in subdirectories
- [ ] Read various file types (.py, .md, .json, .txt, .yaml)
- [ ] Mixed success and failure in the same batch
- [ ] File not found error entry
- [ ] Skill not found top-level error
- [ ] Path traversal attempt in one requested path
- [ ] Invalid skill name
- [ ] Empty `file_paths`
- [ ] Large file batch performance
- [ ] Unicode content

## Notes

- **SKILL.MD as Index**: LLM should read SKILL.MD first to understand what additional files exist
- **Batch-Friendly**: Prefer one call when several small referenced files are needed together
- **No Caching**: Each tool call reads from disk
- **Text Files Only**: Binary files return per-file read errors
- **Cross-Platform**: Path handling works on Windows, Linux, and macOS