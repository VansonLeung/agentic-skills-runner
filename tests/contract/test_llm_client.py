import pytest

from skills_runner.llm_client import LLMClient


def test_llm_client_sends_request_and_parses_response(monkeypatch):
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
                return {
                    "choices": [
                        {"message": {"role": "assistant", "content": "ok"}}
                    ]
                }

        assert url.endswith("/chat/completions")
        assert json["model"] == "gpt-4"
        return Response()

    monkeypatch.setattr("skills_runner.llm_client.requests.post", fake_post)

    message = client.chat([{"role": "user", "content": "hi"}], tools=[])

    assert message["role"] == "assistant"
    assert message["content"] == "ok"
