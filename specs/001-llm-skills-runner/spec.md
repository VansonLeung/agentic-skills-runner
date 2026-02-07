# Feature Specification: LLM/VLM Skills Runner

**Feature Branch**: `001-llm-skills-runner`  
**Created**: 2026-02-07  
**Status**: Draft  
**Input**: User description: "an LLM / VLM kit which has the following features: calls LLM / VLM APIs, when running the API, it has a tool called Skills, what Skills do to assist LLM to do extra powerful things: LIST_SKILLS - obtain a list of skills given a local folder of subfolders, GET_SKILL - given a subfolder name (of the skill) - look for SKILL.MD inside it and obtain / read / study the contents, READ_FILE_IN_SKILL - read any file within a skill subfolder (since not all information is in SKILL.MD, which serves as a table of contents), RUN_PYTHON_SCRIPT - given the subfolder name (of the skill) - let's say an venv is installed inside the subfolder, run a given python script (in which the python script is determined / composed by the LLM, and is probably taught by learning from the skill) and obtain result(s), the main folder to put subfolders of skills shall be configured in an .env or provided by a variable, the LLM / VLM API credentials and urls shall be configured in an .env, your development approach should be mainly focusing on the workable MVP first (i.e. LLM API working, Skills integration working). MVP simplification: scripts have full filesystem access (security/sandbox deferred to post-MVP). Future vision: will become an MCP server after MVP is validated."

## Clarifications

### Session 2026-02-07

- Q: How will users interact with this toolkit - as a CLI tool, library, API service, or GUI application? → A: Python library with optional CLI wrapper - both programmatic and command-line access
- Q: Which LLM/VLM API providers or protocols should be supported? → A: OpenAI-compatible API format (works with OpenAI, Anthropic, local models, etc.)
- Q: What are the working directory and file access boundaries when RUN_PYTHON_SCRIPT executes scripts in a skill's venv? → A: **MVP: Scripts have full filesystem access** (working directory set to skill folder by convention). Security/sandbox deferred to post-MVP.
- Q: When the LLM calls Skills tools, who initiates these calls - automatic or requiring user approval? → A: Automatic execution - LLM calls tools autonomously, user sees tool calls/results

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Basic LLM API Integration (Priority: P1) 🎯 MVP

A developer imports the toolkit as a Python library (or uses the CLI), configures it with OpenAI-compatible API credentials, and makes a simple text completion request, receiving a response from the language model.

**Why this priority**: This is the foundational capability. Without a working LLM connection, the entire toolkit is non-functional. This validates end-to-end API communication and configuration handling, delivering immediate value as a basic LLM wrapper that works with any OpenAI-compatible API.

**Independent Test**: Can be fully tested by providing API credentials via environment variables, making a single API call with a prompt (either via library import or CLI command), and verifying the response text is received and displayed correctly.

**Acceptance Scenarios**:

1. **Given** valid API credentials in .env file, **When** user calls the LLM with a text prompt, **Then** system returns the completion response from the API
2. **Given** missing or invalid API credentials, **When** user attempts to call the LLM, **Then** system displays a clear error message indicating credential issues
3. **Given** an API timeout or network error, **When** user makes a request, **Then** system handles the error gracefully and provides a meaningful error message

---

### User Story 2 - Skills Discovery System (Priority: P2) 🎯 MVP

A developer starts a conversation where the LLM autonomously discovers available skills in the configured folder and reads skill documentation. The LLM can read SKILL.MD as a table of contents, then read additional files within skills for deeper information. Tool calls and results are visible to the user, enabling the LLM to understand what capabilities are available without manual intervention.

**Why this priority**: Skills discovery is the bridge between basic LLM functionality and enhanced capabilities. Once implemented, it allows the system to be self-aware of its extensions, making the toolkit genuinely agentic. The automatic execution model means the LLM can explore and utilize skills naturally during conversation. READ_FILE_IN_SKILL enables rich skill documentation beyond a single markdown file.

**Independent Test**: Can be fully tested by creating a skills folder with several skill subfolders containing SKILL.MD files and additional documentation/scripts, starting a conversation that would benefit from skills, and verifying the LLM autonomously calls LIST_SKILLS, GET_SKILL, and READ_FILE_IN_SKILL with results displayed to the user.

**Acceptance Scenarios**:

1. **Given** a configured skills folder with multiple skill subfolders, **When** user invokes LIST_SKILLS, **Then** system returns a list of all skill names found
2. **Given** a skill subfolder with a SKILL.MD file, **When** user invokes GET_SKILL with the skill name, **Then** system reads and returns the complete contents of SKILL.MD
3. **Given** a skill subfolder without SKILL.MD, **When** user invokes GET_SKILL, **Then** system returns an error indicating missing documentation
4. **Given** an empty or non-existent skills folder path, **When** user invokes LIST_SKILLS, **Then** system returns an empty list or clear message indicating no skills found
5. **Given** an LLM conversation where the tool is available, **When** the LLM decides it needs to know available skills, **Then** LLM can successfully call LIST_SKILLS and use the results
6. **Given** a skill with SKILL.MD referencing additional files, **When** LLM invokes READ_FILE_IN_SKILL with skill name and relative file path, **Then** system reads and returns the file contents
7. **Given** a file path outside the skill folder, **When** LLM attempts to read it via READ_FILE_IN_SKILL, **Then** system returns an error preventing directory traversal

---

### User Story 3 - Skills Execution Engine (Priority: P3)

The LLM generates a Python script based on skill documentation, and the system executes it within the skill's isolated virtual environment, returning results to enhance the LLM's response.

**Why this priority**: This unlocks the full agentic potential - skills can now perform actual computations, data processing, or external integrations. However, it requires the foundation of P1 (LLM working) and P2 (skill awareness) to be useful.

**Independent Test**: Can be fully tested by creating a skill with an initialized venv, having the LLM generate a simple Python script (e.g., math calculation), calling RUN_PYTHON_SCRIPT with the skill name and script, and verifying the script executes in the correct venv and returns output.

**Acceptance Scenarios**:

1. **Given** a skill with an initialized venv, **When** user invokes RUN_PYTHON_SCRIPT with a valid Python script, **Then** system executes the script in the skill's venv and returns stdout/stderr
2. **Given** a Python script with syntax errors, **When** user invokes RUN_PYTHON_SCRIPT, **Then** system captures and returns the Python error message
3. **Given** a script that imports skill-specific packages, **When** executed, **Then** system successfully uses the packages from the skill's venv
4. **Given** a long-running script, **When** execution exceeds a reasonable timeout, **Then** system terminates the process and returns a timeout error
5. **Given** a script that writes files, **When** executed, **Then** system runs script with skill folder as working directory (MVP: full filesystem access)
6. **Given** an LLM conversation requiring computation, **When** LLM autonomously generates appropriate code using skill documentation, **Then** LLM calls RUN_PYTHON_SCRIPT automatically and user sees tool call/results before receiving the enhanced response

---

### Edge Cases

- What happens when the skills folder path in .env points to a non-existent directory?
- What happens when a SKILL.MD file contains malformed or extremely large content?
- How does the system handle concurrent RUN_PYTHON_SCRIPT requests for the same skill?
- What happens when a skill's venv is missing or corrupted?
- How does the system handle skills with identical names in the skills folder?
- What happens when API credentials expire mid-conversation?
- How does the system handle extremely large API responses or images?
- What happens when LLM tries to execute a script but the skill has no venv?
- How does the system prevent infinite loops or resource exhaustion from generated scripts?
- What happens if a script tries to write files to the parent skills directory (should be blocked)?
- How are tool execution errors communicated to both the LLM and the user?
- What happens when the API provider doesn't fully support OpenAI-compatible format?
- How does the CLI handle interactive conversations vs single-shot requests?

## Requirements *(mandatory)*

### Functional Requirements

**Deployment & Interface**

- **FR-001**: System MUST be packaged as a Python library installable via pip
- **FR-002**: System MUST provide a command-line interface (CLI) as an optional entry point for library functionality
- **FR-003**: System MUST expose a programmatic API for library users to import and integrate into their applications

**Configuration & Environment**

- **FR-004**: System MUST load LLM/VLM API credentials (API keys, endpoints, model names) from environment variables or .env file
- **FR-005**: System MUST load skills folder path from environment variables or .env file with a sensible default (e.g., "./skills")
- **FR-006**: System MUST validate that required configuration values are present before attempting operations
- **FR-007**: System MUST provide clear error messages when configuration is missing or invalid

**LLM/VLM API Integration**

- **FR-008**: System MUST use OpenAI-compatible API format for all LLM requests
- **FR-009**: System MUST support HTTP-based API calls to OpenAI-compatible endpoints (text completion)
- **FR-010**: *(Post-MVP)* System SHOULD support vision endpoints for multimodal requests
- **FR-011**: System MUST work with any OpenAI-compatible provider (OpenAI, Anthropic compatibility mode, local models, vLLM, Ollama, etc.)
- **FR-012**: System MUST pass user prompts to the API and return responses to the caller
- **FR-013**: System MUST handle API errors gracefully (timeouts, rate limits, invalid responses)
- **FR-014**: System MUST register Skills tools using OpenAI-compatible tool/function calling format

**Skills Tool - LIST_SKILLS**

- **FR-015**: System MUST scan the configured skills folder for subfolders
- **FR-016**: System MUST return a list of skill names (subfolder names) found in the skills directory
- **FR-017**: System MUST handle cases where the skills folder is empty or doesn't exist
- **FR-018**: System MUST automatically execute LIST_SKILLS when LLM calls it, displaying the tool call and results to the user

**Skills Tool - GET_SKILL**

- **FR-019**: System MUST accept a skill name parameter and locate the corresponding subfolder
- **FR-020**: System MUST read the contents of SKILL.MD file within the specified skill subfolder
- **FR-021**: System MUST return the full text contents of SKILL.MD to the LLM with tool result visible to user
- **FR-022**: System MUST handle cases where SKILL.MD doesn't exist in the skill folder
- **FR-023**: System MUST automatically execute GET_SKILL when LLM calls it, displaying the tool call and results to the user

**Skills Tool - READ_FILE_IN_SKILL**

- **FR-024**: System MUST accept a skill name and relative file path as parameters
- **FR-025**: System MUST locate the specified skill subfolder and resolve the relative file path within it
- **FR-026**: System MUST prevent directory traversal attacks (e.g., "../../../etc/passwd") by validating paths
- **FR-027**: System MUST read and return the contents of the specified file within the skill folder
- **FR-028**: System MUST handle cases where the requested file doesn't exist
- **FR-029**: System MUST automatically execute READ_FILE_IN_SKILL when LLM calls it, displaying the tool call and results to the user
- **FR-030**: System MUST support reading various file types (text, scripts, documentation, configuration files)

**Skills Tool - RUN_PYTHON_SCRIPT**

- **FR-031**: System MUST accept a skill name and Python script code as parameters
- **FR-032**: System MUST locate the specified skill's virtual environment (venv)
- **FR-033**: System MUST execute scripts with the skill folder as the working directory
- **FR-034**: System MUST allow scripts full filesystem access (MVP simplification - security/sandbox deferred to post-MVP)
- **FR-035**: System MUST execute the provided Python script using the skill's venv Python interpreter
- **FR-036**: System MUST capture both stdout and stderr from script execution
- **FR-037**: System MUST return execution results (output or errors) to the LLM with tool result visible to user
- **FR-038**: System MUST implement execution timeout to prevent runaway scripts (default 30 seconds)
- **FR-039**: System MUST handle cases where the skill's venv is missing or invalid
- **FR-040**: System MUST automatically execute RUN_PYTHON_SCRIPT when LLM calls it, displaying the tool call and results to the user

**Error Handling & Safety**

- **FR-041**: System MUST validate skill names and file paths to prevent directory traversal attacks
- **FR-042**: System MUST provide meaningful error messages for all failure scenarios
- **FR-043**: System MUST ensure script execution uses the skill's venv (environment isolation)
- **FR-044**: System MUST display all tool calls and results to the user for transparency

### Key Entities

- **LLMClient**: Represents the connection and interface to LLM/VLM APIs. Attributes include API endpoint URL, authentication credentials, model identifier, and request/response handling.

- **Skill**: Represents a capability extension stored as a subfolder. Attributes include skill name (folder name), documentation path (SKILL.MD), virtual environment path (venv folder), and status (available/unavailable).

- **SkillsTool**: Represents the tool interface exposed to the LLM. Contains four operations (LIST_SKILLS, GET_SKILL, READ_FILE_IN_SKILL, RUN_PYTHON_SCRIPT) and manages skill folder access.

- **ScriptExecution**: Represents a Python script execution request. Attributes include target skill, script code, execution timeout, venv path, and results (output, errors, exit code).

- **Configuration**: Represents system configuration loaded from environment. Attributes include API credentials, API endpoints, skills folder path, timeout values, and validation status.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Developer can install library via pip, configure with .env, and make a successful LLM API call within 5 minutes of setup
- **SC-002**: CLI provides immediate access to toolkit functionality without requiring Python code
- **SC-003**: System successfully retrieves and displays responses from any OpenAI-compatible API with 100% of valid requests
- **SC-004**: LIST_SKILLS operation completes and returns results in under 1 second for folders with up to 100 skills
- **SC-005**: GET_SKILL operation successfully reads and returns SKILL.MD content in under 500ms for files up to 1MB
- **SC-006**: RUN_PYTHON_SCRIPT executes simple scripts (under 100 lines) and returns results in under 5 seconds
- **SC-007**: LLM autonomously uses SKILLS tools (LIST_SKILLS, GET_SKILL, READ_FILE_IN_SKILL, RUN_PYTHON_SCRIPT) to discover, learn documentation, and execute code for at least 3 different skills in a single conversation without manual intervention
- **SC-008**: All tool calls and results are visible to the user in real-time during conversation
- **SC-009**: System handles API errors gracefully with clear messages in 100% of error scenarios
- **SC-010**: Configuration errors are detected and reported with actionable messages before any API calls are attempted
- **SC-011**: READ_FILE_IN_SKILL successfully reads skill files and prevents directory traversal in 100% of attempts
- **SC-012**: System achieves 90% uptime for API operations excluding external API downtime

## Assumptions

- Target LLM/VLM APIs support OpenAI-compatible tool/function calling format
- API providers support the OpenAI-compatible request/response schema (most modern providers do)
- Skills will be organized as individual subfolders within a single parent directory
- Each skill's documentation follows a standard SKILL.MD naming convention (serving as table of contents)
- SKILL.MD may reference additional files within the skill folder for detailed documentation
- Python virtual environments (venv) are pre-created and managed outside this system
- API credentials have sufficient rate limits and quotas for expected usage
- Network connectivity to LLM/VLM API endpoints is available
- Skills folder is on local filesystem (not remote/network storage)
- **MVP Security Model**: Python scripts have full filesystem access - user's responsibility to manage security (sandbox/isolation deferred to post-MVP)
- Users accept automatic tool execution model and rely on visibility for oversight
- Standard environment variable naming will be used (e.g., LLM_API_KEY, LLM_API_BASE_URL, SKILLS_FOLDER_PATH)
- Execution timeout default will be 30 seconds unless specified otherwise

## Out of Scope (MVP)

- **MCP Server Implementation**: Future vision is to become a Model Context Protocol (MCP) server, but MVP will not implement the MCP protocol. Be aware of MCP architecture when designing to facilitate future migration.
- **VLM/Vision Support**: Multimodal image inputs deferred to post-MVP (FR-010). MVP focuses on text-only LLM interactions.
- **Advanced Security Sandbox**: Script execution sandboxing, filesystem access restrictions, resource limits beyond basic timeout
- **Skill Version Management**: Tracking skill versions, updates, or dependencies
- **Multi-tenancy**: Isolating skills or conversations between different users
- **Persistent Conversation State**: Saving/loading conversation history across sessions
