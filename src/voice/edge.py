import asyncio

import edge_tts


async def synthesize(text: str) -> bytes:
    voice = (
        "hi-IN-SwaraNeural"
        if any("\u0900" <= char <= "\u097f" for char in text)
        else "en-IN-NeerjaNeural"
    )
    audio = bytearray()
    async with asyncio.timeout(5):
        async for chunk in edge_tts.Communicate(text, voice).stream():
            if chunk["type"] == "audio":
                audio.extend(chunk["data"])
    return bytes(audio)
