from __future__ import annotations

from typing import Any, Dict, List, Optional
import json
import queue
import threading
import time
import uuid

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from .config import Configuration
from .conversation import Conversation
from .llm_client import LLMClient
from .skills_tool import confirm_create_skill
from .tools import SKILLS_TOOLS


class ChatCompletionRequest(BaseModel):
    model: Optional[str] = None
    messages: List[Dict[str, Any]]
    stream: bool = False

    class Config:
        extra = "allow"


app = FastAPI(title="Skills Runner API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _build_response(content: str, model: str, request_id: str) -> Dict[str, Any]:
    return {
        "id": request_id,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
    }


def _chunk_text(text: str, size: int = 24) -> List[str]:
    return [text[i : i + size] for i in range(0, len(text), size)]


def _stream_response(conversation: Conversation, model: str, request_id: str) -> StreamingResponse:
    created = int(time.time())

    def event_stream() -> Any:
        event_queue: "queue.Queue[Dict[str, Any]]" = queue.Queue()
        done_signal = object()

        def tool_event_handler(
            phase: str, tool_call: Dict[str, Any], result: Optional[Dict[str, Any]]
        ) -> None:
            event_queue.put(
                {
                    "type": "tool",
                    "phase": phase,
                    "tool_call": tool_call,
                    "result": result,
                }
            )

        def run_conversation() -> None:
            try:
                content = conversation.run(tool_event_handler=tool_event_handler)
                event_queue.put({"type": "final", "content": content})
            except Exception as exc:
                event_queue.put({"type": "error", "message": str(exc)})
            finally:
                event_queue.put({"type": "done", "signal": done_signal})

        threading.Thread(target=run_conversation, daemon=True).start()

        first_chunk = {
            "id": request_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model,
            "choices": [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": None}],
        }
        yield f"data: {json.dumps(first_chunk)}\n\n"

        while True:
            event = event_queue.get()
            if event.get("type") == "tool":
                payload = {
                    "type": "tool",
                    "phase": event.get("phase"),
                    "tool_call": event.get("tool_call"),
                    "result": event.get("result"),
                }
                yield f"data: {json.dumps(payload)}\n\n"
                continue

            if event.get("type") == "error":
                payload = {
                    "type": "error",
                    "message": event.get("message"),
                }
                yield f"data: {json.dumps(payload)}\n\n"
                continue

            if event.get("type") == "final":
                content = event.get("content", "")
                for chunk in _chunk_text(content):
                    payload = {
                        "id": request_id,
                        "object": "chat.completion.chunk",
                        "created": created,
                        "model": model,
                        "choices": [
                            {"index": 0, "delta": {"content": chunk}, "finish_reason": None}
                        ],
                    }
                    yield f"data: {json.dumps(payload)}\n\n"

            if event.get("type") == "done":
                done_payload = {
                    "id": request_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": model,
                    "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
                }
                yield f"data: {json.dumps(done_payload)}\n\n"
                yield "data: [DONE]\n\n"
                break

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/v1/chat/completions")
def chat_completions(request: ChatCompletionRequest) -> Any:
    config = Configuration.from_env()
    model = request.model or config.model_name
    client = LLMClient(
        api_key=config.api_key,
        api_base_url=config.api_base_url,
        model_name=model,
        timeout_seconds=config.timeout_seconds,
    )

    conversation = Conversation(client=client, tools=SKILLS_TOOLS, skills_folder=config.skills_folder)
    conversation.load_messages(request.messages)

    request_id = f"chatcmpl-{uuid.uuid4().hex}"

    if request.stream:
        return _stream_response(conversation, model, request_id)

    content = conversation.run()

    payload = _build_response(content, model, request_id)
    return JSONResponse(payload)


@app.get("/v1/models")
def list_models() -> Any:
    """Return the list of available models from config."""
    config = Configuration.from_env()
    models = [
        {"id": name, "object": "model", "owned_by": "config"}
        for name in config.model_names
    ]
    return JSONResponse({"object": "list", "data": models, "default": config.model_name})


class ConfirmCreateSkillRequest(BaseModel):
    confirmation_token: str


@app.post("/v1/confirm_create_skill")
def confirm_create_skill_endpoint(request: ConfirmCreateSkillRequest) -> Any:
    """Execute a pending skill creation after user confirmation."""
    result = confirm_create_skill(request.confirmation_token)
    return JSONResponse(result)
