import json
from typing import Annotated

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel, ConfigDict, StringConstraints, ValidationError

from src.core.settings import Settings
from src.llm.reply import ReplyPath
from src.memory.session import LeadSession


class TextTurn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]
    simulate_failure: bool = False


async def text_session(socket: WebSocket) -> None:
    # Serve the UI on the same origin. Local scripts can omit Origin.
    origin = socket.headers.get("origin")
    host = socket.headers.get("host")
    scheme = "https" if socket.url.scheme == "wss" else "http"
    if origin is not None and origin != f"{scheme}://{host}":
        await socket.close(code=1008)
        return

    settings: Settings = socket.app.state.settings
    replies: ReplyPath = socket.app.state.replies
    session = LeadSession()
    await socket.accept()
    try:
        await socket.send_json(
            {
                "type": "ready",
                "mode": settings.agent_mode,
                "allow_fallback_demo": settings.allow_fallback_demo,
            }
        )
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
            if turn.simulate_failure and not settings.allow_fallback_demo:
                await socket.send_json({"type": "error", "text": "Fallback demo is disabled."})
                continue
            local_reply = session.handle(turn.text) if not turn.simulate_failure else None
            if local_reply is not None:
                await socket.send_json(
                    {
                        "type": "provider",
                        "provider": "session",
                        "model": "Lead session",
                        "status": "active",
                    }
                )
                await socket.send_json({"type": "sentence", "text": local_reply})
                await socket.send_json(
                    {
                        "type": "reply",
                        "text": local_reply,
                        "provider": "session",
                        "mode": "session",
                        "latency_ms": None,
                    }
                )
                session.remember(turn.text, local_reply)
            else:
                async for event in replies.stream(
                    turn.text, simulate=turn.simulate_failure, history=tuple(session.history)
                ):
                    await socket.send_json(event)
                    if event["type"] == "reply" and not turn.simulate_failure:
                        session.remember(turn.text, event["text"])
            await socket.send_json(
                {
                    "type": "profile",
                    "profile": session.profile.model_dump(mode="json", exclude_none=True),
                    "pending": session.pending.model_dump(mode="json", exclude_none=True)
                    if session.pending
                    else None,
                }
            )
    except WebSocketDisconnect:
        return
