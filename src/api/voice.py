import asyncio
import io
import wave
from time import monotonic
from typing import Annotated

import httpx
from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, StringConstraints

from src.core.settings import Settings
from src.llm.gemini import ProviderError
from src.llm.reply import RequestBudget
from src.voice import edge, gemini

router = APIRouter(prefix="/api/voice", tags=["voice"])
MAX_WAV = 416_000
MOCK_TRANSCRIPT = "Can I manage three stores?"


class Transcript(BaseModel):
    text: str
    provider: str
    latency_ms: float


class SpeechRequest(BaseModel):
    text: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=500)]


def check_origin(request: Request) -> None:
    origin = request.headers.get("origin")
    if origin is not None and origin != f"{request.url.scheme}://{request.headers.get('host')}":
        raise HTTPException(403, "Unexpected browser origin")


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
async def transcribe_audio(request: Request) -> Transcript:
    check_origin(request)
    audio = await read_wav(request)
    settings: Settings = request.app.state.settings
    started = monotonic()
    if settings.agent_mode == "mock":
        return Transcript(text=MOCK_TRANSCRIPT, provider="mock", latency_ms=0)
    assert settings.gemini_api_key is not None
    budget: RequestBudget = request.app.state.voice_budget
    client: httpx.AsyncClient = request.app.state.http
    try:
        budget.reserve(600)
        async with asyncio.timeout(12):
            text = await gemini.transcribe(
                client,
                settings.gemini_api_key.get_secret_value().strip(),
                settings.gemini_stt_model,
                audio,
            )
    except (ProviderError, TimeoutError):
        raise HTTPException(503, "Transcription unavailable. You can type your message.") from None
    if not text or len(text) > 500:
        raise HTTPException(
            422, "No short transcript was detected. Try again or type your message."
        )
    return Transcript(
        text=text,
        provider=settings.gemini_stt_model,
        latency_ms=round((monotonic() - started) * 1000, 2),
    )


@router.post(
    "/speak",
    response_class=Response,
    responses={200: {"content": {"audio/mpeg": {}, "audio/wav": {}}}},
)
async def speak_sentence(request: Request, sentence: SpeechRequest) -> Response:
    check_origin(request)
    settings: Settings = request.app.state.settings
    if settings.agent_mode != "live" or settings.voice_tts == "browser":
        return Response(status_code=204)
    try:
        budget: RequestBudget = request.app.state.voice_budget
        budget.reserve(500)
        if settings.voice_tts == "edge":
            audio = await edge.synthesize(sentence.text)
            if not audio:
                return Response(status_code=204)
            return Response(audio, media_type="audio/mpeg", headers={"X-TTS-Provider": "edge-tts"})
        assert settings.gemini_api_key is not None
        async with asyncio.timeout(8):
            audio = await gemini.synthesize(
                request.app.state.http,
                settings.gemini_api_key.get_secret_value().strip(),
                settings.gemini_tts_model,
                sentence.text,
            )
        return Response(
            audio, media_type="audio/wav", headers={"X-TTS-Provider": settings.gemini_tts_model}
        )
    except Exception:
        # Plug-in service errors can contain URLs or caller text. The browser can synthesize locally.
        return Response(status_code=204)
