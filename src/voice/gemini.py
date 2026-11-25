import base64
from typing import Any

import httpx

from src.llm.gemini import ProviderError

INTERACTIONS = "https://generativelanguage.googleapis.com/v1beta/interactions"


async def interact(
    client: httpx.AsyncClient, key: str, body: dict[str, Any]
) -> list[dict[str, Any]]:
    try:
        response = await client.post(INTERACTIONS, json=body, headers={"x-goog-api-key": key})
        if not response.is_success:
            raise ProviderError(response.status_code)
        return [
            part
            for step in response.json().get("steps", [])
            if step.get("type") == "model_output"
            for part in step.get("content", [])
        ]
    except (httpx.HTTPError, ValueError, TypeError, AttributeError):
        raise ProviderError(503) from None


async def transcribe(client: httpx.AsyncClient, key: str, model: str, wav: bytes) -> str:
    parts = await interact(
        client,
        key,
        {
            "model": model,
            "input": [
                {
                    "type": "audio",
                    "mime_type": "audio/wav",
                    "data": base64.b64encode(wav).decode("ascii"),
                }
            ],
        },
    )
    return " ".join(part["text"] for part in parts if part.get("type") == "text").strip()


async def synthesize(client: httpx.AsyncClient, key: str, model: str, text: str) -> bytes:
    parts = await interact(
        client,
        key,
        {
            "model": model,
            "input": [{"type": "user_input", "content": [{"type": "text", "text": text}]}],
            "response_format": {"type": "audio", "mime_type": "audio/wav"},
            "generation_config": {"speech_config": [{"voice": "Kore"}]},
        },
    )
    try:
        audio = next(part["data"] for part in reversed(parts) if part.get("type") == "audio")
        wav = base64.b64decode(audio, validate=True)
        if not wav.startswith(b"RIFF"):
            raise ValueError("Expected WAV")
        return wav
    except (KeyError, StopIteration, TypeError, ValueError):
        raise ProviderError(502) from None
