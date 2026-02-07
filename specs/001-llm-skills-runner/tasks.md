# Tasks: LLM/VLM Skills Runner

**Feature**: 001-llm-skills-runner  
**Branch**: `001-llm-skills-runner`  
**Generated**: 2026-02-07

**Input**: Design documents from `/specs/001-llm-skills-runner/`
- ✅ plan.md (tech stack, structure)
- ✅ spec.md (3 user stories: P1, P2, P3)
- ✅ research.md (8 technical decisions)
- ✅ data-model.md (7 core entities)
- ✅ contracts/ (4 tool contracts)
- ✅ quickstart.md (test scenarios)

## Task Format: `- [ ] [ID] [P?] [Story?] Description with file path`

- **Checkbox**: `- [ ]` (markdown checkbox)
- **[ID]**: Sequential task number (T001, T002...)
- **[P]**: Optional marker for parallelizable tasks
- **[Story]**: Required for user story tasks ([US1], [US2], [US3])
- **Description**: Clear action with exact file path

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Initialize project structure, dependencies, and tooling

- [ ] T001 Create Python project structure per plan.md (src/skills_runner/, tests/)
- [ ] T002 Create pyproject.toml with metadata (name, version, Python 3.9+ requirement)
- [ ] T003 [P] Create .gitignore (venv/, .env, __pycache__, *.pyc, .pytest_cache/, dist/)
- [ ] T004 [P] Create README.md with project overview and quickstart instructions
- [ ] T005 [P] Create requirements.txt with core dependencies (requests, click, python-dotenv)
- [ ] T006 [P] Create requirements-dev.txt with test dependencies (pytest, pytest-mock, pytest-asyncio)
- [ ] T007 [P] Configure pytest in pyproject.toml (test paths, markers, coverage)
- [ ] T008 Create src/skills_runner/__init__.py with version and public API exports

**Checkpoint**: Project structure ready for foundational module implementation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T009 [P] Implement Configuration class in src/skills_runner/config.py (load env vars, validate API credentials)
- [ ] T010 [P] Create unit tests for Configuration in tests/unit/test_config.py
- [ ] T011 [P] Create base error classes in src/skills_runner/exceptions.py (SkillsRunnerError, ConfigError, SkillNotFoundError, ToolExecutionError)
- [ ] T012 [P] Create skills folder validator in src/skills_runner/config.py (check path exists, create if missing)
- [ ] T013 Create .env.example with all required environment variables (LLM_API_KEY, LLM_API_BASE_URL, LLM_MODEL_NAME, SKILLS_FOLDER_PATH, SCRIPT_TIMEOUT_SECONDS)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Basic LLM API Integration (Priority: P1) 🎯 MVP

**Goal**: Developer can configure API credentials, make LLM API calls, and receive responses via library or CLI

**Independent Test**: Provide API credentials via .env, make single API call with prompt, verify response received

### Contract Tests for User Story 1

- [ ] T014 [P] [US1] Create contract test for LLM API request/response in tests/contract/test_llm_client.py
- [ ] T015 [P] [US1] Create integration test for basic conversation flow in tests/integration/test_conversation.py

### Implementation for User Story 1

- [ ] T016 [P] [US1] Implement LLMClient class in src/skills_runner/llm_client.py (OpenAI-compatible API calls)
- [ ] T017 [P] [US1] Implement Message class in src/skills_runner/models.py (role, content, tool_calls, tool_call_id)
- [ ] T018 [US1] Implement Conversation class in src/skills_runner/conversation.py (message history, send_to_llm method)
- [ ] T019 [US1] Implement basic CLI command in src/skills_runner/cli.py (chat command accepting prompt)
- [ ] T020 [US1] Add error handling for API failures in src/skills_runner/llm_client.py (timeout, auth errors, network issues)
- [ ] T021 [P] [US1] Create unit tests for LLMClient in tests/unit/test_llm_client.py
- [ ] T022 [P] [US1] Create unit tests for Conversation in tests/unit/test_conversation.py

**Checkpoint**: User Story 1 complete - can make LLM API calls and receive responses

---

## Phase 4: User Story 2 - Skills Discovery System (Priority: P2) 🎯 MVP

**Goal**: LLM can autonomously discover skills, read SKILL.MD, and read additional files within skills. All tool calls visible to user.

**Independent Test**: Create skills folder with subfolders containing SKILL.MD and additional files, start conversation, verify LLM calls LIST_SKILLS, GET_SKILL, READ_FILE_IN_SKILL with results displayed

### Contract Tests for User Story 2

- [ ] T023 [P] [US2] Create contract test for LIST_SKILLS in tests/contract/test_list_skills.py
- [ ] T024 [P] [US2] Create contract test for GET_SKILL in tests/contract/test_get_skill.py
- [ ] T025 [P] [US2] Create contract test for READ_FILE_IN_SKILL in tests/contract/test_read_file_in_skill.py
- [ ] T026 [P] [US2] Create integration test for skills discovery flow in tests/integration/test_skills_discovery.py

### Implementation for User Story 2

- [ ] T027 [P] [US2] Implement Skill class in src/skills_runner/models.py (name, folder_path, documentation_path, venv_path)
- [ ] T028 [P] [US2] Implement list_skills function in src/skills_runner/skills_tool.py (scan skills folder, return skill names)
- [ ] T029 [P] [US2] Implement get_skill function in src/skills_runner/skills_tool.py (read SKILL.MD for specified skill)
- [ ] T030 [P] [US2] Implement read_file_in_skill function in src/skills_runner/skills_tool.py (read file with path traversal protection)
- [ ] T031 [US2] Create ToolDefinition constants in src/skills_runner/tools.py (4 tool schemas: list_skills, get_skill, read_file_in_skill, run_python_script)
- [ ] T032 [US2] Integrate tools with Conversation class in src/skills_runner/conversation.py (register tools, execute tool calls, return results)
- [ ] T033 [US2] Add tool execution visibility in src/skills_runner/conversation.py (display tool calls and results to user)
- [ ] T034 [US2] Add skill name validation in src/skills_runner/skills_tool.py (reject /, \, .. characters)
- [ ] T035 [US2] Add error handling for missing skills/files in src/skills_runner/skills_tool.py
- [ ] T036 [P] [US2] Create unit tests for Skill model in tests/unit/test_models.py
- [ ] T037 [P] [US2] Create unit tests for list_skills in tests/unit/test_skills_tool.py
- [ ] T038 [P] [US2] Create unit tests for get_skill in tests/unit/test_skills_tool.py
- [ ] T039 [P] [US2] Create unit tests for read_file_in_skill in tests/unit/test_skills_tool.py

**Checkpoint**: User Story 2 complete - LLM can discover and read skills autonomously

---

## Phase 5: User Story 3 - Skills Execution Engine (Priority: P3)

**Goal**: LLM can generate Python scripts and execute them in skill venvs, receiving results to enhance responses

**Independent Test**: Create skill with initialized venv, have LLM generate simple script, call RUN_PYTHON_SCRIPT, verify execution in correct venv with output returned

### Contract Tests for User Story 3

- [ ] T040 [P] [US3] Create contract test for RUN_PYTHON_SCRIPT in tests/contract/test_run_python_script.py
- [ ] T041 [P] [US3] Create integration test for script execution flow in tests/integration/test_script_execution.py

### Implementation for User Story 3

- [ ] T042 [P] [US3] Implement ScriptExecution class in src/skills_runner/models.py (skill_name, script, stdout, stderr, returncode, timed_out)
- [ ] T043 [P] [US3] Implement venv detection in src/skills_runner/executor.py (find Python interpreter in skill venv)
- [ ] T044 [US3] Implement run_python_script function in src/skills_runner/skills_tool.py (execute via subprocess with timeout)
- [ ] T045 [US3] Add working directory setup in src/skills_runner/executor.py (set cwd to skill folder)
- [ ] T046 [US3] Add timeout handling in src/skills_runner/executor.py (default 30s, capture partial output on timeout)
- [ ] T047 [US3] Add stdout/stderr capture in src/skills_runner/executor.py (capture_output=True, text=True)
- [ ] T048 [US3] Add error handling for missing venv in src/skills_runner/skills_tool.py (clear error message if no venv)
- [ ] T049 [US3] Integrate RUN_PYTHON_SCRIPT with Conversation in src/skills_runner/conversation.py (execute when LLM calls tool)
- [ ] T050 [P] [US3] Create unit tests for ScriptExecution model in tests/unit/test_models.py
- [ ] T051 [P] [US3] Create unit tests for executor in tests/unit/test_executor.py
- [ ] T052 [P] [US3] Create unit tests for run_python_script in tests/unit/test_skills_tool.py

**Checkpoint**: All 3 user stories complete - full MVP functionality ready

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements affecting multiple user stories, documentation, and final validation

- [ ] T053 [P] Add library usage examples in README.md (import, configure, call LLM)
- [ ] T054 [P] Add CLI usage examples in README.md (skills-runner chat command)
- [ ] T055 [P] Create example .env file with placeholder credentials in .env.example
- [ ] T056 [P] Create example skill structure in examples/calculator/ (SKILL.MD, examples/, venv/)
- [ ] T057 [P] Update pyproject.toml with entry points for CLI (skills-runner = skills_runner.cli:main)
- [ ] T058 Add type hints validation across all modules (mypy --strict compatibility)
- [ ] T059 Add docstrings to all public APIs (classes, functions, modules)
- [ ] T060 Run quickstart.md validation per quickstart guide test scenarios
- [ ] T061 [P] Add performance logging for tool operations (list_skills, get_skill, read_file_in_skill, run_python_script)
- [ ] T062 [P] Create CONTRIBUTING.md with development setup and testing guidelines
- [ ] T063 Code cleanup and refactoring (remove dead code, improve naming)
- [ ] T064 Performance optimization if targets not met (SC-004, SC-005, SC-006)
- [ ] T065 Security audit of path validation and subprocess execution
- [ ] T066 [P] Add logging configuration in src/skills_runner/config.py (optional logging to file)

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
     ↓
Phase 2 (Foundational) ← BLOCKS all user stories
     ↓
     ├─→ Phase 3 (User Story 1 - P1) [Can run in parallel with Phase 4, 5]
     ├─→ Phase 4 (User Story 2 - P2) [Can run in parallel with Phase 3, 5]
     └─→ Phase 5 (User Story 3 - P3) [Can run in parallel with Phase 3, 4]
     ↓
Phase 6 (Polish) ← After all desired user stories complete
```

### User Story Independence

- **User Story 1 (P1)**: Independent - only depends on Foundational (T009-T013)
- **User Story 2 (P2)**: Independent - only depends on Foundational + US1's Conversation class (T018)
- **User Story 3 (P3)**: Independent - only depends on Foundational + US2's Skill model (T027)

### Parallelization Opportunities

**Phase 1**: T003, T004, T005, T006, T007 can run in parallel after T001-T002

**Phase 2**: T009, T010, T011, T012, T013 can all run in parallel

**Phase 3 (US1)**:
- Tests: T014, T015 can run in parallel (both are contract/integration tests)
- Models: T016, T017 can run in parallel (independent modules)
- Unit tests: T021, T022 can run in parallel

**Phase 4 (US2)**:
- Tests: T023, T024, T025, T026 can all run in parallel
- Implementation: T027, T028, T029, T030 can run in parallel (independent functions)
- Unit tests: T036, T037, T038, T039 can all run in parallel

**Phase 5 (US3)**:
- Tests: T040, T041 can run in parallel
- Models: T042, T043 can run in parallel
- Unit tests: T050, T051, T052 can all run in parallel

**Phase 6**: T053, T054, T055, T056, T057, T061, T062, T066 can all run in parallel

### Recommended MVP Implementation Order

1. **Complete Phase 1-2** (Setup + Foundational): T001-T013
2. **Complete User Story 1** (P1 - Basic LLM): T014-T022
3. **Validate US1**: Test basic LLM conversation works end-to-end
4. **Complete User Story 2** (P2 - Skills Discovery): T023-T039
5. **Validate US1+US2**: Test skills discovery in conversation
6. **Complete User Story 3** (P3 - Script Execution): T040-T052
7. **Validate US1+US2+US3**: Test full workflow (discover skill → read docs → execute script)
8. **Polish** (Phase 6): T053-T066

---

## Parallel Execution Example: User Story 2

**Scenario**: Team of 3 developers implementing Skills Discovery simultaneously

```bash
# Developer 1: Contract tests (can write before implementation exists)
- T023 [P] [US2] Contract test for LIST_SKILLS
- T024 [P] [US2] Contract test for GET_SKILL
- T025 [P] [US2] Contract test for READ_FILE_IN_SKILL

# Developer 2: Core implementation (3 independent tool functions)
- T027 [P] [US2] Skill model
- T028 [P] [US2] list_skills function
- T029 [P] [US2] get_skill function
- T030 [P] [US2] read_file_in_skill function

# Developer 3: Integration and validation
- T026 [P] [US2] Integration test
- T031 [US2] Tool definitions (depends on T028-T030 completion)
- T032 [US2] Integrate with Conversation (depends on T031)
```

All three developers can work simultaneously on different files without conflicts.

---

## Task Summary

- **Total Tasks**: 66
- **Phase 1 (Setup)**: 8 tasks
- **Phase 2 (Foundational)**: 5 tasks (BLOCKING)
- **Phase 3 (User Story 1 - P1)**: 9 tasks (4 tests, 5 implementation)
- **Phase 4 (User Story 2 - P2)**: 17 tasks (4 tests, 13 implementation)
- **Phase 5 (User Story 3 - P3)**: 13 tasks (2 tests, 11 implementation)
- **Phase 6 (Polish)**: 14 tasks

**Parallelizable Tasks**: 41 tasks marked with [P] can run in parallel within their phase

**Estimated MVP Scope**: Phase 1-2 + User Story 1 = 22 tasks (T001-T022)
- Delivers: Working LLM API integration via library and CLI
- Validates: Core value proposition (OpenAI-compatible LLM wrapper)
- MVP Duration: ~3-5 days for single developer

**Full Feature Scope**: All 66 tasks
- Delivers: Complete Skills Runner with all 4 tools
- Duration: ~10-15 days for single developer, ~5-7 days for team of 3

---

## Testing Strategy

### Contract Tests (Tests First, Ensure FAIL)
- Write contract tests before implementation
- Verify they FAIL with clear error (no implementation yet)
- Implement feature until tests PASS
- Contract tests validate tool input/output schemas per contracts/

### Integration Tests
- Test end-to-end flows (conversation with tools)
- Verify automatic tool execution and user visibility
- Test error handling across system boundaries

### Unit Tests
- Test individual modules in isolation
- Mock external dependencies (API calls, filesystem)
- Validate edge cases and error conditions

### Performance Validation
- LIST_SKILLS <1s for 100 skills (SC-004)
- GET_SKILL <500ms for 1MB files (SC-005)
- RUN_PYTHON_SCRIPT <5s for simple scripts (SC-006)
- Measure and log actual performance in tests

---

## Implementation Strategy

### MVP-First Approach
1. **Start with US1 only** (T001-T022) - validates API integration
2. **Test with real API** - ensure OpenAI-compatible format works
3. **Expand to US2** - adds skills discovery (T023-T039)
4. **Complete with US3** - adds script execution (T040-T052)
5. **Polish last** - documentation, optimization (T053-T066)

### Incremental Delivery
- Each user story is independently testable
- Can release after US1 (basic LLM wrapper)
- Can release after US2 (skills discovery)
- Full feature after US3 (script execution)

### Quality Gates
- All tests PASS before marking task complete
- Code review before merging tasks
- Type hints validated with mypy
- No TODO/FIXME comments in production code
- All error messages are clear and actionable

---

## Notes

- **File Paths**: All paths assume single project structure per plan.md
- **Parallelization**: Tasks marked [P] have no dependencies within their phase
- **User Story Labels**: [US1], [US2], [US3] enable tracking by story
- **Tests Optional**: Contract/integration tests can be deferred if rapid MVP needed
- **MVP Flexibility**: Can release after any complete user story (US1, US1+US2, or US1+US2+US3)
