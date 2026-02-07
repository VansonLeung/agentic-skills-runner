# Quickstart Guide: LLM/VLM Skills Runner

**Feature**: 001-llm-skills-runner  
**Purpose**: Get up and running quickly with the Skills Runner toolkit

## Prerequisites

- Python 3.9 or higher
- OpenAI-compatible API credentials (OpenAI, Anthropic, or local model)
- pip for package installation

## Installation

### From PyPI (when published)
```bash
pip install skills-runner
```

### From Source (development)
```bash
git clone https://github.com/yourorg/agentic-skills-runner.git
cd agentic-skills-runner
pip install -e .
```

## Configuration

Create a `.env` file in your project root:

```bash
# Required: API credentials
LLM_API_KEY=sk-your-api-key-here
LLM_API_BASE_URL=https://api.openai.com/v1
LLM_MODEL_NAME=gpt-4

# Optional: Skills folder path (default: ./skills)
SKILLS_FOLDER_PATH=./skills

# Optional: Script execution timeout (default: 30 seconds)
SCRIPT_TIMEOUT_SECONDS=30
```

### Provider Examples

**OpenAI**:
```bash
LLM_API_KEY=sk-...
LLM_API_BASE_URL=https://api.openai.com/v1
LLM_MODEL_NAME=gpt-4
```

**Anthropic** (via compatibility endpoint):
```bash
LLM_API_KEY=sk-ant-...
LLM_API_BASE_URL=https://api.anthropic.com/v1
LLM_MODEL_NAME=claude-3-sonnet-20240229
```

**Local Model** (Ollama):
```bash
LLM_API_KEY=dummy
LLM_API_BASE_URL=http://localhost:11434/v1
LLM_MODEL_NAME=llama2
```

## Create Your First Skill

Create a skills folder with a sample skill:

```bash
mkdir -p skills/calculator
cd skills/calculator
```

Create `SKILL.MD`:
```markdown
# Calculator Skill

Provides basic arithmetic operations using Python.

## Capabilities

- Addition, subtraction, multiplication, division
- Power and modulo operations
- Works with integers and floating-point numbers

## Usage

Execute Python expressions for calculations:

```python
# Simple arithmetic
result = 2 + 2
print(result)  # Output: 4

# More complex
import math
result = math.sqrt(16) + math.pow(2, 3)
print(result)  # Output: 12.0
```

## Python Packages

This skill uses Python's built-in `math` module. No external packages required.
```

Optional: Create a virtual environment for the skill:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install numpy  # Example: add packages your skill needs
deactivate
```

## Usage

### Command Line Interface

**Start an interactive conversation:**
```bash
skills-runner chat
```

Or:
```bash
python -m skills_runner chat
```

**Single-shot query:**
```bash
skills-runner chat "What skills are available?"
```

**Example Session:**
```
$ skills-runner chat
Skills Runner v0.1.0
Type 'exit' to quit

You: What skills do I have?

🔧 Tool: list_skills()
🔧 Result: {" skills": ["calculator"]}