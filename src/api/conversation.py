"""Validate live understanding and let application state authorize side effects."""

import asyncio
from contextlib import aclosing
from datetime import datetime
from typing import Any

from fastapi import WebSocket

from src.analytics.core import TurnAnalysis
from src.analytics.worker import Call
from src.api.live_mode import ConnectionMode, send_mode
from src.crm.live_booking import LiveBooking
from src.llm.claims import CHECK_SHORT_EN, CHECK_SHORT_HI, HINDI
from src.llm.reply import ReplyPath
from src.memory.session import IST, ConfirmableDetails, LeadSession
from src.rag.index import Knowledge

OFFLINE = "Live model unavailable, switching to mock."


async def live_turn(
    socket: WebSocket,
    text: str,
    state: ConnectionMode,
    replies: ReplyPath,
    knowledge: Knowledge,
    session: LeadSession,
    booking: LiveBooking,
    call: Call,
) -> TurnAnalysis:
    evidence = await asyncio.to_thread(knowledge.retrieve, text)
    profile = session.profile.model_dump(mode="json", exclude_none=True)
    if session.pending:
        profile["pending_confirmation"] = session.pending.model_dump(mode="json", exclude_none=True)
    profile["booking"] = booking.snapshot()
    profile["local_time_ist"] = datetime.now(IST).isoformat()
    profile["decline_question_asked"] = call.decline_question_asked
    quota = False
    reply: dict[str, Any] = {}
    analysis = TurnAnalysis(status="not_analyzed")
    async with aclosing(
        replies.converse(text, tuple(session.history), profile, evidence)
    ) as events:
        async for event in events:
            if event["type"] == "draft":
                reply, analysis = await apply_draft(event, text, session, booking, call)
                if reply.pop("guardrail", False):
                    await socket.send_json(
                        {
                            "type": "provider",
                            "provider": "policy",
                            "model": "Knowledge guardrail",
                            "status": "active",
                        }
                    )
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
        reply = {
            "type": "reply",
            "text": label,
            "mode": "mock",
            "provider": "mock",
            "origin": "approved",
            "latency_ms": None,
            "sentences": [label],
        }
        call.negative_streak = 0
    for sentence in reply.pop("sentences"):
        await socket.send_json({"type": "sentence", "text": sentence})
    await socket.send_json(reply)
    if reply["mode"] == "mock":
        await send_mode(socket, state, replies, "quota" if quota else "unavailable", reply["text"])
    session.remember(text, reply["text"])
    return analysis


async def apply_draft(
    event: dict[str, Any],
    text: str,
    session: LeadSession,
    booking: LiveBooking,
    call: Call,
) -> tuple[dict[str, Any], TurnAnalysis]:
    signal = event["buying_signal"]
    draft = event["analysis"]
    analyzed = (
        draft is not None
        and draft.sentiment is not None
        and draft.score is not None
        and draft.confidence is not None
    )
    analysis = (
        draft.model_copy(update={"status": "analyzed", "buying_signal": signal})
        if analyzed
        else TurnAnalysis(status="not_analyzed", buying_signal=signal)
    )
    call.negative_streak = call.negative_streak + 1 if analysis.sentiment == "Negative" else 0
    proposal = event["booking"]
    confirmation = None
    lead_update = event["lead_update"]
    if event["action"] == "lead":
        if session.pending and proposal and proposal.intent in {"affirm", "decline"}:
            if proposal.intent == "affirm":
                for key, value in session.pending.model_dump(exclude_none=True).items():
                    setattr(session.profile, key, value)
                confirmation = "Thanks, I’ve confirmed those details."
            else:
                confirmation = "Please tell me the correct details."
            session.pending = None
            proposal = None
        elif lead_update:
            for key, value in lead_update.model_dump(
                exclude_unset=True, exclude_none=True, exclude={"store_count", "target_date"}
            ).items():
                setattr(session.profile, key, value)
            details = ConfirmableDetails(
                store_count=lead_update.store_count, target_date=lead_update.target_date
            )
            if value := details.spoken(bool(HINDI.search(text))):
                session.pending = details
                confirmation = f"I heard {value}. Is that correct?"
    receipt = (
        await asyncio.to_thread(
            booking.advance,
            proposal,
            session.profile.model_dump(mode="json", exclude_none=True, exclude={"language"}),
        )
        if proposal
        else None
    )
    lines = event["lines"]
    blocked = any(line.blocked for line in lines)
    source = next((line.evidence for line in lines if line.evidence), None)
    model_written = any(not line.blocked and line.evidence is None for line in lines)
    spoken = [line.text for line in lines]
    origin = "gemini" if model_written else "knowledge"
    mode = "live" if model_written else "knowledge"
    hindi = bool(HINDI.search(text))
    if receipt or confirmation:
        spoken = [receipt or confirmation]
        origin, mode, source, blocked = "approved", "booking" if receipt else "session", None, False
    elif call.negative_streak == 2:
        spoken = [
            "माफ़ कीजिए। क्या आप हमारी टीम के किसी व्यक्ति से बात करना चाहेंगे?"
            if hindi
            else "I’m sorry this has been frustrating. Would you like to speak with someone from our team?"
        ]
        origin, mode, source, blocked = "approved", "session", None, False
    elif blocked:
        # One replacement for the entire rejected draft. No generated text survives this path.
        spoken = [CHECK_SHORT_HI if hindi else CHECK_SHORT_EN]
        origin, mode, source = "approved", "policy", None
    elif signal == "ready_to_buy":
        next_step = (
            "Would you like to book a demo, and what phone number or email should I use?"
            if not booking.contact
            else "Would you like to book a demo, and what time would suit you in IST?"
        )
        if hindi:
            next_step = (
                "क्या आप डेमो बुक करना चाहेंगे? अपना फ़ोन नंबर या ईमेल बताइए।"
                if not booking.contact
                else "क्या आप डेमो बुक करना चाहेंगे? आईएसटी में कौन सा समय ठीक रहेगा?"
            )
        spoken = ([source.text] if source else []) + [next_step]
        origin, mode = "approved", "knowledge" if source else "session"
    elif signal == "declining":
        if call.decline_question_asked:
            spoken = [
                "समझ गया। हम यहीं रुक सकते हैं।" if hindi else "Understood. We can leave it there."
            ]
        else:
            spoken = [
                "समझ गया। अगर बताना चाहें, तो वजह कीमत, समय या ज़रूरत से जुड़ी है?"
                if hindi
                else "Understood. If you’re comfortable sharing, was it the price, timing, or fit?"
            ]
            call.decline_question_asked = True
        origin, mode, source = "approved", "session", None
    return (
        {
            "type": "reply",
            "text": " ".join(spoken),
            "sentences": spoken,
            "mode": mode,
            "origin": origin,
            "provider": event["model"],
            "latency_ms": event["latency_ms"],
            "citation": {"id": source.id, "title": source.title, "source": source.source}
            if source
            else None,
            "passage": source.text if source else None,
            "guardrail": blocked,
            "booking": booking.snapshot(),
        },
        analysis,
    )
