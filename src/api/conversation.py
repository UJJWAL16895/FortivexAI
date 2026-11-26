"""Run a live turn before dispatching any requested application action."""

import asyncio
from contextlib import aclosing
from typing import Any

from fastapi import WebSocket

from src.api.live_mode import ConnectionMode, send_mode
from src.crm.conversation import BookingSession
from src.llm.reply import ReplyPath
from src.memory.session import LeadSession
from src.rag.index import Knowledge

OFFLINE = "Live model unavailable, switching to mock."


async def live_turn(
    socket: WebSocket,
    text: str,
    state: ConnectionMode,
    replies: ReplyPath,
    knowledge: Knowledge,
    session: LeadSession,
    booking: BookingSession,
) -> None:
    evidence = await asyncio.to_thread(knowledge.retrieve, text)
    profile = session.profile.model_dump(mode="json", exclude_none=True)
    if session.pending:
        profile["pending_confirmation"] = session.pending.model_dump(mode="json", exclude_none=True)
    profile["booking_offered"] = bool(booking.slot and not booking.booked)
    quota = False
    reply: dict[str, Any] = {}
    async with aclosing(
        replies.converse(text, tuple(session.history), profile, evidence)
    ) as events:
        async for event in events:
            if event["type"] == "draft":
                action = event["action"]
                receipt = (
                    await asyncio.to_thread(booking.handle, text, session)
                    if action == "booking"
                    else None
                )
                confirmation = session.handle(text) if action == "lead" else None
                lines = event["lines"]
                spoken = [line.text for line in lines]
                source = next((line.evidence for line in lines if line.evidence), None)
                blocked = any(line.blocked for line in lines)
                model_written = any(not line.blocked and line.evidence is None for line in lines)
                origin = (
                    "gemini"
                    if model_written
                    else "knowledge"
                    if source and not blocked
                    else "approved"
                )
                mode = "live" if model_written else "knowledge" if source else "policy"
                if receipt or confirmation:
                    spoken = [receipt or confirmation]
                    source, blocked, origin = None, False, "approved"
                    mode = "booking" if receipt else "session"
                reply = {
                    "type": "reply",
                    "text": " ".join(spoken),
                    "mode": mode,
                    "origin": origin,
                    "provider": event["model"],
                    "latency_ms": event["latency_ms"],
                    "citation": {"id": source.id, "title": source.title, "source": source.source}
                    if source
                    else None,
                    "passage": source.text if source else None,
                    "approved_follow_up": blocked and (model_written or source is not None),
                }
                if blocked:
                    await socket.send_json(
                        {
                            "type": "provider",
                            "provider": "policy",
                            "model": "Knowledge guardrail",
                            "status": "active",
                        }
                    )
                for sentence in spoken:
                    await socket.send_json({"type": "sentence", "text": sentence})
            elif event["type"] != "unavailable":
                quota = quota or event.get("code") == 429
                await socket.send_json(event)
    if not reply:
        state.mode = "mock"
        quota = quota or state.quota_notice
        state.quota_notice = False
        label = "Live quota reached, using mock" if quota else OFFLINE
        await socket.send_json(
            {"type": "provider", "provider": "mock", "model": "mock", "status": "active"}
        )
        await socket.send_json({"type": "sentence", "text": label})
        reply = {
            "type": "reply",
            "text": label,
            "mode": "mock",
            "provider": "mock",
            "origin": "approved",
            "latency_ms": None,
        }
    await socket.send_json(reply)
    if reply["mode"] == "mock":
        await send_mode(socket, state, replies, "quota" if quota else "unavailable", reply["text"])
    session.remember(text, reply["text"])
