# LLM Skills Runner

A lightweight Python toolkit for OpenAI-compatible LLM APIs with Skills-based tool execution.

## Quickstart

```bash
pip install -e .
```

Create a .env file:

```bash
LLM_API_KEY=sk-your-api-key
LLM_API_BASE_URL=https://api.openai.com/v1
LLM_MODEL_NAME=gpt-4
SKILLS_FOLDER_PATH=./skills
SCRIPT_TIMEOUT_SECONDS=30
```

Start a chat session:

```bash
python -m skills_runner chat "What skills are available?"
```

Start the API server:

```bash
uvicorn skills_runner.api:app --reload
```

## Library Usage

```python
from skills_runner.config import Configuration
from skills_runner.conversation import Conversation
from skills_runner.llm_client import LLMClient
from skills_runner.tools import SKILLS_TOOLS

config = Configuration.from_env()
client = LLMClient(
    api_key=config.api_key,
    api_base_url=config.api_base_url,
    model_name=config.model_name,
    timeout_seconds=config.timeout_seconds,
)

conversation = Conversation(
    client=client,
    tools=SKILLS_TOOLS,
    skills_folder=config.skills_folder,
)

response = conversation.send("What skills are available?")
print(response)
```

## CLI Usage

Interactive mode:
```bash
skills-runner chat
```

Single-shot mode:
```bash
skills-runner chat "List my skills"
```

## API Usage

OpenAI-compatible chat endpoint:

```bash
curl http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "gpt-4",
        "messages": [{"role": "user", "content": "What skills are available?"}]
    }'
```

Streaming response:

```bash
curl http://localhost:8000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -d '{
        "model": "gpt-4",
        "stream": true,
        "messages": [{"role": "user", "content": "What skills are available?"}]
    }'
```

## Security Considerations

- MVP scripts run with full filesystem access; users must trust skill code and generated scripts.
- Skill name and file path validation prevents directory traversal for read tools.
- No sandboxing or resource isolation is enforced in MVP (post-MVP enhancement).
