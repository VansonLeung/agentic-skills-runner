# API Contract: Conversation Flow

**Purpose**: Define the conversation loop and OpenAI-compatible API integration

## OpenAI Chat Completions API

**Endpoint Pattern**: `POST {api_base_url}/chat/completions`

Example: `POST https://api.openai.com/v1/chat/completions`

### Request Format

```json
{
  "model": "gpt-4",
  "messages": [
    {
      "role": "system",
      "content": "You are a helpful assistant with access to skills."
    },
    {
      "role": "user",
      "content": "What skills are available?"
    }
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "list_skills",
        "description": "List all available skills",
        "parameters": {
          "type": "object",
          "properties": {},
          "required": []
        }
      }
    }
  ],
  "tool_choice": "auto"
}
```

### Response Format (Tool Call)

```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "gpt-4",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": null,
        "tool_calls": [
          {
            "id": "call_abc123",
            "type": "function",
            "function": {
              "name": "list_skills",
              "arguments": "{}"
            }
          }
        ]
      },
      "finish_reason": "tool_calls"
    }
  ]
}
```

### Response Format (Final Answer)

```json
{
  "id": "chatcmpl-124",
  "object": "chat.completion",
  "created": 1234567891,
  "model": "gpt-4",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "I found three skills available: calculator, weather, and web_search."
      },
      "finish_reason": "stop"
    }
  ]
}
```

## Conversation Loop

### Flow Diagram

```
1. [Initialize]
   ↓
2. [Add User Message]
   ↓
3. [Send to LLM API]
   ↓
4. [Process Response]
   ↓
5. [Has Tool Calls?]
   ├─ No → [Return Answer] → [END]
   └─ Yes → [Execute Tools]
              ↓
          [Add Tool Results]
              ↓
          [Go to Step 3]
```

### Detailed Steps

**Step 1: Initialize**
```python
messages = [
    {"role": "system", "content": "You are a helpful assistant with skills."}
]
tools = [list_skills_def, get_skill_def, run_python_script_def]
```

**Step 2: Add User Message**
```python
messages.append({"role": "user", "content": user_input})
```

**Step 3: Send to LLM**
```python
response = requests.post(
    f"{api_base_url}/chat/completions",
    headers={"Authorization": f"Bearer {api_key}"},
    json={
        "model": model_name,
        "messages": messages,
        "tools": tools,
        "tool_choice": "auto"
    }
)
```

**Step 4: Process Response**
```python
assistant_message = response.json()["choices"][0]["message"]
messages.append(assistant_message)
```

**Step 5: Check for Tool Calls**
```python
if assistant_message.get("tool_calls"):
    # Has tool calls → Execute them
    for tool_call in assistant_message["tool_calls"]:
        result = execute_tool(tool_call)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call["id"],
            "name": tool_call["function"]["name"],
            "content": json.dumps(result)
        })
    # Loop back to Step 3 (send updated messages to LLM)
else:
    # No tool calls → Return final answer
    return assistant_message["content"]
```

## Tool Execution Dispatch

```python
def execute_tool(tool_call: dict) -> dict:
    function_name = tool_call["function"]["name"]
    arguments = json.loads(tool_call["function"]["arguments"])
    
    if function_name == "list_skills":
        return list_skills()
    elif function_name == "get_skill":
        return get_skill(arguments["skill_name"])
    elif function_name == "run_python_script":
        return run_python_script(
            arguments["skill_name"], 
            arguments["script"]
        )
    else:
        return {"error": f"Unknown tool: {function_name}"}
```

## Complete Example Flow

### User Request
```
User: "Use the calculator skill to compute 25 * 4"
```

### Message Sequence

**1. Initial State**
```json
[
  {"role": "system", "content": "You are a helpful assistant with skills."},
  {"role": "user", "content": "Use the calculator skill to compute 25 * 4"}
]
```

**2. First API Call → LLM Decides to List Skills**
```json
Response: {
  "choices": [{
    "message": {
      "role": "assistant",
      "tool_calls": [{
        "id": "call_1",
        "function": {"name": "list_skills", "arguments": "{}"}
      }]
    }
  }]
}
```

**3. Execute list_skills → Update Messages**
```json
[
  {...previous messages...},
  {
    "role": "assistant",
    "tool_calls": [{"id": "call_1", "function": {"name": "list_skills", "arguments": "{}"}}]
  },
  {
    "role": "tool",
    "tool_call_id": "call_1",
    "name": "list_skills",
    "content": "{\"skills\": [\"calculator\", \"weather\"]}"
  }
]
```

**4. Second API Call → LLM Gets Skill Documentation**
```json
Response: {
  "choices": [{
    "message": {
      "role": "assistant",
      "tool_calls": [{
        "id": "call_2",
        "function": {"name": "get_skill", "arguments": "{\"skill_name\": \"calculator\"}"}
      }]
    }
  }]
}
```

**5. Execute get_skill → Update Messages**
```json
[
  {...previous messages...},
  {
    "role": "assistant",
    "tool_calls": [{"id": "call_2", "function": {"name": "get_skill", "arguments": "{\"skill_name\": \"calculator\"}"}}]
  },
  {
    "role": "tool",
    "tool_call_id": "call_2",
    "name": "get_skill",
    "content": "{\"skill_name\": \"calculator\", \"documentation\": \"# Calculator\\n\\nBasic arithmetic...\"}"
  }
]
```

**6. Third API Call → LLM Runs Script**
```json
Response: {
  "choices": [{
    "message": {
      "role": "assistant",
      "tool_calls": [{
        "id": "call_3",
        "function": {
          "name": "run_python_script",
          "arguments": "{\"skill_name\": \"calculator\", \"script\": \"result = 25 * 4\\nprint(result)\"}"
        }
      }]
    }
  }]
}
```

**7. Execute run_python_script → Update Messages**
```json
[
  {...previous messages...},
  {
    "role": "assistant",
    "tool_calls": [{"id": "call_3", "function": {...}}]
  },
  {
    "role": "tool",
    "tool_call_id": "call_3",
    "name": "run_python_script",
    "content": "{\"skill_name\": \"calculator\", \"stdout\": \"100\\n\", \"stderr\": \"\", \"returncode\": 0, \"timed_out\": false}"
  }
]
```

**8. Fourth API Call → LLM Provides Answer**
```json
Response: {
  "choices": [{
    "message": {
      "role": "assistant",
      "content": "Using the calculator skill, I computed 25 × 4 = 100"
    },
    "finish_reason": "stop"
  }]
}
```

**9. Final Answer Returned to User**
```
"Using the calculator skill, I computed 25 × 4 = 100"
```

## Error Handling

### API Errors

```python
try:
    response = requests.post(url, json=payload, timeout=30)
    response.raise_for_status()
except requests.Timeout:
    return "Error: API request timed out"
except requests.HTTPError as e:
    return f"Error: API returned {e.response.status_code}"
except requests.RequestException as e:
    return f"Error: Network error - {e}"
```

### Tool Errors

When a tool returns an error, include it in the tool result:

```json
{
  "role": "tool",
  "tool_call_id": "call_123",
  "name": "get_skill",
  "content": "{\"error\": \"Skill 'nonexistent' not found\"}"
}
```

The LLM will see the error and can respond appropriately to the user.

## Authentication

**Header**: `Authorization: Bearer {api_key}`

**Environment Variable**: `LLM_API_KEY`

## Rate Limiting

- Respect provider rate limits (implementation-specific)
- Implement exponential backoff for 429 responses (future enhancement)
- Track token usage if available in response

## Visibility Requirement (FR-039)

All tool calls and results must be displayed to the user in real-time. Implementation options:

**CLI**: Print tool calls as they happen
```
🔧 Calling tool: list_skills
🔧 Result: {"skills": ["calculator", "weather"]}
```

**Library**: Provide callback or event system
```python
def on_tool_call(tool_name, arguments):
    print(f"Tool: {tool_name}({arguments})")

runner = SkillsRunner(on_tool_call=on_tool_call)
```
