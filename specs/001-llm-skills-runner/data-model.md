# Data Model: LLM/VLM Skills Runner

**Feature**: 001-llm-skills-runner  
**Created**: 2026-02-07  
**Purpose**: Entity definitions and relationships

## Overview

This system uses a file-based data model with no persistent database. State is represented through:
- Configuration objects (loaded from environment)
- File system structure (skills folders and SKILL.MD files)
- Runtime objects (conversation state, tool execution results)

## Core Entities

### 1. Configuration

**Purpose**: Holds all system configuration loaded from environment variables and `.env` file.

**Attributes**:
- `api_key: str` - LLM/VLM API authentication key (from `LLM_API_KEY`)
- `api_base_url: str` - API endpoint base URL (from `LLM_API_BASE_URL`)
- `model_name: str` - Model identifier to use (from `LLM_MODEL_NAME`)
- `skills_folder: Path` - Path to skills directory (from `SKILLS_FOLDER_PATH`, default: `./skills`)
- `timeout: int` - Script execution timeout in seconds (from `SCRIPT_TIMEOUT_SECONDS`, default: 30)

**Validation Rules**:
- `api_key` must not be empty
- `api_base_url` must be valid URL
- `model_name` must not be empty
- `skills_folder` must be valid path (created if doesn't exist)
- `timeout` must be positive integer

**Lifecycle**: Created on startup, immutable during runtime

**Example**:
```python
config = Configuration(
    api_key="sk-...",
    api_base_url="https://api.openai.com/v1",
    model_name="gpt-4",
    skills_folder=Path("./skills"),
    timeout=30
)
```

---

### 2. Skill

**Purpose**: Represents a capability extension stored as a subfolder in the skills directory.

**Attributes**:
- `name: str` - Skill identifier (folder name)
- `folder_path: Path` - Absolute path to skill folder
- `documentation_path: Path` - Path to `SKILL.MD` file (serves as table of contents)
- `venv_path: Optional[Path]` - Path to virtual environment folder (if exists)
- `has_venv: bool` - Whether skill has a venv available
- `has_documentation: bool` - Whether `SKILL.MD` exists

**Derived Properties**:
- `python_executable: Optional[Path]` - Path to Python interpreter in venv (if has_venv)
  - Linux/Mac: `{venv_path}/bin/python`
  - Windows: `{venv_path}/Scripts/python.exe`

**Documentation Strategy**: 
- `SKILL.MD` serves as the main table of contents and quick reference
- Additional files (examples, detailed docs, configs) stored in skill folder
- LLM reads SKILL.MD first, then uses READ_FILE_IN_SKILL for referenced files

**Discovery**: Skills are discovered by scanning directories in `skills_folder`

**Validation Rules**:
- Skill name must not contain `/`, `\`, or `..` (prevent directory traversal)
- Skill folder must exist
- If `venv` folder exists, it must contain valid Python interpreter

**Filesystem Structure**:
```
skills/
└── calculator/              # Skill folder (skill.name = "calculator")
    ├── SKILL.MD             # Documentation (skill.documentation_path) - table of contents
    ├── examples/            # Additional documentation
    │   ├── basic.py         # Code examples
    │   └── advanced.py
    ├── docs/                # Detailed documentation
    │   └── api_reference.md
    ├── venv/                # Virtual environment (skill.venv_path)
    │   ├── bin/python       # Python interpreter
    │   └── lib/...
    └── data/                # Skill-specific data (optional)
```

**Example**:
```python
skill = Skill(
    name="calculator",
    folder_path=Path("/path/to/skills/calculator"),
    documentation_path=Path("/path/to/skills/calculator/SKILL.MD"),
    venv_path=Path("/path/to/skills/calculator/venv"),
    has_venv=True,
    has_documentation=True
)
```

---

### 3. Message

**Purpose**: Represents a single message in the conversation history (OpenAI format).

**Attributes**:
- `role: Literal["system", "user", "assistant", "tool"]` - Message role
- `content: Optional[str]` - Message text content
- `tool_calls: Optional[List[ToolCall]]` - Tool invocations (for assistant messages)
- `tool_call_id: Optional[str]` - ID of tool call being responded to (for tool messages)
- `name: Optional[str]` - Tool name (for tool messages)

**OpenAI Format Compliance**: Directly maps to OpenAI Chat Completions API message format

**Example**:
```python
# User message
Message(role="user", content="What skills are available?")

# Assistant message with tool call
Message(
    role="assistant",
    content=None,
    tool_calls=[
        ToolCall(id="call_123", function=FunctionCall(name="list_skills", arguments="{}"))
    ]
)

# Tool response message
Message(role="tool", tool_call_id="call_123", name="list_skills", content='["calculator", "weather"]')

# Final assistant response
Message(role="assistant", content="I found two skills: calculator and weather.")
```

---

### 4. ToolCall

**Purpose**: Represents a tool invocation by the LLM (OpenAI format).

**Attributes**:
- `id: str` - Unique identifier for this tool call (needed for tool response)
- `type: Literal["function"]` - Type of tool call (always "function")
- `function: FunctionCall` - Function details

**Nested: FunctionCall**:
- `name: str` - Function name (`list_skills`, `get_skill`, or `run_python_script`)
- `arguments: str` - JSON string of function arguments

**Example**:
```python
tool_call = ToolCall(
    id="call_abc123",
    type="function",
    function=FunctionCall(
        name="run_python_script",
        arguments='{"skill_name": "calculator", "script": "print(2 + 2)"}'
    )
)
```

---

### 5. ToolDefinition

**Purpose**: Defines a skill tool's interface for the LLM (OpenAI function calling format).

**Attributes**:
- `type: Literal["function"]` - Tool type
- `function: FunctionDefinition` - Function metadata

**Nested: FunctionDefinition**:
- `name: str` - Function name
- `description: str` - Natural language description for LLM
- `parameters: dict` - JSON Schema describing parameters

**Available Tools**:

**list_skills**:
```python
{
    "type": "function",
    "function": {
        "name": "list_skills",
        "description": "List all available skills in the skills folder",
        "parameters": {"type": "object", "properties": {}, "required": []}
    }
}
```

**get_skill**:
```python
{
    "type": "function",
    "function": {
        "name": "get_skill",
        "description": "Read SKILL.MD documentation for a specific skill. SKILL.MD serves as table of contents.",
        "parameters": {
            "type": "object",
            "properties": {
                "skill_name": {"type": "string", "description": "Skill folder name"}
            },
            "required": ["skill_name"]
        }
    }
}
```

**read_file_in_skill**:
```python
{
    "type": "function",
    "function": {
        "name": "read_file_in_skill",
        "description": "Read any file within a skill's folder. Use when SKILL.MD references additional files.",
        "parameters": {
            "type": "object",
            "properties": {
                "skill_name": {"type": "string", "description": "Skill folder name"},
                "file_path": {"type": "string", "description": "Relative path within skill (e.g., 'examples/usage.py')"}
            },
            "required": ["skill_name", "file_path"]
        }
    }
}
```

**run_python_script**:
```python
{
    "type": "function",
    "function": {
        "name": "run_python_script",
        "description": "Execute Python script in skill's venv with full filesystem access (MVP), returns stdout/stderr",
        "parameters": {
            "type": "object",
            "properties": {
                "skill_name": {"type": "string", "description": "Skill folder name"},
                "script": {"type": "string", "description": "Python code to execute"}
            },
            "required": ["skill_name", "script"]
        }
    }
}
```

---

### 6. ScriptExecution

**Purpose**: Represents the state and result of Python script execution.

**Attributes**:
- `skill_name: str` - Skill whose venv was used
- `script: str` - Python code that was executed
- `working_directory: Path` - Directory where script executed (skill folder)
- `python_executable: Path` - Path to Python interpreter used
- `timeout: int` - Timeout in seconds
- `stdout: str` - Standard output captured
- `stderr: str` - Standard error captured
- `returncode: int` - Process exit code (0 = success)
- `timed_out: bool` - Whether execution exceeded timeout
- `error: Optional[str]` - Error message if execution failed

**Success Criteria**: `returncode == 0` and not `timed_out`

**Example**:
```python
execution = ScriptExecution(
    skill_name="calculator",
    script="print(2 + 2)",
    working_directory=Path("/path/to/skills/calculator"),
    python_executable=Path("/path/to/skills/calculator/venv/bin/python"),
    timeout=30,
    stdout="4\n",
    stderr="",
    returncode=0,
    timed_out=False,
    error=None
)
```

---

### 7. Conversation

**Purpose**: Manages conversation state and message history.

**Attributes**:
- `messages: List[Message]` - All messages in conversation order
- `config: Configuration` - System configuration
- `skills_folder: Path` - Path to skills directory
- `tools: List[ToolDefinition]` - Available tools

**Methods** (conceptual):
- `add_user_message(content: str)` - Add user message to history
- `send_to_llm() -> Message` - Send messages + tools to API, get response
- `execute_tool_calls(tool_calls: List[ToolCall]) -> List[Message]` - Run tools, return results
- `run() -> str` - Main conversation loop

**Lifecycle**: Created per-conversation, maintains state until completion

---

## Relationships

```
Configuration ──┐
                ├──> Conversation ──> Message ──> ToolCall
                │         │                           │
                │         ├──> ToolDefinition         │
                │         │                           ↓
                │         └──> Skill <──────── ScriptExecution
                │
                └──> Skill (via skills_folder)

```

**Key Relationships**:
1. **Configuration → Conversation**: Config provides API credentials and skills folder path
2. **Conversation → Message**: Conversation contains ordered list of messages
3. **Message → ToolCall**: Assistant messages may contain tool calls
4. **ToolCall → Skill**: Tool execution operates on specific skill
5. **Skill → ScriptExecution**: Script runs in skill's context (venv, working dir)
6. **Conversation → ToolDefinition**: Tools are registered with conversation for LLM

---

## State Transitions

### Conversation Flow

```
[Initialize] → [User Input] → [Send to LLM] → [Process Response]
                    ↑                               │
                    │                               ↓
                    │                      [Has Tool Calls?]
                    │                         ├─No──> [Return Answer]
                    │                         │
                    │                         └─Yes─> [Execute Tools]
                    │                                      │
                    └──────────────────────────────────────┘
```

### Tool Execution Flow

```
[Tool Call] → [Validate Skill] → [Execute Operation] → [Return Result]
                     │                     │                  │
                     │                     │                  ↓
                   [Error]             [Error]          [Add to Messages]
                     │                     │                  │
                     └─────────────────────┴──────────────────┘
```

---

## Validation Rules Summary

| Entity | Validation |
|--------|------------|
| Configuration | API key not empty, valid URL, positive timeout |
| Skill | Name sans special chars, folder exists, venv valid if present |
| Message | Role in allowed values, content/tool_calls based on role |
| ToolCall | ID not empty, function name in allowed set, arguments valid JSON |
| ScriptExecution | Timeout positive, skill exists, venv available |

---

## File System Contract

The system expects this file structure:

```
./                           # Repository root
├── .env                     # Configuration (gitignored)
├── skills/                  # Skills directory (configurable)
│   ├── skill1/
│   │   ├── SKILL.MD         # Required: skill documentation (table of contents)
│   │   ├── examples/        # Optional: code examples
│   │   ├── docs/            # Optional: detailed documentation
│   │   ├── venv/            # Optional: virtual environment
│   │   │   └── bin/python   # Python interpreter
│   │   └── ...              # Skill-specific files
│   └── skill2/
│       └── SKILL.MD
└── src/skills_runner/       # Application code
```

**Contracts**:
- Skills folder contains skill subfolders (not files)
- Each skill subfolder may contain `SKILL.MD` (documentation/table of contents)
- Each skill may contain additional files (examples, docs, configs) readable via READ_FILE_IN_SKILL
- Each skill subfolder may contain `venv/` (virtual environment)
- Skill names are folder names (no `/`, `\`, `..` for security)
- Scripts execute with skill folder as working directory
- Scripts have full filesystem access (MVP - user's responsibility)

---

## Notes

- **No database**: All state in memory or filesystem
- **Stateless**: Each conversation is independent
- **Immutable config**: Configuration doesn't change during runtime
- **Lazy loading**: Skills discovered on-demand, not preloaded
- **OpenAI compatibility**: All message/tool formats match OpenAI spec
