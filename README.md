# Agentic Skills Runner

A lightweight Python toolkit for OpenAI-compatible LLM APIs with Skills-based tool execution.



https://github.com/user-attachments/assets/73b36255-e050-4777-b734-b5f458b3cd08



## Quickstart

```bash
pip install -e .
```

Create a `.env` file:

```bash
LLM_API_KEY=sk-your-api-key            # Optional for local LLMs (LM Studio, Ollama, vLLM)
LLM_API_BASE_URL=https://api.openai.com/v1
LLM_MODEL_NAME=gpt-4                   # Default model
LLM_MODEL_NAMES=gpt-4,gpt-3.5-turbo   # Comma-separated list for model selector (optional)
SKILLS_FOLDER_PATH=./SKILLS
SCRIPT_TIMEOUT_SECONDS=300
```

| Variable | Required | Description |
|---|---|---|
| `LLM_API_KEY` | No | API key for the LLM provider. Optional for local servers. |
| `LLM_API_BASE_URL` | **Yes** | Base URL of the OpenAI-compatible API endpoint. |
| `LLM_MODEL_NAME` | Yes* | Default model name to use. |
| `LLM_MODEL_NAMES` | No | Comma-separated list of models. Enables the model selector dropdown in the frontend. If set, `LLM_MODEL_NAME` can be omitted (first model becomes default). |
| `SKILLS_FOLDER_PATH` | No | Path to the skills folder. Defaults to `./skills`. |
| `SCRIPT_TIMEOUT_SECONDS` | No | Timeout for script execution and LLM API calls. Defaults to `30`. Increase for slower models. |

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

## Extending with Custom SKILLS

Learn how to create your own SKILLS to extend the LLM's capabilities:

- **[SKILLS Guide](SKILLS_GUIDE.md)**: Complete tutorial on creating custom SKILLS with examples and best practices
- **[Example SKILLS](example_skills/)**: Study the `calculator` and `web_browser` example SKILLS to understand the structure and patterns


## My remarks

I have been dabbling the core foundation of Claude Code Skills and made my own Skills runner. I can now download and install agent skills and use them with my locally hosted LLMs' chat API endpoint - while not paying 1 cent to Claude Code. hashtag#agentic

That said, it still blows my mind how simple and how useful it is to use agent skills. I believe Anthropic is going to beat OpenAI really really hard. There must be full of geniuses in Anthropic. If Anthropic goes public someday, I will deposit all my money in it.

localhost coder LLMs finally deserve some recognitions.
