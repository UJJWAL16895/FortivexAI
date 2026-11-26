import asyncio
import json
import random
from collections import deque
from collections.abc import AsyncGenerator
from contextlib import aclosing
from time import monotonic
from typing import Any, Protocol

import httpx
from pydantic import ValidationError

from src.core.settings import Settings
from src.llm.conversation import PERSONA, Evidence, LiveDraft, check_line, sentences
from src.llm.gemini import ProviderError, stream_gemini
from src.llm.mock import MockLLM
from src.llm.sentences import SentenceBuffer

REPLY_TIMEOUT = 9.0


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

    def usage(self) -> dict[str, int]:
        now = monotonic()
        while self.calls and self.calls[0] <= now - 86400:
            self.calls.popleft()
        return {"used": len(self.calls), "cap": self.daily}

    def reserve(self, estimated_tokens: int) -> None:
        now = monotonic()
        self.tokens = min(3.0, self.tokens + (now - self.last) * self.rpm / 60)
        self.last = now
        usage = self.usage()
        while self.recent_tokens and self.recent_tokens[0][0] <= now - 60:
            self.recent_tokens.popleft()
        if (
            now < self.cooldown
            or usage["used"] >= usage["cap"]
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

    async def converse(
        self,
        text: str,
        history: tuple[tuple[str, str], ...],
        profile: dict[str, Any],
        evidence: tuple[Evidence, ...],
    ) -> AsyncGenerator[dict[str, Any]]:
        settings = self.settings
        context = json.dumps(
            {
                "lead": profile,
                "passages": [{"id": item.id, "text": item.text} for item in evidence],
            },
            ensure_ascii=False,
        )
        system = PERSONA + "\nSession data: " + context
        started = monotonic()
        for label, model, thinking in (
            ("Gemini A", settings.gemini_model, settings.gemini_thinking),
            ("Gemini B", settings.gemini_fallback_model, settings.gemini_fallback_thinking),
        ):
            if not model:
                continue
            yield {"type": "provider", "provider": label, "model": model, "status": "trying"}
            first = None
            raw = ""
            try:
                async with aclosing(self._live(model, thinking, text, history, system)) as stream:
                    async for delta in stream:
                        if first is None and delta.strip():
                            first = round((monotonic() - started) * 1000, 2)
                            yield {"type": "first_text", "latency_ms": first}
                        raw += delta
                        if len(raw) > 2400:
                            raise ProviderError(502)
                draft = LiveDraft.model_validate_json(raw)
            except (ProviderError, ValidationError) as error:
                code = error.status if isinstance(error, ProviderError) else 502
                if code == 429 and isinstance(error, ProviderError) and not error.local:
                    self.budget.cooldown = monotonic() + 10
                yield {
                    "type": "provider",
                    "provider": label,
                    "model": model,
                    "status": "failed",
                    "code": code,
                }
                continue
            lines = [
                check_line(line.model_copy(update={"text": sentence}), evidence)
                for line in draft.lines
                for sentence in sentences(line.text)
            ][:2]
            if not lines:
                yield {
                    "type": "provider",
                    "provider": label,
                    "model": model,
                    "status": "failed",
                    "code": 502,
                }
                continue
            yield {"type": "provider", "provider": label, "model": model, "status": "active"}
            yield {
                "type": "draft",
                "action": draft.action,
                "lines": lines,
                "model": model,
                "latency_ms": first,
            }
            return
        yield {"type": "unavailable"}

    async def _live(
        self,
        model: str,
        thinking: str,
        text: str,
        history: tuple[tuple[str, str], ...],
        system: str,
    ) -> AsyncGenerator[str]:
        assert self.client is not None and self.settings.gemini_api_key is not None
        key = self.settings.gemini_api_key.get_secret_value().strip()
        context_bytes = sum(
            len(buyer.encode()) + len(agent.encode()) + 16 for buyer, agent in history
        )
        for attempt in range(2):
            self.budget.reserve(len((system + text).encode()) + context_bytes + 32)
            parts: list[str] = []
            try:
                async with (
                    asyncio.timeout(REPLY_TIMEOUT),
                    aclosing(
                        stream_gemini(
                            self.client,
                            key,
                            model,
                            thinking,
                            text,
                            history,
                            system,
                            LiveDraft.model_json_schema(),
                        )
                    ) as chunks,
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

    async def stream(self, text: str, *, simulate: bool = False) -> AsyncGenerator[dict[str, Any]]:
        if simulate:
            for label, model in (
                ("Gemini A", self.settings.gemini_model),
                ("Gemini B", self.settings.gemini_fallback_model),
            ):
                yield {
                    "type": "provider",
                    "provider": label,
                    "model": model,
                    "status": "failed",
                    "code": 503,
                }
        started = monotonic()
        yield {"type": "provider", "provider": "mock", "model": "mock", "status": "active"}
        buffer = SentenceBuffer()
        draft = ""
        async for chunk in self.mock.stream(text):
            draft += chunk
        first = round((monotonic() - started) * 1000, 2)
        yield {"type": "first_text", "latency_ms": first}
        yield {"type": "delta", "text": draft}
        for sentence in [*buffer.push(draft), *buffer.finish()]:
            yield {"type": "sentence", "text": sentence}
        yield {
            "type": "reply",
            "text": draft,
            "mode": "mock",
            "origin": "mock",
            "provider": "mock",
            "latency_ms": first,
        }
