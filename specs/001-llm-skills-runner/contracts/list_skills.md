# Tool Contract: list_skills

**Operation**: Discover available skills in the configured skills folder

**Tool Name**: `list_skills`

**Description**: List all available skills in the skills folder. Returns skill names as a JSON array.

## Input Schema

**Parameters**: None (empty object)

```json
{
  "type": "object",
  "properties": {},
  "required": []
}
```

**Example LLM Tool Call**:
```json
{
  "id": "call_abc123",
  "type": "function",
  "function": {
    "name": "list_skills",
    "arguments": "{}"
  }
}
```

## Output Schema

**Success Response**:
```json
{
  "skills": ["skill_name_1", "skill_name_2", "..."]
}
```

**Empty Response** (no skills found):
```json
{
  "skills": []
}
```

**Error Response**:
```json
{
  "error": "Error message describing what went wrong"
}
```

## Examples

### Example 1: Successful Discovery

**Input**:
```json
{}
```

**Output**:
```json
{
  "skills": ["calculator", "weather", "web_search"]
}
```

**Tool Result Message** (added to conversation):
```json
{
  "role": "tool",
  "tool_call_id": "call_abc123",
  "name": "list_skills",
  "content": "{\"skills\": [\"calculator\", \"weather\", \"web_search\"]}"
}
```

### Example 2: Empty Skills Folder

**Input**:
```json
{}
```

**Output**:
```json
{
  "skills": []
}
```

### Example 3: Skills Folder Not Found

**Input**:
```json
{}
```

**Output**:
```json
{
  "error": "Skills folder not found at path: /path/to/skills"
}
```

## Behavior

1. **Discovery**: Scan configured skills folder for subdirectories
2. **Filtering**: Only return names of subdirectories (not files)
3. **Validation**: Exclude directories with invalid names (containing `/`, `\`, `..`)
4. **Sorting**: Return skills in alphabetical order
5. **Performance**: Complete in <1 second for up to 100 skills

## Error Conditions

| Condition | Response |
|-----------|----------|
| Skills folder doesn't exist | `{"error": "Skills folder not found at path: ..."}` |
| Skills folder not readable | `{"error": "Permission denied reading skills folder"}` |
| No subdirectories found | `{"skills": []}` (empty list, not error) |

## Implementation Notes

- Use `pathlib.Path.iterdir()` to scan directory
- Filter with `path.is_dir()` to get only directories
- Validate each name before including in results
- Handle OS-level exceptions gracefully
