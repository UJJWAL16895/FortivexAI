"""Socket-owned mode and an opaque handle for its existing HTTP voice requests."""

import asyncio
import logging
from dataclasses import dataclass
from time import monotonic
from typing import Literal

from fastapi import WebSocket

from src.core.settings import Settings
from src.llm.gemini import ProviderError, probe_gemini
from src.llm.reply import ReplyPath
from src.voice.local import warm

Mode = Literal["mock", "live"]
logger = logging.getLogger("uvicorn.error")


@dataclass
class ConnectionMode:
    mode: Mode
    cloud_stt: bool = False
    quota_notice: bool = False
    warmed: bool = False


def live_allowed(settings: Settings) -> bool:
    return not settings.public_demo or settings.public_live_enabled


def provider_reason(error: ProviderError) -> str:
    if error.status == 429:
        return (
            "Live quota reached, using mock"
            if error.local
            else "Gemini returned a quota limit (HTTP 429)."
        )
    if error.status == 401 or error.invalid_key:
        return "Gemini rejected the API key as invalid."
    if error.status == 403:
        return "Gemini denied access (HTTP 403). Check API key restrictions and model access."
    if error.status == 404:
        return "The configured Gemini model was not found (HTTP 404)."
    if error.status == 503:
        return "Gemini is unavailable or could not be reached (503)."
    return f"Gemini readiness failed (HTTP {error.status})."


async def send_mode(
    socket: WebSocket,
    state: ConnectionMode,
    replies: ReplyPath,
    phase: str,
    message: str = "",
    *,
    probe_ms: float | None = None,
) -> None:
    await socket.send_json(
        {
            "type": "mode_status",
            "mode": state.mode,
            "phase": phase,
            "message": message,
            "model": replies.settings.gemini_model
            if state.mode == "live" or probe_ms is not None
            else None,
            "probe_ms": probe_ms,
            "quota": replies.budget.usage(),
        }
    )


async def switch_mode(
    socket: WebSocket, state: ConnectionMode, target: Mode, replies: ReplyPath
) -> None:
    settings = replies.settings
    if target == "mock":
        state.mode = "mock"
        state.quota_notice = False
        logger.info("Connection mode set to mock")
        await send_mode(socket, state, replies, "ready", "Mock mode enabled.")
        return
    state.mode = "mock"
    if not live_allowed(settings):
        await send_mode(
            socket, state, replies, "failed", "Live switching is disabled for this public preview."
        )
        return
    key = settings.gemini_api_key.get_secret_value().strip() if settings.gemini_api_key else ""
    if not key or key.startswith("replace_with_"):
        await send_mode(socket, state, replies, "failed", "No API key configured on the server")
        return
    if not settings.gemini_model or settings.gemini_model == settings.gemini_fallback_model:
        await send_mode(
            socket,
            state,
            replies,
            "failed",
            "Configure a valid Gemini model and distinct fallback.",
        )
        return
    await send_mode(socket, state, replies, "checking", "Checking Gemini…")
    started = monotonic()
    try:
        replies.budget.reserve(32)
        assert replies.client is not None
        async with asyncio.timeout(10):
            await probe_gemini(replies.client, key, settings.gemini_model, settings.gemini_thinking)
    except ProviderError as error:
        if error.status == 429 and not error.local:
            replies.budget.cooldown = monotonic() + 10
        await send_mode(socket, state, replies, "failed", provider_reason(error))
        return
    except TimeoutError:
        await send_mode(socket, state, replies, "failed", "Gemini readiness timed out.")
        return
    probe_ms = round((monotonic() - started) * 1000, 2)
    await send_mode(socket, state, replies, "warming", "Warming up voice…", probe_ms=probe_ms)
    message = "Live mode enabled."
    if settings.voice_stt == "local":
        try:
            async with asyncio.timeout(20):
                state.warmed = state.warmed or await warm()
                state.cloud_stt = not state.warmed
        except TimeoutError:
            state.cloud_stt = True
        if state.cloud_stt:
            message = "Whisper unavailable. Gemini STT will be used as the fallback."
    else:
        state.cloud_stt = True
        message = "Live mode enabled. Voice uses Gemini STT."
    state.mode = "live"
    state.quota_notice = False
    logger.info("Connection mode set to live")
    await send_mode(socket, state, replies, "ready", message, probe_ms=probe_ms)
