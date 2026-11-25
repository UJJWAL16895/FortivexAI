"""Optional pre-downloaded CPU recognition. Decodes the validated WAV directly."""

import asyncio
import importlib
import io
import wave
from functools import lru_cache
from typing import Any


@lru_cache(maxsize=2)
def model(name: str) -> Any:
    whisper = importlib.import_module("faster_whisper")
    return whisper.WhisperModel(
        name, device="cpu", compute_type="int8", cpu_threads=4, local_files_only=True
    )


def _recognize(audio: bytes, language: str) -> str:
    np = importlib.import_module("numpy")
    with wave.open(io.BytesIO(audio)) as clip:
        pcm = np.frombuffer(clip.readframes(clip.getnframes()), dtype="<i2")
    engine = model("small" if language == "hi" else "base")
    segments, _ = engine.transcribe(pcm.astype(np.float32) / 32768, language=language, beam_size=1)
    return " ".join(segment.text.strip() for segment in segments)


async def recognize(audio: bytes, language: str) -> str:
    return await asyncio.to_thread(_recognize, audio, language)


async def warm() -> None:
    for name in ("base", "small"):
        try:
            await asyncio.to_thread(model, name)
        except (ImportError, OSError, RuntimeError, ValueError):
            # A missing local model leaves the Gemini fallback available.
            continue
