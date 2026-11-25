"""Measure the post-clip Gemini Live endpoint to first audio, without exposing credentials."""

import argparse
import asyncio
import base64
import json
import wave
from pathlib import Path
from time import perf_counter
from urllib.parse import urlencode

from dotenv import dotenv_values
from websockets.asyncio.client import connect

ENDPOINT = (
    "wss://generativelanguage.googleapis.com/ws/"
    "google.ai.generativelanguage.v1beta.GenerativeService.BidiGenerateContent"
)


async def probe(key: str, audio: bytes) -> None:
    started = perf_counter()
    async with asyncio.timeout(18), connect(ENDPOINT + "?" + urlencode({"key": key})) as socket:
        await socket.send(
            json.dumps(
                {
                    "setup": {
                        "model": "models/gemini-3.8-live",
                        "generationConfig": {"responseModalities": ["AUDIO"]},
                        "realtimeInputConfig": {"automaticActivityDetection": {"disabled": True}},
                        "inputAudioTranscription": {},
                        "systemInstruction": {
                            "parts": [{"text": "Acknowledge briefly in the caller's language."}]
                        },
                    }
                }
            )
        )
        if "setupComplete" not in json.loads(await socket.recv()):
            print("setup failed")
            return
        await socket.send('{"realtimeInput":{"activityStart":{}}}')
        for start in range(0, len(audio), 3200):
            await socket.send(
                json.dumps(
                    {
                        "realtimeInput": {
                            "audio": {
                                "mimeType": "audio/pcm;rate=16000",
                                "data": base64.b64encode(audio[start : start + 3200]).decode(),
                            }
                        }
                    }
                )
            )
        await socket.send('{"realtimeInput":{"activityEnd":{}}}')
        endpoint = perf_counter()
        first = None
        words = []
        async for event in socket:
            item = json.loads(event).get("serverContent", {})
            if text := item.get("inputTranscription", {}).get("text"):
                words.append(text)
            if first is None and any(
                part.get("inlineData", {}).get("data")
                for part in item.get("modelTurn", {}).get("parts", [])
            ):
                first = perf_counter()
            if item.get("turnComplete"):
                print(
                    "first_audio_ms",
                    round((first - endpoint) * 1000) if first else None,
                    "cold_total_ms",
                    round((first - started) * 1000) if first else None,
                    "transcript",
                    json.dumps("".join(words)),
                    flush=True,
                )
                break


async def main(folder: Path) -> None:
    key = dotenv_values(".env").get("GEMINI_API_KEY")
    if not key:
        raise SystemExit("Missing local Gemini key")
    for language in ("en", "hi"):
        print(language, flush=True)
        try:
            with wave.open(str(folder / f"{language}-input.wav")) as clip:
                await probe(key, clip.readframes(clip.getnframes()))
        except Exception as error:
            code = getattr(getattr(error, "rcvd", None), "code", None)
            print("failed", type(error).__name__, code, flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    asyncio.run(main(parser.parse_args().folder))
