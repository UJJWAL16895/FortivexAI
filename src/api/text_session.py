import asyncio
import json
from typing import Annotated

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel, ConfigDict, StringConstraints, ValidationError

from src.analytics.worker import Call, Insights
from src.core.settings import Settings
from src.crm.conversation import BookingSession
from src.llm.reply import ReplyPath
from src.memory.session import LeadSession
from src.rag.index import Knowledge


class TextTurn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]
    simulate_failure: bool = False
    end_call: bool = False


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
    knowledge: Knowledge = socket.app.state.knowledge
    session = LeadSession()
    booking = BookingSession(socket.app.state.crm)
    insights: Insights = socket.app.state.insights
    call = Call()
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
            if turn.end_call:
                await socket.send_json(
                    {
                        "type": "reply",
                        "text": "Conversation ended. Review the call in Insights.",
                        "mode": "session",
                        "latency_ms": None,
                    }
                )
                await socket.close()
                return
            booking_reply = (
                await asyncio.to_thread(booking.handle, turn.text, session)
                if not turn.simulate_failure
                else None
            )
            local_reply = booking_reply or (
                session.handle(turn.text) if not turn.simulate_failure else None
            )
            answer = (
                await asyncio.to_thread(knowledge.lookup, turn.text)
                if local_reply is None and not turn.simulate_failure
                else None
            )
            if local_reply is not None or answer is not None:
                label = "booking" if booking_reply else "session" if answer is None else "knowledge"
                text = answer.text if answer else local_reply
                citation = (
                    {"id": answer.chunk.id, "title": answer.chunk.title, "source": answer.source}
                    if answer and answer.chunk
                    else None
                )
                await socket.send_json(
                    {
                        "type": "provider",
                        "provider": label,
                        "model": {
                            "session": "Lead session",
                            "knowledge": "ShelfPilot knowledge",
                            "booking": "Booking and CRM",
                        }[label],
                        "status": "active",
                    }
                )
                await socket.send_json({"type": "sentence", "text": text})
                await socket.send_json(
                    {
                        "type": "reply",
                        "text": text,
                        "provider": label,
                        "mode": label,
                        "citation": citation,
                        "latency_ms": None,
                    }
                )
                assert text is not None
                if booking_reply is None:
                    session.remember(turn.text, text)
            else:
                async for event in replies.stream(
                    turn.text, simulate=turn.simulate_failure, history=tuple(session.history)
                ):
                    await socket.send_json(event)
                    if event["type"] == "reply" and not turn.simulate_failure:
                        session.remember(turn.text, event["text"])
            if booking.contact and not turn.simulate_failure:
                fields = session.profile.model_dump(
                    mode="json", exclude_none=True, exclude={"language"}
                )
                await asyncio.to_thread(booking.crm.save, booking.contact, fields)
            if not turn.simulate_failure:
                call.booked = booking.booked
                insights.submit(call, turn.text)
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
    finally:
        insights.submit(call, None)
