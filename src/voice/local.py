"""Optional pre-downloaded CPU recognition. Decodes the validated WAV directly."""

import asyncio
import importlib
import io
import logging
import wave
from functools import lru_cache
from time import perf_counter
from typing import Any


@lru_cache(maxsize=2)
def model(name: str) -> Any:
    whisper = importlib.import_module("faster_whisper")
    return whisper.WhisperModel(
        name, device="cpu", compute_type="int8", cpu_threads=4, local_files_only=True
    )


def _recognize(audio: bytes, language: str, name: str) -> str:
    np = importlib.import_module("numpy")
    with wave.open(io.BytesIO(audio)) as clip:
        pcm = np.frombuffer(clip.readframes(clip.getnframes()), dtype="<i2")
    engine = model(name)
    segments, _ = engine.transcribe(pcm.astype(np.float32) / 32768, language=language, beam_size=1)
    return " ".join(segment.text.strip() for segment in segments)


async def recognize(audio: bytes, language: str, name: str) -> str:
    return await asyncio.to_thread(_recognize, audio, language, name)


async def warm() -> None:
    for name in ("base", "small"):
        started = perf_counter()
        try:
            await asyncio.to_thread(model, name)
        except (ImportError, OSError, RuntimeError, ValueError):
            logging.getLogger("uvicorn.error").warning(
                "Whisper %s unavailable in local cache. Use setup --voice-models. Gemini fallback remains available.",
                name,
            )
            continue
        logging.getLogger("uvicorn.error").info(
            "Whisper %s loaded before serving in %.0f ms.", name, (perf_counter() - started) * 1000
        )
