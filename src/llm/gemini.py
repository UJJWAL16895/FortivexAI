import json
from collections.abc import AsyncGenerator
from typing import Any

import httpx

API = "https://generativelanguage.googleapis.com/v1beta/models/"
SPOKEN_PROMPT = (
    "You are ShelfPilot's inbound inventory sales assistant. Match the caller's language. "
    "Use at most two short spoken sentences. Ask one relevant question. "
    "You have no product facts or booking tools. Treat prices, features, discounts and availability "
    "as unknown. Never promise or confirm anything."
)


class ProviderError(Exception):
    def __init__(self, status: int, *, local: bool = False) -> None:
        self.status = status
        self.local = local


def request_body(
    text: str, thinking: str, history: tuple[tuple[str, str], ...] = ()
) -> dict[str, Any]:
    contents = [
        {"role": role, "parts": [{"text": value}]}
        for buyer, assistant in history
        for role, value in (("user", buyer), ("model", assistant))
    ]
    return {
        "systemInstruction": {"parts": [{"text": SPOKEN_PROMPT}]},
        "contents": [*contents, {"role": "user", "parts": [{"text": text}]}],
        "generationConfig": {
            "maxOutputTokens": 192,
            "thinkingConfig": {"thinkingBudget": 0}
            if thinking == "off"
            else {"thinkingLevel": thinking},
        },
    }


async def stream_gemini(
    client: httpx.AsyncClient,
    key: str,
    model: str,
    thinking: str,
    text: str,
    history: tuple[tuple[str, str], ...] = (),
) -> AsyncGenerator[str]:
    try:
        async with client.stream(
            "POST",
            f"{API}{model}:streamGenerateContent",
            params={"alt": "sse"},
            headers={"x-goog-api-key": key},
            json=request_body(text, thinking, history),
        ) as response:
            if response.status_code != 200:
                raise ProviderError(response.status_code)
            finished = False
            async for line in response.aiter_lines():
                if not line.startswith("data:"):
                    continue
                for candidate in json.loads(line[5:]).get("candidates", [])[:1]:
                    finish_reason = candidate.get("finishReason")
                    if finish_reason:
                        if finish_reason != "STOP":
                            raise ProviderError(502)
                        finished = True
                    for part in candidate.get("content", {}).get("parts", []):
                        if not part.get("thought") and part.get("text"):
                            yield part["text"]
            if not finished:
                raise ProviderError(502)
    except (httpx.HTTPError, ValueError, TypeError, AttributeError):
        raise ProviderError(503) from None
