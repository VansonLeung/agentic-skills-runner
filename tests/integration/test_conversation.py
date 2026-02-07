from pathlib import Path

from skills_runner.conversation import Conversation
from skills_runner.llm_client import LLMClient


def test_basic_conversation_flow(monkeypatch):
    client = LLMClient(
        api_key="test-key",
        api_base_url="https://api.example.com/v1",
        model_name="gpt-4"
    )

    def fake_chat(messages, tools):
        return {"role": "assistant", "content": "hello"}

    monkeypatch.setattr(client, "chat", fake_chat)

    convo = Conversation(client=client, tools=[], skills_folder=Path("."))
    response = convo.send("hello")

    assert response == "hello"
