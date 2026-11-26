import asyncio
import io
import wave
from time import monotonic
from typing import Annotated, Literal

import httpx
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, StringConstraints

from src.api.live_mode import ConnectionMode
from src.core.settings import Settings
from src.llm.gemini import ProviderError
from src.llm.reply import RequestBudget
from src.voice import edge, gemini, local

router = APIRouter(prefix="/api/voice", tags=["voice"])
MAX_WAV = 416_000
MOCK_TRANSCRIPT = "Can I manage three stores?"


class Transcript(BaseModel):
    text: str
    provider: str
    latency_ms: float
    api_ms: float


class SpeechRequest(BaseModel):
    text: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]


def check_origin(request: Request) -> None:
    origin = request.headers.get("origin")
    if origin is not None and origin != f"{request.url.scheme}://{request.headers.get('host')}":
        raise HTTPException(403, "Unexpected browser origin")


def connection_mode(request: Request) -> ConnectionMode | None:
    handle = request.headers.get("X-Voice-Session")
    if handle is None:
        return None
    state: ConnectionMode | None = request.app.state.voice_sessions.get(handle)
    if state is None:
        raise HTTPException(409, "Voice session expired. Reconnect to the console.")
    return state


def voice_budget(request: Request) -> RequestBudget:
    budget: RequestBudget = request.app.state.replies.budget
    return budget


async def read_wav(request: Request) -> bytes:
    if request.headers.get("content-type") != "audio/wav":
        raise HTTPException(415, "Send mono 16 kHz PCM WAV")
    audio = bytearray()
    async for chunk in request.stream():
        if len(audio) + len(chunk) > MAX_WAV:
            raise HTTPException(413, "Recording is too large")
        audio.extend(chunk)
    try:
        with wave.open(io.BytesIO(audio)) as clip:
            frames = clip.getnframes()
            if (clip.getnchannels(), clip.getsampwidth(), clip.getframerate()) != (1, 2, 16000):
                raise ValueError
            if not 1 <= frames <= 208000 or len(clip.readframes(frames)) != frames * 2:
                raise ValueError
    except (wave.Error, EOFError, ValueError):
        raise HTTPException(422, "Invalid or empty PCM WAV recording") from None
    return bytes(audio)


@router.post(
    "/transcribe",
    response_model=Transcript,
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {"audio/wav": {"schema": {"type": "string", "format": "binary"}}},
        }
    },
)
async def transcribe_audio(request: Request, language: Literal["en", "hi"] = "en") -> Transcript:
    check_origin(request)
    received = monotonic()
    audio = await read_wav(request)
    settings: Settings = request.app.state.settings
    started = monotonic()
    state = connection_mode(request)
    budget = voice_budget(request)
    if state and state.mode == "live":
        usage = budget.usage()
        if usage["used"] >= usage["cap"]:
            state.quota_notice = True
    if (state.mode if state else settings.agent_mode) == "mock" or (state and state.quota_notice):
        return Transcript(
            text=MOCK_TRANSCRIPT,
            provider="mock",
            latency_ms=0,
            api_ms=(monotonic() - received) * 1000,
        )
    assert settings.gemini_api_key is not None
    client: httpx.AsyncClient = request.app.state.http
    providers = (
        ("local", "gemini")
        if settings.voice_stt == "local" and not (state and state.cloud_stt)
        else ("gemini", "local")
    )
    for provider in providers:
        try:
            if provider == "local":
                name = "small" if language == "hi" else settings.whisper_en_model
                async with asyncio.timeout(5):
                    text = await local.recognize(audio, language, name)
                label = f"faster-whisper {name}"
            else:
                budget.reserve(600)
                async with asyncio.timeout(10):
                    text = await gemini.transcribe(
                        client,
                        settings.gemini_api_key.get_secret_value().strip(),
                        settings.gemini_stt_model,
                        audio,
                    )
                label = settings.gemini_stt_model
        except ProviderError as error:
            if state and error.status == 429:
                state.quota_notice = True
            continue
        except (TimeoutError, ImportError, OSError, RuntimeError, ValueError):
            continue
        if text.strip() and len(text) <= 500:
            now = monotonic()
            return Transcript(
                text=text,
                provider=label,
                latency_ms=(now - started) * 1000,
                api_ms=(now - received) * 1000,
            )
    if state and state.quota_notice:
        return Transcript(
            text=MOCK_TRANSCRIPT,
            provider="mock",
            latency_ms=0,
            api_ms=(monotonic() - received) * 1000,
        )
    raise HTTPException(503, "Transcription unavailable. Type your message to continue.")


@router.post(
    "/speak",
    response_class=Response,
    responses={200: {"content": {"audio/mpeg": {}, "audio/wav": {}}}},
)
async def speak_sentence(request: Request, sentence: SpeechRequest) -> Response:
    check_origin(request)
    settings: Settings = request.app.state.settings
    state = connection_mode(request)
    if (
        (state.mode if state else settings.agent_mode) != "live"
        or settings.voice_tts == "browser"
        or (state is not None and state.quota_notice)
    ):
        return Response(status_code=204)
    try:
        budget = (
            voice_budget(request)
            if settings.voice_tts == "gemini"
            else request.app.state.voice_budget
        )
        budget.reserve(500)
        if settings.voice_tts == "edge":
            audio, first_byte = await edge.synthesize(sentence.text)
            if not audio:
                return Response(status_code=204)
            return Response(
                audio,
                media_type="audio/mpeg",
                headers={"X-TTS-Provider": "edge-tts", "X-TTS-First-Byte-Ms": str(first_byte)},
            )
        assert settings.gemini_api_key is not None
        started = monotonic()
        async with asyncio.timeout(8):
            audio = await gemini.synthesize(
                request.app.state.http,
                settings.gemini_api_key.get_secret_value().strip(),
                settings.gemini_tts_model,
                sentence.text,
            )
        return Response(
            audio,
            media_type="audio/wav",
            headers={
                "X-TTS-Provider": settings.gemini_tts_model,
                "X-TTS-First-Byte-Ms": str((monotonic() - started) * 1000),
            },
        )
    except ProviderError as error:
        if state and settings.voice_tts == "gemini" and error.status == 429:
            state.quota_notice = True
        return Response(status_code=204)
    except Exception:
        # Plug-in service errors can contain URLs or caller text. The browser can synthesize locally.
        return Response(status_code=204)
