import json
from time import perf_counter_ns
from typing import Annotated

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel, ConfigDict, StringConstraints, ValidationError

from src.llm.mock import MockLLM


class TextTurn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]


async def text_session(socket: WebSocket) -> None:
    # Serve the UI on the same origin. Local scripts can omit Origin.
    origin = socket.headers.get("origin")
    host = socket.headers.get("host")
    scheme = "https" if socket.url.scheme == "wss" else "http"
    if origin is not None and origin != f"{scheme}://{host}":
        await socket.close(code=1008)
        return

    provider = MockLLM()
    await socket.accept()
    try:
        await socket.send_json({"type": "ready", "provider": provider.name})
        while True:
            frame = await socket.receive()
            if frame["type"] == "websocket.disconnect":
                return
            raw = frame.get("text")
            try:
                if raw is None or len(raw) > 4096:
                    raise ValueError("Expected a text frame up to 4096 characters")
                turn = TextTurn.model_validate(json.loads(raw))
            except (ValidationError, ValueError, RecursionError):
                await socket.send_json({"type": "error", "text": "Enter 1–500 characters."})
                continue
            started = perf_counter_ns()
            answer = await provider.reply(turn.text)
            await socket.send_json(
                {
                    "type": "reply",
                    "text": answer,
                    "latency_ms": round((perf_counter_ns() - started) / 1_000_000, 3),
                }
            )
    except WebSocketDisconnect:
        return
