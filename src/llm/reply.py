import asyncio
import random
from collections import deque
from collections.abc import AsyncGenerator
from contextlib import aclosing
from time import monotonic
from typing import Any, Protocol

import httpx

from src.core.settings import Settings
from src.llm.claims import (
    APPROVED,
    CHECK_SHORT_EN,
    CHECK_SHORT_HI,
    HINDI,
    PRODUCT_QUESTION,
    follow_up,
)
from src.llm.gemini import SPOKEN_PROMPT, ProviderError, stream_gemini
from src.llm.mock import MockLLM
from src.llm.sentences import SentenceBuffer

# Cache only fixed synthetic quick prompts, without customer content or conversation history.
CACHEABLE = {"How do I manage multiple stores?", "How much does it cost?", "Can I see a demo?"}


class LLMProvider(Protocol):
    def stream(self, text: str) -> AsyncGenerator[str]: ...


class RequestBudget:
    """One process-wide token bucket and rolling daily request ceiling."""

    def __init__(self, rpm: int, daily: int, tpm: int) -> None:
        self.rpm, self.daily, self.tpm = rpm, daily, tpm
        self.tokens = 3.0
        self.last = monotonic()
        self.calls: deque[float] = deque()
        self.recent_tokens: deque[tuple[float, int]] = deque()
        self.cooldown = 0.0

    def reserve(self, estimated_tokens: int) -> None:
        now = monotonic()
        self.tokens = min(3.0, self.tokens + (now - self.last) * self.rpm / 60)
        self.last = now
        while self.calls and self.calls[0] <= now - 86400:
            self.calls.popleft()
        while self.recent_tokens and self.recent_tokens[0][0] <= now - 60:
            self.recent_tokens.popleft()
        if (
            now < self.cooldown
            or len(self.calls) >= self.daily
            or self.tokens < 1
            or sum(tokens for _, tokens in self.recent_tokens) + estimated_tokens > self.tpm
        ):
            raise ProviderError(429, local=True)
        self.tokens -= 1
        self.calls.append(now)
        self.recent_tokens.append((now, estimated_tokens))


class ReplyPath:
    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        self.settings = settings
        self.client = client
        self.mock: LLMProvider = MockLLM()
        self.budget = RequestBudget(settings.gemini_rpm, settings.gemini_daily, settings.gemini_tpm)
        self.cache: dict[tuple[str, str], tuple[float, str]] = {}

    async def _live(
        self, model: str, thinking: str, text: str, simulate: bool
    ) -> AsyncGenerator[str]:
        if simulate:
            raise ProviderError(503)
        assert self.client is not None and self.settings.gemini_api_key is not None
        key = self.settings.gemini_api_key.get_secret_value().strip()
        cached = self.cache.get((model, text))
        if cached and monotonic() - cached[0] < 300:
            yield cached[1]
            return
        for attempt in range(2):
            self.budget.reserve(len((SPOKEN_PROMPT + text).encode()) + 32)
            parts: list[str] = []
            try:
                async with (
                    asyncio.timeout(9),
                    aclosing(stream_gemini(self.client, key, model, thinking, text)) as chunks,
                ):
                    async for delta in chunks:
                        parts.append(delta)
                        yield delta
                break
            except TimeoutError:
                raise ProviderError(504) from None
            except ProviderError as error:
                if parts or attempt or error.status not in {500, 502, 503, 504}:
                    raise
                await asyncio.sleep(0.15 * 2**attempt + random.uniform(0, 0.1))
        if text in CACHEABLE and parts:
            self.cache[(model, text)] = (monotonic(), "".join(parts))

    async def stream(self, text: str, *, simulate: bool = False) -> AsyncGenerator[dict[str, Any]]:
        settings = self.settings
        if PRODUCT_QUESTION.search(text) and not simulate:
            sentences = follow_up(text)
            yield {
                "type": "provider",
                "provider": "policy",
                "model": "Knowledge guardrail",
                "status": "active",
            }
            for sentence in sentences:
                yield {"type": "sentence", "text": sentence}
            yield {
                "type": "reply",
                "text": " ".join(sentences),
                "provider": "policy",
                "latency_ms": None,
                "mode": "policy",
            }
            return
        slots = (
            ("Gemini A", settings.gemini_model, settings.gemini_thinking),
            ("Gemini B", settings.gemini_fallback_model, settings.gemini_fallback_thinking),
        )
        candidates = (
            [(label, model, thinking) for label, model, thinking in slots if model or simulate]
            if simulate or settings.agent_mode == "live"
            else []
        )
        started = monotonic()
        for label, model, thinking in [*candidates, ("mock", "mock", "")]:
            yield {"type": "provider", "provider": label, "model": model, "status": "trying"}
            buffer = SentenceBuffer()
            parts: list[str] = []
            spoken: list[str] = []
            blocked = False
            first_ms = 0.0
            chunks = (
                self.mock.stream(text)
                if label == "mock"
                else self._live(model, thinking, text, simulate)
            )
            try:
                async with aclosing(chunks) as stream:
                    async for delta in stream:
                        if not parts and not delta.strip():
                            continue
                        if not parts:
                            first_ms = round((monotonic() - started) * 1000, 2)
                            yield {
                                "type": "provider",
                                "provider": label,
                                "model": model,
                                "status": "active",
                            }
                            yield {"type": "first_text", "latency_ms": first_ms}
                        parts.append(delta)
                        for sentence in buffer.push(delta):
                            if sentence in APPROVED and not spoken:
                                spoken.append(sentence)
                                yield {
                                    "type": "delta",
                                    "text": (" " if len(spoken) > 1 else "") + sentence,
                                }
                                yield {"type": "sentence", "text": sentence}
                            elif sentence not in APPROVED:
                                blocked = True
                                break
                        if blocked:
                            break
                if not parts:
                    raise ProviderError(502)
            except ProviderError as error:
                yield {
                    "type": "provider",
                    "provider": label,
                    "model": model,
                    "status": "failed",
                    "code": error.status,
                    "quota": "local limit"
                    if error.local
                    else "provider throttled"
                    if error.status == 429
                    else None,
                }
                if error.status == 429 and not error.local and not simulate:
                    self.budget.cooldown = monotonic() + 10
                if spoken:
                    yield {
                        "type": "error",
                        "text": "The reply was interrupted. Please send a new turn.",
                    }
                    return
                continue
            for sentence in [] if blocked else buffer.finish():
                if sentence in APPROVED and not blocked:
                    spoken.append(sentence)
                    yield {"type": "delta", "text": (" " if len(spoken) > 1 else "") + sentence}
                    yield {"type": "sentence", "text": sentence}
                elif sentence not in APPROVED:
                    blocked = True
            use_policy = not spoken
            if use_policy or blocked:
                yield {
                    "type": "provider",
                    "provider": "policy",
                    "model": "Knowledge guardrail",
                    "status": "active",
                }
                safe = (
                    follow_up(text)
                    if use_policy
                    else (CHECK_SHORT_HI if HINDI.search(text) else CHECK_SHORT_EN,)
                )
                for sentence in safe:
                    if sentence not in spoken:
                        spoken.append(sentence)
                        yield {"type": "sentence", "text": sentence}
            yield {
                "type": "reply",
                "text": " ".join(spoken),
                "provider": model,
                "latency_ms": first_ms,
                "mode": "policy" if use_policy else "mock" if label == "mock" else "live",
            }
            return
