from pathlib import Path

from skills_runner.conversation import Conversation
from skills_runner.llm_client import LLMClient


def test_conversation_returns_assistant_message(monkeypatch):
    client = LLMClient(
        api_key="test-key",
        api_base_url="https://api.example.com/v1",
        model_name="gpt-4"
    )

    def fake_chat(messages, tools):
        return {"role": "assistant", "content": "hello"}

    monkeypatch.setattr(client, "chat", fake_chat)

    convo = Conversation(client=client, tools=[], skills_folder=Path("."))
    assert convo.send("hi") == "hello"


def test_conversation_handles_tool_calls(monkeypatch, tmp_path):
    client = LLMClient(
        api_key="test-key",
        api_base_url="https://api.example.com/v1",
        model_name="gpt-4"
    )

    calls = {"count": 0}

    def fake_chat(messages, tools):
        if calls["count"] == 0:
            calls["count"] += 1
            return {
                "role": "assistant",
                "tool_calls": [
                    {"id": "call_1", "function": {"name": "list_skills", "arguments": "{}"}}
                ],
            }
        return {"role": "assistant", "content": "done"}

    monkeypatch.setattr(client, "chat", fake_chat)

    convo = Conversation(client=client, tools=[], skills_folder=tmp_path)

    assert convo.send("hi") == "done"
