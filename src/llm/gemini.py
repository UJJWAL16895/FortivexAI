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
    def __init__(self, status: int, *, local: bool = False, invalid_key: bool = False) -> None:
        self.status = status
        self.local = local
        self.invalid_key = invalid_key


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


async def probe_gemini(client: httpx.AsyncClient, key: str, model: str, thinking: str) -> None:
    body = request_body("Reply OK.", thinking)
    del body["systemInstruction"]
    body["generationConfig"]["maxOutputTokens"] = 8
    try:
        response = await client.post(
            f"{API}{model}:generateContent", headers={"x-goog-api-key": key}, json=body
        )
    except httpx.TimeoutException:
        raise TimeoutError from None
    except httpx.HTTPError:
        raise ProviderError(503) from None
    if response.status_code != 200:
        raise ProviderError(
            response.status_code, invalid_key=b'"API_KEY_INVALID"' in response.content
        )
    try:
        parts = response.json()["candidates"][0]["content"]["parts"]
        if any(part.get("text", "").strip() and not part.get("thought") for part in parts):
            return
    except (KeyError, IndexError, ValueError, TypeError, AttributeError):
        pass
    raise ProviderError(502)
