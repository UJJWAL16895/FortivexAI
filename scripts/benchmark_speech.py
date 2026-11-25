"""Short synthetic EN/HI speech comparison. Temporary artifacts stay outside Git."""

import asyncio
import io
import json
import tempfile
import wave
from pathlib import Path
from time import perf_counter

import edge_tts
import httpx
import numpy as np
from av import AudioResampler
from av import open as av_open
from dotenv import dotenv_values
from faster_whisper import WhisperModel

from src.llm.gemini import ProviderError
from src.voice.gemini import synthesize, transcribe

SCRIPTS = {
    "en": ("Our three stores need a demo on Friday.", "en-IN-NeerjaNeural"),
    "hi": ("मेरी तीन दुकानों के लिए शुक्रवार को डेमो चाहिए।", "hi-IN-SwaraNeural"),
}


def to_pcm_wav(audio: bytes) -> bytes:
    target = io.BytesIO()
    with av_open(io.BytesIO(audio)) as src, av_open(target, "w", format="wav") as dst:
        stream = dst.add_stream("pcm_s16le", rate=16000, layout="mono")
        resampler = AudioResampler(format="s16", layout="mono", rate=16000)
        for frame in src.decode(audio=0):
            for converted in resampler.resample(frame):
                for packet in stream.encode(converted):
                    dst.mux(packet)
        for converted in resampler.resample(None):
            for packet in stream.encode(converted):
                dst.mux(packet)
        for packet in stream.encode(None):
            dst.mux(packet)
    return target.getvalue()


async def main() -> None:
    key = dotenv_values(".env").get("GEMINI_API_KEY")
    if not key:
        raise SystemExit("Set GEMINI_API_KEY in the local .env first")
    locations = Path(tempfile.mkdtemp(prefix="fortivex-speech-"))
    print("Synthetic artifacts:", locations, flush=True)
    async with httpx.AsyncClient(timeout=18, trust_env=False) as client:
        for language, (script, voice) in SCRIPTS.items():
            wavs = {}
            for engine in ("edge", "gemini"):
                started = perf_counter()
                try:
                    if engine == "edge":
                        chunks = []
                        first = 0.0
                        async with asyncio.timeout(15):
                            async for item in edge_tts.Communicate(script, voice).stream():
                                if item["type"] == "audio":
                                    if not chunks:
                                        first = (perf_counter() - started) * 1000
                                    chunks.append(item["data"])
                        total = (perf_counter() - started) * 1000
                        wav = to_pcm_wav(b"".join(chunks))
                    else:
                        wav = await synthesize(client, key, "gemini-3.8-flash-tts", script)
                        first = total = (perf_counter() - started) * 1000
                    wavs[engine] = wav
                    (locations / f"{language}-{engine}.wav").write_bytes(wav)
                    print(
                        language,
                        engine,
                        "tts first_ms",
                        round(first),
                        "total_ms",
                        round(total),
                        "wav_bytes",
                        len(wav),
                        flush=True,
                    )
                except Exception as error:
                    print(
                        language,
                        engine,
                        "tts error",
                        getattr(error, "status", type(error).__name__),
                        flush=True,
                    )
            if not wavs:
                continue
            audio = wavs.get("edge") or wavs["gemini"]
            (locations / f"{language}-input.wav").write_bytes(audio)
            started = perf_counter()
            try:
                text = await transcribe(client, key, "gemini-3.5-transcribe", audio)
                print(
                    language,
                    "gemini stt ms",
                    round((perf_counter() - started) * 1000),
                    json.dumps(text),
                    flush=True,
                )
            except ProviderError as error:
                print(language, "gemini stt error", error.status, flush=True)
    if not any(locations.glob("*-input.wav")):
        return
    started = perf_counter()
    try:
        model = WhisperModel("tiny", device="cpu", compute_type="int8")
    except Exception as error:
        print("faster-whisper model load error", type(error).__name__, flush=True)
        return
    print("faster-whisper model startup ms", round((perf_counter() - started) * 1000), flush=True)
    for artifact in sorted(locations.glob("*.wav")):
        if artifact.stem.endswith("-input"):
            continue
        started = perf_counter()
        with wave.open(io.BytesIO(to_pcm_wav(artifact.read_bytes()))) as clip:
            samples = np.frombuffer(clip.readframes(clip.getnframes()), dtype="<i2")
        segments, _ = model.transcribe(samples.astype(np.float32) / 32768, beam_size=1)
        text = " ".join(segment.text.strip() for segment in segments)
        print(
            artifact.stem,
            "faster-whisper ms",
            round((perf_counter() - started) * 1000),
            json.dumps(text),
            flush=True,
        )


if __name__ == "__main__":
    asyncio.run(main())
