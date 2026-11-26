import asyncio
import json
from collections.abc import Callable
from contextlib import aclosing
from secrets import token_urlsafe
from typing import Annotated, Any

from anyio import create_task_group
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, ValidationError

from src.analytics.worker import Call, Insights
from src.api.live_mode import ConnectionMode, Mode, live_allowed, send_mode, switch_mode
from src.core.settings import Settings
from src.crm.conversation import BookingSession
from src.llm.claims import small_talk
from src.llm.grounded import HOW
from src.llm.reply import ReplyPath
from src.llm.sentences import SentenceBuffer
from src.memory.session import LeadSession
from src.rag.index import Knowledge


class TextTurn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    text: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]
    simulate_failure: bool = False
    end_call: bool = False
    turn_id: Annotated[int, Field(ge=1, le=2_147_483_647)] | None = None


class ModeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mode: Mode


async def text_session(socket: WebSocket) -> None:
    # Serve the UI on the same origin. Local scripts can omit Origin.
    origin = socket.headers.get("origin")
    host = socket.headers.get("host")
    scheme = "https" if socket.url.scheme == "wss" else "http"
    if origin is not None and origin != f"{scheme}://{host}":
        await socket.close(code=1008)
        return

    await socket.accept()
    incoming: asyncio.Queue[dict[str, object]] = asyncio.Queue(maxsize=4)

    async def receive() -> None:
        while True:
            frame = await socket.receive()
            if frame["type"] == "websocket.disconnect":
                return
            if incoming.full():
                await socket.close(code=1008)
                return
            incoming.put_nowait(dict(frame))

    async with create_task_group() as tasks:

        async def read_until_disconnect() -> None:
            try:
                await receive()
            finally:
                tasks.cancel_scope.cancel()

        async def handle_until_end() -> None:
            try:

                async def publish_analysis(
                    turn_id: int, result: asyncio.Future[dict[str, Any]]
                ) -> None:
                    try:
                        await socket.send_json(
                            {"type": "analysis", "turn_id": turn_id, **await result}
                        )
                    except WebSocketDisconnect:
                        return

                def publish(turn_id: int, result: asyncio.Future[dict[str, Any]]) -> None:
                    tasks.start_soon(publish_analysis, turn_id, result)

                await run_turns(socket, incoming, publish)
            finally:
                tasks.cancel_scope.cancel()

        tasks.start_soon(read_until_disconnect)
        tasks.start_soon(handle_until_end)


async def run_turns(
    socket: WebSocket,
    incoming: asyncio.Queue[dict[str, object]],
    publish: Callable[[int, asyncio.Future[dict[str, Any]]], None],
) -> None:

    settings: Settings = socket.app.state.settings
    replies: ReplyPath = socket.app.state.replies
    knowledge: Knowledge = socket.app.state.knowledge
    session = LeadSession()
    booking = BookingSession(socket.app.state.crm)
    insights: Insights = socket.app.state.insights
    call = Call()
    state = ConnectionMode(settings.agent_mode, cloud_stt=settings.voice_stt == "gemini")
    voice_session = token_urlsafe(24)
    socket.app.state.voice_sessions[voice_session] = state
    try:
        await socket.send_json(
            {
                "type": "ready",
                "mode": settings.agent_mode,
                "allow_fallback_demo": settings.allow_fallback_demo,
                "voice_session": voice_session,
                "live_allowed": live_allowed(settings),
                "model": settings.gemini_model if state.mode == "live" else None,
                "quota": replies.budget.usage() if isinstance(replies, ReplyPath) else None,
            }
        )
        while True:
            frame = await incoming.get()
            raw = frame.get("text")
            try:
                if not isinstance(raw, str) or len(raw) > 4096:
                    raise ValueError("Expected a text frame up to 4096 characters")
                payload = json.loads(raw)
                if isinstance(payload, dict) and "mode" in payload:
                    request = ModeRequest.model_validate(payload)
                    await switch_mode(socket, state, request.mode, replies)
                    continue
                turn = TextTurn.model_validate(payload)
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
            starting_live = state.mode == "live"
            if starting_live and not turn.simulate_failure:
                usage = replies.budget.usage()
                if state.quota_notice or usage["used"] >= usage["cap"]:
                    state.mode = "mock"
                    state.quota_notice = False
                    await send_mode(
                        socket, state, replies, "quota", "Live quota reached, using mock"
                    )
            booking_reply = (
                await asyncio.to_thread(booking.handle, turn.text, session)
                if not turn.simulate_failure
                else None
            )
            local_reply = booking_reply or (
                (session.handle(turn.text) or small_talk(turn.text))
                if not turn.simulate_failure
                else None
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
                origin = "knowledge" if citation else "approved"
                first = None
                if (
                    answer
                    and answer.chunk
                    and answer.chunk.kind in {"product", "faq"}
                    and state.mode == "live"
                    and HOW.search(turn.text)
                ):
                    elaboration, first, limited = await replies.elaborate(answer.text)
                    state.quota_notice = limited
                    if elaboration:
                        text, origin = elaboration, "gemini"
                        await socket.send_json(
                            {
                                "type": "provider",
                                "provider": "Gemini A",
                                "model": settings.gemini_model,
                                "status": "active",
                            }
                        )
                        await socket.send_json({"type": "first_text", "latency_ms": first})
                assert text is not None
                if origin == "gemini":
                    splitter = SentenceBuffer()
                    for sentence in [*splitter.push(text), *splitter.finish()]:
                        await socket.send_json({"type": "sentence", "text": sentence})
                else:
                    await socket.send_json({"type": "sentence", "text": text})
                await socket.send_json(
                    {
                        "type": "reply",
                        "text": text,
                        "provider": settings.gemini_model if origin == "gemini" else label,
                        "mode": label,
                        "citation": citation,
                        "latency_ms": first if origin == "gemini" else None,
                        "origin": origin,
                        "passage": answer.text if origin == "gemini" and answer else None,
                    }
                )
                if booking_reply is None:
                    session.remember(turn.text, text)
            else:
                async with aclosing(
                    replies.stream(
                        turn.text,
                        simulate=turn.simulate_failure,
                        history=tuple(session.history),
                        mode=state.mode,
                    )
                ) as events:
                    async for event in events:
                        await socket.send_json(event)
                        if starting_live and not turn.simulate_failure and event.get("code") == 429:
                            state.quota_notice = True
                        if event["type"] == "reply" and not turn.simulate_failure:
                            session.remember(turn.text, event["text"])
            if booking.contact and not turn.simulate_failure:
                fields = session.profile.model_dump(
                    mode="json", exclude_none=True, exclude={"language"}
                )
                await asyncio.to_thread(booking.crm.save, booking.contact, fields)
            result = None
            if not turn.simulate_failure:
                call.booked = booking.booked
                if turn.turn_id is not None:
                    result = asyncio.get_running_loop().create_future()
                insights.submit(call, turn.text, result)
            await socket.send_json(
                {
                    "type": "profile",
                    "profile": session.profile.model_dump(mode="json", exclude_none=True),
                    "pending": session.pending.model_dump(mode="json", exclude_none=True)
                    if session.pending
                    else None,
                }
            )
            if turn.turn_id is not None and result is not None:
                publish(turn.turn_id, result)
            if starting_live and not turn.simulate_failure:
                usage = replies.budget.usage()
                if state.mode == "live" and (state.quota_notice or usage["used"] >= usage["cap"]):
                    state.mode = "mock"
                    state.quota_notice = False
                    await send_mode(
                        socket, state, replies, "quota", "Live quota reached, using mock"
                    )
                elif state.mode == "live":
                    await socket.send_json({"type": "quota", "quota": usage})
    except WebSocketDisconnect:
        return
    finally:
        socket.app.state.voice_sessions.pop(voice_session, None)
        insights.submit(call, None)
