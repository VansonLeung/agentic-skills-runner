import pytest
import requests

from skills_runner.exceptions import ToolExecutionError
from skills_runner.llm_client import LLMClient


def test_chat_returns_message(monkeypatch):
    client = LLMClient(
        api_key="test-key",
        api_base_url="https://api.example.com/v1",
        model_name="gpt-4"
    )

    def fake_post(url, headers, json, timeout):
        class Response:
            def raise_for_status(self):
                return None

            def json(self):
                return {"choices": [{"message": {"role": "assistant", "content": "ok"}}]}

        return Response()

    monkeypatch.setattr("skills_runner.llm_client.requests.post", fake_post)

    message = client.chat([{"role": "user", "content": "hi"}], tools=[])

    assert message["content"] == "ok"


def test_chat_raises_on_request_error(monkeypatch):
    client = LLMClient(
        api_key="test-key",
        api_base_url="https://api.example.com/v1",
        model_name="gpt-4"
    )

    def fake_post(url, headers, json, timeout):
        raise requests.RequestException("boom")

    monkeypatch.setattr("skills_runner.llm_client.requests.post", fake_post)

    with pytest.raises(ToolExecutionError):
        client.chat([{"role": "user", "content": "hi"}], tools=[])
