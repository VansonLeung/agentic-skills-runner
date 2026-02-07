# Implementation Plan: LLM/VLM Skills Runner

**Branch**: `001-llm-skills-runner` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-llm-skills-runner/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build an agentic LLM toolkit that connects to OpenAI-compatible APIs and extends capabilities through a Skills system. Skills (stored as subfolders) provide documentation and executable Python scripts. The LLM can autonomously discover skills (LIST_SKILLS), read documentation (GET_SKILL, READ_FILE_IN_SKILL), and execute Python code (RUN_PYTHON_SCRIPT) in skill-specific virtual environments. Deployed as a Python library with CLI wrapper for dual programmatic and command-line access. MVP focuses on working API integration, automatic tool execution with user visibility, and simplified security model (full filesystem access, isolation deferred post-MVP). Future vision: migrate to MCP server after MVP validation. VLM/vision support deferred to post-MVP.

## Technical Context

**Language/Version**: Python 3.9+ (type hints, async support, broad compatibility)  
**Primary Dependencies**: requests (HTTP client), click (CLI framework), python-dotenv (config)  
**Storage**: File-based (skills as subdirectories with SKILL.MD + optional files + venv)  
**Testing**: pytest, pytest-asyncio, pytest-mock (unit, integration, contract tests)  
**Target Platform**: Cross-platform (Linux, macOS, Windows) - local execution  
**Project Type**: Single project (Python library + CLI wrapper)  
**Performance Goals**: LIST_SKILLS <1s for 100 skills, GET_SKILL <500ms for 1MB files, READ_FILE_IN_SKILL <500ms, RUN_PYTHON_SCRIPT <5s for simple scripts  
**Constraints**: <30s script execution timeout (default), OpenAI-compatible API format required, MVP text-only (VLM post-MVP)  
**Scale/Scope**: MVP supports single user, local skills folder, synchronous API calls, text-only LLM interactions

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**I. Separation of Concerns** - ✅ PASS  
Four distinct tools (LIST_SKILLS, GET_SKILL, READ_FILE_IN_SKILL, RUN_PYTHON_SCRIPT) with clear, non-overlapping responsibilities. Configuration, API client, skills management, and execution are separate modules.

**II. Modularization** - ✅ PASS  
Single Python project with modular design: Configuration module, LLMClient module, SkillsTool module (4 operations), Executor module. CLI wraps library. Each module independently testable.

**III. Code Simplicity** - ✅ PASS  
MVP-first approach with simplified security model (full filesystem access, no complex sandbox). KISS/YAGNI demonstrated: synchronous HTTP (no unnecessary async), simple subprocess execution, file-based storage (no database overhead). READ_FILE_IN_SKILL is straightforward file read with path validation.

**IV. Code Quality** - ✅ PASS  
Python 3.9+ type hints required, pytest for testing, linting standards expected. Clear error messages for all failure scenarios (FR-042).

**V. Testing Standards** - ✅ PASS  
Contract tests specified for all 4 tools (input/output validation), unit tests for modules, integration tests for API flow. Success criteria include measurable performance targets.

**VI. UX Consistency** - ✅ PASS  
All tools follow consistent execution pattern: automatic execution with visible tool calls/results (FR-044). CLI and library provide parallel interfaces. Error messages follow clear, actionable format.

**VII. Performance Requirements** - ✅ PASS  
Explicit performance targets: LIST_SKILLS <1s (100 skills), GET_SKILL <500ms (1MB), READ_FILE_IN_SKILL <500ms, RUN_PYTHON_SCRIPT <5s (simple scripts), 30s timeout (default).

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/skills_runner/
├── __init__.py
├── config.py         # Environment/configuration management
├── exceptions.py     # Custom exception classes
├── models.py         # Data classes (Message, Skill, ScriptExecution)
├── llm_client.py     # OpenAI-compatible API client
├── skills_tool.py    # Four tools: LIST_SKILLS, GET_SKILL, READ_FILE_IN_SKILL, RUN_PYTHON_SCRIPT
├── tools.py          # ToolDefinition constants (4 tool schemas)
├── executor.py       # Subprocess execution (script runner)
├── conversation.py   # Conversation loop orchestration
└── cli.py            # Command-line interface

tests/
├── contract/         # Tool contract tests (input/output schemas)
├── integration/      # End-to-end API + tools flow
└── unit/             # Module-level tests
```

**Structure Decision**: Single project structure selected. This is a focused Python library with a single responsibility (LLM + Skills integration), no frontend/backend separation needed. Monolithic package simplifies distribution via pip and keeps all related code co-located for MVP development.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

**No violations** - All 7 constitution principles pass. No complexity justification required.

---

## Phase 0: Research & Decisions ✅

See [research.md](./research.md) for complete technical decisions.

**Key Decisions**:
1. OpenAI-compatible API format (broad provider support)
2. Python library + CLI packaging (dual interface)
3. requests HTTP client (synchronous, simple MVP)
4. click CLI framework (decorator-based, mature)
5. Subprocess execution with MVP simplified security (full filesystem access)
6. python-dotenv configuration management
7. READ_FILE_IN_SKILL for rich skill documentation
8. Tool schemas in OpenAI function calling format

---

## Phase 1: Design & Contracts ✅

### Data Model

See [data-model.md](./data-model.md) for complete entity definitions.

**Core Entities**:
1. **Configuration**: Environment variables, API credentials, skills folder path
2. **Skill**: Subfolder with SKILL.MD (table of contents) + optional files + venv
3. **Message**: OpenAI-format conversation history
4. **ToolCall**: LLM tool invocation
5. **ToolDefinition**: Function schema for LLM (4 tools)
6. **ScriptExecution**: Python execution state and results
7. **Conversation**: Orchestrator managing message flow and tool execution

### API Contracts

See [contracts/](./contracts/) for complete contract specifications.

**Tools**:
- **list_skills**: Scan skills folder, return skill names
- **get_skill**: Read SKILL.MD for a skill (table of contents)
- **read_file_in_skill**: Read any file within skill folder (e.g., examples, docs)
- **run_python_script**: Execute Python in skill's venv with full filesystem access

### Quickstart Guide

See [quickstart.md](./quickstart.md) for developer onboarding.

### Agent Context Update

GitHub Copilot context updated: `.github/agents/copilot-instructions.md`
- Language: Python 3.9+
- Framework: requests, click, python-dotenv
- Database: File-based skills structure
- Project Type: Single project

---

## Post-Phase 1 Constitution Re-evaluation ✅

*GATE: Re-check constitution compliance after design*

**I. Separation of Concerns** - ✅ PASS  
Design maintains clear separation: 4 distinct tools (LIST_SKILLS, GET_SKILL, READ_FILE_IN_SKILL, RUN_PYTHON_SCRIPT), separate modules (config, llm_client, skills_tool, executor, conversation, cli). No overlapping responsibilities.

**II. Modularization** - ✅ PASS  
Design produces 7 independently testable modules with clear interfaces. CLI wraps library functions. Each tool operates independently. Contract tests validate module boundaries.

**III. Code Simplicity** - ✅ PASS  
Design adheres to KISS/YAGNI: READ_FILE_IN_SKILL is simple file read with path validation. Simplified security model (full filesystem access) reduces MVP complexity. No premature optimization or unnecessary abstractions.

**IV. Code Quality** - ✅ PASS  
Design specifies Python 3.9+ type hints, pytest testing, clear error messages. Contracts define expected quality standards (input validation, error handling).

**V. Testing Standards** - ✅ PASS  
Design includes 4 contract specifications with test scenarios (35+ test cases across all contracts), unit test structure, integration test flows. Performance targets measurable.

**VI. UX Consistency** - ✅ PASS  
Design ensures consistent tool execution pattern with user visibility (FR-044). All tools follow same OpenAI format. Error messages standardized across contracts.

**VII. Performance Requirements** - ✅ PASS  
Design specifies quantifiable targets: LIST_SKILLS <1s, GET_SKILL <500ms, READ_FILE_IN_SKILL <500ms, RUN_PYTHON_SCRIPT <5s, 30s timeout. All achievable with proposed implementation.

**Conclusion**: All constitution principles remain PASSED after Phase 1 design. No violations introduced. Design is ready for Phase 2 (task breakdown).

---

## Next Steps

✅ **Phase 0 (Research)**: Complete - 8 technical decisions documented  
✅ **Phase 1 (Design)**: Complete - Data model, 4 contracts, quickstart guide  
⏭️ **Phase 2 (Tasks)**: Run `/speckit.tasks` to generate task breakdown  
⏭️ **Implementation**: Run `/speckit.implement` to begin development
