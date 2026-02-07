from pathlib import Path

from skills_runner.conversation import Conversation
from skills_runner.llm_client import LLMClient


def test_skills_discovery_flow(monkeypatch):
    client = LLMClient(
        api_key="test-key",
        api_base_url="https://api.example.com/v1",
        model_name="gpt-4"
    )

    def fake_chat(messages, tools):
        return {"role": "assistant", "content": "done"}

    monkeypatch.setattr(client, "chat", fake_chat)

    convo = Conversation(client=client, tools=[], skills_folder=Path("."))
    response = convo.send("list skills")

    assert response == "done"
