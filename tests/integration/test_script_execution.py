from skills_runner.conversation import Conversation
from skills_runner.llm_client import LLMClient


def test_script_execution_flow(monkeypatch, tmp_path):
    client = LLMClient(
        api_key="test-key",
        api_base_url="https://api.example.com/v1",
        model_name="gpt-4"
    )

    def fake_chat(messages, tools):
        return {"role": "assistant", "content": "done"}

    monkeypatch.setattr(client, "chat", fake_chat)

    convo = Conversation(client=client, tools=[], skills_folder=tmp_path)
    response = convo.send("run script")

    assert response == "done"
