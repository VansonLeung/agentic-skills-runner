# Research: LLM/VLM Skills Runner

**Feature**: 001-llm-skills-runner  
**Created**: 2026-02-07  
**Purpose**: Technical decision documentation and best practices research

## Decision 1: OpenAI-Compatible API Format

**Context**: Need to support LLM/VLM APIs from multiple providers while keeping implementation simple.

**Decision**: Use OpenAI-compatible API format (chat completions endpoint with tool/function calling).

**Rationale**:
- Industry standard adopted by most major providers (OpenAI, Anthropic via compatibility layer, Azure OpenAI, local models via llama.cpp/Ollama/vLLM)
- Well-documented schema for requests, responses, and tool calling
- Enables provider flexibility without abstraction layers
- Request format: `POST /v1/chat/completions` with `messages` array and `tools` array
- Tool calling uses standardized `tool_calls` and `tool_choice` fields

**Alternatives Considered**:
- Native multi-provider support (OpenAI + Anthropic + Google) → Rejected: Adds complexity, violates YAGNI; most providers now support OpenAI format
- Custom abstraction layer → Rejected: Premature optimization; MVP should validate single format first
- Provider-specific implementation → Rejected: Limits compatibility; OpenAI format offers broader reach

**Implementation Notes**:
- Use standard OpenAI SDK client or compatible HTTP client
- Environment vars: `LLM_API_KEY`, `LLM_API_BASE_URL`, `LLM_MODEL_NAME`
- Tool schema follows OpenAI function calling format (JSON Schema for parameters)

**References**:
- OpenAI Chat Completions API: https://platform.openai.com/docs/api-reference/chat
- OpenAI Function Calling: https://platform.openai.com/docs/guides/function-calling

---

## Decision 2: Python Packaging Structure (Library + CLI)

**Context**: Need to provide both programmatic API (import library) and CLI interface.

**Decision**: Single package with integrated CLI using entry points.

**Rationale**:
- Single source of truth - CLI wraps library functions
- Simplifies maintenance - one codebase, one test suite
- Industry standard pattern: `click`, `typer`, `requests` all use this approach
- Package structure: `src/skills_runner/` with `__main__.py` for CLI
- Entry point in `pyproject.toml`: `skills-runner = skills_runner.cli:main`

**Alternatives Considered**:
- Separate CLI package → Rejected: Violates DRY, doubles maintenance burden
- CLI-only tool → Rejected: Limits programmatic integration use cases
- Library-only with examples → Rejected: Reduces accessibility for end users

**Implementation Notes**:
- Users can: `pip install skills-runner` → `skills-runner chat` (CLI)
- Or: `from skills_runner import SkillsRunner` (library)
- Or: `python -m skills_runner` (module execution)
- Use `pyproject.toml` with modern Python packaging (PEP 517/518)

**References**:
- Python Packaging Guide: https://packaging.python.org/
- Click documentation: https://click.palletsprojects.com/
- Typer documentation: https://typer.tiangolo.com/

---

## Decision 3: HTTP Client (requests vs httpx)

**Context**: Need HTTP client for OpenAI-compatible API calls.

**Decision**: Use `requests` library for MVP (synchronous, simple).

**Rationale**:
- Simplest, most widely-used HTTP library in Python ecosystem
- Synchronous model sufficient for MVP (single-process, single-conversation)
- Zero learning curve - ubiquitous in Python community
- Mature, stable, well-documented
- Performance adequate for LLM API calls (network latency dominates)

**Alternatives Considered**:
- httpx (async support) → Deferred: MVP doesn't require concurrency; can migrate if needed
- aiohttp → Rejected: Same reason as httpx; premature optimization
- urllib (stdlib) → Rejected: Lower-level API, more verbose code

**Implementation Notes**:
- Simple sync pattern: `response = requests.post(url, json=payload, headers=headers)`
- Timeout handling: `timeout=(connect_timeout, read_timeout)`
- Retry logic can be added via `requests.adapters.HTTPAdapter` if needed

**Migration Path**: If async becomes requirement, httpx provides compatible API for easy migration.

**References**:
- requests documentation: https://requests.readthedocs.io/

---

## Decision 4: CLI Framework (click vs typer vs argparse)

**Context**: Need CLI framework for command-line interface.

**Decision**: Use `click` for CLI framework.

**Rationale**:
- Industry standard for Python CLI tools
- Decorator-based API - clean, readable command definitions
- Automatic help generation and input validation
- Rich ecosystem of plugins and extensions
- Lower cognitive load than argparse (stdlib)
- More mature than typer (though typer is excellent for type-first approach)

**Alternatives Considered**:
- typer → Alternative choice: Type-hints-first approach, built on click, excellent for type safety advocates
- argparse (stdlib) → Rejected: More verbose, less intuitive API
- docopt → Rejected: Less maintained, unconventional approach

**Implementation Notes**:
```python
import click

@click.group()
def cli():
    pass

@cli.command()
@click.argument('prompt')
def chat(prompt):
    # Implementation
    pass
```

**Note**: Either click or typer acceptable. Typer offers better type safety but adds dependency. For MVP, click's maturity and simplicity preferred.

**References**:
- Click documentation: https://click.palletsprojects.com/

---

## Decision 5: Subprocess Execution and Security Model (MVP)

**Context**: RUN_PYTHON_SCRIPT executes user/LLM-generated code in skill venv.

**Decision**: Use `subprocess.run()` with explicit `cwd` (working directory), path validation, and **full filesystem access for MVP**.

**Rationale**:
- **MVP Simplification**: Scripts have full filesystem access - user's responsibility to manage security
- Working directory control: Set `cwd=skill_folder_path` provides skill context for relative paths
- Path validation: Reject skill names with `..`, `/`, `\` to prevent directory traversal in skill name
- Timeout: `subprocess.run(timeout=30)` prevents runaway processes
- Capture output: `capture_output=True` captures stdout/stderr for LLM
- **Post-MVP**: Add sandboxing, resource limits, filesystem isolation when MVP is validated

**MVP Security Model**:
1. **Full filesystem access**: Scripts can read/write anywhere (simpler MVP, user responsibility)
2. **Working directory**: Scripts execute with `cwd` set to skill folder (convention for relative paths)
3. **Path validation**: Reject malicious skill names before execution (prevent directory traversal in skill folder lookup)
4. **Timeout**: 30-second default prevents infinite loops
5. **Venv isolation**: Use skill's Python interpreter: `skill_folder/venv/bin/python` (package isolation only)
6. **No network isolation**: Scripts can make network calls (Python's strength, useful for API skills)

**Alternatives Considered**:
- Docker/containers → Deferred to post-MVP: Adds infrastructure complexity, violates KISS
- Python sandbox (RestrictedPython, PyPy sandbox) → Deferred: Incomplete protection, adds complexity
- chroot/jail → Deferred: Platform-specific, requires elevated privileges
- Read-only filesystem mount → Deferred: Requires OS-level permissions, not cross-platform
- Fine-grained filesystem permissions → Deferred: Complex to implement correctly, MVP bottleneck

**Implementation Notes**:
```python
def validate_skill_name(name: str) -> bool:
    # Prevent directory traversal
    return '/' not in name and '\\' not in name and '..' not in name

def run_script(skill_name: str, script: str, timeout: int = 30) -> dict:
    skill_path = skills_dir / skill_name
    venv_python = skill_path / "venv" / "bin" / "python"
    
    result = subprocess.run(
        [str(venv_python), "-c", script],
        cwd=str(skill_path),
        capture_output=True,
        text=True,
        timeout=timeout
    )
    return {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode}
```

**MVP Trade-offs (Accepted)**:
- Scripts have full filesystem access (read/write anywhere) - user's responsibility
- Scripts can make network requests - no sandboxing
- Scripts can consume CPU/memory within process limits - only timeout protection
- **Trust Model**: MVP assumes users control what skills are installed and what LLM generates
- **Migration Path**: Post-MVP can add Docker, chroot, or seccomp-bpf for production deployments

**References**:
- subprocess documentation: https://docs.python.org/3/library/subprocess.html

---

## Decision 6: Configuration Management

**Context**: Need to load API credentials, skills folder path, and other settings.

**Decision**: Use `python-dotenv` to load `.env` file, with environment variable fallback.

**Rationale**:
- Industry standard for Python configuration (used by Flask, Django, FastAPI)
- Supports `.env` file for local development and env vars for deployment
- Simple API: `load_dotenv()` + `os.getenv()`
- Security: `.env` in `.gitignore` prevents credential leaks
- Clear error messages for missing required config

**Configuration Variables**:
```
LLM_API_KEY=sk-...                    # Required
LLM_API_BASE_URL=https://api.openai.com/v1  # Required
LLM_MODEL_NAME=gpt-4                  # Required
SKILLS_FOLDER_PATH=./skills           # Optional, default: ./skills
SCRIPT_TIMEOUT_SECONDS=30             # Optional, default: 30
```

**Alternatives Considered**:
- TOML config file → Rejected: Env vars are standard for sensitive data
- YAML config → Rejected: Overcomplicated for simple key-value pairs
- Click's context passing → Supplement, not replacement: use for runtime options

**Implementation Notes**:
```python
from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    api_key: str = os.getenv("LLM_API_KEY")
    api_base_url: str = os.getenv("LLM_API_BASE_URL")
    model_name: str = os.getenv("LLM_MODEL_NAME")
    skills_folder: Path = Path(os.getenv("SKILLS_FOLDER_PATH", "./skills"))
    timeout: int = int(os.getenv("SCRIPT_TIMEOUT_SECONDS", "30"))
    
    def validate(self):
        if not self.api_key:
            raise ValueError("LLM_API_KEY is required")
        # ... more validation
```

**References**:
- python-dotenv: https://github.com/theskumar/python-dotenv

---

## Decision 7: READ_FILE_IN_SKILL Implementation

**Context**: Skills may have rich documentation beyond SKILL.MD (examples, config templates, reference docs). SKILL.MD serves as table of contents, LLM needs to read referenced files.

**Decision**: Implement READ_FILE_IN_SKILL tool accepting skill name + relative file path, with directory traversal protection.

**Rationale**:
- SKILL.MD as index: Main documentation points to additional resources
- Flexible documentation: Skills can structure docs/scripts/examples hierarchically
- Security boundary: Path must resolve within skill folder (reject `../` traversal)
- Simple implementation: `pathlib.Path.resolve()` + validation + file read
- Performance: Direct file reads, no caching needed for MVP

**Alternatives Considered**:
- Embed all docs in SKILL.MD → Rejected: Forces flat structure, limits organization
- Automatic file discovery → Rejected: LLM should explicitly request based on SKILL.MD guidance
- ZIP/archive format → Rejected: Unnecessary complexity for file access

**Implementation Notes**:
```python
def read_file_in_skill(skill_name: str, file_path: str) -> str:
    skill_dir = Path(skills_folder) / skill_name
    requested_file = (skill_dir / file_path).resolve()
    
    # Ensure resolved path is within skill folder (prevent ../../../etc/passwd)
    if not requested_file.is_relative_to(skill_dir):
        raise ValueError(f"Path traversal detected: {file_path}")
    
    return requested_file.read_text()
```

**Security Considerations**:
- Directory traversal prevention via `resolve()` + `is_relative_to()` check
- File size limits can be added post-MVP if needed
- Binary files handled via encoding detection or explicit text-only constraint

**References**:
- pathlib documentation: https://docs.python.org/3/library/pathlib.html

---

## Decision 8: Tool Calling Schema Format

**Context**: Skills tools (LIST_SKILLS, GET_SKILL, READ_FILE_IN_SKILL, RUN_PYTHON_SCRIPT) must be registered with LLM using OpenAI function calling format.

**Decision**: Define tools using JSON Schema for parameters, following OpenAI function calling specification.

**Rationale**:
- OpenAI function calling uses JSON Schema to describe tool parameters
- LLM uses schema to understand when and how to call tools
- Standard format ensures compatibility across OpenAI-compatible providers

**Tool Definitions**:
```python
SKILLS_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_skills",
            "description": "List all available skills in the skills folder. Returns skill names.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_skill",
            "description": "Read the SKILL.MD documentation for a specific skill. SKILL.MD serves as the main table of contents and may reference additional files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "skill_name": {
                        "type": "string",
                        "description": "Name of the skill (folder name)"
                    }
                },
                "required": ["skill_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file_in_skill",
            "description": "Read any file within a skill's folder. Use this when SKILL.MD references additional documentation, examples, or configuration files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "skill_name": {
                        "type": "string",
                        "description": "Name of the skill (folder name)"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Relative path to file within skill folder (e.g., 'examples/usage.py')"
                    }
                },
                "required": ["skill_name", "file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_python_script",
            "description": "Execute a Python script in the specified skill's virtual environment. Script has full filesystem access. Returns stdout, stderr, and exit code.",
            "parameters": {
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
        }
    }
]
```

**Implementation Notes**:
- Send tools array in API request: `{"messages": [...], "tools": SKILLS_TOOLS}`
- Handle tool calls in response: Check `response.choices[0].message.tool_calls`
- Execute tool, return result in next message with `role="tool"`

**References**:
- OpenAI Function Calling Guide: https://platform.openai.com/docs/guides/function-calling

---

## Best Practices Summary

### Testing Strategy
- **Unit tests**: Isolated tests for config, tools, executor with mocked dependencies
- **Integration tests**: End-to-end workflows with test skills folder
- **Contract tests**: Verify OpenAI API format compatibility with mock API server

### Error Handling
- Validate configuration on startup (fail fast)
- Wrap API calls with try/except for network errors (graceful degradation)
- Capture subprocess errors and include in tool result
- Log all errors with context for debugging

### Code Quality
- Type hints on all public APIs (`mypy --strict`)
- Docstrings for all modules, classes, functions
- Black + ruff for formatting and linting
- Keep functions small (<50 lines) per code simplicity principle

### Performance
- Lazy-load skills list (don't scan directory until needed)
- Stream API responses if available (not in MVP, but consider)
- Cache SKILL.MD contents if repeatedly accessed (deferred to post-MVP)

---

## Open Questions (None)

All technical decisions resolved during research phase. Ready to proceed to Phase 1 (data model and contracts).
