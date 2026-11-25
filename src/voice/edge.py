import asyncio
from time import monotonic

import edge_tts


async def synthesize(text: str) -> tuple[bytes, float]:
    voice = (
        "hi-IN-SwaraNeural"
        if any("\u0900" <= char <= "\u097f" for char in text)
        else "en-IN-NeerjaNeural"
    )
    audio = bytearray()
    started = monotonic()
    first_byte = 0.0
    async with asyncio.timeout(5):
        async for chunk in edge_tts.Communicate(text, voice).stream():
            if chunk["type"] == "audio":
                if not audio:
                    first_byte = (monotonic() - started) * 1000
                audio.extend(chunk["data"])
    return bytes(audio), first_byte
